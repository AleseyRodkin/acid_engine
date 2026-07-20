import csv
from ..validators.three_valued import PASS, FAIL, SKIPPED, ThreeValuedLogic
from .module_loader import ModuleLoader

class StageRunner:
    def __init__(self, stage_ast, module_loader=None, sources=None, logger=None):
        self.ast = stage_ast
        self.logic = ThreeValuedLogic()
        self.module_loader = module_loader or ModuleLoader()
        self.sources = sources or {}
        self.logger = logger

    def run(self, data, collect_errors=False):
        if self.logger:
            self.logger.log({"event": "stage_start", "stage": self.ast.get("name")})

        report = {"pass": 0, "fail": 0, "skipped": 0}
        validated_data = []
        errors_list = []

        schema = self.ast.get("schema", [])
        rules = self.ast.get("require", [])
        join_list = self.ast.get("join", [])
        enrich_list = self.ast.get("enrich", [])
        derive_list = self.ast.get("derive", [])
        contract = None

        # ---------- JOIN и ENRICH ----------
        if join_list or enrich_list:
            data = self._apply_joins_and_enrich(data, join_list, enrich_list)

        # ---------- DERIVE ----------
        if derive_list:
            data = self._apply_derive(data, derive_list)

        # ---------- Построение контракта ----------
        if schema:
            from acid_engine.core import Contract, Field
            schema_dict = {}
            for field_def in schema:
                if isinstance(field_def, dict):
                    field_name = field_def["field"]
                    if field_def.get("value") == "integer":
                        schema_dict[field_name] = Field(type=int)
                    elif field_def.get("value") == "float":
                        schema_dict[field_name] = Field(type=float)
                    elif field_def.get("value") == "string":
                        schema_dict[field_name] = Field(type=str)
            contract = Contract(schema=schema_dict)

        if contract and rules:
            for rule in rules:
                if isinstance(rule, dict):
                    contract.add_rule(self._rule_to_string(rule))

        module_name = self.ast.get("use")

        if contract:
            for row in data:
                casted_row = self._cast_row(row, schema)
                if casted_row is None:
                    report["fail"] += 1
                    if collect_errors:
                        errors_list.append({
                            "row": row,
                            "message": "Cast failed",
                            "reason": "Type mismatch"
                        })
                    continue
                result = contract.validate([casted_row])
                if result.errors:
                    report["fail"] += 1
                    if collect_errors:
                        for err in result.errors:
                            errors_list.append({
                                "row": casted_row,
                                "message": err.message,
                                "reason": err.reason,
                                "expected": err.expected,
                                "received": err.received
                            })
                else:
                    report["pass"] += 1
                    validated_data.append(casted_row)
            if self.logger:
                self.logger.log({"event": "stage_end", "report": report})
            return validated_data, report, errors_list

        if module_name:
            try:
                module = self.module_loader.get_module(module_name)
                if hasattr(module, 'Contract'):
                    module_contract = module.Contract()
                    validated_data, errors = module_contract.validate(data)
                    report["pass"] = len(validated_data)
                    report["fail"] = len(errors)
                    if self.logger:
                        self.logger.log({"event": "stage_end", "report": report})
                    return validated_data, report, errors
                elif hasattr(module, 'validate'):
                    validated_data, errors = module.validate(data)
                    report["pass"] = len(validated_data)
                    report["fail"] = len(errors)
                    if self.logger:
                        self.logger.log({"event": "stage_end", "report": report})
                    return validated_data, report, errors
                else:
                    raise ValueError(f"Module {module_name} has no validate method")
            except Exception as e:
                if self.logger:
                    self.logger.log({"event": "error", "message": str(e)})
                report["fail"] = len(data)
                return [], report, []

        # fallback
        for row in data:
            results = []
            for rule in rules:
                if isinstance(rule, dict):
                    res = self._apply_rule(row, rule)
                    results.append(res)
            if results:
                final_result = self.logic.and_all(results)
                if final_result == PASS:
                    report["pass"] += 1
                    validated_data.append(row)
                elif final_result == FAIL:
                    report["fail"] += 1
                else:
                    report["skipped"] += 1
            else:
                report["pass"] += 1
                validated_data.append(row)
        if self.logger:
            self.logger.log({"event": "stage_end", "report": report})
        return validated_data, report, errors_list

    def _load_source(self, name):
        path = self.sources.get(name, f"{name}.csv")
        with open(path, 'r') as f:
            return list(csv.DictReader(f))

    def _apply_joins_and_enrich(self, data, join_list, enrich_list):
        if not join_list and not enrich_list:
            return data
        joined_data = []
        for row in data:
            enriched_row = dict(row)
            for j in join_list:
                target = j["target"]
                on = j["on"]
                ref_data = self._load_source(target)
                value = row.get(on)
                if value:
                    for ref_row in ref_data:
                        if ref_row.get(on) == value:
                            for k, v in ref_row.items():
                                enriched_row[f"{target}.{k}"] = v
                            break
            for e in enrich_list:
                field = e["field"]
                source = e["source"]
                source_field = e["source_field"]
                enriched_row[field] = enriched_row.get(f"{source}.{source_field}")
            joined_data.append(enriched_row)
        return joined_data

    def _apply_derive(self, data, derive_list):
        derived_data = []
        for row in data:
            new_row = dict(row)
            for d in derive_list:
                if not isinstance(d, dict):
                    continue
                target = d["target"]
                left = new_row.get(d["left"], 0)
                right = new_row.get(d["right"], 0)
                try:
                    left = float(left)
                    right = float(right)
                except:
                    left = 0
                    right = 0
                op = d["op"]
                if op == "+":
                    new_row[target] = left + right
                elif op == "-":
                    new_row[target] = left - right
                elif op == "*":
                    new_row[target] = left * right
                elif op == "/":
                    new_row[target] = left / right if right != 0 else 0
            derived_data.append(new_row)
        return derived_data

    def _cast_row(self, row, schema):
        casted = {}
        for field_def in schema:
            if not isinstance(field_def, dict):
                continue
            field_name = field_def["field"]
            value = row.get(field_name)
            if value is None:
                continue
            expected_type = field_def.get("value")
            try:
                if expected_type == "integer":
                    casted[field_name] = int(value)
                elif expected_type == "float":
                    casted[field_name] = float(value)
                else:
                    casted[field_name] = value
            except (ValueError, TypeError):
                return None
        for k, v in row.items():
            if k not in casted:
                casted[k] = v
        return casted

    def _apply_rule(self, row, rule):
        field_name = rule["field"]
        value = row.get(field_name)
        if value is None:
            return SKIPPED
        try:
            op = rule["operator"]
            if op == "is":
                expected_type = rule["value"]
                if expected_type == "integer":
                    int(value)
                    return PASS
                elif expected_type == "float":
                    float(value)
                    return PASS
                elif expected_type == "string":
                    return PASS if isinstance(value, str) else FAIL
            elif op in (">", "<", ">=", "<=", "!="):
                num_value = float(value)
                threshold = rule["value"]
                if op == ">":
                    return PASS if num_value > threshold else FAIL
                elif op == "<":
                    return PASS if num_value < threshold else FAIL
                elif op == ">=":
                    return PASS if num_value >= threshold else FAIL
                elif op == "<=":
                    return PASS if num_value <= threshold else FAIL
                elif op == "!=":
                    return PASS if num_value != threshold else FAIL
            elif op == "between":
                low, high = rule["value"]
                num_value = float(value)
                return PASS if low <= num_value <= high else FAIL
        except (ValueError, TypeError):
            return FAIL
        return SKIPPED

    def _rule_to_string(self, rule):
        op = rule["operator"]
        if op == "is":
            return f"{rule['field']} is {rule['value']}"
        elif op == "between":
            low, high = rule["value"]
            return f"{rule['field']} >= {low} and {rule['field']} <= {high}"
        else:
            return f"{rule['field']} {op} {rule['value']}"