from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from animals.schemas.species import (
    SpeciesCreate,
    SpeciesUpdate,
    SpeciesPartialUpdate
)
from core.models import Specie


async def list_species(session: AsyncSession):
    stmt = select(Specie)
    result = await session.scalars(stmt)
    return result.all()


async def get_specie_by_id(session: AsyncSession, specie_id: int):
    stmt = select(Specie).where(Specie.id == specie_id)
    result = await session.scalars(stmt)
    return result.first()


async def create_specie(session: AsyncSession, species_in: SpeciesCreate):
    exist_specie = await session.execute(
        select(Specie).where(Specie.name == species_in.name)
    )
    if exist_specie.scalar_one_or_none():
        raise HTTPException(status_code=401, detail="Species with this name already exists")

    stmt = Specie(**species_in.model_dump())
    session.add(stmt)
    await session.commit()
    await session.refresh(stmt)
    return stmt


async def update_specie(
        session: AsyncSession,
        specie: Specie,
        specie_update: SpeciesUpdate | SpeciesPartialUpdate,
        partial: bool = False,
) -> Specie:
    if specie_update.name is not None:
        existing_animal_query = await session.execute(
            select(Specie).where(Specie.name == specie_update.name, Specie.id != specie.id)
        )
        existing_specie = existing_animal_query.scalar_one_or_none()
        if existing_specie:
            raise HTTPException(status_code=400, detail="Animal with this name already exists.")

    for name, value in specie_update.model_dump(exclude_unset=partial).items():
        setattr(specie, name, value)
    try:
        await session.commit()
        await session.refresh(specie)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="An integrity error occurred, likely a duplicate name.")
    return specie


async def delete_specie(session: AsyncSession, specie: Specie) -> None:
    await session.delete(specie)
    await session.commit()
