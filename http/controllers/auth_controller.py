from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.get("/logout")
async def logout():
    raise NotImplementedError("Logout functionality not implemented yet.")
