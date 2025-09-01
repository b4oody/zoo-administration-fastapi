from typing import cast

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, aliased

from animals.schemas import AnimalCreate, AnimalUpdate, AnimalPartialUpdate, AnimalFilters
from core.models import Animal


async def get_parent_by_id(session: AsyncSession, animal_id: int):
    result = await session.execute(
        select(Animal).options(
            joinedload(Animal.parent),
            selectinload(Animal.children)
        ).where(Animal.id == animal_id)
    )
    return result.scalars().first()


def apply_filters(query, filters, Animal):
    conditions = []

    if filters.name:
        conditions.append(Animal.name.ilike(f"%{filters.name}%"))
    if filters.sex:
        conditions.append(Animal.sex == filters.sex)
    if filters.min_age is not None:
        conditions.append(Animal.age >= filters.min_age)
    if filters.max_age is not None:
        conditions.append(Animal.age <= filters.max_age)
    if filters.species:
        conditions.append(Animal.species == filters.species)

    if filters.only_parents:
        conditions.append(Animal.children.any())
    if filters.only_children:
        conditions.append(Animal.parent_id.is_not(None))
    if filters.without_children:
        conditions.append(~Animal.children.any())

    if conditions:
        query = query.where(*conditions)

    if filters.min_children is not None or filters.max_children is not None:
        Child = aliased(Animal)
        query = query.join(Child, Animal.children).group_by(Animal.id)
        if filters.min_children is not None:
            query = query.having(func.count(Child.id) >= filters.min_children)
        if filters.max_children is not None:
            query = query.having(func.count(Child.id) <= filters.max_children)

    return query


async def get_animals(session: AsyncSession, page: int, size: int, filters: AnimalFilters):
    query = (
        select(Animal)
        .options(selectinload(Animal.parent))
        .options(selectinload(Animal.children))
    )
    query = apply_filters(query, filters, Animal)
    query = query.offset((page - 1) * size).limit(size)
    result = await session.scalars(query)
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
    if animal_update.name is not None:
        existing_animal_query = await session.execute(
            select(Animal).where(Animal.name == animal_update.name, Animal.id != animal.id)
        )
        existing_animal = existing_animal_query.scalar_one_or_none()
        if existing_animal:
            raise HTTPException(status_code=400, detail="Animal with this name already exists.")

    for name, value in animal_update.model_dump(exclude_unset=partial).items():
        setattr(animal, name, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="An integrity error occurred, likely a duplicate name.")
    return animal


async def delete_animal(session: AsyncSession, animal: Animal) -> None:
    await session.delete(animal)
    await session.commit()
