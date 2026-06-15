from .core import Contract, Container, ContractViolation


class ScopeError(Exception):
    """Ошибка в структуре скоупа."""
    pass


class global_scope:
    """
    Контекстный менеджер для шага обработки данных.
    Внутри одного global_scope должен быть ровно один @orchestrator.
    """
    def __init__(self, name: str):
        self.name = name
        self._inputs = {}   # входные константы (замороженные контейнеры)
        self._outputs = {}  # выходные константы
        self._orchestrator_called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # При ошибке всё, что было временного, будет удалено (выходные данные не запомнятся)
        if exc_type is not None:
            return False  # пробрасываем исключение дальше
        # Успешное завершение: все выходные данные заморожены (если ещё нет) и сохранены
        for name, value in self._outputs.items():
            if isinstance(value, Container):
                value.freeze()
        return False

    def const(self, container: Container):
        """Зарегистрировать входной контейнер (константу) и заморозить его."""
        if not isinstance(container, Container):
            raise ScopeError("Входной параметр должен быть контейнером (Container)")
        container.freeze()
        # Сохраняем под внутренним ключом (пока безымянно, можно добавить имя позже)
        self._inputs[id(container)] = container
        return container

    def const_output(self, name: str, value):
        """Зарегистрировать выходные данные."""
        if not isinstance(value, Container):
            raise ScopeError("Выходной параметр должен быть контейнером")
        self._outputs[name] = value

    @property
    def inputs(self):
        return list(self._inputs.values())

    @property
    def outputs(self):
        return dict(self._outputs)


def orchestrator(_func=None, *, input_contract=None, output_contract=None):
    """
    Декоратор для функции-оркестратора внутри global_scope.
    Проверяет соответствие переданных данных контрактам (если указаны).
    """
    def decorator(func):
        def wrapper(data):
            # Проверка входного контракта
            if input_contract is not None:
                if not isinstance(data, Container):
                    raise ContractViolation(
                        f"Ожидался контейнер с контрактом {input_contract}, "
                        f"но получен {type(data).__name__}"
                    )
                # Сравниваем основные параметры контрактов
                if (data.contract.unique != input_contract.unique or
                    data.contract.ordered != input_contract.ordered or
                    not data.is_frozen):  # данные должны быть заморожены
                    raise ContractViolation("Входные данные не соответствуют контракту")
            result = func(data)
            # Проверка выходного контракта
            if output_contract is not None:
                if not isinstance(result, Container):
                    raise ContractViolation("Результат должен быть контейнером")
                if (result.contract.unique != output_contract.unique or
                    result.contract.ordered != output_contract.ordered):
                    raise ContractViolation("Результат не соответствует выходному контракту")
            return result
        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)