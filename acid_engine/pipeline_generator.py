# acid_engine/pipeline_generator.py

def generate_pipeline(ast) -> str:
    lines = []
    lines.append("# Auto-generated pipeline by AcidEngine")
    lines.append("import pandas as pd")
    lines.append("from acid_engine.core import Contract, Field")
    lines.append("")

    for src in ast.get("input", []):
        lines.append(f"# Загрузка {src['name']}")
        lines.append(f"{src['name']} = pd.read_csv('{src['name']}.csv')")
        lines.append("")

    for stage in ast.get("implementation", []):
        stage_name = stage["name"]
        lines.append(f"# Стадия: {stage_name}")
        lines.append(f"def {stage_name}(df):")

        # Join
        for join in stage.get("join", []):
            target = join["target"]
            on = join["on"]
            lines.append(f"    # Join: {target}")
            lines.append(f"    {target} = pd.read_csv('{target}.csv')")
            lines.append(f"    df = df.merge({target}, on='{on}', how='left')")

        # Cast
        for cast in stage.get("cast", []):
            field = cast["field"]
            dtype = cast["type"]
            pd_type = "int" if dtype == "integer" else "float" if dtype == "float" else "str"
            lines.append(f"    # Cast: {field} to {dtype}")
            lines.append(f"    df['{field}'] = df['{field}'].astype({pd_type})")

        # Normalize
        for norm in stage.get("normalize", []):
            lines.append(f"    # Normalize: {norm}")
            lines.append(f"    df['{norm}'] = (df['{norm}'] - df['{norm}'].mean()) / df['{norm}'].std()")

        # Enrich — просто копирует колонку (после join она уже есть)
        for enrich in stage.get("enrich", []):
            lines.append(f"    # Enrich: {enrich}")
            lines.append(f"    df['{enrich}'] = df['{enrich}']")

        # Filter
        filter_data = stage.get("filter")
        if isinstance(filter_data, dict):
            field = filter_data["field"]
            op = filter_data["operator"]
            value = filter_data["value"]
            lines.append(f"    # Filter: {field} {op} {value}")
            if op in (">", "<", ">=", "<="):
                lines.append(f"    df = df[df['{field}'] {op} {value}]")
            elif op == "==":
                lines.append(f"    df = df[df['{field}'] == '{value}']")
            elif op == "between":
                low, high = value
                lines.append(f"    df = df[(df['{field}'] >= {low}) & (df['{field}'] <= {high})]")

        # Deduplicate
        dedup_data = stage.get("deduplicate")
        if isinstance(dedup_data, dict):
            field = dedup_data["field"]
            lines.append(f"    # Deduplicate: {field}")
            lines.append(f"    df = df.drop_duplicates(subset=['{field}'])")

        lines.append("    return df")
        lines.append("")

    lines.append("# Оркестратор")
    lines.append("def main():")
    for stage in ast.get("implementation", []):
        stage_name = stage["name"]
        if stage == ast["implementation"][0]:
            src = stage.get("input", "data")
            lines.append(f"    df = {src}.copy()")
        lines.append(f"    df = {stage_name}(df)")
    output = ast.get("output", [])[0]["name"] if ast.get("output") else "output"
    lines.append(f"    df.to_csv('{output}.csv', index=False)")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    main()")

    return "\n".join(lines)