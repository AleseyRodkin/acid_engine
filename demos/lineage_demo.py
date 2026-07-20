from acid_engine.core import Contract, Field
from acid_engine.lineage import ContractLineage

# Создаём три контракта
base = Contract(
    schema={"id": Field(type=int, min=1), "email": Field.Email()},
    unique=["id"]
)

extended = Contract(
    schema={"id": Field(type=int, min=1), "email": Field.Email(), "age": Field(type=int, min=0, max=120)},
    unique=["id"]
)

final = Contract(
    schema={"id": Field(type=int, min=1), "email": Field.Email(), "age": Field(type=int, min=0, max=120), "status": Field(type=str, choices=["new", "active"])},
    unique=["id"]
)

# Строим lineage
lineage = ContractLineage()
lineage.add_contract(base)
lineage.add_contract(extended, parents=[base])
lineage.add_contract(final, parents=[extended])

# Отчёт
print("=== Lineage Report for 'final' contract ===")
print(lineage.lineage_report(final))

print("\n=== Lineage Report for 'extended' contract ===")
print(lineage.lineage_report(extended))

print("\n=== Lineage Report for 'base' contract ===")
print(lineage.lineage_report(base))