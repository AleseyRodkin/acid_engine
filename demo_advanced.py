import pandas as pd
from acid_engine.modules.core import ModuleCore

# Подготовим данные
df = pd.DataFrame({
    "order_id": [1, 2, 2, 3, 4],
    "price": [10.0, -5.0, 20.0, 30.0, -2.0]
})

# Запускаем с Hot Reload и чекпоинтами
module = ModuleCore("acid_engine/modules/validate_orders",
                    hot_reload=True, resume=True)
result = module.execute(df)
print("Result:\n", result)
print(module.report())

# Теперь, если мы изменим код функции и перезапустим скрипт,
# Hot Reload подхватит изменения, а чекпоинты позволят
# продолжить с последней точки без пересчёта всего.