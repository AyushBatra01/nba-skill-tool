import pandas as pd
from src.db.database import engine

def load_table(table_name: str):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)

def get_player(player_id: int):
    query = """
        SELECT *
        FROM players
        WHERE PLAYER_ID = :player_id
    """
    df = pd.read_sql(query, engine, params={"player_id": player_id})
    if df.empty:
        return None
    return df.iloc[0].to_dict()