from fastapi import APIRouter

from src.services.players import get_player_overall, get_player_skill, get_player_pillar

router = APIRouter(
    prefix="/player",
    tags=["player"]
)

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