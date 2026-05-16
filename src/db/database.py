from sqlalchemy import create_engine
from pathlib import Path

# Get project root
ROOT = Path(__file__).resolve().parents[2]

# Ensure data folder exists
DATA_DIR = ROOT / "data"
Path(DATA_DIR).mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "nba.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL)

# Force database creation
with engine.connect() as conn:
    pass

print("Database initialized.")