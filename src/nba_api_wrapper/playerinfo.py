import pandas as pd
import time

from src.utils.general import headers, SEASON_START
from nba_api.stats.endpoints import commonplayerinfo, commonallplayers

def player_info(player_id, sleep=1):
    time.sleep(sleep)
    resp = commonplayerinfo.CommonPlayerInfo(
        player_id=player_id,
        league_id_nullable='00',
        timeout=60,
        headers=headers
    )
    info = resp.get_data_frames()[0]
    info['PLAYER_ID'] = player_id
    relevant = ['PLAYER_ID', 'FIRST_NAME', 'LAST_NAME', 'HEIGHT', 'WEIGHT', 'JERSEY', 'TEAM_ID', 'TEAM_ABBREVIATION', 'FROM_YEAR', 'TO_YEAR']
    return info[relevant]


def player_list(sleep=1):
    time.sleep(sleep)
    resp = commonallplayers.CommonAllPlayers(
        league_id='00'
    )
    df = resp.get_data_frames()[0]
    df['FROM_YEAR'] = df['FROM_YEAR'].astype(int)
    df['TO_YEAR'] = df['TO_YEAR'].astype(int)
    df = df[(df['TO_YEAR'] >= SEASON_START)]
    return df

