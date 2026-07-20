from acid_engine.core import Contract, Field
from acid_engine.registry import ContractRegistry

# Создаём два контракта
contract1 = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email()
    },
    unique=["id"]
)
contract2 = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)

# Реестр
registry = ContractRegistry()
fp1 = registry.register(contract1)
fp2 = registry.register(contract2)

print(f"Contract 1 fingerprint: {fp1}")
print(f"Contract 2 fingerprint: {fp2}")
print(f"Registry fingerprints: {registry.list_fingerprints()}")
print(f"Find contract 1 by fingerprint: {registry.find(fp1) is not None}")
print(f"Contracts compatible: {registry.compatible(fp1, fp2)}")