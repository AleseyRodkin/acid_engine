# acid_engine/soft_contracts.py
# Поддержка Soft Contracts: уровни серьёзности INFO / WARNING / ERROR

from enum import Enum
from typing import List, Dict, Any, Union
from .core import Contract, ContractViolation

class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class SoftRule:
    """Обёртка над правилом с уровнем серьёзности."""
    def __init__(self, rule, severity: Severity = Severity.ERROR, message: str = ""):
        self.rule = rule
        self.severity = severity
        self.message = message

class SoftContract(Contract):
    """Расширенный контракт с поддержкой мягких правил."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._soft_rules: List[SoftRule] = []

    def add_soft_rule(self, rule, severity: Severity = Severity.ERROR, message: str = ""):
        """Добавляет правило с указанием серьёзности."""
        self._soft_rules.append(SoftRule(rule, severity, message))

    def validate_soft(self, data: list) -> Dict[str, Any]:
        """
        Валидирует данные с учётом уровней серьёзности.
        Возвращает расширенный отчёт с группировкой по уровням.
        """
        container = self.create_container()
        from .core import QualityGate
        gate = QualityGate(container, max_error_rate=1.0, mode="quarantine", collect_errors=True)

        # Сначала применяем обычные правила
        for rule in self._rules:
            gate.container.contract.add_rule(rule)

        # Затем мягкие правила
        soft_results = {Severity.INFO: [], Severity.WARNING: [], Severity.ERROR: []}
        for soft_rule in self._soft_rules:
            gate.container.contract.add_rule(soft_rule.rule)
            # Временно, пока не интегрируем в QualityGate
            soft_results[soft_rule.severity].append(soft_rule)

        # Прогоняем данные
        for row in data:
            gate.add(row)

        # Собираем отчёт
        report = {
            "total": gate.total,
            "errors": gate.errors,
            "error_rate": gate.errors / max(1, gate.total),
            "by_severity": {
                "info": len(soft_results[Severity.INFO]),
                "warning": len(soft_results[Severity.WARNING]),
                "error": len(soft_results[Severity.ERROR])
            },
            "violations": gate.error_records
        }
        return report