# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

# Демонстрация политик QualityGate v2
from acid_engine.core import Contract, QualityGate, QualityGateExceeded, ErrorRecord

Ints = Contract(dtype=int)

def test_mode(mode, good=None, archive=None, collect=False):
    print(f"\n=== Режим: {mode} ===")
    main = Ints.create_container()
    gate = QualityGate(main, max_error_rate=0.35,
                       mode=mode,
                       good_container=good,
                       archive_container=archive,
                       collect_errors=collect)

    gate.add(10)        # хорошо
    gate.add(20)        # хорошо
    gate.add("bad1")    # ошибка (1/3 = 33% < 35% – пока ок)
    try:
        gate.add("bad2")  # ошибка (2/4 = 50% > 35% – превышение)
    except QualityGateExceeded as e:
        print("Исключение:", e)

    print("Основной контейнер:", list(main))
    if good is not None:
        print("good_container:", good)
    if archive is not None:
        print("archive_container:", archive)
    if collect:
        print("ErrorRecords:")
        for rec in gate.error_records:
            print(" ", rec)

# 1. Strict (полный откат)
test_mode("strict")

# 2. Recovery (откат + хорошие в отдельный список)
good = []
test_mode("recovery", good=good)

# 3. Audit (откат + все записи в архив)
archive = []
test_mode("audit", archive=archive)

# 4. Quarantine (без отката)
test_mode("quarantine")

# 5. Quarantine с коллекционированием ошибок
test_mode("quarantine", collect=True)