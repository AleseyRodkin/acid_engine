from acid_engine.parser.parser import parse_contract
from acid_engine.visualization import generate_mermaid

# Парсим контракт
ast = parse_contract("test_derived.ae")

# Генерируем Mermaid
mermaid_code = generate_mermaid(ast)
print("=== Mermaid Code ===\n")
print(mermaid_code)
print("\nСкопируйте этот код на https://mermaid.live для просмотра графа.")

# Сохраняем в файл
with open("pipeline_graph.mermaid", "w") as f:
    f.write(mermaid_code)
print("\nГраф также сохранён в pipeline_graph.mermaid")