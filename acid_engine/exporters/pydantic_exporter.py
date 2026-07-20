# acid_engine/exporters/pydantic_exporter.py
# Генерация Pydantic-моделей из контракта AcidEngine.

from ..core import Contract, Field

def to_pydantic_model(contract: Contract, class_name: str = "AcidModel") -> str:
    """
    Генерирует строку с определением класса Pydantic на основе контракта.
    """
    lines = []
    lines.append("from pydantic import BaseModel, validator, Field as PydanticField")
    lines.append("import re")
    lines.append("")
    lines.append(f"class {class_name}(BaseModel):")

    if contract.schema:
        for field_name, field in contract.schema.items():
            # Определяем тип
            if field.type == int:
                py_type = "int"
            elif field.type == float:
                py_type = "float"
            elif field.type == str:
                py_type = "str"
            else:
                py_type = "str"

            # Собираем параметры для Field
            params = []
            if field.min is not None:
                params.append(f"ge={field.min}")
            if field.max is not None:
                params.append(f"le={field.max}")
            if field.min_length is not None:
                params.append(f"min_length={field.min_length}")
            if field.max_length is not None:
                params.append(f"max_length={field.max_length}")
            if field.regex is not None:
                params.append(f"regex=r\"{field.regex}\"")
            if field.choices is not None:
                params.append(f"choices={field.choices}")

            field_def = f"PydanticField(...)" if not params else f"PydanticField({', '.join(params)})"
            lines.append(f"    {field_name}: {py_type} = {field_def}")

        # Валидаторы для уникальности и правил
        if contract.unique:
            unique_fields = list(contract.unique) if isinstance(contract.unique, list) else [contract.unique]
            lines.append("")
            lines.append("    @validator('*', pre=True)")
            lines.append("    def check_unique(cls, v, values, field):")
            lines.append("        # Заглушка: уникальность проверяется на уровне набора данных")
            lines.append("        return v")

        if contract._rules:
            lines.append("")
            lines.append("    @validator('*', pre=True)")
            lines.append("    def check_rules(cls, v, values, field):")
            lines.append("        # Заглушка: бизнес-правила проверяются отдельно")
            lines.append("        return v")

    return "\n".join(lines)