import enum
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator

from animals.schemas.species import SpeciesRead


class AnimalBase(BaseModel):
    id: int
    name: str
    species: Optional[SpeciesRead] = None
    age: int
    sex: str
    created_at: datetime


class AnimalCreate(BaseModel):
    name: str = Field(max_length=32)
    species_id: Optional[int] = Field(None, ge=1)
    age: int = Field(ge=0, le=150)
    sex: str = Field(pattern=r"^(male|female|other)$")
    parent_id: Optional[int] = Field(None, ge=1)
    created_at: Optional[datetime] = None

    @model_validator(mode="before")
    def set_created_at(cls, values):
        if not values.get("created_at"):
            values["created_at"] = datetime.utcnow()
        return values

    @model_validator(mode="after")
    def validate_created_at(cls, model):
        if model.created_at > datetime.utcnow():
            raise ValueError("created_at cannot be in the future")
        return model


class AnimalUpdate(AnimalCreate):
    pass


class AnimalPartialUpdate(
    BaseModel,
):
    name: str | None = Field(None, max_length=32)
    species_id: Optional[int] = Field(None, ge=1)
    age: int | None = Field(None, ge=0, le=150)
    sex: str | None = Field(None, pattern=r"^(male|female|other)$")
    parent_id: Optional[int] | None = None


class AnimalRead(BaseModel):
    id: int
    name: str
    species: Optional["SpeciesRead"] = None
    age: int
    sex: str
    parent: Optional["AnimalBase"] = None
    created_at: datetime

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
    name: Optional[str] = Field(None, max_length=32)
    sex: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    min_age: Optional[int] = Field(None, ge=0, description="Мінімальний вік")
    max_age: Optional[int] = Field(None, ge=0, le=150, description="Максимальний вік")
    species: Optional[str] = None
    only_children: bool = Field(False, description="Тільки ті, що мають дітей")
    without_children: bool = Field(False, description="Тільки ті які не мають дітей")
    only_parents: bool = Field(False, description="Тільки ті, що мають батьків")
    min_children: Optional[int] = Field(None, ge=0, description="Мінімальний вік")
    max_children: Optional[int] = Field(None, ge=0, le=100, description="Максимальний вік")

    @model_validator(mode='before')
    def check_min_max_values(cls, values):
        min_age = values.get('min_age')
        max_age = values.get('max_age')
        min_children = values.get('min_children')
        max_children = values.get('max_children')

        if min_age is not None and max_age is not None and min_age > max_age:
            raise ValueError('min_age не може бути більшим за max_age')
        if min_children is not None and max_children is not None and min_children > max_children:
            raise ValueError('min_children не може бути більшим за max_children')
        return values

    @model_validator(mode='before')
    def check_boolean_conflicts(cls, values):
        only_children = values.get('only_children')
        without_children = values.get('without_children')

        if only_children and without_children:
            raise ValueError('Параметри "only_children" та "without_children" не можуть бути встановлені одночасно.')
        return values

    @model_validator(mode='before')
    def check_parents_and_children_conflict(cls, values):
        only_parents = values.get('only_parents')
        without_children = values.get('without_children')

        if only_parents and without_children:
            raise ValueError('Параметри "only_parents" та "without_children" конфліктують.')
        return values
