# Auto-generated tests by AcidEngine
import pytest
from acid_engine.parser.parser import parse_contract
from acid_engine.runtime.runner import StageRunner
import csv
import os

CONTRACT_FILE = "test_derived.ae"

def load_data():
    return [
        {"order_id": "1", "price": "10.0", "quantity": "5"},
        {"order_id": "bad", "price": "-1", "quantity": "200"},
    ]

def test_contract_validation():
    ast = parse_contract(CONTRACT_FILE)
    data = load_data()
    for stage in ast['implementation']:
        runner = StageRunner(stage)
        validated, report, errors = runner.run(data, collect_errors=True)
        assert report['pass'] >= 0
        assert report['fail'] >= 0
        assert len(validated) == report['pass']

def test_rule_validate_price_gt_0_0():
    ast = parse_contract(CONTRACT_FILE)
    data = [{"order_id": 1, "price": 1.0, "quantity": 1, "total": 1.0}]
    for stage in ast['implementation']:
        runner = StageRunner(stage)
        validated, report, errors = runner.run(data, collect_errors=True)
        assert report['fail'] == 0, f"Rule test_rule_validate_price_gt_0_0 failed"

def test_rule_validate_quantity_between_1_100():
    ast = parse_contract(CONTRACT_FILE)
    data = [{"order_id": 1, "price": 1.0, "quantity": 50.5, "total": 1.0}]
    for stage in ast['implementation']:
        runner = StageRunner(stage)
        validated, report, errors = runner.run(data, collect_errors=True)
        assert report['fail'] == 0, f"Rule test_rule_validate_quantity_between_1_100 failed"
