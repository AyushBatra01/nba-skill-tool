import pandas as pd
import time

from src.utils.general import headers, season_to_str
from nba_api.stats.endpoints import leaguedashptdefend, leagueseasonmatchups

def def_tracking(season, category="Overall", sleep=1):
    time.sleep(sleep)
    resp = leaguedashptdefend.LeagueDashPtDefend(
        defense_category=category,
        season=season_to_str(season),
        per_mode_simple="Totals",
        league_id='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp.get_data_frames()[0]
    df = df.rename(columns = {'CLOSE_DEF_PERSON_ID' : 'PLAYER_ID'})
    df = df.drop_duplicates(subset = 'PLAYER_ID')
    if category == "Overall":
        return df[['PLAYER_ID', 'D_FGA', 'PCT_PLUSMINUS']]
    elif category == "Less Than 6Ft":
        return df[['PLAYER_ID', 'FGA_LT_06', 'PLUSMINUS']]
    return df

def get_matchups(season):
    resp = leagueseasonmatchups.LeagueSeasonMatchups(
        season=season_to_str(season),
        per_mode_simple="Totals",
        league_id='00',
        season_type_playoffs='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp.get_data_frames()[0]
    return df