import pandas as pd
import time

from src.utils.general import headers, season_to_str, resp_to_df
from nba_api.stats.endpoints import synergyplaytypes

def playtype_raw(season, playtype, columns=None, sleep=1):
    time.sleep(sleep)
    resp = synergyplaytypes.SynergyPlayTypes(
        play_type_nullable=playtype,
        player_or_team_abbreviation='P',
        season=season_to_str(season),
        per_mode_simple='Totals',
        league_id='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    if columns is None:
        return df
    return df[['PLAYER_ID'] + columns]