import pandas as pd
from src.db.database import engine

def save_table(df: pd.DataFrame, table_name: str):
    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False
    )