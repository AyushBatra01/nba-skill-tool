import pandas as pd

from src.scoring.pipeline import build_skill_table, build_full_table
from src.config.load_config import configs, pillar_views

bio_info = ["PLAYER_NAME", "PLAYER_ID", "SEASON", "TEAM", "TEAM_ID", "MIN"]

def get_overall_leaderboard(season, minimum=500):
    df = build_full_table(season, configs, minimum)
    cols = ["Creation", "OffBall", "Defense", "Physicality", "Role", "Rating"]
    df = df[bio_info + cols]
    df = df.sort_values("Rating", ascending=False)
    return df

def get_skill_leaderboard(season, skill, minimum=500):
    config = configs[skill.lower()]
    df = build_skill_table(season, config, skill, minimum)
    pillars = config['pillars']
    cols = [pillar_name for pillar_name in pillars.keys()]
    cols.append(skill)
    df = df[bio_info + cols]
    df = df.sort_values(skill, ascending=False)
    return df

def get_pillar_leaderboard(season, skill, pillar, minimum=500):
    config = configs[skill.lower()]
    df = build_skill_table(season, config, skill, minimum)
    cols = pillar_views[skill][pillar]
    df = df[bio_info + cols]
    df = df.sort_values(pillar, ascending=False)
    return df