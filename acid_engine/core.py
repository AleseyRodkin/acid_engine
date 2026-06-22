# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

import re, copy, os
from typing import Optional, List, Any, Callable, Union, Tuple

class ContractViolation(Exception):
    def __init__(self, message: str, contract_name: str = None,
                 expected: str = None, received: str = None, reason: str = None):
        super().__init__(message)
        self.contract_name = contract_name
        self.expected = expected
        self.received = received
        self.reason = reason

    def explain(self) -> str:
        parts = []
        if self.contract_name:
            parts.append(f"Contract: {self.contract_name}")
        if self.expected:
            parts.append(f"Expected: {self.expected}")
        if self.received:
            parts.append(f"Received: {self.received}")
        if self.reason:
            parts.append(f"Reason: {self.reason}")
        return "\n".join(parts) if parts else str(self)


class QualityGateExceeded(Exception):
    pass


class ErrorRecord:
    def __init__(self, row, contract_name: str, violation: str, message: str,
                 expected: str = None, received: str = None, reason: str = None):
        self.row = row
        self.contract_name = contract_name
        self.violation = violation
        self.message = message
        self.expected = expected
        self.received = received
        self.reason = reason

    def __repr__(self):
        return (f"ErrorRecord(row={self.row!r}, contract={self.contract_name!r}, "
                f"expected={self.expected!r}, received={self.received!r}, "
                f"reason={self.reason!r}, message={self.message!r})")


class Field:
    def __init__(self, type=None, validators=None, regex=None,
                 min=None, max=None, min_length=None, max_length=None,
                 choices=None):
        self.type = type
        self.validators = validators or []
        self.regex = regex
        self.min = min
        self.max = max
        self.min_length = min_length
        self.max_length = max_length
        self.choices = choices

    def validate(self, value):
        if self.type is not None and not isinstance(value, self.type):
            raise ContractViolation(
                f"Ожидался тип {self.type.__name__}, получен {type(value).__name__}",
                contract_name="Field", expected=str(self.type.__name__),
                received=type(value).__name__, reason="Type mismatch"
            )
        if self.min is not None and value < self.min:
            raise ContractViolation(
                f"Значение {value} меньше минимального {self.min}",
                contract_name="Field", expected=f">= {self.min}",
                received=str(value), reason="Below minimum"
            )
        if self.max is not None and value > self.max:
            raise ContractViolation(
                f"Значение {value} больше максимального {self.max}",
                contract_name="Field", expected=f"<= {self.max}",
                received=str(value), reason="Above maximum"
            )
        if self.min_length is not None and len(value) < self.min_length:
            raise ContractViolation(
                f"Длина меньше {self.min_length}",
                contract_name="Field", expected=f"length >= {self.min_length}",
                received=f"length {len(value)}", reason="Too short"
            )
        if self.max_length is not None and len(value) > self.max_length:
            raise ContractViolation(
                f"Длина больше {self.max_length}",
                contract_name="Field", expected=f"length <= {self.max_length}",
                received=f"length {len(value)}", reason="Too long"
            )
        if self.regex is not None and not re.match(self.regex, str(value)):
            raise ContractViolation(
                f"Значение не соответствует регулярному выражению {self.regex}",
                contract_name="Field", expected=f"matches {self.regex}",
                received=str(value), reason="Regex mismatch"
            )
        if self.choices is not None and value not in self.choices:
            raise ContractViolation(
                f"Значение должно быть одним из {self.choices}",
                contract_name="Field", expected=str(self.choices),
                received=str(value), reason="Not in allowed choices"
            )
        for idx, validator in enumerate(self.validators):
            try:
                result = validator(value)
                if result is False:
                    raise ContractViolation(
                        f"Валидатор #{idx} не пройден для {value!r}",
                        contract_name="Field", expected="custom validation passed",
                        received="custom validation failed", reason=f"Validator #{idx} returned False"
                    )
            except ContractViolation:
                raise
            except Exception as e:
                raise ContractViolation(
                    f"Ошибка в валидаторе #{idx}: {e}",
                    contract_name="Field", reason=f"Validator #{idx} raised {type(e).__name__}"
                )

    def __call__(self, value):
        self.validate(value)
        return value

    def describe(self) -> str:
        desc = []
        if self.type:
            desc.append(f"type: {self.type.__name__}")
        if self.regex:
            desc.append(f"regex: {self.regex}")
        if self.min is not None:
            desc.append(f"min: {self.min}")
        if self.max is not None:
            desc.append(f"max: {self.max}")
        if self.min_length is not None:
            desc.append(f"min_length: {self.min_length}")
        if self.max_length is not None:
            desc.append(f"max_length: {self.max_length}")
        if self.choices:
            desc.append(f"choices: {self.choices}")
        if self.validators:
            desc.append(f"validators: {len(self.validators)} custom")
        return ", ".join(desc)

    @classmethod
    def Email(cls):
        return cls(type=str, regex=r"^[^@]+@[^@]+\.[^@]+$")

    @classmethod
    def HttpUrl(cls):
        return cls(type=str, validators=[lambda v: v.startswith("https://")])

    @classmethod
    def Url(cls):
        return cls(type=str, validators=[lambda v: any(v.startswith(s) for s in ("http://", "https://"))])

    @classmethod
    def Phone(cls):
        return cls(type=str, regex=r"^\+?\d{7,15}$")

    @classmethod
    def UUID(cls):
        return cls(type=str, regex=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    @classmethod
    def IPv4(cls):
        return cls(type=str, regex=r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$")

    @classmethod
    def IPv6(cls):
        return cls(type=str, regex=r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")


class ValidationResult:
    def __init__(self, valid_data: list, errors: list, summary: dict):
        self.valid_data = valid_data
        self.errors = errors
        self.summary = summary

    def explain(self) -> str:
        lines = []
        lines.append(f"Всего проверено: {self.summary.get('total', 0)}")
        lines.append(f"Ошибок: {self.summary.get('errors', 0)}")
        lines.append(f"Успешно: {self.summary.get('total', 0) - self.summary.get('errors', 0)}")
        if self.summary.get('error_rate') is not None:
            lines.append(f"Процент ошибок: {self.summary['error_rate']:.1%}")

        if self.summary.get('top_violations'):
            lines.append("\nТоп нарушений:")
            for reason, count in self.summary['top_violations']:
                lines.append(f"  {reason}: {count}")

        if self.errors:
            lines.append(f"\nПримеры ошибочных записей (первые 5):")
            for err in self.errors[:5]:
                lines.append(f"  Запись: {err.row}")
                if err.reason:
                    lines.append(f"    Причина: {err.reason}")
                if err.expected:
                    lines.append(f"    Ожидалось: {err.expected}")
                if err.received:
                    lines.append(f"    Получено: {err.received}")
                lines.append("")

        return "\n".join(lines)

    def to_markdown(self, filepath: str):
        """Сохраняет отчёт в Markdown-файл."""
        md = []
        md.append("# Отчёт о качестве данных\n")
        md.append(f"**Всего проверено:** {self.summary.get('total', 0)}  \n")
        md.append(f"**Ошибок:** {self.summary.get('errors', 0)}  \n")
        md.append(f"**Успешно:** {self.summary.get('total', 0) - self.summary.get('errors', 0)}  \n")
        if self.summary.get('error_rate') is not None:
            md.append(f"**Процент ошибок:** {self.summary['error_rate']:.1%}  \n")

        if self.summary.get('top_violations'):
            md.append("\n## Топ нарушений\n")
            for reason, count in self.summary['top_violations']:
                md.append(f"- {reason}: {count}\n")

        if self.errors:
            md.append("\n## Примеры ошибочных записей\n")
            for err in self.errors[:5]:
                md.append(f"### Запись: `{err.row}`\n")
                if err.reason:
                    md.append(f"- **Причина:** {err.reason}\n")
                if err.expected:
                    md.append(f"- **Ожидалось:** {err.expected}\n")
                if err.received:
                    md.append(f"- **Получено:** {err.received}\n")
                md.append("\n")

        with open(filepath, 'w') as f:
            f.writelines(md)


class Contract:
    def __init__(self, unique=False, ordered=False, frozen=False,
                 dtype=None, validators=None, max_error_rate=None,
                 item_contract=None, schema=None,
                 pipeline_meta=None):
        self.unique = unique
        self.ordered = ordered
        self.frozen = frozen
        self.dtype = dtype
        self.validators = validators or []
        self.max_error_rate = max_error_rate
        self.is_map = isinstance(dtype, tuple) and len(dtype) == 2
        self.item_contract = item_contract
        self.schema = schema
        self._rules = []
        self.pipeline_meta = pipeline_meta or {}

    def add_rule(self, rule):
        self._rules.append(rule)

    def create_container(self):
        return Container(self)

    def describe(self) -> str:
        lines = []
        if self.unique:
            lines.append("unique: True")
        if self.ordered:
            lines.append("ordered: True")
        if self.frozen:
            lines.append("frozen: True")
        if self.item_contract:
            lines.append(f"item_contract: {self.item_contract.describe()}")
        if self.schema:
            lines.append("schema:")
            for name, field in self.schema.items():
                lines.append(f"  {name}: {field.describe()}")
        if self._rules:
            lines.append("rules:")
            for r in self._rules:
                lines.append(f"  {r}")
        return "\n".join(lines) if lines else "No constraints"

    def validate(self, data):
        # Если передан DataFrame, конвертируем в список словарей
        try:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient='records')
        except ImportError:
            pass  # pandas не установлен – работаем как со списком

        if not isinstance(data, list):
            raise TypeError("data должен быть списком словарей или pandas DataFrame")

        container = self.create_container()
        gate = QualityGate(container, max_error_rate=1.0,
                           mode="quarantine", collect_errors=True)
        for row in data:
            gate.add(row)
        return ValidationResult(
            valid_data=list(container),
            errors=gate.error_records,
            summary=gate.summary()
        )

    def to_yaml(self, filepath: str = None) -> str:
        import yaml
        yaml_data = {}
        if self.schema:
            yaml_data['schema'] = {}
            for name, field in self.schema.items():
                yaml_data['schema'][name] = {
                    'type': field.type.__name__ if field.type else 'str',
                    'min': field.min,
                    'max': field.max,
                    'min_length': field.min_length,
                    'max_length': field.max_length,
                    'regex': field.regex,
                    'choices': field.choices
                }
        if self.unique:
            yaml_data['unique'] = self.unique
        if self._rules:
            yaml_data['rules'] = [str(r) for r in self._rules]
        if self.validators:
            yaml_data['validators'] = [str(v) for v in self.validators]
        yaml_str = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
        if filepath:
            with open(filepath, 'w') as f:
                f.write(yaml_str)
        return yaml_str

    @classmethod
    def from_yaml(cls, source: str):
        import yaml
        if source.endswith('.yaml') or source.endswith('.yml'):
            with open(source, 'r') as f:
                data = yaml.safe_load(f)
        else:
            data = yaml.safe_load(source)
        schema = {}
        if 'schema' in data:
            for name, field_data in data['schema'].items():
                if isinstance(field_data, dict):
                    field_type = field_data.get('type', 'str')
                    if field_type == 'int':
                        field = Field(type=int)
                    elif field_type == 'float':
                        field = Field(type=float)
                    else:
                        field = Field(type=str)
                    if 'min' in field_data and field_data['min'] is not None:
                        field.min = field_data['min']
                    if 'max' in field_data and field_data['max'] is not None:
                        field.max = field_data['max']
                    if 'min_length' in field_data:
                        field.min_length = field_data['min_length']
                    if 'max_length' in field_data:
                        field.max_length = field_data['max_length']
                    if 'regex' in field_data:
                        field.regex = field_data['regex']
                    if 'choices' in field_data:
                        field.choices = field_data['choices']
                    schema[name] = field
        unique = data.get('unique', False)
        rules = data.get('rules', [])
        pipeline_meta = data.get('pipeline', {})
        contract = cls(schema=schema, unique=unique, pipeline_meta=pipeline_meta)
        for rule in rules:
            contract.add_rule(rule)
        return contract

    @classmethod
    def from_data(cls, data: list, sample_size: int = 100):
        if not data:
            return cls(), {}
        profile = {}
        sample = data[:sample_size]
        keys = list(sample[0].keys())
        heuristics = [
            ("email", Field.Email()),
            ("url", Field.Url()),
            ("http_url", Field.HttpUrl()),
            ("uuid", Field.UUID()),
            ("phone", Field.Phone()),
            ("ipv4", Field.IPv4()),
        ]
        for key in keys:
            values = [row[key] for row in sample if key in row]
            types = {type(v).__name__ for v in values}
            unique = len(values) == len(set(str(v) for v in values))
            nulls = sum(1 for v in values if v is None or v == '')
            best_field = None
            best_score = 0
            for name, field in heuristics:
                score = 0
                for v in values:
                    if v is None or v == '':
                        continue
                    try:
                        field.validate(v)
                        score += 1
                    except ContractViolation:
                        pass
                if score / max(1, len(values)) > 0.8 and score > best_score:
                    best_score = score
                    best_field = field
            profile[key] = {
                "types": types,
                "unique": unique,
                "nulls": nulls,
                "total": len(values),
                "suggested_field": best_field
            }
        schema = {}
        for key, info in profile.items():
            if info["suggested_field"]:
                schema[key] = info["suggested_field"]
            else:
                if len(info["types"]) == 1:
                    dtype = list(info["types"])[0]
                    if dtype == "int":
                        schema[key] = Field(type=int)
                    elif dtype == "float":
                        schema[key] = Field(type=float)
                    else:
                        schema[key] = Field(type=str)
                else:
                    schema[key] = Field(type=str)
        return cls(schema=schema), profile

    def generate_pipeline(self, output_path: str = None) -> str:
        meta = self.pipeline_meta
        input_desc = meta.get('input', 'input_data')
        output_desc = meta.get('output', 'output_data')
        steps = meta.get('processing', [])

        lines = []
        lines.append("# Auto-generated pipeline by AcidEngine")
        lines.append("from acid_engine.scope import global_scope, orchestrator")
        lines.append("from acid_engine.core import Contract, Field, QualityGate")
        lines.append("")
        lines.append("# Загрузка контракта (пример, замените на свой)")
        lines.append("contract = Contract.from_yaml('users.contract.yaml')")
        lines.append("")
        lines.append("")
        for step in steps:
            lines.append(f"def {step}():")
            lines.append("    pass")
            lines.append("")
        lines.append("")
        lines.append("@orchestrator")
        lines.append("def process():")
        lines.append(f"    # Вход: {input_desc}")
        lines.append(f"    # Выход: {output_desc}")
        for step in steps:
            lines.append(f"    {step}()")
        lines.append("")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    with global_scope('generated_pipeline'):")
        lines.append("        process()")

        code = "\n".join(lines)
        if output_path:
            with open(output_path, 'w') as f:
                f.write(code)
        return code


class Container:
    def __init__(self, contract: Contract):
        self.contract = contract
        self._data = []
        self._frozen = contract.frozen

    def add(self, item, key=None):
        if self._frozen:
            raise ContractViolation("Контейнер заморожен", contract_name="Container", reason="Frozen")

        if self.contract.schema is not None:
            if not isinstance(item, dict):
                raise ContractViolation("Для schema требуется словарь", contract_name="Container",
                                        expected="dict", received=type(item).__name__, reason="Schema validation")
            validated = {}
            for field_name, field in self.contract.schema.items():
                if field_name not in item:
                    raise ContractViolation(f"Отсутствует поле '{field_name}'", contract_name="Container",
                                            expected=f"field '{field_name}'", received="None", reason="Missing field")
                validated[field_name] = field(item[field_name])
            item = validated
        elif self.contract.item_contract is not None:
            item = self.contract.item_contract(item)

        if self.contract.schema and self.contract._rules:
            for rule in self.contract._rules:
                if isinstance(rule, str):
                    try:
                        from simpleeval import simple_eval
                        result = simple_eval(rule, names=item)
                        if not result:
                            raise ContractViolation(
                                f"Cross‑field правило не пройдено: '{rule}'",
                                contract_name="CrossField",
                                expected="True",
                                received=str(result),
                                reason="Cross‑field rule failed"
                            )
                    except ContractViolation:
                        raise
                    except Exception as e:
                        raise ContractViolation(
                            f"Ошибка в cross‑field правиле '{rule}': {e}",
                            contract_name="CrossField",
                            reason=f"Rule evaluation error: {e}"
                        )
                else:
                    try:
                        result = rule(item)
                        if not result:
                            raise ContractViolation(
                                "Cross‑field правило не пройдено",
                                contract_name="CrossField",
                                expected="True",
                                received="False",
                                reason="User‑defined cross‑field rule failed"
                            )
                    except ContractViolation:
                        raise
                    except Exception as e:
                        raise ContractViolation(
                            f"Ошибка в cross‑field правиле: {e}",
                            contract_name="CrossField",
                            reason=f"Rule error: {e}"
                        )

        if self.contract.is_map:
            if key is None:
                raise ContractViolation("Для словаря нужен ключ (key=...)", contract_name="Container")
            key_type, val_type = self.contract.dtype
            if not isinstance(key, key_type):
                raise ContractViolation(
                    f"Ключ должен быть {key_type.__name__}, получен {type(key).__name__}",
                    contract_name="Container", expected=str(key_type.__name__), received=type(key).__name__)
            if not isinstance(item, val_type):
                raise ContractViolation(
                    f"Значение должно быть {val_type.__name__}, получено {type(item).__name__}",
                    contract_name="Container", expected=str(val_type.__name__), received=type(item).__name__)
            if self.contract.unique:
                for k, v in self._data:
                    if k == key:
                        raise ContractViolation(f"Дубликат ключа: {key}", contract_name="Container",
                                                expected="unique key", received=str(key), reason="Duplicate")
            self._run_validators(item)
            self._data.append((key, item))
        else:
            if self.contract.dtype is not None and not isinstance(item, self.contract.dtype):
                raise ContractViolation(
                    f"Ожидался тип {self.contract.dtype.__name__}, получен {type(item).__name__}",
                    contract_name="Container", expected=self.contract.dtype.__name__, received=type(item).__name__)
            if self.contract.unique and item in self._data:
                raise ContractViolation(f"Дубликат: {item}", contract_name="Container",
                                        expected="unique", received=str(item), reason="Duplicate")
            self._run_validators(item)
            self._data.append(item)

    def _run_validators(self, item):
        for idx, validator in enumerate(self.contract.validators):
            try:
                result = validator(item)
                if result is False:
                    raise ContractViolation(f"Валидатор #{idx} не пройден для {item!r}",
                                            contract_name="Container", reason=f"Validator #{idx} failed")
            except ContractViolation:
                raise
            except Exception as e:
                raise ContractViolation(f"Ошибка в валидаторе #{idx}: {e}",
                                        contract_name="Container", reason=f"Validator #{idx} raised {type(e).__name__}")

    def freeze(self):
        self._frozen = True

    @property
    def is_frozen(self):
        return self._frozen

    def snapshot(self):
        return {'data': copy.deepcopy(self._data), 'frozen': self._frozen}

    def restore_snapshot(self, snap):
        self._data = copy.deepcopy(snap['data'])
        self._frozen = snap['frozen']

    def get(self, index: int):
        if not self.contract.ordered:
            raise ContractViolation("Индексация доступна только для упорядоченных контейнеров (ordered=True)",
                                    contract_name="Container", reason="Not ordered")
        if index < 0 or index >= len(self._data):
            raise IndexError("Индекс вне диапазона")
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        if self.contract.is_map:
            return item in self._data
        return item in self._data

    def __repr__(self):
        return f"Container({self._data!r})"


class QualityGate:
    def __init__(self, container: Container, max_error_rate: float,
                 mode: str = "strict",
                 good_container: Optional[List] = None,
                 archive_container: Optional[List] = None,
                 error_container: Optional[List] = None,
                 collect_errors: bool = False):
        self.container = container
        self.max_error_rate = max_error_rate
        self.mode = mode
        self.good_container = good_container
        self.archive_container = archive_container
        self.error_container = error_container
        self.collect_errors = collect_errors
        self.error_records: List[ErrorRecord] = []
        self.snapshot = container.snapshot()
        self.errors = 0
        self.total = 0
        self._good_buffer = []
        self._all_buffer = []

    def add(self, item, key=None):
        self.total += 1
        is_good = True
        try:
            self.container.add(item, key)
        except ContractViolation as e:
            is_good = False
            self.errors += 1
            if self.collect_errors:
                self.error_records.append(
                    ErrorRecord(
                        row=item,
                        contract_name=e.contract_name or 'container',
                        violation=type(e).__name__,
                        message=str(e),
                        expected=e.expected,
                        received=e.received,
                        reason=e.reason
                    )
                )
            if self.error_container is not None:
                self.error_container.append((item, key, str(e)))

        if self.mode in ("recovery", "audit"):
            if is_good:
                self._good_buffer.append((item, key))
            if self.mode == "audit":
                self._all_buffer.append((item, key, is_good))

        if self.total > 0 and (self.errors / self.total) > self.max_error_rate:
            if self.mode == "strict":
                self.container.restore_snapshot(self.snapshot)
                raise QualityGateExceeded(
                    f"Порог ошибок {self.max_error_rate:.0%} превышен: "
                    f"{self.errors}/{self.total} ({self.errors/self.total:.1%}). Контейнер откачен."
                )
            elif self.mode == "recovery":
                self.container.restore_snapshot(self.snapshot)
                if self.good_container is not None:
                    self.good_container.extend(self._good_buffer)
                raise QualityGateExceeded(
                    f"Порог ошибок {self.max_error_rate:.0%} превышен: "
                    f"{self.errors}/{self.total} ({self.errors/self.total:.1%}). "
                    f"Хорошие записи сохранены в good_container."
                )
            elif self.mode == "audit":
                self.container.restore_snapshot(self.snapshot)
                if self.archive_container is not None:
                    self.archive_container.extend(self._all_buffer)
                raise QualityGateExceeded(
                    f"Порог ошибок {self.max_error_rate:.0%} превышен: "
                    f"{self.errors}/{self.total} ({self.errors/self.total:.1%}). "
                    f"Все записи сохранены в archive_container."
                )
            elif self.mode == "quarantine":
                raise QualityGateExceeded(
                    f"Порог ошибок {self.max_error_rate:.0%} превышен: "
                    f"{self.errors}/{self.total} ({self.errors/self.total:.1%}). "
                    f"Контейнер не откачен."
                )
        return is_good

    @property
    def data(self):
        return list(self.container)

    def summary(self) -> dict:
        top_errors = {}
        for rec in self.error_records:
            key = rec.reason or rec.message
            top_errors[key] = top_errors.get(key, 0) + 1
        return {
            "total": self.total,
            "errors": self.errors,
            "error_rate": self.errors / self.total if self.total else 0,
            "top_violations": sorted(top_errors.items(), key=lambda x: -x[1])[:5]
        }