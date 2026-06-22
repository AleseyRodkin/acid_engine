import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from acid_engine.core import (
    ContractViolation, QualityGateExceeded,
    Field, Contract, Container, QualityGate, ValidationResult, ErrorRecord
)
from acid_engine.ai import AIGuard

# ---------- Field ----------
def test_field_valid():
    f = Field(type=int, min=1, max=100)
    f.validate(50)  # не должно вызывать исключений

def test_field_below_min():
    f = Field(type=int, min=1, max=100)
    with pytest.raises(ContractViolation):
        f.validate(0)

def test_field_above_max():
    f = Field(type=int, min=1, max=100)
    with pytest.raises(ContractViolation):
        f.validate(150)

def test_field_email_valid():
    f = Field.Email()
    f.validate("a@b.com")

def test_field_email_invalid():
    f = Field.Email()
    with pytest.raises(ContractViolation):
        f.validate("bad")

# ---------- Container + Contract ----------
def test_container_add_and_duplicate():
    c = Contract(unique=True, schema={"id": Field(type=int, min=1)})
    container = c.create_container()
    container.add({"id": 1})
    assert len(container) == 1
    with pytest.raises(ContractViolation):
        container.add({"id": 1})

def test_container_frozen():
    c = Contract(unique=True, schema={"id": Field(type=int, min=1)})
    container = c.create_container()
    container.add({"id": 1})
    container.freeze()
    with pytest.raises(ContractViolation):
        container.add({"id": 2})

# ---------- Cross‑Field Rules ----------
def test_crossfield_valid():
    c = Contract(schema={"a": Field(type=int), "b": Field(type=int)})
    c.add_rule("a < b")
    container = c.create_container()
    container.add({"a": 1, "b": 2})
    assert len(container) == 1

def test_crossfield_invalid():
    c = Contract(schema={"a": Field(type=int), "b": Field(type=int)})
    c.add_rule("a < b")
    container = c.create_container()
    with pytest.raises(ContractViolation):
        container.add({"a": 3, "b": 2})

# ---------- QualityGate ----------
def test_qualitygate_strict():
    c = Contract(schema={"x": Field(type=int, min=0)})
    main = c.create_container()
    # сначала добавляем два хороших элемента
    main.add({"x": 1})
    main.add({"x": 2})
    # создаём QualityGate с порогом 0.3 — теперь снапшот содержит два элемента
    gate = QualityGate(main, max_error_rate=0.3, mode="strict")
    # добавляем плохой элемент — порог превышен (1/3 ≈ 33% > 30%), срабатывает откат
    with pytest.raises(QualityGateExceeded):
        gate.add({"x": -1})
    # после отката контейнер должен вернуться к состоянию снапшота (два элемента)
    assert len(main) == 2

# ---------- Explain Engine ----------
def test_explain_engine():
    c = Contract(schema={"email": Field.Email()})
    result = c.validate([
        {"email": "ok@b.com"},
        {"email": "bad"}
    ])
    assert result.summary["total"] == 2
    assert result.summary["errors"] == 1
    output = result.explain()
    assert "Ошибок: 1" in output or "Errors: 1" in output or "errors" in output.lower()

# ---------- YAML ----------
def test_yaml_roundtrip():
    c = Contract(schema={"val": Field(type=int, min=5)})
    yaml_str = c.to_yaml()
    c_loaded = Contract.from_yaml(yaml_str)
    assert "val" in c_loaded.schema
    assert c_loaded.schema["val"].min == 5

# ---------- Pipeline Generator ----------
def test_pipeline_generator():
    c = Contract(
        schema={"id": Field(type=int)},
        pipeline_meta={
            "input": "test.csv",
            "output": "out.csv",
            "processing": ["load", "clean"]
        }
    )
    code = c.generate_pipeline()
    assert "def load" in code
    assert "def clean" in code
    assert "@orchestrator" in code

# ---------- AI Guard ----------
def test_ai_guard_good():
    contract = Contract(schema={"answer": Field(type=str, min_length=1)})
    guard = AIGuard(contract)
    result = guard.validate({"answer": "hello"})
    assert result.summary["errors"] == 0

def test_ai_guard_bad():
    contract = Contract(schema={"answer": Field(type=str, min_length=1)})
    guard = AIGuard(contract)
    result = guard.validate({"answer": ""})
    assert result.summary["errors"] == 1