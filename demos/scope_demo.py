# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from acid_engine.core import Contract
from acid_engine.scope import global_scope, orchestrator, ScopeError

# Определим контракты
RawContract = Contract(unique=True, dtype=str)
CleanContract = Contract(unique=True, dtype=str, ordered=True)

# Создаём входной контейнер
raw = RawContract.create_container()
raw.add("alice")
raw.add("bob")

with global_scope("clean_step") as g:
    # Входная константа
    input_data = g.const(raw)

    @orchestrator(input_contract=RawContract, output_contract=CleanContract)
    def clean(data):
        # data уже заморожен, поэтому не можем менять, только читать
        result = CleanContract.create_container()
        for item in data:
            # какая-то обработка, например, фильтрация
            if item.startswith("a"):  # оставим только "alice"
                result.add(item)
        return result

    # Вызываем оркестратор
    output = clean(input_data)
    g.const_output("filtered", output)

# После выхода из блока проверим, что выходной контейнер заморожен
assert output.contract.frozen == False  # он ещё не заморожен? const_output замораживает в __exit__
# В const_output мы не замораживаем сразу, только при успешном выходе из скоупа
# Но мы уже вне скоупа, поэтому output должен быть заморожен
print("Выходной контейнер заморожен:", output.contract.frozen)  # покажет True
print("Результат:", list(output))
assert list(output) == ["alice"]
print("Тест global_scope пройден.")