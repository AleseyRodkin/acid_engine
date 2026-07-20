from acid_engine.core import Contract, Field
from acid_engine.soft_contracts import SoftContract, Severity

# Создаём мягкий контракт
contract = SoftContract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)

# Добавляем правила с разной серьёзностью
contract.add_soft_rule("age >= 18", severity=Severity.ERROR, message="Возраст должен быть >= 18")
contract.add_soft_rule("age >= 21", severity=Severity.WARNING, message="Рекомендуется возраст >= 21")
contract.add_soft_rule("email not null", severity=Severity.INFO, message="Email должен быть заполнен")

# Тестовые данные
data = [
    {"id": 1, "email": "a@b.com", "age": 25},
    {"id": 2, "email": "bad", "age": 17},
    {"id": 3, "email": "c@d.com", "age": 20},
]

# Валидация
report = contract.validate_soft(data)

print("=== Soft Contract Validation Report ===")
print(f"Total: {report['total']}")
print(f"Errors: {report['errors']} (rate: {report['error_rate']:.1%})")
print(f"By severity:")
print(f"  INFO: {report['by_severity']['info']}")
print(f"  WARNING: {report['by_severity']['warning']}")
print(f"  ERROR: {report['by_severity']['error']}")

print("\n=== Violations ===")
for err in report['violations']:
    print(f"  {err}")