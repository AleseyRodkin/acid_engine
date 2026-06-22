# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract, Field

# Создаём контракт вручную
contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
contract.add_rule("age >= 18")

# Экспортируем в YAML
yaml_str = contract.to_yaml()
print("=== YAML ===")
print(yaml_str)

# Сохраняем в файл
contract.to_yaml("demos/users.contract.yaml")

# Загружаем из файла
loaded = Contract.from_yaml("demos/users.contract.yaml")
print("Загруженный контракт:")
print(loaded.describe())

# Проверяем, что работает
data = [
    {"id": 1, "email": "alice@mail.com", "age": 25},
    {"id": 2, "email": "bob@mail.com", "age": 17},  # нарушает age >= 18
]
result = loaded.validate(data)
print("\nРезультат валидации:")
print(result.explain())