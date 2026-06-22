# AcidEngine — Data Control Layer

**Контрактно-ориентированная платформа управления качеством данных.**
Описывайте правила данных декларативно, и AcidEngine гарантирует их соблюдение на всех этапах: от загрузки CSV до генерации production-пайплайнов.

---

## Проблема

Правила данных (уникальность ID, формат email, диапазон возраста) дублируются между сервисами, размазываются по коду и со временем превращаются в хаос.

Типичный ETL-скрипт постепенно обрастает десятками проверок:

```python
seen_ids = set()

for row in data:
    if not row["id"]:
        continue

    if row["id"] in seen_ids:
        continue

    if "@" not in row["email"]:
        continue

    # ...
```

Через несколько месяцев становится трудно понять:

* Какие правила реально действуют
* Где находятся бизнес-ограничения
* Какие проверки уже реализованы
* Какие данные считаются валидными

---

# Before / After (реальный CSV-кейс)

## Задача

Загрузить `users.csv` с полями:

* `id` — уникальный, > 0
* `email` — валидный email
* `age` — диапазон 0–120
* `phone` — формат `+7XXXXXXXXXX`
* если email заканчивается на `@company.com`, возраст должен быть >= 18

---

## Before (чистый Python)

```python
import csv
import re

seen_ids = set()
clean = []

with open("users.csv") as f:
    for row in csv.DictReader(f):

        # id
        try:
            id_val = int(row["id"])

            if id_val < 1:
                continue

            if id_val in seen_ids:
                continue

            seen_ids.add(id_val)

        except Exception:
            continue

        # email
        if "@" not in row["email"] or "." not in row["email"]:
            continue

        # age
        try:
            age = int(row["age"])

            if age < 0 or age > 120:
                continue

        except Exception:
            continue

        # phone
        if not re.match(r"^\+7\d{10}$", row.get("phone", "")):
            continue

        # business rule
        if row["email"].endswith("@company.com") and age < 18:
            continue

        clean.append(row)
```

---

## After (AcidEngine)

```python
from acid_engine import Contract, Field

contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120),
        "phone": Field(
            type=str,
            regex=r"^\+7\d{10}$"
        )
    },
    unique=["id"]
)

contract.add_rule(
    "age >= 18 if email.endswith('@company.com')"
)

result = contract.validate("users.csv")

result.explain()
```

---

### Результат

| Метрика               | Обычный Python | AcidEngine    |
| --------------------- | -------------- | ------------- |
| Строк кода            | 30+            | ~6            |
| Проверки типов        | Вручную        | Автоматически |
| Проверки уникальности | Вручную        | Автоматически |
| Бизнес-правила        | В коде цикла   | В контракте   |
| Отчёт об ошибках      | Вручную        | Встроен       |
| Читаемость            | Средняя        | Высокая       |

Контракт становится единственной точкой правды для правил данных.

---

# Ключевые возможности

| Возможность                  | Описание                                            |
| ---------------------------- | --------------------------------------------------- |
| **Field Contracts**          | Типы, диапазоны, regex, choices, встроенные пресеты |
| **Cross-Field Rules**        | Правила между полями (`start_date <= end_date`)     |
| **Business Rules**           | Декларативные ограничения (`age >= 18 if ...`)      |
| **QualityGate**              | strict / recovery / audit / quarantine              |
| **Automatic Rollback**       | Откат при превышении порога ошибок                  |
| **Explain Engine**           | Статистика, топ ошибок, примеры записей             |
| **YAML Support**             | `Contract.from_yaml()` и `Contract.to_yaml()`       |
| **Pipeline Generator**       | Генерация Python-пайплайнов из контракта            |
| **Pandas Integration**       | Поддержка DataFrame                                 |
| **CSV Loader**               | Загрузка и валидация CSV                            |
| **Smart Contract Generator** | Автоматическое построение контракта по данным       |
| **Global Scope**             | Структурирование ETL-пайплайнов                     |
| **Quality Reports**          | Markdown-отчёты по результатам проверки             |

---

# YAML Contracts

Контракты можно описывать как конфигурацию:

```yaml
schema:
  id:
    type: int
    min: 1

  email:
    type: email

  age:
    type: int
    min: 0
    max: 120

unique:
  - id

rules:
  - age >= 18 if email.endswith('@company.com')
```

Загрузка:

```python
contract = Contract.from_yaml(
    "users.contract.yaml"
)
```

---

# Quick Start

Установка:

```bash
pip install acid-engine
```

Пример:

```python
from acid_engine import Contract
from acid_engine import Field

contract = Contract(
    schema={
        "email": Field.Email(),
        "age": Field(
            type=int,
            min=0,
            max=120
        )
    }
)

result = contract.validate(data)

result.explain()
```

---

# Пример отчёта

```text
Всего проверено: 1000

Ошибок: 37

Успешно: 963

Процент ошибок: 3.7%

Топ нарушений:

Email invalid .............. 21
Age out of range ........... 10
Duplicate ID ............... 6
```

---

# Архитектурная философия

AcidEngine строится вокруг простой идеи:

> Контракт описывает поведение данных и тем самым определяет их структуру.

Контракт является primary source of truth.

Код становится реализацией контракта, а не местом хранения бизнес-логики.

Это позволяет:

* убрать дублирование проверок
* сделать правила данных явными
* повысить читаемость ETL-кода
* упростить сопровождение проектов
* стандартизировать обработку данных

---

# Roadmap

## v1.0

* [x] Field Contracts
* [x] Contract Engine
* [x] Container Validation
* [x] Cross-Field Rules
* [x] Safe Rule Engine
* [x] QualityGate
* [x] Explain Engine
* [x] YAML Support
* [x] Pandas Integration
* [x] CSV Loader
* [x] Smart Contract Generator
* [x] Pipeline Generator

## v1.1

* [ ] AI Guard
* [ ] Contract Registry
* [ ] Audit Trail
* [ ] Polars Adapter

## v2.0

* [ ] Kafka Integration
* [ ] Spark Integration
* [ ] Contract Marketplace
* [ ] Rust Performance Core

---

# Status

✅ Core v1.0 completed

✅ Ready for pilot projects

🔄 Active development

---

# License

Apache License 2.0

Copyright © 2025 Alexey Rodkin
