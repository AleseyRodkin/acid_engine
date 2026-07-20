from acid_engine.core import Contract, Field
from acid_engine.exporters.json_schema import to_json_schema_string

# Создаём контракт
contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120),
        "status": Field(type=str, choices=["new", "processing", "shipped", "cancelled"])
    },
    unique=["id"]
)
contract.add_rule("age >= 18 if email.endswith('@company.com')")

# Экспортируем в JSON Schema
json_str = to_json_schema_string(contract, title="User Validation Contract")
print(json_str)

# Сохраняем в файл
with open("contract_schema.json", "w") as f:
    f.write(json_str)
print("\nSaved to contract_schema.json")