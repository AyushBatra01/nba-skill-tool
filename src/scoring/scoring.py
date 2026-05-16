import pandas as pd

from src.db.load import load_table
from src.utils.general import standardize

def standardize_stats(df, config):
    # get stats to normalize
    to_normalize = []
    pillars = config['pillars']
    for pillar_name, pillar_info in pillars.items():
        for stat in pillar_info['stats'].keys():
            to_normalize.append(stat)
    # Normalize
    for stat in to_normalize:
        df[f"{stat}_z"] = standardize(df[stat].copy())
    return df

def compute_pillars(df, config):
    pillars = config['pillars']
    for pillar_name, pillar_info in pillars.items():
        pillar_value = 0
        for stat, stat_info in pillar_info['stats'].items():
            stat_weight = stat_info['weight']
            pillar_value += stat_weight * df[f'{stat}_z']
        df[pillar_name] = standardize(pillar_value)
    return df

def compute_skill(df, config, skill_name):
    pillars = config['pillars']
    skill = 0
    for pillar_name, pillar_info in pillars.items():
        pillar_weight = pillar_info['weight']
        skill += pillar_weight * df[pillar_name]
    df[skill_name] = standardize(skill)
    return df

def create_skill_score(df, config, skill_name, minimum=500):
    df = df[df['MIN'] >= minimum]
    df = standardize_stats(df, config)
    df = compute_pillars(df, config)
    df = compute_skill(df, config, skill_name)
    return df

def create_overall_score(df, config):
    # Compute
    for composite, skills in config.items():
        rating = 0
        for skill, skill_info in skills.items():
            skill_weight = skill_info['weight']
            rating += skill_weight * df[skill]
        df[composite] = standardize(rating)
    return df

def build_skill_table(season, config, skill, minimum=500, add_bio=True):
    bio_df = load_table("basic_info")
    df = load_table(skill.lower())
    df = df[df['SEASON'] == season]
    skill_df = create_skill_score(df, config, skill, minimum)
    if add_bio:
        final_df = bio_df.merge(skill_df, on=['PLAYER_ID', 'SEASON'], how='inner')
    else:
        final_df = skill_df
    return final_df

def build_full_table(season, configs, minimum=500):
    dfs = {'Bio': load_table("basic_info")}
    for skill in ["Creation", "OffBall", "Defense", "Physicality"]:
        tbl = build_skill_table(season, configs[skill], skill, minimum, add_bio=False)
        dfs[skill] = tbl
    final_df = dfs['Bio']
    for skill in ["Creation", "OffBall", "Defense", "Physicality"]:
        final_df = final_df.merge(dfs[skill], on=['PLAYER_ID', 'SEASON'])
    final_df = create_overall_score(final_df, configs["Combined"])
    return final_df
