# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine import Contract, Field, AIGuard

# Контракт для ожидаемой структуры ответа LLM
contract = Contract(
    schema={
        "user_id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["user_id"]
)

# Создаём охранника
guard = AIGuard(contract)

# Симулируем ответ LLM (хороший)
good_response = {
    "user_id": 1,
    "email": "alice@example.com",
    "age": 25
}

result = guard.validate(good_response)
print("=== Good response ===")
print(result.explain())

# Симулируем ответ LLM с ошибкой (плохой email, возраст > 120)
bad_response = {
    "user_id": 2,
    "email": "bob",
    "age": 150
}

result = guard.validate(bad_response)
print("\n=== Bad response ===")
print(result.explain())