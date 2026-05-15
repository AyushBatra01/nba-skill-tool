from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///data/nba.db"

engine = create_engine(DATABASE_URL)