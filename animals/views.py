from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from animals import crud
from animals.crud import get_parent_by_id
from animals.dependencies import get_animal_by_id
from animals.schemas import AnimalReadParentChildren, AnimalRead, AnimalCreate, AnimalUpdate, AnimalPartialUpdate
from core import db_helper
from core.models import Animal

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


@router.put("/{animal_id}", response_model=AnimalReadParentChildren)
async def update_animal(
        animal_update: AnimalUpdate,
        animal: Animal = Depends(get_animal_by_id),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_animal(
        session=session,
        animal=animal,
        animal_update=animal_update,
    )


@router.patch("/{animal_id}", response_model=AnimalReadParentChildren)
async def update_animal_partial(
        animal_update: AnimalPartialUpdate,
        animal: Animal = Depends(get_animal_by_id),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_animal(
        session=session,
        animal=animal,
        animal_update=animal_update,
        partial=True,
    )


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
        animal: Animal = Depends(get_animal_by_id),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    await crud.delete_animal(session=session, animal=animal)
