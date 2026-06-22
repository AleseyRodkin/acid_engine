"""
Полный end‑to‑end сценарий AcidEngine:
- загрузка контракта из YAML
- валидация грязных данных
- отчёт об ошибках (Explain Engine)
- генерация каркаса пайплайна
- AI Guard (проверка ответа LLM)
- LangChain плагин
"""
from acid_engine.core import Contract, Field
from acid_engine.ai import AIGuard
from acid_engine.langchain_plugin import AcidOutputGuard

# 1. Загрузка контракта из YAML
print("=" * 60)
print("1. ЗАГРУЗКА КОНТРАКТА ИЗ YAML")
print("=" * 60)
contract = Contract.from_yaml("demos/users.contract.yaml")
print(contract.describe())

# 2. Валидация грязных данных
print("\n" + "=" * 60)
print("2. ВАЛИДАЦИЯ ГРЯЗНЫХ ДАННЫХ")
print("=" * 60)
dirty_data = [
    {"id": 1, "email": "alice@company.com", "age": 25},   # OK
    {"id": 2, "email": "bob@mail.com", "age": 17},        # OK
    {"id": 3, "email": "bad", "age": 30},                 # плохой email
    {"id": 4, "email": "eve@company.com", "age": 16},     # сотрудник < 18
    {"id": 1, "email": "dup@mail.com", "age": 40},        # дубликат ID
    {"id": 5, "email": "user@test.com", "age": 200},      # возраст > 120
]
result = contract.validate(dirty_data)
print(result.explain())

# 3. Экспорт отчёта в Markdown
print("\n" + "=" * 60)
print("3. ЭКСПОРТ ОТЧЁТА В MARKDOWN")
print("=" * 60)
result.to_markdown("demos/full_report.md")
print("Отчёт сохранён: demos/full_report.md")

# 4. Генерация пайплайна
print("\n" + "=" * 60)
print("4. ГЕНЕРАЦИЯ ПРОИЗВОДСТВЕННОГО ПАЙПЛАЙНА")
print("=" * 60)
pipeline_code = contract.generate_pipeline("demos/generated_pipeline.py")
print("Сгенерирован файл: demos/generated_pipeline.py")
print("\nПервые 8 строк кода:")
for line in pipeline_code.split("\n")[:8]:
    print(line)

# 5. AI Guard (проверка ответа LLM)
print("\n" + "=" * 60)
print("5. AI GUARD (ПРОВЕРКА ОТВЕТА LLM)")
print("=" * 60)
ai_contract = Contract(schema={"answer": Field(type=str, min_length=1)})
guard = AIGuard(ai_contract)

# Хороший ответ
good = {"answer": "Hello, I am fine."}
ai_result = guard.validate(good)
print(f"Good response — errors: {ai_result.summary['errors']}")

# Плохой ответ
bad = {"answer": ""}
ai_result = guard.validate(bad)
print(f"Bad response — errors: {ai_result.summary['errors']}")

# 6. LangChain Plugin
print("\n" + "=" * 60)
print("6. LANGCHAIN ПЛАГИН")
print("=" * 60)
lang_guard = AcidOutputGuard(ai_contract, on_failure="raise")
try:
    lang_guard({"answer": "Valid output"})
    print("✅ Valid output accepted")
except ValueError:
    print("❌ Unexpected rejection")

try:
    lang_guard({"answer": ""})
    print("❌ Should have been rejected")
except ValueError as e:
    print("✅ Invalid output blocked")

print("\n" + "=" * 60)
print("All scenarios executed successfully. AcidEngine is ready.")
print("=" * 60)