from typing import cast

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from animals.schemas import AnimalCreate, AnimalUpdate, AnimalPartialUpdate
from core.models import Animal


async def get_parent_by_id(session: AsyncSession, animal_id: int):
    result = await session.execute(
        select(Animal).options(
            joinedload(Animal.parent),
            selectinload(Animal.children)
        ).where(Animal.id == animal_id)
    )
    return result.scalars().first()


async def get_animals(session: AsyncSession, page: int, size: int):
    stmt = (
        select(Animal)
        .options(selectinload(Animal.parent))
        .options(selectinload(Animal.children))
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await session.scalars(stmt)
    return result.all()


async def get_animals_count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(Animal))


async def create_animal_full(animal: AnimalCreate, session: AsyncSession):
    if animal.parent_id is not None:
        statement = select(Animal).where(
            cast("ColumnElement[bool]", Animal.id == animal.parent_id)
        )
        result = await session.execute(statement)
        parent = result.scalar_one_or_none()

        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent with id {animal.parent_id} not found")

    statement = select(Animal).where(
        cast("ColumnElement[bool]", Animal.name == animal.name)
    )
    result = await session.execute(statement)
    existing_animal = result.scalar_one_or_none()

    if existing_animal:
        raise HTTPException(status_code=400, detail="Animal with this name already exists")

    db_animal = Animal(**animal.model_dump())

    session.add(db_animal)
    await session.commit()
    await session.refresh(db_animal)

    stmt = select(Animal).options(joinedload(Animal.parent)).where(
        cast("ColumnElement[bool]", Animal.id == db_animal.id)
    )
    result = await session.execute(stmt)
    db_animal_with_parent = result.scalar_one()

    return db_animal_with_parent


async def update_animal(
        session: AsyncSession,
        animal: Animal,
        animal_update: AnimalUpdate | AnimalPartialUpdate,
        partial: bool = False,
) -> Animal:
    for name, value in animal_update.model_dump(exclude_unset=partial).items():
        setattr(animal, name, value)
    await session.commit()
    return animal


async def delete_animal(session: AsyncSession, animal: Animal) -> None:
    await session.delete(animal)
    await session.commit()
