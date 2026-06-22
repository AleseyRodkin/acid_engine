# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

"""
Полный цикл работы с AcidEngine:
1. Загрузка контракта из YAML
2. Валидация грязных данных
3. Отчёт об ошибках
4. Генерация пайплайна для production
"""
from acid_engine.core import Contract

# 1. Загрузка контракта из YAML
print("=" * 50)
print("1. ЗАГРУЗКА КОНТРАКТА ИЗ YAML")
print("=" * 50)
contract = Contract.from_yaml("demos/users.contract.yaml")
print(contract.describe())

# 2. Валидация данных
print("\n" + "=" * 50)
print("2. ВАЛИДАЦИЯ ГРЯЗНЫХ ДАННЫХ")
print("=" * 50)

dirty_data = [
    {"id": 1, "email": "alice@company.com", "age": 25},  # ОК
    {"id": 2, "email": "bob@mail.com", "age": 17},       # ОК
    {"id": 3, "email": "bad", "age": 30},                 # плохой email
    {"id": 4, "email": "eve@company.com", "age": 16},     # сотрудник, < 18
    {"id": 1, "email": "dup@mail.com", "age": 40},        # дубликат id
    {"id": 5, "email": "user@test.com", "age": 200},      # возраст > 120
]

result = contract.validate(dirty_data)
print(result.explain())

# 3. Сохранение отчёта
print("\n" + "=" * 50)
print("3. ЭКСПОРТ ОТЧЁТА")
print("=" * 50)
with open("demos/report.md", "w") as f:
    f.write("# Отчёт о качестве данных\n\n")
    f.write(result.explain())
print("Отчёт сохранён в demos/report.md")

# 4. Генерация пайплайна
print("\n" + "=" * 50)
print("4. ГЕНЕРАЦИЯ PIPELINE")
print("=" * 50)
pipeline_code = contract.generate_pipeline("demos/generated_pipeline.py")
print("Сгенерирован файл: demos/generated_pipeline.py")
print("\nПервые 10 строк:")
for line in pipeline_code.split("\n")[:10]:
    print(line)