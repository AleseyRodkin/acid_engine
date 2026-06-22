# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine import Contract, Field, AcidOutputGuard

# Контракт для ответа LLM
contract = Contract(
    schema={
        "name": Field(type=str, min_length=1),
        "age": Field(type=int, min=18, max=65)
    }
)

# Создаём guard
guard = AcidOutputGuard(contract, on_failure="raise")

# Симулируем ответ LLM (корректный)
good_output = {"name": "Alice", "age": 30}
try:
    validated = guard(good_output)
    print("✅ Good output accepted:", validated)
except ValueError as e:
    print("❌ Unexpected error:", e)

# Симулируем ответ LLM (некорректный: возраст вне диапазона)
bad_output = {"name": "Bob", "age": 12}
try:
    validated = guard(bad_output)
    print("✅ Bad output accepted (should not happen)")
except ValueError as e:
    print("❌ Bad output blocked:", e)