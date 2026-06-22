# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract, Field

# Создаём контракт с правилами
contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
contract.add_rule(lambda row: row["age"] >= 18 if row["email"].endswith("@company.com") else True)

# Тестовые данные
data = [
    {"id": 1, "email": "alice@company.com", "age": 25},  # ок
    {"id": 2, "email": "bob@mail.com", "age": 17},       # ок (не сотрудник компании)
    {"id": 3, "email": "bad", "age": 30},                 # плохой email
    {"id": 4, "email": "eve@company.com", "age": 16},     # сотрудник, но возраст < 18
    {"id": 1, "email": "dup@mail.com", "age": 40},        # дубликат id
    {"id": 5, "email": "user@test.com", "age": 200},      # возраст > 120
]

# Валидация и отчёт
result = contract.validate(data)
print(result.explain())