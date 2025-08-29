from typing import Optional, List

from pydantic import BaseModel


class AnimalBase(BaseModel):
    id: int
    name: str
    species: str
    age: int
    sex: str


class AnimalCreate(BaseModel):
    name: str
    species: str
    age: int
    sex: str
    parent_id: Optional[int] = None


class AnimalUpdate(AnimalCreate):
    pass


class AnimalPartialUpdate(BaseModel):
    name: str | None = None
    species: str | None = None
    age: int | None = None
    sex: str | None = None
    parent_id: Optional[int] | None = None


class AnimalRead(BaseModel):
    id: int
    name: str
    species: str
    age: int
    sex: str
    parent: Optional["AnimalBase"] = None

    class Config:
        from_attributes = True


class AnimalReadParentChildren(AnimalRead):
    children: List[AnimalBase]
