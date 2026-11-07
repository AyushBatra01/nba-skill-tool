import pandas as pd

from src.db.database import engine
from src.db.load import get_available_seasons, get_player_seasons


def test_existing_database_exposes_only_complete_seasons():
    seasons = get_available_seasons()

    table_names = ("basic_info", "creation", "offball", "defense", "physicality")
    expected = None
    for table_name in table_names:
        table_seasons = set(
            pd.read_sql(f"SELECT DISTINCT SEASON FROM {table_name}", engine)["SEASON"]
        )
        expected = table_seasons if expected is None else expected & table_seasons

    assert seasons == sorted(expected, reverse=True)


def test_player_seasons_come_from_stored_stats():
    seasons = get_player_seasons(2544)

    assert seasons
    assert seasons == sorted(seasons)
    assert set(seasons).issubset(get_available_seasons())
