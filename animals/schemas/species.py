from pydantic import BaseModel, Field


class SpeciesBase(BaseModel):
    name: str = Field(max_length=32)


class SpeciesCreate(SpeciesBase):
    name: str = Field(max_length=32)


class SpeciesUpdate(SpeciesBase):
    pass


class SpeciesRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SpeciesPartialUpdate(SpeciesBase):
    name: str | None = Field(None, max_length=32)
