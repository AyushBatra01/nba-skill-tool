import numpy as np

headers = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, /",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Accept-Language": "en-US,en;q=0.9"
}

def resp_to_df(resp):
    df = resp.get_data_frames()[0]
    df = df.drop_duplicates(subset='PLAYER_ID')
    return df

def season_to_str(season):
    return f"{season - 1}-{season % 100}"

def standardize(arr):
    return (arr - np.mean(arr)) / (np.std(arr) + 1e-8)