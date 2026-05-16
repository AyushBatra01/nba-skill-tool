import pandas as pd

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

def create_overall_score(config, bio, creation, offball, defense, physicality):
    # Merge
    combined = bio.merge(creation, on=['PLAYER_ID','SEASON'])
    combined = combined.merge(offball, on=['PLAYER_ID', 'SEASON'])
    combined = combined.merge(defense, on=['PLAYER_ID', 'SEASON'])
    combined = combined.merge(physicality, on=['PLAYER_ID', 'SEASON'])
    # Compute
    for composite, skills in config.items():
        rating = 0
        for skill, skill_info in skills.items():
            skill_weight = skill_info['weight']
            rating += skill_weight * combined[skill]
        combined[composite] = standardize(rating)
    return combined
