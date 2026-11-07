# nba-skill-tool
Future web tool for analyzing advanced NBA stats, separated by specific skill types

## Run locally

Install the dependencies, then serve the dashboard and API together at
<http://localhost:8000>:

```bash
make install
make run
```

## Refresh the database

Run database updates from the project root. These scripts are the only place
the project calls `nba_api`; dashboard visitors only read the stored SQLite
database.

```bash
# Rebuild every data table for the configured 2018–2027 range and refresh teams.
make update-full

# Replace only the 2026–27 rows; team metadata is intentionally left unchanged.
make update-latest
```

The equivalent commands with custom seasons are:

```bash
python -m scripts.update.update_database full --start-year 2019 --end-year 2027
python -m scripts.update.update_database latest --end-year 2027
```

Both modes retain only players with at least 100 minutes in each stored season.
They download and validate every table in a temporary database before replacing
`data/nba.db`. The previously published database is kept at `data/nba.db.bak`.
The updater first opens NBA.com with a Chrome-compatible transport so the stats
requests carry the browser fingerprint and cookies expected by `stats.nba.com`.
The player-profile step makes one NBA API request per player and waits three
seconds between requests by default, so a full refresh can take about an hour.
Latest-season refreshes reuse existing profiles and only request players that
have not appeared in the database before.
Use `--player-sleep SECONDS` only if you need to adjust that rate limit.

## Team metadata

Team pages read their names and franchise metadata from the local SQLite database.
Refresh that table with:

```bash
python -m scripts.update.update_teams
```

This command only uses the static team catalogue bundled with `nba_api`; it makes
no request to the NBA API. Run it after upgrading `nba_api` or when rebuilding
`data/nba.db`.

## Deploy on Render (free)

This repository includes [render.yaml](render.yaml), which deploys the frontend
and FastAPI backend as one free Render web service. The local `data/nba.db` file
is part of the deployment, so refresh it locally, commit the changed database,
and push before deploying.

1. Create a free [Render](https://render.com) account and connect GitHub.
2. In Render, choose **New → Blueprint**, select this repository, and approve
   the detected `render.yaml` configuration.
3. Choose the **Free** instance and deploy. Render will provide an
   `onrender.com` URL and automatically redeploy when `main` changes.

Free Render web services spin down after 15 minutes without traffic, so the
first visit after idle can take about a minute. The database is read-only at
runtime; do not run the updater on Render's free service.
