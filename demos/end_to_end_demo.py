# Полный цикл: CSV → контракт → валидация → отчёт
from acid_engine.csv_loader import load_csv

# Загружаем CSV с автоматическим контрактом
container, gate, profile = load_csv(
    "sample.csv",
    max_error_rate=0.5,
    mode="quarantine",
    collect_errors=True
)

print("=== Data Profile ===")
for field, info in profile.items():
    suggested = info['suggested_field'].describe() if info['suggested_field'] else 'no suggestion'
    print(f"{field}: types={info['types']}, unique={info['unique']}, nulls={info['nulls']}/{info['total']}")
    print(f"   suggested: {suggested}")

print("\n=== Accepted Records ===")
for item in container:
    print(item)

print("\n=== Error Records ===")
for rec in gate.error_records:
    print(rec)

print("\n=== Quality Summary ===")
summary = gate.summary()
print(f"Total: {summary['total']}, Errors: {summary['errors']}, Error Rate: {summary['error_rate']:.1%}")
print("Top violations:")
for reason, count in summary['top_violations']:
    print(f"  {reason}: {count}")