from acid_engine.core import Contract, QualityGate, QualityGateExceeded

Ints = Contract(dtype=int)

def test_policy(policy, good=None, archive=None, errors=None):
    print(f"\n=== Политика: {policy} ===")
    main = Ints.create_container()
    gate = QualityGate(main, max_error_rate=0.35,  # 35%
                       policy=policy,
                       good_container=good,
                       archive_container=archive,
                       error_container=errors)

    gate.add(10)        # хорошо
    gate.add(20)        # хорошо
    gate.add("bad1")    # плохо (1/3 = 33% < 35% – пока ок)
    try:
        gate.add("bad2")  # плохо (2/4 = 50% > 35% – превышение)
    except QualityGateExceeded as e:
        print("Исключение:", e)

    print("Основной контейнер:", list(main))
    if good is not None:
        print("good_container:", good)
    if archive is not None:
        print("archive_container:", archive)
    if errors is not None:
        print("error_container:", errors)

# 1. Полный откат
test_policy("rollback")

# 2. Откат + хорошие в отдельный массив
good = []
test_policy("rollback_with_good", good=good)

# 3. Откат + все записи в архив
archive = []
test_policy("rollback_with_all", archive=archive)

# 4. Фильтр без отката
test_policy("filter")

# 5. Фильтр + сбор ошибок
errors = []
test_policy("filter", errors=errors)