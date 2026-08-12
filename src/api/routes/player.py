from fastapi import APIRouter, HTTPException

from src.services.players import get_player_overall, get_player_skill, get_player_pillar
from src.db.load import get_player, get_player_directory

router = APIRouter(
    prefix="/player",
    tags=["player"]
)


@router.get("/directory")
def player_directory(season: int = 2026):
    return get_player_directory(season)

@router.get("/{player_id}/overall")
def overall_player(player_id: int, minimum: int = 500):
    df = get_player_overall(player_id, minimum)
    return df.to_dict(orient='records')

@router.get("/{player_id}/skill/{skill}")
def skill_player(player_id: int, skill: str, minimum: int = 500):
    df = get_player_skill(player_id, skill, minimum)
    return df.to_dict(orient='records')

@router.get("/{player_id}/pillar/{skill}/{pillar}")
def pillar_player(player_id: int, skill: str, pillar: str, minimum: int = 500):
    df = get_player_pillar(player_id, skill, pillar, minimum)
    return df.to_dict(orient='records')

@router.get("/{player_id}/info")
def info_player(player_id: int):
    player = get_player(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
