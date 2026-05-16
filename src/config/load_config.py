import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"

def load_config(skill_name):
    path = CONFIG_DIR / f"{skill_name}.json"
    with open(path, 'r') as f:
        config = json.load(f)
    return config


configs = {}
for skill in ["combined", "creation", "offball", "defense", "physicality"]:
    configs[skill] = load_config(skill)

column_data = load_config("column_metadata")
pillar_views = load_config("pillar_views")