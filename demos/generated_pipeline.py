# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

# Auto-generated pipeline by AcidEngine
from acid_engine.scope import global_scope, orchestrator
from acid_engine.core import Contract, Field, QualityGate

# Загрузка контракта (пример, замените на свой)
contract = Contract.from_yaml('users.contract.yaml')



@orchestrator
def process():
    # Вход: input_data
    # Выход: output_data


if __name__ == '__main__':
    with global_scope('generated_pipeline'):
        process()