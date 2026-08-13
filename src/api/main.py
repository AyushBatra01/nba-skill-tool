from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.api.routes.leaderboard import router as leaderboard_router
from src.api.routes.player import router as player_router
from src.api.routes.team import router as team_router
from src.api.routes.glossary import router as glossary_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaderboard_router)
app.include_router(player_router)
app.include_router(team_router)
app.include_router(glossary_router)

# Serve the dashboard and API from one origin in production. This keeps the
# shipped site free of environment-specific API URLs.
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
