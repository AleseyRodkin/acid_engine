# acid_engine/testing/manifest_tester.py
import yaml
import os
import pandas as pd

class ManifestTestGenerator:
    """Генерирует интеграционные тесты на основе functions.manifest."""

    def __init__(self, module_dir: str, manifest_name: str = "functions.manifest"):
        self.module_dir = module_dir
        self.manifest_path = os.path.join(module_dir, manifest_name)
        with open(self.manifest_path, "r") as f:
            self.manifest = yaml.safe_load(f)

    def generate(self, output_path: str = "test_module_integration.py"):
        """Генерирует файл с тестами."""
        lines = []
        lines.append("# Auto-generated integration tests by AcidEngine")
        lines.append("import pytest")
        lines.append("import pandas as pd")
        lines.append("from acid_engine.modules.core import ModuleCore")
        lines.append("")
        lines.append(f"MODULE_DIR = '{self.module_dir}'")
        lines.append("")
        lines.append("def load_test_data():")
        lines.append("    # Замените на свои тестовые данные")
        lines.append("    return pd.DataFrame({")
        lines.append("        'order_id': [1, 2, 2, 3, 4],")
        lines.append("        'price': [10.0, -5.0, 20.0, 30.0, -2.0]")
        lines.append("    })")
        lines.append("")
        lines.append("def test_module_execution():")
        lines.append("    module = ModuleCore(MODULE_DIR)")
        lines.append("    data = load_test_data()")
        lines.append("    result = module.execute(data)")
        lines.append("    # Проверяем, что результат — не пустой DataFrame")
        lines.append("    assert not result.empty")
        lines.append("    # Проверяем, что нет отрицательных цен (после filter_price)")
        lines.append("    assert (result['price'] > 0).all()")
        lines.append("    # Проверяем, что нет дубликатов order_id")
        lines.append("    assert result['order_id'].is_unique")
        lines.append("")
        lines.append("def test_tracer_report():")
        lines.append("    module = ModuleCore(MODULE_DIR)")
        lines.append("    data = load_test_data()")
        lines.append("    module.execute(data)")
        lines.append("    report = module.report()")
        lines.append("    # Проверяем, что все функции отрапортовали")
        lines.append("    for func in ['filter_price', 'cast_types', 'dedup_orders']:")
        lines.append("        assert func in report")
        lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        return output_path