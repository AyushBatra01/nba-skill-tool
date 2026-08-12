"""Offline team metadata helpers.

``nba_api.stats.static.teams`` ships with the installed package and does not
make a request to stats.nba.com.  The update script persists its result in our
SQLite database so the application never calls nba_api at page-request time.
"""

import pandas as pd
from nba_api.stats.static import teams


def team_directory() -> pd.DataFrame:
    """Build the current 30-team metadata table from nba_api's bundled data."""
    dataframe = pd.DataFrame(teams.get_teams())
    dataframe = dataframe.rename(columns={
        "id": "TEAM_ID",
        "full_name": "FULL_NAME",
        "abbreviation": "ABBREVIATION",
        "nickname": "NICKNAME",
        "city": "CITY",
        "state": "STATE",
        "year_founded": "YEAR_FOUNDED",
    })
    return dataframe[[
        "TEAM_ID", "FULL_NAME", "ABBREVIATION", "NICKNAME", "CITY",
        "STATE", "YEAR_FOUNDED",
    ]]
