from pydantic import BaseModel, validator, Field as PydanticField
import re

class UserModel(BaseModel):
    id: int = PydanticField(ge=1)
    email: str = PydanticField(regex=r"^[^@]+@[^@]+\.[^@]+$")
    age: int = PydanticField(ge=0, le=120)
    status: str = PydanticField(choices=['new', 'processing', 'shipped', 'cancelled'])

    @validator('*', pre=True)
    def check_unique(cls, v, values, field):
        # Заглушка: уникальность проверяется на уровне набора данных
        return v

    @validator('*', pre=True)
    def check_rules(cls, v, values, field):
        # Заглушка: бизнес-правила проверяются отдельно
        return v