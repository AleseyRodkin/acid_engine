# acid_engine/exporters/json_schema.py
# Экспорт контракта AcidEngine в формат JSON Schema.

import json
from ..core import Contract, Field

def to_json_schema(contract: Contract, title: str = "AcidEngine Contract") -> dict:
    """
    Преобразует контракт AcidEngine в JSON Schema (dict).
    Поддерживает: тип, min, max, regex, choices, unique (через custom).
    """
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": title,
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }

    if contract.schema:
        for field_name, field in contract.schema.items():
            prop = {}
            # Тип поля
            if field.type == int:
                prop["type"] = "integer"
            elif field.type == float:
                prop["type"] = "number"
            elif field.type == str:
                prop["type"] = "string"
            else:
                prop["type"] = "string"

            # Числовые ограничения
            if field.min is not None:
                prop["minimum"] = field.min
            if field.max is not None:
                prop["maximum"] = field.max

            # Ограничения длины строк
            if field.min_length is not None:
                prop["minLength"] = field.min_length
            if field.max_length is not None:
                prop["maxLength"] = field.max_length

            # Регулярное выражение
            if field.regex is not None:
                prop["pattern"] = field.regex

            # Список допустимых значений
            if field.choices is not None:
                prop["enum"] = field.choices

            schema["properties"][field_name] = prop

        # Все поля обязательны (можно будет доработать опциональность)
        schema["required"] = list(contract.schema.keys())

    # Уникальность (пользовательское расширение JSON Schema)
    if contract.unique:
        schema["x-acid-unique"] = list(contract.unique) if isinstance(contract.unique, list) else [contract.unique]

    # Правила (пользовательское расширение)
    if contract._rules:
        schema["x-acid-rules"] = [str(r) for r in contract._rules]

    return schema

def to_json_schema_string(contract: Contract, title: str = "AcidEngine Contract", indent: int = 2) -> str:
    """Возвращает JSON-строку схемы."""
    return json.dumps(to_json_schema(contract, title), indent=indent, ensure_ascii=False)