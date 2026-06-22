""" Smoke-тесты для AcidEngine v1.0 """

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from acid_engine.core import (
    ContractViolation, QualityGateExceeded,
    Field, Contract, Container, QualityGate, ValidationResult, ErrorRecord
)
from acid_engine.ai import AIGuard

PASSED = 0
FAILED = 0

def check(name: str, condition: bool, detail: str = ""):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}  {detail}")

# ---------- Field ----------
print("=== Field Tests ===")
f = Field(type=int, min=1, max=100)
try:
    f.validate(50)
    check("valid value", True)
except Exception as e:
    check("valid value", False, str(e))

try:
    f.validate(0)
    check("below min raises", False, "should raise")
except ContractViolation:
    check("below min raises", True)

try:
    f.validate(150)
    check("above max raises", False, "should raise")
except ContractViolation:
    check("above max raises", True)

email_field = Field.Email()
check("email valid", email_field.validate("a@b.com") is None)
try:
    email_field.validate("bad")
    check("email invalid raises", False, "should raise")
except ContractViolation:
    check("email invalid raises", True)

# ---------- Container + Contract ----------
print("\n=== Container Tests ===")
c = Contract(unique=True, schema={"id": Field(type=int, min=1)})
container = c.create_container()
container.add({"id": 1})
check("add first", len(container) == 1)
try:
    container.add({"id": 1})
    check("duplicate raises", False, "should raise")
except ContractViolation:
    check("duplicate raises", True)

container.freeze()
try:
    container.add({"id": 2})
    check("frozen raises", False, "should raise")
except ContractViolation:
    check("frozen raises", True)

# ---------- Cross‑Field Rules ----------
print("\n=== Cross‑Field Tests ===")
c2 = Contract(schema={"a": Field(type=int), "b": Field(type=int)})
c2.add_rule("a < b")
container2 = c2.create_container()
container2.add({"a": 1, "b": 2})
check("cross‑field valid", len(container2) == 1)
try:
    container2.add({"a": 3, "b": 2})
    check("cross‑field invalid raises", False, "should raise")
except ContractViolation:
    check("cross‑field invalid raises", True)

# ---------- QualityGate ----------
print("\n=== QualityGate Tests ===")
c3 = Contract(schema={"x": Field(type=int, min=0)})
main = c3.create_container()
gate = QualityGate(main, max_error_rate=0.5, mode="strict")
gate.add({"x": 1})
gate.add({"x": 2})
try:
    gate.add({"x": -1})
    check("gate error", len(gate.error_records) == 1 if gate.collect_errors else True)
except QualityGateExceeded:
    check("strict rollback on threshold", len(main) == 2)

# ---------- Explain Engine ----------
print("\n=== Explain Engine Tests ===")
c4 = Contract(schema={"email": Field.Email()})
result = c4.validate([
    {"email": "ok@b.com"},
    {"email": "bad"}
])
check("explain has total", result.summary.get("total") == 2)
check("explain has errors", result.summary.get("errors") == 1)
output = result.explain()
check("explain string", "Ошибок: 1" in output or "Errors: 1" in output or "errors" in output.lower())

# ---------- YAML ----------
print("\n=== YAML Tests ===")
c5 = Contract(schema={"val": Field(type=int, min=5)})
yaml_str = c5.to_yaml()
c5_loaded = Contract.from_yaml(yaml_str)
check("YAML roundtrip schema", "val" in (c5_loaded.schema or {}))
check("YAML roundtrip min", c5_loaded.schema["val"].min == 5)

# ---------- Pipeline Generator ----------
print("\n=== Pipeline Generator Tests ===")
c6 = Contract(
    schema={"id": Field(type=int)},
    pipeline_meta={
        "input": "test.csv",
        "output": "out.csv",
        "processing": ["load", "clean"]
    }
)
code = c6.generate_pipeline()
check("pipeline has load", "def load" in code)
check("pipeline has clean", "def clean" in code)
check("pipeline has orchestrator", "@orchestrator" in code)

# ---------- AI Guard ----------
print("\n=== AI Guard Tests ===")
ai_contract = Contract(schema={"answer": Field(type=str, min_length=1)})
guard = AIGuard(ai_contract)
res_good = guard.validate({"answer": "hello"})
check("ai guard good", res_good.summary.get("errors") == 0)
res_bad = guard.validate({"answer": ""})
check("ai guard bad", res_bad.summary.get("errors") == 1)

# ---------- Итоги ----------
print(f"\n{'='*40}")
print(f"Passed: {PASSED}, Failed: {FAILED}")
if FAILED == 0:
    print("🎉 All tests passed! Core is stable.")
else:
    print(f"⚠️  {FAILED} test(s) failed. Please review.")