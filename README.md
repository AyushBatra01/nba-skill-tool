# nba-skill-tool
Future web tool for analyzing advanced NBA stats, separated by specific skill types

## Team metadata

Team pages read their names and franchise metadata from the local SQLite database.
Refresh that table with:

```bash
python -m scripts.update.update_teams
```

This command only uses the static team catalogue bundled with `nba_api`; it makes
no request to the NBA API. Run it after upgrading `nba_api` or when rebuilding
`data/nba.db`.
