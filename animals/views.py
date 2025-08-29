from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from animals import crud
from animals.crud import get_parent_by_id
from animals.schemas import AnimalReadParentChildren, AnimalRead, AnimalCreate
from core import db_helper

router = APIRouter(prefix="/api/v1/animals", tags=["animals"])


@router.get("/", response_model=List[AnimalRead])
async def get_animals(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.get_animals(session)


@router.get("/{animal_id}", response_model=AnimalReadParentChildren)
async def get_parent_view(
        animal_id: int, session:
        AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    animal = await get_parent_by_id(session, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@router.post("/add_animal", response_model=AnimalRead)
async def add_animal_with_children(
        animal: AnimalCreate,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.create_animal_full(
        session=session,
        animal=animal
    )
