import numpy as np

SEASON_START = 2018
SEASON_END = 2027

headers = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
}

def resp_to_df(resp):
    df = resp.get_data_frames()[0]
    df = df.drop_duplicates(subset='PLAYER_ID')
    return df

def season_to_str(season):
    return f"{season - 1}-{season % 100}"

def standardize(arr):
    return (arr - np.mean(arr)) / (np.std(arr) + 1e-8)
