from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import ValidationError, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from animals import crud
from animals.crud import get_parent_by_id, get_animals_count, get_animals
from animals.dependencies import get_animal_by_id
from animals.schemas import (
    AnimalReadParentChildren,
    AnimalRead,
    AnimalCreate,
    AnimalUpdate,
    AnimalPartialUpdate,
    PaginatedAnimals, AnimalFilters
)
from core import db_helper
from core.models import Animal

router = APIRouter(prefix="/api/v1/animals", tags=["animals"])


@router.get("/", response_model=PaginatedAnimals)
async def list_animals(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
        filters: AnimalFilters = Depends()
):
    total = await get_animals_count(session)
    animals = await get_animals(session=session, page=page, size=size, filters=filters)

    return PaginatedAnimals(
        total=total,
        page=page,
        size=size,
        animals=[
            AnimalReadParentChildren.model_validate(animal, from_attributes=True)
            for animal in animals
        ],
    )


@router.get("/{animal_id}", response_model=AnimalReadParentChildren)
async def get_parent_view(
        animal_id: int = Path(ge=1),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
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
