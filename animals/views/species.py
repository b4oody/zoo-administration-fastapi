from typing import Annotated

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from animals.crud import species
from animals.dependencies import get_specie_by_id_or_404
from animals.schemas.species import SpeciesRead, SpeciesCreate, SpeciesPartialUpdate, SpeciesUpdate
from core import db_helper
from core.models import Specie

router = APIRouter(prefix="/api/v1/animals/species", tags=["animals/species"])


@router.get("/")
async def list_species(
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await species.list_species(session)


@router.get("/{specie_id}")
async def read_specie(
        specie_id: Annotated[int, Path(ge=1)],
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_specie_by_id_or_404(session=session, specie_id=specie_id)


@router.post("/add_specie", response_model=SpeciesRead)
async def create_specie(
        species_in: SpeciesCreate,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await species.create_specie(species_in=species_in, session=session)


@router.put(
    "/{specie_id}",
    response_model=SpeciesRead,
    # dependencies=[Depends(get_current_user)],
)
async def update_specie(
        specie_update: SpeciesUpdate,
        specie: Specie = Depends(get_specie_by_id_or_404),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await species.update_specie(
        session=session,
        specie=specie,
        specie_update=specie_update,
    )


@router.patch(
    "/{specie_id}",
    response_model=SpeciesRead,
    # dependencies=[Depends(get_current_user)],
)
async def update_specie_partial(
        specie_update: SpeciesPartialUpdate,
        specie: Specie = Depends(get_specie_by_id_or_404),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await species.update_specie(
        session=session,
        specie=specie,
        specie_update=specie_update,
        partial=True,
    )


@router.delete(
    "/{specie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(get_current_user)],
)
async def delete_animal(
        specie: Specie = Depends(get_specie_by_id_or_404),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    await species.delete_specie(session=session, specie=specie)
