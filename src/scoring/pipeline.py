import pandas as pd

from src.db.load import load_table
from src.scoring.scoring import create_skill_score, create_overall_score

def build_skill_table(season, config, skill, minimum=500, add_bio=True):
    bio_df = load_table("basic_info")
    df = load_table(skill.lower())
    df = df[df['SEASON'] == season]
    skill_df = create_skill_score(df, config, skill, minimum)
    skill_df = skill_df.drop(columns=['MIN', 'POSS'])
    if add_bio:
        final_df = bio_df.merge(skill_df, on=['PLAYER_ID', 'SEASON'], how='inner')
    else:
        final_df = skill_df
    final_df = final_df.replace({float('nan'): None})
    return final_df

def build_full_table(season, configs, minimum=500):
    dfs = {'Bio': load_table("basic_info")}
    for skill in ["Creation", "OffBall", "Defense", "Physicality"]:
        tbl = build_skill_table(season, configs[skill.lower()], skill, minimum, add_bio=False)
        dfs[skill] = tbl
    final_df = dfs['Bio']
    for skill in ["Creation", "OffBall", "Defense", "Physicality"]:
        final_df = final_df.merge(dfs[skill], on=['PLAYER_ID', 'SEASON'])
    final_df = create_overall_score(final_df, configs["combined"])
    final_df = final_df.replace({float('nan'): None})
    return final_df