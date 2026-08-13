"""Refresh the locally stored NBA Skills database.

Examples:
    python -m scripts.update.update_database full
    python -m scripts.update.update_database latest
    python -m scripts.update.update_database full --start-year 2019 --end-year 2026

All NBA API calls occur here, never during dashboard requests. ``full``
rebuilds every season in the requested range and refreshes team metadata.
``latest`` replaces only the end-year rows and deliberately leaves teams alone.
"""

import argparse
from collections.abc import Callable

import pandas as pd
from tqdm import tqdm

from src.db.load import load_table
from src.db.save import replace_season_rows, save_table
from src.metrics.creation import get_creation_metrics
from src.metrics.defense import get_defense_metrics
from src.metrics.offball import get_offball_metrics
from src.metrics.physicality import get_physicality_metrics
from src.nba_api_wrapper.basic import basic_info
from src.nba_api_wrapper.playerinfo import player_info
from src.nba_api_wrapper.teaminfo import team_directory
from src.utils.general import SEASON_END, SEASON_START


MINIMUM_MINUTES = 100
METRIC_UPDATES: tuple[tuple[str, Callable[[int, int], pd.DataFrame]], ...] = (
    ("creation", get_creation_metrics),
    ("offball", get_offball_metrics),
    ("defense", get_defense_metrics),
    ("physicality", get_physicality_metrics),
)


def seasons_between(start_year: int, end_year: int) -> range:
    if start_year > end_year:
        raise ValueError("start year cannot be later than end year")
    return range(start_year, end_year + 1)


def collect_seasons(
    label: str,
    fetch: Callable[[int, int], pd.DataFrame],
    seasons: range,
) -> pd.DataFrame:
    """Fetch all requested seasons before replacing the corresponding table."""
    frames = []
    for season in seasons:
        print(f"Updating {label}: {season - 1}-{season % 100:02d}")
        frames.append(fetch(season, MINIMUM_MINUTES))
    return pd.concat(frames, ignore_index=True)


def update_player_metadata(player_ids: list[int], sleep: float) -> pd.DataFrame:
    rows = []
    for player_id in tqdm(player_ids, desc="Updating player profiles"):
        rows.append(player_info(player_id, sleep=sleep))
    return pd.concat(rows, ignore_index=True).drop_duplicates(subset="PLAYER_ID", keep="last")


def replace_player_metadata(new_players: pd.DataFrame, full: bool):
    if full:
        save_table(new_players, "players")
        return

    existing = load_table("players")
    existing = existing[~existing["PLAYER_ID"].isin(new_players["PLAYER_ID"])]
    save_table(pd.concat([existing, new_players], ignore_index=True), "players")


def run_full(start_year: int, end_year: int, player_sleep: float):
    seasons = seasons_between(start_year, end_year)
    basic = collect_seasons("basic player data", basic_info, seasons)
    save_table(basic, "basic_info")

    for table_name, metric_function in METRIC_UPDATES:
        metrics = collect_seasons(table_name, metric_function, seasons)
        save_table(metrics, table_name)

    player_ids = sorted(basic["PLAYER_ID"].unique().tolist())
    replace_player_metadata(update_player_metadata(player_ids, player_sleep), full=True)
    save_table(team_directory(), "teams")
    print("Full database refresh complete (including local team metadata).")


def run_latest(end_year: int, player_sleep: float):
    basic = basic_info(end_year, minimum=MINIMUM_MINUTES)
    replace_season_rows(basic, "basic_info", end_year)

    for table_name, metric_function in METRIC_UPDATES:
        print(f"Updating {table_name}: {end_year - 1}-{end_year % 100:02d}")
        metrics = metric_function(end_year, minimum=MINIMUM_MINUTES)
        replace_season_rows(metrics, table_name, end_year)

    player_ids = sorted(basic["PLAYER_ID"].unique().tolist())
    replace_player_metadata(update_player_metadata(player_ids, player_sleep), full=False)
    print("Latest-season database refresh complete (team metadata unchanged).")


def parse_args():
    parser = argparse.ArgumentParser(description="Refresh the local NBA Skills database.")
    parser.add_argument("mode", choices=("full", "latest"), help="Refresh all seasons or only the end year.")
    parser.add_argument("--start-year", type=int, default=SEASON_START, help=f"First full-refresh season (default: {SEASON_START}).")
    parser.add_argument("--end-year", type=int, default=SEASON_END, help=f"Last season / latest refresh season (default: {SEASON_END}).")
    parser.add_argument("--player-sleep", type=float, default=3, help="Seconds to wait between CommonPlayerInfo requests (default: 3).")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.player_sleep < 0:
        raise ValueError("player sleep cannot be negative")
    if args.mode == "full":
        run_full(args.start_year, args.end_year, args.player_sleep)
    else:
        run_latest(args.end_year, args.player_sleep)


if __name__ == "__main__":
    main()
