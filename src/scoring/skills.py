def compute_skill(df, config, skill_name):

    pillars = config['pillars']

    skill = 0

    for pillar_name, pillar_info in pillars.items():

        pillar_weight = pillar_info['weight']

        skill += pillar_weight * df[pillar_name]

    df[skill_name] = skill

    return df