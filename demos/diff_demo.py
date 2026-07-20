from acid_engine.core import Contract, Field
from acid_engine.diff import diff_contracts

# Старый контракт
old = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
old.add_rule("age >= 18")

# Новый контракт (добавили поле, изменили правило, убрали уникальность)
new = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=18, max=100),
        "phone": Field(type=str, regex=r"^\+7\d{10}$")
    },
    unique=[]  # убрали уникальность
)
new.add_rule("age >= 21")
new.add_rule("price > 0")

print(diff_contracts(old, new))