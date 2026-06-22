# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from typing import Dict, Any
from .core import Contract, ValidationResult

class AcidOutputGuard:
    """
    LangChain-совместимый guard для валидации выходных данных LLM.
    Используется как output parser или валидатор в цепочке.
    """
    def __init__(self, contract: Contract, on_failure: str = "raise"):
        """
        contract: экземпляр Contract AcidEngine
        on_failure: "raise" (по умолчанию) или "ignore" (пропустить ошибку)
        """
        self.contract = contract
        self.on_failure = on_failure

    def validate(self, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """Проверяет словарь и возвращает его, если он корректен."""
        result = self.contract.validate([llm_output])
        if result.summary.get("errors", 0) > 0:
            if self.on_failure == "raise":
                raise ValueError(
                    f"LLM output failed contract validation:\n{result.explain()}"
                )
            # иначе просто возвращаем как есть
        return llm_output

    def __call__(self, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        return self.validate(llm_output)