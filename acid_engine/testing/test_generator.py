import os

class ContractTestGenerator:
    def __init__(self, contract_ast):
        self.ast = contract_ast

    def generate(self, output_path="test_contract.py"):
        tests = self._build_tests()
        with open(output_path, "w") as f:
            f.write(tests)
        return output_path

    def _build_tests(self):
        lines = []
        lines.append("# Auto-generated tests by AcidEngine")
        lines.append("import pytest")
        lines.append("from acid_engine.parser.parser import parse_contract")
        lines.append("from acid_engine.runtime.runner import StageRunner")
        lines.append("import csv")
        lines.append("import os")
        lines.append("")
        lines.append(f"CONTRACT_FILE = \"{self.ast.get('_source_file', 'test.ae')}\"")
        lines.append("")
        lines.append("def load_data():")
        lines.append("    return [")
        lines.append("        {\"order_id\": \"1\", \"price\": \"10.0\", \"quantity\": \"5\"},")
        lines.append("        {\"order_id\": \"bad\", \"price\": \"-1\", \"quantity\": \"200\"},")
        lines.append("    ]")
        lines.append("")
        lines.append("def test_contract_validation():")
        lines.append("    ast = parse_contract(CONTRACT_FILE)")
        lines.append("    data = load_data()")
        lines.append("    for stage in ast['implementation']:")
        lines.append("        runner = StageRunner(stage)")
        lines.append("        validated, report, errors = runner.run(data, collect_errors=True)")
        lines.append("        assert report['pass'] >= 0")
        lines.append("        assert report['fail'] >= 0")
        lines.append("        assert len(validated) == report['pass']")
        lines.append("")

        # Собираем полную схему из всех стадий
        all_schema = {}
        derived_fields = set()
        for stage in self.ast.get("implementation", []):
            for field_def in stage.get("schema", []):
                if isinstance(field_def, dict):
                    all_schema[field_def["field"]] = field_def.get("value", "string")
            for d in stage.get("derive", []):
                if isinstance(d, dict):
                    derived_fields.add(d.get("target", ""))

        # Генерируем тест для каждого правила
        for stage in self.ast.get("implementation", []):
            for rule in stage.get("require", []):
                if isinstance(rule, dict):
                    field = rule["field"]
                    if field in derived_fields:
                        continue
                    op = rule["operator"]
                    value = rule["value"]
                    safe_op = op.replace(">", "gt").replace("<", "lt").replace("=", "eq").replace("!", "not")
                    if isinstance(value, list):
                        safe_val = f"{value[0]}_{value[1]}"
                    else:
                        safe_val = str(value).replace(".", "_").replace("-", "minus")
                    test_name = f"test_rule_{stage['name']}_{field}_{safe_op}_{safe_val}"
                    lines.append(f"def {test_name}():")
                    lines.append(f"    ast = parse_contract(CONTRACT_FILE)")
                    # Строим полную строку со всеми полями схемы
                    row_parts = []
                    for f, t in all_schema.items():
                        if f == field:
                            val = self._make_valid_value(op, value, t)
                        else:
                            val = self._make_default_value(t)
                        row_parts.append(f"\"{f}\": {repr(val)}")
                    lines.append(f"    data = [{{{', '.join(row_parts)}}}]")
                    lines.append(f"    for stage in ast['implementation']:")
                    lines.append(f"        runner = StageRunner(stage)")
                    lines.append(f"        validated, report, errors = runner.run(data, collect_errors=True)")
                    lines.append(f"        assert report['fail'] == 0, f\"Rule {test_name} failed\"")
                    lines.append("")
        return "\n".join(lines)

    def _make_valid_value(self, op, value, dtype):
        """Генерирует заведомо валидное значение для правила."""
        if op in (">", ">="):
            return value + 1
        elif op in ("<", "<="):
            return value - 1 if value > 0 else value / 2
        elif op == "!=":
            return value + 1
        elif op == "between":
            low, high = value
            return (low + high) / 2
        elif op == "is":
            if dtype == "integer":
                return 1
            elif dtype == "float":
                return 1.0
            elif dtype == "string":
                return "hello"
        return 1

    def _make_default_value(self, dtype):
        """Генерирует значение по умолчанию для поля, не участвующего в правиле."""
        if dtype == "integer":
            return 1
        elif dtype == "float":
            return 1.0
        elif dtype == "string":
            return "hello"
        return 1