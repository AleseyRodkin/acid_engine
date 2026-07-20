# acid_engine/lineage.py
# Отслеживание зависимостей между контрактами

from .core import Contract
from .hashing import contract_fingerprint
from typing import List, Set, Dict, Optional

class ContractLineage:
    """Отслеживает зависимости между контрактами."""

    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {}  # fingerprint -> set of parent fingerprints
        self._contracts: Dict[str, Contract] = {}      # fingerprint -> Contract

    def add_contract(self, contract: Contract, parents: Optional[List[Contract]] = None):
        """Добавляет контракт и его зависимости (родительские контракты)."""
        fp = contract_fingerprint(contract)
        self._contracts[fp] = contract
        if parents:
            self._dependencies[fp] = set()
            for parent in parents:
                parent_fp = contract_fingerprint(parent)
                self._dependencies[fp].add(parent_fp)
                # Гарантируем, что родитель тоже есть в реестре
                if parent_fp not in self._contracts:
                    self._contracts[parent_fp] = parent
        else:
            self._dependencies[fp] = set()

    def ancestors(self, contract: Contract) -> List[str]:
        """Возвращает список fingerprint всех предков контракта."""
        fp = contract_fingerprint(contract)
        visited = set()
        result = []
        def dfs(current_fp):
            if current_fp in visited:
                return
            visited.add(current_fp)
            for parent_fp in self._dependencies.get(current_fp, []):
                result.append(parent_fp)
                dfs(parent_fp)
        dfs(fp)
        return result

    def lineage_report(self, contract: Contract) -> str:
        """Генерирует отчёт о происхождении контракта."""
        fp = contract_fingerprint(contract)
        ancestors = self.ancestors(contract)
        lines = []
        lines.append(f"Contract: {fp}")
        lines.append(f"Direct ancestors: {len(ancestors)}")
        if ancestors:
            lines.append("Lineage tree:")
            for ancestor_fp in ancestors:
                lines.append(f"  - {ancestor_fp}")
        else:
            lines.append("  (root contract, no ancestors)")
        return "\n".join(lines)