"""Safely refresh the locally stored NBA Skills database.

All remote data is collected before the live database is touched. The update is
then built and validated in a temporary SQLite database. Only a complete update
is published, and the previous database is retained as ``data/nba.db.bak``.
"""

import argparse
import os
import shutil
import tempfile
import time
from collections.abc import Callable, Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect
from tqdm import tqdm

from src.db.database import DB_PATH, engine as production_engine
from src.db.save import replace_season_rows, save_table
from src.metrics.creation import get_creation_metrics
from src.metrics.defense import get_defense_metrics
from src.metrics.offball import get_offball_metrics
from src.metrics.physicality import get_physicality_metrics
from src.nba_api_wrapper.basic import basic_info
from src.nba_api_wrapper.playerinfo import player_info
from src.nba_api_wrapper.session import configure_nba_session, refresh_nba_session
from src.nba_api_wrapper.teaminfo import team_directory
from src.utils.general import SEASON_END, SEASON_START


MINIMUM_MINUTES = 100
SEASON_TABLES = ("basic_info", "creation", "offball", "defense", "physicality")
METRIC_UPDATES: tuple[tuple[str, Callable[[int, int], pd.DataFrame]], ...] = (
    ("creation", get_creation_metrics),
    ("offball", get_offball_metrics),
    ("defense", get_defense_metrics),
    ("physicality", get_physicality_metrics),
)


def fetch_with_retries(label: str, fetch: Callable[[], pd.DataFrame], attempts: int) -> pd.DataFrame:
    """Retry a remote dataset without ever accepting a partial result."""
    for attempt in range(1, attempts + 1):
        try:
            return fetch()
        except Exception:
            if attempt == attempts:
                raise
            delay = 5 * attempt
            print(f"{label} failed (attempt {attempt}/{attempts}); retrying in {delay}s")
            refresh_nba_session()
            time.sleep(delay)
    raise RuntimeError(f"{label} could not be downloaded")


def seasons_between(start_year: int, end_year: int) -> range:
    if start_year > end_year:
        raise ValueError("start year cannot be later than end year")
    return range(start_year, end_year + 1)


def collect_seasons(
    label: str,
    fetch: Callable[[int, int], pd.DataFrame],
    seasons: Iterable[int],
    retries: int,
) -> pd.DataFrame:
    frames = []
    for season in seasons:
        print(f"Updating {label}: {season - 1}-{season % 100:02d}")
        frames.append(
            fetch_with_retries(
                f"{label} {season}",
                lambda season=season: fetch(season, MINIMUM_MINUTES),
                retries,
            )
        )
    return pd.concat(frames, ignore_index=True)


def update_player_metadata(player_ids: list[int], sleep: float, retries: int) -> pd.DataFrame:
    rows = []
    for player_id in tqdm(player_ids, desc="Updating player profiles"):
        rows.append(
            fetch_with_retries(
                f"player profile {player_id}",
                lambda player_id=player_id: player_info(player_id, sleep=sleep),
                retries,
            )
        )
    return pd.concat(rows, ignore_index=True).drop_duplicates(subset="PLAYER_ID", keep="last")


def merge_current_player_metadata(
    basic: pd.DataFrame,
    existing_players: pd.DataFrame,
    new_players: pd.DataFrame,
) -> pd.DataFrame:
    """Reuse known profiles and apply current team data from the season table."""
    current_ids = set(basic["PLAYER_ID"])
    known_players = existing_players[existing_players["PLAYER_ID"].isin(current_ids)]
    current_players = pd.concat([known_players, new_players], ignore_index=True)
    current_players = current_players.drop_duplicates(subset="PLAYER_ID", keep="last")

    team_data = basic.drop_duplicates(subset="PLAYER_ID").set_index("PLAYER_ID")
    current_players["TEAM_ID"] = current_players["PLAYER_ID"].map(team_data["TEAM_ID"])
    current_players["TEAM_ABBREVIATION"] = current_players["PLAYER_ID"].map(team_data["TEAM"])
    return current_players


def validate_update_frames(tables: dict[str, pd.DataFrame], seasons: Iterable[int]) -> None:
    """Reject incomplete or malformed downloads before staging them."""
    for season in seasons:
        basic = tables["basic_info"]
        basic = basic[basic["SEASON"] == season]
        if basic.empty:
            raise ValueError(f"basic_info has no rows for season {season}")
        if basic["PLAYER_ID"].duplicated().any():
            raise ValueError(f"basic_info has duplicate players for season {season}")
        expected_players = set(basic["PLAYER_ID"])

        for table_name in SEASON_TABLES:
            frame = tables[table_name]
            required = {"PLAYER_ID", "SEASON", "MIN"}
            missing = required - set(frame.columns)
            if missing:
                raise ValueError(f"{table_name} is missing columns: {sorted(missing)}")

            season_frame = frame[frame["SEASON"] == season]
            if season_frame.empty:
                raise ValueError(f"{table_name} has no rows for season {season}")
            if season_frame["PLAYER_ID"].duplicated().any():
                raise ValueError(f"{table_name} has duplicate players for season {season}")
            if set(season_frame["PLAYER_ID"]) != expected_players:
                raise ValueError(f"{table_name} player coverage differs from basic_info for season {season}")

            numeric = season_frame.select_dtypes(include="number")
            if np.isinf(numeric.to_numpy()).any():
                raise ValueError(f"{table_name} contains infinite values for season {season}")

    players = tables["players"]
    if players.empty or players["PLAYER_ID"].duplicated().any():
        raise ValueError("player metadata is empty or contains duplicate players")
    all_player_ids = set(tables["basic_info"]["PLAYER_ID"])
    if not all_player_ids.issubset(set(players["PLAYER_ID"])):
        raise ValueError("player metadata does not cover every downloaded player")


def validate_staged_database(stage_engine, expected_seasons: Iterable[int], full: bool) -> None:
    expected_seasons = set(expected_seasons)
    table_names = set(inspect(stage_engine).get_table_names())
    required_tables = set(SEASON_TABLES) | {"players", "teams"}
    if not required_tables.issubset(table_names):
        raise ValueError(f"staged database is missing tables: {sorted(required_tables - table_names)}")

    basic_ids: dict[int, set[int]] = {}
    for season in expected_seasons:
        rows = pd.read_sql(
            "SELECT PLAYER_ID FROM basic_info WHERE SEASON = :season",
            stage_engine,
            params={"season": season},
        )
        basic_ids[season] = set(rows["PLAYER_ID"])

    for table_name in SEASON_TABLES:
        seasons = set(
            pd.read_sql(f"SELECT DISTINCT SEASON FROM {table_name}", stage_engine)["SEASON"]
            .astype(int)
            .tolist()
        )
        if full and seasons != expected_seasons:
            raise ValueError(f"{table_name} has unexpected seasons: {sorted(seasons)}")
        if not expected_seasons.issubset(seasons):
            raise ValueError(f"{table_name} is missing an expected season")

        for season in expected_seasons:
            rows = pd.read_sql(
                f"SELECT PLAYER_ID FROM {table_name} WHERE SEASON = :season",
                stage_engine,
                params={"season": season},
            )
            if rows["PLAYER_ID"].duplicated().any() or set(rows["PLAYER_ID"]) != basic_ids[season]:
                raise ValueError(f"{table_name} failed staged coverage validation for season {season}")


def publish_database(
    tables: dict[str, pd.DataFrame],
    seasons: Iterable[int],
    full: bool,
) -> None:
    """Build a temporary database, validate it, and atomically publish it."""
    seasons = tuple(seasons)
    db_path = Path(DB_PATH)
    backup_path = db_path.with_suffix(f"{db_path.suffix}.bak")
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix="nba-update-",
        suffix=".db",
        dir=db_path.parent,
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)
    stage_engine = None

    try:
        if not full:
            shutil.copy2(db_path, temporary_path)
        stage_engine = create_engine(f"sqlite:///{temporary_path}")

        for table_name in SEASON_TABLES:
            if full:
                save_table(tables[table_name], table_name, stage_engine)
            else:
                replace_season_rows(tables[table_name], table_name, seasons[0], stage_engine)

        if full:
            save_table(tables["players"], "players", stage_engine)
            save_table(tables["teams"], "teams", stage_engine)
        else:
            existing_players = pd.read_sql("SELECT * FROM players", stage_engine)
            new_players = tables["players"]
            existing_players = existing_players[
                ~existing_players["PLAYER_ID"].isin(new_players["PLAYER_ID"])
            ]
            save_table(
                pd.concat([existing_players, new_players], ignore_index=True),
                "players",
                stage_engine,
            )

        validate_staged_database(stage_engine, seasons, full)
        stage_engine.dispose()
        stage_engine = None

        production_engine.dispose()
        shutil.copy2(db_path, backup_path)
        os.replace(temporary_path, db_path)
        print(f"Published validated database. Previous version: {backup_path}")
    finally:
        if stage_engine is not None:
            stage_engine.dispose()
        if temporary_path.exists():
            temporary_path.unlink()


def run_full(start_year: int, end_year: int, player_sleep: float, retries: int):
    seasons = tuple(seasons_between(start_year, end_year))
    tables = {"basic_info": collect_seasons("basic player data", basic_info, seasons, retries)}
    for table_name, metric_function in METRIC_UPDATES:
        tables[table_name] = collect_seasons(table_name, metric_function, seasons, retries)

    player_ids = sorted(tables["basic_info"]["PLAYER_ID"].unique().tolist())
    tables["players"] = update_player_metadata(player_ids, player_sleep, retries)
    tables["teams"] = team_directory()
    validate_update_frames(tables, seasons)
    publish_database(tables, seasons, full=True)
    print("Full database refresh complete (including local team metadata).")


def run_latest(end_year: int, player_sleep: float, retries: int):
    tables = {
        "basic_info": fetch_with_retries(
            f"basic player data {end_year}",
            lambda: basic_info(end_year, minimum=MINIMUM_MINUTES),
            retries,
        )
    }
    for table_name, metric_function in METRIC_UPDATES:
        print(f"Updating {table_name}: {end_year - 1}-{end_year % 100:02d}")
        tables[table_name] = fetch_with_retries(
            f"{table_name} {end_year}",
            lambda metric_function=metric_function: metric_function(
                end_year,
                minimum=MINIMUM_MINUTES,
            ),
            retries,
        )

    existing_players = pd.read_sql("SELECT * FROM players", production_engine)
    current_ids = set(tables["basic_info"]["PLAYER_ID"])
    known_ids = set(existing_players["PLAYER_ID"])
    new_player_ids = sorted(current_ids - known_ids)
    print(
        f"Updating {len(new_player_ids)} new player profiles "
        f"({len(current_ids) - len(new_player_ids)} existing profiles reused)."
    )
    if new_player_ids:
        new_players = update_player_metadata(new_player_ids, player_sleep, retries)
    else:
        new_players = existing_players.iloc[0:0].copy()
    tables["players"] = merge_current_player_metadata(
        tables["basic_info"],
        existing_players,
        new_players,
    )
    validate_update_frames(tables, (end_year,))
    publish_database(tables, (end_year,), full=False)
    print("Latest-season database refresh complete (team metadata unchanged).")


def parse_args():
    parser = argparse.ArgumentParser(description="Refresh the local NBA Skills database.")
    parser.add_argument("mode", choices=("full", "latest"), help="Refresh all seasons or only the end year.")
    parser.add_argument("--start-year", type=int, default=SEASON_START, help=f"First full-refresh season (default: {SEASON_START}).")
    parser.add_argument("--end-year", type=int, default=SEASON_END, help=f"Last season / latest refresh season (default: {SEASON_END}).")
    parser.add_argument("--player-sleep", type=float, default=3, help="Seconds to wait between CommonPlayerInfo requests (default: 3).")
    parser.add_argument("--retries", type=int, default=3, help="Attempts for each remote dataset (default: 3).")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.player_sleep < 0:
        raise ValueError("player sleep cannot be negative")
    if args.retries < 1:
        raise ValueError("retries must be at least one")
    configure_nba_session()
    if args.mode == "full":
        run_full(args.start_year, args.end_year, args.player_sleep, args.retries)
    else:
        run_latest(args.end_year, args.player_sleep, args.retries)


if __name__ == "__main__":
    main()
