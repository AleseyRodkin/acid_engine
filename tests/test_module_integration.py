# Auto-generated integration tests by AcidEngine
import pytest
import pandas as pd
from acid_engine.modules.core import ModuleCore

MODULE_DIR = 'acid_engine/modules/validate_orders'

def load_test_data():
    # Замените на свои тестовые данные
    return pd.DataFrame({
        'order_id': [1, 2, 2, 3, 4],
        'price': [10.0, -5.0, 20.0, 30.0, -2.0]
    })

def test_module_execution():
    module = ModuleCore(MODULE_DIR)
    data = load_test_data()
    result = module.execute(data)
    # Проверяем, что результат — не пустой DataFrame
    assert not result.empty
    # Проверяем, что нет отрицательных цен (после filter_price)
    assert (result['price'] > 0).all()
    # Проверяем, что нет дубликатов order_id
    assert result['order_id'].is_unique

def test_tracer_report():
    module = ModuleCore(MODULE_DIR)
    data = load_test_data()
    module.execute(data)
    report = module.report()
    # Проверяем, что все функции отрапортовали
    for func in ['filter_price', 'cast_types', 'dedup_orders']:
        assert func in report
