"""Refresh locally stored NBA team metadata.

This reads static data bundled with nba_api; it does not call the NBA API.
Run this offline update before serving the application after upgrading nba_api.
"""

from src.db.save import save_table
from src.nba_api_wrapper.teaminfo import team_directory


save_table(team_directory(), "teams")
print("Saved NBA team metadata to data/nba.db")
