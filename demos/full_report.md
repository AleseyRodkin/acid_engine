# Отчёт о качестве данных
**Всего проверено:** 6  
**Ошибок:** 4  
**Успешно:** 2  
**Процент ошибок:** 66.7%  

## Топ нарушений
- Cross‑field rule failed: 2
- Regex mismatch: 1
- Above maximum: 1

## Примеры ошибочных записей
### Запись: `{'id': 2, 'email': 'bob@mail.com', 'age': 17}`
- **Причина:** Cross‑field rule failed
- **Ожидалось:** True
- **Получено:** False

### Запись: `{'id': 3, 'email': 'bad', 'age': 30}`
- **Причина:** Regex mismatch
- **Ожидалось:** matches ^[^@]+@[^@]+\.[^@]+$
- **Получено:** bad

### Запись: `{'id': 4, 'email': 'eve@company.com', 'age': 16}`
- **Причина:** Cross‑field rule failed
- **Ожидалось:** True
- **Получено:** False

### Запись: `{'id': 5, 'email': 'user@test.com', 'age': 200}`
- **Причина:** Above maximum
- **Ожидалось:** <= 120
- **Получено:** 200

