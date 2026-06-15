# Демонстрация Field Contracts
from acid_engine.core import Field, Contract, ContractViolation

# --- 1. Простой Field с типом и валидатором ---
UrlField = Field.HttpUrl()
try:
    url = UrlField("https://example.com")
    print("1. OK:", url)
except ContractViolation as e:
    print("1. Ошибка:", e)

try:
    url = UrlField("http://bad.com")
except ContractViolation as e:
    print("   Не прошло:", e)

# --- 2. Email ---
EmailField = Field.Email()
try:
    email = EmailField("user@test.com")
    print("2. OK:", email)
except ContractViolation as e:
    print("2. Ошибка:", e)

try:
    email = EmailField("not_an_email")
except ContractViolation as e:
    print("   Не прошло:", e)

# --- 3. Использование в item_contract ---
IntField = Field(type=int, min=1, max=100)
Numbers = Contract(unique=True, item_contract=IntField)
nums = Numbers.create_container()

nums.add(10)
nums.add(20)
print("3. Контейнер с item_contract:", list(nums))
try:
    nums.add(200)
except ContractViolation as e:
    print("   Ошибка:", e)

# --- 4. Схема (schema) ---
UserContract = Contract(
    unique=True,
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "source": Field.HttpUrl()
    }
)
users = UserContract.create_container()
users.add({"id": 1, "email": "alice@test.com", "source": "https://acid.ai"})
users.add({"id": 2, "email": "bob@test.com", "source": "https://acid.ai"})
print("4. Схема контракт:")
for u in users:
    print("  ", u)

try:
    users.add({"id": 3, "email": "invalid", "source": "https://acid.ai"})
except ContractViolation as e:
    print("   Ошибка схемы:", e)