from typing import Annotated

from fastapi import Path, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from animals import crud
from core import db_helper
from animals.crud import species, animals


async def get_animal_by_id(
        animal_id: Annotated[int, Path(ge=1)],
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    animal = await crud.animals.get_parent_by_id(session=session, animal_id=animal_id)
    if animal is not None:
        return animal
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Animal not found",
    )


async def get_specie_by_id_or_404(
        specie_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    specie = await species.get_specie_by_id(session=session, specie_id=specie_id)
    if specie is not None:
        return specie
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Specie not found",
    )
