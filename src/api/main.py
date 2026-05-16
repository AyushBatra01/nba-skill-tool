from fastapi import FastAPI

from src.api.routes.leaderboard import router as leaderboard_router

app = FastAPI()

app.include_router(leaderboard_router)