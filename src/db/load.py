import pandas as pd
from src.db.database import engine


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas missing values to JSON-safe Python ``None`` values."""
    return df.astype(object).where(pd.notna(df), None)

def load_table(table_name: str):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)

def get_player(player_id: int):
    query = """
        SELECT p.*, t.FULL_NAME AS TEAM_NAME,
               b.COLLEGE, b.DRAFT_YEAR, b.DRAFT_NUMBER
        FROM players p
        LEFT JOIN teams t ON p.TEAM_ID = t.TEAM_ID
        LEFT JOIN basic_info b ON p.PLAYER_ID = b.PLAYER_ID
            AND b.SEASON = (
                SELECT MAX(SEASON)
                FROM basic_info latest
                WHERE latest.PLAYER_ID = p.PLAYER_ID
            )
        WHERE p.PLAYER_ID = :player_id
    """
    df = pd.read_sql(query, engine, params={"player_id": player_id})
    if df.empty:
        return None
    return _clean_dataframe(df).iloc[0].to_dict()


def get_team(team_id: int):
    query = """
        SELECT *
        FROM teams
        WHERE TEAM_ID = :team_id
    """
    df = pd.read_sql(query, engine, params={"team_id": team_id})
    if df.empty:
        return None
    return _clean_dataframe(df).iloc[0].to_dict()


def get_player_directory(season: int):
    """Return players who meet the stored 100-minute threshold in a season."""
    query = """
        SELECT p.PLAYER_ID, p.FIRST_NAME, p.LAST_NAME, b.TEAM_ID,
               b.TEAM AS TEAM_ABBREVIATION, b.MIN,
               t.FULL_NAME AS TEAM_NAME
        FROM players p
        INNER JOIN basic_info b ON p.PLAYER_ID = b.PLAYER_ID
        LEFT JOIN teams t ON b.TEAM_ID = t.TEAM_ID
        WHERE b.SEASON = :season
        ORDER BY p.LAST_NAME, p.FIRST_NAME
    """
    df = pd.read_sql(query, engine, params={"season": season})
    return _clean_dataframe(df).to_dict(orient="records")


def get_team_directory():
    """Return teams that are represented by the locally stored scoring data."""
    query = """
        SELECT t.*
        FROM teams t
        INNER JOIN (SELECT DISTINCT TEAM_ID FROM basic_info) b
            ON t.TEAM_ID = b.TEAM_ID
        ORDER BY t.FULL_NAME
    """
    return _clean_dataframe(pd.read_sql(query, engine)).to_dict(orient="records")
