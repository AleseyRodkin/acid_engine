import pandas as pd
from acid_engine.modules.core import ModuleCore

# Подготовим тестовые данные
df = pd.DataFrame({
    "order_id": [1, 2, 2, 3],
    "price": [10.0, -5.0, 20.0, 30.0]
})

# Загружаем модуль
module = ModuleCore("acid_engine/modules/validate_orders")
result = module.execute(df)
print("Result:\n", result)
print(module.report())