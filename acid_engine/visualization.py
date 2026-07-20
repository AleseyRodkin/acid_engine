# acid_engine/visualization.py
# Генератор Mermaid-графов пайплайнов

def generate_mermaid(ast) -> str:
    """
    Генерирует Mermaid-строку для визуализации пайплайна.
    Поддерживаются: стадии, входы, выходы, join, enrich, derive.
    """
    lines = ["graph TD"]

    # Источники (Input)
    for src in ast.get("input", []):
        lines.append(f"    {src['name']}[{src['name']}]")

    # Стадии
    for stage in ast.get("implementation", []):
        stage_name = stage["name"]
        lines.append(f"    {stage_name}[{stage_name}]")

        # Вход стадии
        input_name = stage.get("input")
        if input_name:
            lines.append(f"    {input_name} --> {stage_name}")

        # Join-ы и enrich-и
        for join in stage.get("join", []):
            target = join["target"]
            lines.append(f"    {target} --> {stage_name}")
            lines.append(f"    {target}[{target}]")

        # Выход стадии
        output_name = stage.get("output")
        if output_name:
            lines.append(f"    {stage_name} --> {output_name}")

    return "\n".join(lines)