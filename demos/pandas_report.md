# Отчёт о качестве данных
**Всего проверено:** 6  
**Ошибок:** 3  
**Успешно:** 3  
**Процент ошибок:** 50.0%  

## Топ нарушений
- Regex mismatch: 1
- User‑defined cross‑field rule failed: 1
- Above maximum: 1

## Примеры ошибочных записей
### Запись: `{'id': 3, 'email': 'bad', 'age': 30}`
- **Причина:** Regex mismatch
- **Ожидалось:** matches ^[^@]+@[^@]+\.[^@]+$
- **Получено:** bad

### Запись: `{'id': 4, 'email': 'eve@company.com', 'age': 16}`
- **Причина:** User‑defined cross‑field rule failed
- **Ожидалось:** True
- **Получено:** False

### Запись: `{'id': 5, 'email': 'user@test.com', 'age': 200}`
- **Причина:** Above maximum
- **Ожидалось:** <= 120
- **Получено:** 200

