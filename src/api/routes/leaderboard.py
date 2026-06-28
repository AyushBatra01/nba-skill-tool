from fastapi import APIRouter

from src.services.leaderboard import get_overall_leaderboard, get_skill_leaderboard, get_pillar_leaderboard

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"]
)

@router.get("/overall")
def overall_leaderboard(season: int, minimum: int = 500, detailed: bool = False):
    df = get_overall_leaderboard(season, minimum, detailed)
    return df.to_dict(orient='records')

@router.get("/skill/{skill}")
def skill_leaderboard(skill: str, season: int, minimum: int = 500, detailed: bool = False):
    df = get_skill_leaderboard(season, skill, minimum, detailed)
    return df.to_dict(orient='records')

@router.get("/pillar/{skill}/{pillar}")
def pillar_leaderboard(skill: str, pillar: str, season: int, minimum: int = 500, detailed: bool = False):
    df = get_pillar_leaderboard(season, skill, pillar, minimum, detailed)
    return df.to_dict(orient='records')