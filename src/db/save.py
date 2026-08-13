import pandas as pd
from sqlalchemy import inspect
from src.db.database import engine

def save_table(df: pd.DataFrame, table_name: str):
    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False
    )


def replace_season_rows(df: pd.DataFrame, table_name: str, season: int):
    """Replace one season while preserving all previously stored seasons.

    This is used by the latest-season refresh: all API work completes before
    the database table is replaced, so a failed download cannot erase the
    historical rows for that table.
    """
    if "SEASON" not in df.columns:
        raise ValueError(f"{table_name} must include a SEASON column")

    if inspect(engine).has_table(table_name):
        existing = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        existing = existing[existing["SEASON"] != season]
        df = pd.concat([existing, df], ignore_index=True)

    save_table(df, table_name)
