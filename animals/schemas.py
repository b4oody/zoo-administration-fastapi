import enum
from typing import Optional, List

from pydantic import BaseModel, Field


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
    children: List[AnimalBase] = []


class PaginatedAnimals(BaseModel):
    total: int
    page: int
    size: int
    animals: list[AnimalReadParentChildren] = []


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class AnimalFilters(BaseModel):
    name: Optional[str] = None
    sex: Optional[str] = None
    min_age: Optional[int] = Field(None, ge=0, description="Мінімальний вік")
    max_age: Optional[int] = Field(None, ge=0, description="Максимальний вік")
    species: Optional[str] = None
    only_children: bool = Field(False, description="Тільки ті, що мають дітей")
    without_children: bool = Field(False, description="Тільки ті які не мають дітей")
    only_parents: bool = Field(False, description="Тільки ті, що мають батьків")
    min_children: Optional[int] = Field(None, ge=0, description="Мінімальний вік")
    max_children: Optional[int] = Field(None, ge=0, description="Максимальний вік")
