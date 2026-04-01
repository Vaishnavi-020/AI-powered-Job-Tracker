from fastapi import APIRouter

router=APIRouter(prefix="/test")

@router.get("/example")
def test():
    return ("FastAPI running properly")