import json

def load_config(skill_name):

    path = f'config/{skill_name}.json'

    with open(path, 'r') as f:
        config = json.load(f)

    return config