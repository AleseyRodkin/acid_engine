# acid_engine/registry.py
# Простой реестр контрактов (MVP)

from .core import Contract
from .hashing import contract_fingerprint

class ContractRegistry:
    """Хранилище контрактов с возможностью поиска по fingerprint."""

    def __init__(self):
        self._contracts = {}  # fingerprint -> Contract

    def register(self, contract: Contract) -> str:
        """Регистрирует контракт и возвращает его fingerprint."""
        fp = contract_fingerprint(contract)
        if fp not in self._contracts:
            self._contracts[fp] = contract
        return fp

    def find(self, fingerprint: str):
        """Находит контракт по fingerprint или возвращает None."""
        return self._contracts.get(fingerprint)

    def list_fingerprints(self):
        """Возвращает список всех fingerprint в реестре."""
        return list(self._contracts.keys())

    def compatible(self, fp1: str, fp2: str) -> bool:
        """Проверяет, совпадают ли два контракта (по fingerprint)."""
        return fp1 == fp2 and fp1 in self._contracts