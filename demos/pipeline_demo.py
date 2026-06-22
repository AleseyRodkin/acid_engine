# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract, Field

# Создаём контракт с метаданными пайплайна
contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"],
    pipeline_meta={
        "input": "users.csv",
        "output": "clean_users.csv",
        "processing": ["load_users", "validate_users", "save_users"]
    }
)
contract.add_rule("age >= 18 if email.endswith('@company.com')")

# Генерируем пайплайн
code = contract.generate_pipeline("demos/generated_pipeline.py")
print("=== Сгенерированный код ===")
print(code)