# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from .core import Contract, ValidationResult

class AIGuard:
    """
    Валидация ответов LLM через контракт AcidEngine.
    """
    def __init__(self, contract: Contract):
        self.contract = contract

    def validate(self, llm_response: dict) -> ValidationResult:
        """
        Проверяет JSON-ответ LLM.
        llm_response должен быть словарем (распарсенный JSON).
        """
        if not isinstance(llm_response, dict):
            raise TypeError("LLM response must be a dict (parsed JSON)")
        return self.contract.validate([llm_response])

    def validate_json_string(self, json_string: str) -> ValidationResult:
        """Парсит JSON-строку и проверяет её."""
        import json
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        return self.validate(data)