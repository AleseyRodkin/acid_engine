# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract, Field

contract = Contract(
    schema={
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    }
)

# Добавляем бизнес-правила
contract.add_rule("age >= 18")
contract.add_rule(lambda row: row["email"].endswith(".com"))

c = contract.create_container()

# OK
c.add({"email": "a@b.com", "age": 25})
print("Добавлено: 25, a@b.com")

# OK
c.add({"email": "x@y.com", "age": 18})
print("Добавлено: 18, x@y.com")

# Нарушение age >= 18
try:
    c.add({"email": "kid@b.com", "age": 15})
except Exception as e:
    print(f"Ошибка: {e}")

# Нарушение email.endswith('.com')
try:
    c.add({"email": "user@org.ru", "age": 30})
except Exception as e:
    print(f"Ошибка: {e}")
