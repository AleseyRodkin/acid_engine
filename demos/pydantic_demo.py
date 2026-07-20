from acid_engine.core import Contract, Field
from acid_engine.exporters.pydantic_exporter import to_pydantic_model

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

pydantic_code = to_pydantic_model(contract, class_name="UserModel")
print(pydantic_code)

with open("generated_model.py", "w") as f:
    f.write(pydantic_code)
print("\nSaved to generated_model.py")