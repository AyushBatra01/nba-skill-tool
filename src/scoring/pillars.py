def compute_pillars(df, config):

    pillars = config['pillars']

    for pillar_name, pillar_info in pillars.items():

        pillar_value = 0

        for stat, weight in pillar_info['stats'].items():

            pillar_value += weight * df[f'{stat}_z']

        df[pillar_name] = pillar_value

    return df