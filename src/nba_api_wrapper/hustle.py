import pandas as pd
import time

from src.utils.general import headers, season_to_str, resp_to_df
from nba_api.stats.endpoints import leaguehustlestatsplayer

def hustle(season, columns=None, sleep=1):
    time.sleep(sleep)
    resp = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
        season=season_to_str(season),
        per_mode_time="Totals",
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    if columns is None:
        return df
    return df[['PLAYER_ID'] + columns]