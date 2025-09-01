from typing import Annotated

from fastapi import Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from animals import crud
from core import db_helper


async def get_animal_by_id(
        animal_id: Annotated[int, Path(ge=1)],
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    animal = await crud.get_parent_by_id(session=session, animal_id=animal_id)
    if animal is not None:
        return animal
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Animal not found",
    )
