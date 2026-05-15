import pandas as pd
from src.db.database import engine

def load_table(table_name: str):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)