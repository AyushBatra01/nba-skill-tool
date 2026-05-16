import pandas as pd
import time

from src.utils.general import headers, season_to_str, resp_to_df
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashplayerbiostats

def minutes(season, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Base',
        per_mode_detailed='Totals',
        season=season_to_str(season),
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    return df[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN']]

def possessions(season, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Advanced',
        per_mode_detailed='Totals',
        season=season_to_str(season),
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    return df[['PLAYER_ID', 'POSS']]

def traditional(season, columns=None, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Base',
        per_mode_detailed='Totals',
        season=season_to_str(season),
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    df['SEASON'] = season
    if columns is None:
        return df
    return df[['PLAYER_ID', 'SEASON'] + columns]

def per100(season, columns=None, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        measure_type_detailed_defense='Base',
        per_mode_detailed='Per100Possessions',
        season=season_to_str(season),
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    df['SEASON'] = season
    if columns is None:
        return df
    return df[['PLAYER_ID', 'SEASON'] + columns]

def get_height(season, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
        season=season_to_str(season),
        league_id='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    df = df.rename(columns={'PLAYER_HEIGHT_INCHES' : 'HEIGHT', 'PLAYER_WEIGHT' : 'WEIGHT'})
    return df[['PLAYER_ID', 'HEIGHT', 'WEIGHT']]

def get_misc(season, sleep=1):
    time.sleep(sleep)
    resp = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season_to_str(season),
        measure_type_detailed_defense="Misc",
        per_mode_detailed="Totals",
        league_id_nullable='00',
        season_type_all_star='Regular Season',
        timeout=60,
        headers=headers
    )
    df = resp_to_df(resp)
    return df[['PLAYER_ID', 'PTS_FB', 'PTS_PAINT', 'PFD']]

def basic_info(season, minimum=100):
    min_df = minutes(season)
    poss_df = possessions(season)
    info = min_df.merge(poss_df, on='PLAYER_ID', how='inner')
    info['SEASON'] = season
    info = info[info['MIN'] >= minimum]
    info = info.rename(columns = {'TEAM_ABBREVIATION' : 'TEAM'})
    return info[['PLAYER_ID', 'SEASON', 'PLAYER_NAME', 'TEAM', 'MIN', 'POSS']]



