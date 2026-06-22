# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

import pandas as pd
from acid_engine.core import Contract, Field

# Создаём контракт
contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
contract.add_rule(lambda row: row["age"] >= 18 if row["email"].endswith("@company.com") else True)

# Загружаем данные в DataFrame
df = pd.DataFrame({
    "id": [1, 2, 3, 4, 1, 5],
    "email": ["alice@company.com", "bob@mail.com", "bad", "eve@company.com", "dup@mail.com", "user@test.com"],
    "age": [25, 17, 30, 16, 40, 200]
})

# Валидация DataFrame
result = contract.validate(df)
print(result.explain())

# Сохраняем отчёт в Markdown
result.to_markdown("demos/pandas_report.md")
print("\nОтчёт сохранён в pandas_report.md")