from fastapi import APIRouter, HTTPException

from src.services.leaderboard import get_overall_leaderboard, get_skill_leaderboard, get_pillar_leaderboard
from src.db.load import get_team, get_team_directory

router = APIRouter(
    prefix="/team",
    tags=["team"]
)


@router.get("/directory")
def team_directory():
    return get_team_directory()


@router.get("/{team_id}/info")
def info_team(team_id: int):
    team = get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/{team_id}/overall")
def overall_team(team_id: int, season: int, minimum: int = 500, detailed: bool = False):
    df = get_overall_leaderboard(season, minimum, detailed)
    df = df[df["TEAM_ID"] == team_id]
    return df.to_dict(orient='records')

@router.get("/{team_id}/skill/{skill}")
def skill_team(team_id: int, skill: str, season: int, minimum: int = 500, detailed: bool = False):
    df = get_skill_leaderboard(season, skill, minimum, detailed)
    df = df[df["TEAM_ID"] == team_id]
    return df.to_dict(orient='records')

@router.get("/{team_id}/pillar/{skill}/{pillar}")
def pillar_team(team_id: int, skill: str, pillar: str, season: int, minimum: int = 500, detailed: bool = False):
    df = get_pillar_leaderboard(season, skill, pillar, minimum, detailed)
    df = df[df["TEAM_ID"] == team_id]
    return df.to_dict(orient='records')
