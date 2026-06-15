# AcidEngine

**Контрактно-ориентированный движок данных** для Python.

Позволяет описывать гарантии данных (уникальность, тип, неизменяемость, ограничения) в виде контракта, который автоматически соблюдается при работе с контейнерами.

## Пример

```python
from acid_engine import Contract

URLs = Contract(unique=True, dtype=str,
                validators=[lambda x: x.startswith("https://")])
urls = URLs.create_container()

urls.add("https://example.com")   # ok
urls.add("ftp://bad.url")         # ContractViolation