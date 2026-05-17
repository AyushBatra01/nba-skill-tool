from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.leaderboard import router as leaderboard_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaderboard_router)

# run from project root:
# uvicorn src.api.main:app --port 8000 --reload

# run in separate terminal (from frontend directory):
# python -m http.server 3000

# Open in browser:
# http://localhost:3000