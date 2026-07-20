# acid_engine/hashing.py
# Генерация уникального хеша контракта

import hashlib
import json
from .core import Contract
from .exporters.json_schema import to_json_schema

def contract_fingerprint(contract: Contract) -> str:
    """
    Возвращает SHA256-хеш контракта.
    Использует JSON Schema представление для стабильности.
    """
    schema = to_json_schema(contract)
    # Убираем нестабильные ключи
    schema.pop("title", None)
    schema.pop("$schema", None)
    serialized = json.dumps(schema, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()[:16]