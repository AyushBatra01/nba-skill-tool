import pandas as pd
import pytest
from sqlalchemy import create_engine

from scripts.update.update_database import (
    SEASON_TABLES,
    fetch_with_retries,
    merge_current_player_metadata,
    validate_staged_database,
    validate_update_frames,
)


def update_frames():
    season_rows = pd.DataFrame(
        {
            "PLAYER_ID": [1, 2],
            "SEASON": [2027, 2027],
            "MIN": [300, 250],
        }
    )
    frames = {table: season_rows.copy() for table in SEASON_TABLES}
    frames["players"] = pd.DataFrame({"PLAYER_ID": [1, 2]})
    return frames


def test_update_validation_accepts_matching_player_coverage():
    validate_update_frames(update_frames(), (2027,))


def test_remote_fetch_is_retried(monkeypatch):
    attempts = []
    monkeypatch.setattr("scripts.update.update_database.time.sleep", lambda _: None)
    monkeypatch.setattr("scripts.update.update_database.refresh_nba_session", lambda: None)

    def fetch():
        attempts.append(1)
        if len(attempts) < 3:
            raise TimeoutError
        return pd.DataFrame({"ok": [True]})

    result = fetch_with_retries("test data", fetch, attempts=3)

    assert len(attempts) == 3
    assert result["ok"].all()


def test_latest_metadata_reuses_profiles_and_updates_current_team():
    basic = pd.DataFrame(
        {
            "PLAYER_ID": [1, 2],
            "TEAM_ID": [10, 20],
            "TEAM": ["AAA", "BBB"],
        }
    )
    existing = pd.DataFrame(
        {
            "PLAYER_ID": [1],
            "FIRST_NAME": ["Known"],
            "TEAM_ID": [99],
            "TEAM_ABBREVIATION": ["OLD"],
        }
    )
    new = pd.DataFrame(
        {
            "PLAYER_ID": [2],
            "FIRST_NAME": ["New"],
            "TEAM_ID": [0],
            "TEAM_ABBREVIATION": [""],
        }
    )

    result = merge_current_player_metadata(basic, existing, new).set_index("PLAYER_ID")

    assert result.loc[1, "FIRST_NAME"] == "Known"
    assert result.loc[1, "TEAM_ID"] == 10
    assert result.loc[1, "TEAM_ABBREVIATION"] == "AAA"
    assert result.loc[2, "TEAM_ID"] == 20


def test_update_validation_rejects_partial_metric_table():
    frames = update_frames()
    frames["defense"] = frames["defense"].iloc[:1]

    with pytest.raises(ValueError, match="coverage differs"):
        validate_update_frames(frames, (2027,))


def test_staged_validation_rejects_duplicate_player_seasons():
    engine = create_engine("sqlite://")
    frames = update_frames()
    for table in SEASON_TABLES:
        frame = frames[table]
        if table == "creation":
            frame = pd.concat([frame, frame.iloc[:1]], ignore_index=True)
        frame.to_sql(table, engine, index=False)
    frames["players"].to_sql("players", engine, index=False)
    pd.DataFrame({"TEAM_ID": [1]}).to_sql("teams", engine, index=False)

    with pytest.raises(ValueError, match="coverage validation"):
        validate_staged_database(engine, (2027,), full=True)
