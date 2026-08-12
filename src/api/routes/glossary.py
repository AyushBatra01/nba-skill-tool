from fastapi import APIRouter

from src.services.glossary import get_glossary


router = APIRouter(prefix="/glossary", tags=["glossary"])


@router.get("")
def glossary():
    return get_glossary()
