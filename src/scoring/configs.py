from src.config.load_config import load_config

configs = {}
for skill in ["combined", "creation", "offball", "defense", "physicality"]:
    configs[skill] = load_config(skill)

column_data = load_config("column_metadata")
pillar_views = load_config("pillar_views")