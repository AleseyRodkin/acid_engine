# acid_engine/diff.py
# Сравнение двух контрактов и отображение изменений.

from .core import Contract

def _rule_to_str(rule):
    """Преобразует правило в строку для сравнения."""
    if isinstance(rule, str):
        return rule
    return str(rule)

def diff_contracts(old: Contract, new: Contract) -> str:
    """
    Сравнивает два контракта и возвращает человекочитаемый отчёт об изменениях.
    """
    report = []

    # 1. Сравнение схемы (поля)
    old_schema = old.schema or {}
    new_schema = new.schema or {}

    added_fields = set(new_schema.keys()) - set(old_schema.keys())
    removed_fields = set(old_schema.keys()) - set(new_schema.keys())
    common_fields = set(old_schema.keys()) & set(new_schema.keys())

    if added_fields:
        report.append("=== Added Fields ===")
        for f in added_fields:
            report.append(f"  + {f}")
        report.append("")

    if removed_fields:
        report.append("=== Removed Fields ===")
        for f in removed_fields:
            report.append(f"  - {f}")
        report.append("")

    # Изменённые поля
    modified = []
    for f in common_fields:
        old_field = old_schema[f]
        new_field = new_schema[f]
        if old_field.describe() != new_field.describe():
            modified.append((f, old_field.describe(), new_field.describe()))

    if modified:
        report.append("=== Modified Fields ===")
        for f, old_desc, new_desc in modified:
            report.append(f"  ~ {f}:")
            report.append(f"      was: {old_desc}")
            report.append(f"      now: {new_desc}")
        report.append("")

    # 2. Сравнение правил (require)
    old_rules = {_rule_to_str(r) for r in old._rules}
    new_rules = {_rule_to_str(r) for r in new._rules}

    added_rules = new_rules - old_rules
    removed_rules = old_rules - new_rules

    if added_rules:
        report.append("=== Added Rules ===")
        for r in added_rules:
            report.append(f"  + {r}")
        report.append("")

    if removed_rules:
        report.append("=== Removed Rules ===")
        for r in removed_rules:
            report.append(f"  - {r}")
        report.append("")

    # 3. Уникальность
    if old.unique != new.unique:
        report.append("=== Uniqueness Changed ===")
        report.append(f"  was: {old.unique}")
        report.append(f"  now: {new.unique}")
        report.append("")

    # 4. Полный YAML diff
    old_yaml = old.to_yaml()
    new_yaml = new.to_yaml()
    if old_yaml != new_yaml:
        report.append("=== Full Contract Diff ===")
        import difflib
        diff = difflib.unified_diff(
            old_yaml.splitlines(),
            new_yaml.splitlines(),
            lineterm=""
        )
        report.append("\n".join(diff))

    return "\n".join(report) if report else "No changes detected."