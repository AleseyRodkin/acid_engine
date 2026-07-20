from acid_engine.core import Contract, Field
from acid_engine.hashing import contract_fingerprint

contract1 = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
contract1.add_rule("age >= 18")

contract2 = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=21, max=100)
    },
    unique=["id"]
)

print(f"Contract 1 fingerprint: {contract_fingerprint(contract1)}")
print(f"Contract 2 fingerprint: {contract_fingerprint(contract2)}")
print(f"Fingerprints match: {contract_fingerprint(contract1) == contract_fingerprint(contract2)}")