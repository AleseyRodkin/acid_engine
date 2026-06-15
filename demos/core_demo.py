# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract, ContractViolation

# ---- 1. Контейнер строк (уникальные, упорядоченные) ----
Strings = Contract(unique=True, ordered=True, dtype=str)
s = Strings.create_container()

s.add("hello")
s.add("world")
assert list(s) == ["hello", "world"], "Порядок нарушен"
print("1. Порядок OK:", list(s))

try:
    s.add("hello")
except ContractViolation as e:
    print("   Дубликат пойман:", e)

# ---- 2. Словарь (int -> str) с уникальными ключами ----
UserIndex = Contract(unique=True, dtype=(int, str))
idx = UserIndex.create_container()

idx.add(key=1, item="alice")
idx.add(key=2, item="bob")
print("2. Словарь:", list(idx))

try:
    idx.add(key=1, item="charlie")
except ContractViolation as e:
    print("   Дубликат ключа пойман:", e)

try:
    idx.add(key="bad", item="test")
except ContractViolation as e:
    print("   Неверный тип ключа:", e)

try:
    idx.add(key=3, item=123)
except ContractViolation as e:
    print("   Неверный тип значения:", e)

# ---- 3. Валидаторы: только строки-URL ----
URLs = Contract(unique=True, dtype=str,
                validators=[lambda x: x.startswith("https://")])
urls = URLs.create_container()

urls.add("https://example.com")
print("3. URLs до:", list(urls))
try:
    urls.add("ftp://bad.url")
except ContractViolation as e:
    print("   Плохой URL пойман:", e)

# ---- 4. Заморозка ----
Ints = Contract(unique=False, dtype=int, frozen=True)  # сразу заморожен
ints = Ints.create_container()

try:
    ints.add(5)
except ContractViolation as e:
    print("4. Заморозка при создании:", e)

# Создадим незамороженный и заморозим руками
ints2 = Contract(dtype=int).create_container()
ints2.add(10)
ints2.freeze()
try:
    ints2.add(20)
except ContractViolation as e:
    print("   Заморозка после freeze:", e)

print("\nВсе проверки пройдены!")

# ---- 5. Проверка ordered ----
Ordered = Contract(unique=False, ordered=True, dtype=str)
ordered = Ordered.create_container()
ordered.add("a")
ordered.add("b")
assert ordered.get(0) == "a"
assert ordered.get(1) == "b"
print("5. Доступ по индексу (ordered=True):", ordered.get(0), ordered.get(1))

# Неупорядоченный контейнер не должен давать доступ по индексу
Unordered = Contract(unique=False, ordered=False, dtype=str)
unordered = Unordered.create_container()
unordered.add("x")
try:
    unordered.get(0)
except ContractViolation as e:
    print("   Попытка индексации неупорядоченного:", e)