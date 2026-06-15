import csv
from .core import Contract, QualityGate, QualityGateExceeded

def load_csv(filepath: str, contract: Contract = None, max_error_rate: float = 0.5,
             mode: str = "quarantine", collect_errors: bool = True):
    """
    Загружает CSV-файл, применяет контракт (или генерирует его автоматически).
    Возвращает (container, gate, profile).
    """
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    if contract is None:
        contract, profile = Contract.from_data(data)
    else:
        profile = None

    container = contract.create_container()
    gate = QualityGate(container, max_error_rate=max_error_rate,
                       mode=mode, collect_errors=collect_errors)

    for row in data:
        gate.add(row)   # добавляем как есть (строки)

    return container, gate, profile