# Claude API с Prompt Caching для UNITGROUP

## 📋 Описание

Интеграция Claude API (Opus 4.5) с **prompt caching** для оптимизации:
- ⚡ **Скорость**: Кэшированный контекст обрабатывается быстрее
- 💰 **Экономия токенов**: До 90% экономии на повторных запросах
- 🎯 **Точность**: Opus 4.5 для сложных расчётов
- 🔄 **Надёжность**: Автоматические повторы при ошибках

## 🚀 Установка

### 1. Добавить API ключ
```bash
# .env файл
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
# или отдельно:
pip install anthropic>=0.25.0
```

### 3. Запустить Flask приложение
```bash
python -m app.api_server
```

## 📌 API Endpoints

### 1. Расчет стоимости
**POST** `/api/claude/calculate`

```json
{
  "material": "plastic|furniture|metal",
  "params": {
    "height": 200,
    "width": 150,
    "thickness": 2,
    "quantity": 100
  },
  "use_cache": true
}
```

**Response:**
```json
{
  "status": "success",
  "material": "plastic",
  "result": "Итоговая стоимость...",
  "usage": {
    "input_tokens": 512,
    "output_tokens": 128,
    "cache_creation_input_tokens": 450,
    "cache_read_input_tokens": 0
  }
}
```

### 2. Анализ заказа
**POST** `/api/claude/analyze-order`

```json
{
  "order_text": "Нужно 500 коробок размер 300x200x100мм из пластика",
  "order_history": [
    {"date": "2024-07-10", "material": "plastic", "amount": 50000}
  ],
  "use_cache": true
}
```

### 3. Генерация КП
**POST** `/api/claude/generate-proposal`

```json
{
  "order_data": {
    "material": "metal",
    "type": "construction",
    "weight": "500кг",
    "quantity": 1,
    "price": 150000
  },
  "company_info": {
    "company": "UNITGROUP",
    "email": "sales@unitgroup.tech",
    "phone": "+7 (999) 999-99-99"
  },
  "use_cache": true
}
```

### 4. Проверка здоровья
**GET** `/api/claude/health`

```json
{
  "status": "ok",
  "service": "claude-api",
  "model": "claude-opus-4-5"
}
```

## 💡 Примеры использования

### Python (прямое использование)
```python
from app.claude_api import ClaudeAPIClient

client = ClaudeAPIClient()

# Расчет
result = client.calculate_price(
    "plastic",
    {"height": 200, "width": 150, "thickness": 2, "quantity": 100},
    use_cache=True
)
print(result['result'])
print(f"Экономия токенов: {result['usage']['cache_read_input_tokens']}")
```

### JavaScript (веб-фронтенд)
```javascript
// Расчет стоимости с кэшированием
async function calculatePrice() {
  const response = await fetch('/api/claude/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      material: 'plastic',
      params: {
        height: 200,
        width: 150,
        thickness: 2,
        quantity: 100
      },
      use_cache: true
    })
  });

  const data = await response.json();
  console.log('Результат:', data.result);
  console.log('Токены сохранены:', data.usage.cache_read_input_tokens);
  return data;
}
```

### cURL
```bash
# Расчет пластика
curl -X POST http://localhost:5000/api/claude/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "material": "plastic",
    "params": {"height": 200, "width": 150, "thickness": 2, "quantity": 100},
    "use_cache": true
  }'

# Анализ заказа
curl -X POST http://localhost:5000/api/claude/analyze-order \
  -H "Content-Type: application/json" \
  -d '{
    "order_text": "Нужно 500 коробок 300x200x100мм из пластика",
    "use_cache": true
  }'

# Проверка API
curl http://localhost:5000/api/claude/health
```

## 🎯 Оптимизация

### Prompt Caching работает когда:
✅ Системный контекст (system prompt) больше 1024 токенов
✅ Используется один и тот же материал в нескольких запросах
✅ Контекст не меняется между запросами

### Экономия токенов:
```
Первый запрос:  512 input + 50 cache_creation = 562 (полная стоимость)
Второй запрос:  50 cache_read = 50 (90% экономия)
Третий запрос:  50 cache_read = 50 (90% экономия)
```

### Лучшие практики:
1. **Кэшировать по материалам**: Разные контексты для plastic/furniture/metal
2. **Использовать в цикле**: Несколько расчётов подряд - экономия растёт
3. **История заказов**: Кэшировать последние заказы для контекста
4. **Переиспользовать шаблоны**: КП генерируется с одним кэшированным шаблоном

## 📊 Мониторинг

Каждый ответ содержит статистику использования:

```json
"usage": {
  "input_tokens": 512,           // Всё токены ввода
  "output_tokens": 128,          // Токены вывода
  "cache_creation_input_tokens": 450,  // Создано в кэше (первый запрос)
  "cache_read_input_tokens": 0        // Прочитано из кэша (последующие)
}
```

**Формула экономии:**
```
Стоимость = (input + cache_creation) * 0.25 + output * 1.0
Кэшировано = cache_read * 0.01  (90% дешевле)
```

## 🔧 Конфигурация

### В app/claude_api.py:

```python
class ClaudeAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.model = "claude-opus-4-5"  # Можно изменить на claude-sonnet-5
```

### Параметры:
- **Model**: claude-opus-4-5 (лучшая точность) / claude-sonnet-5 (быстрее)
- **Max tokens**: Настраивается per запрос
- **Cache type**: "ephemeral" (временный, 5 минут) или постоянный

## 🐛 Troubleshooting

### ❌ "API Key not found"
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# или в .env файл
```

### ❌ "Cache not working"
- Проверь что system prompt > 1024 токенов
- Повтори запрос с тем же материалом
- Смотри cache_read_input_tokens в response

### ❌ "Rate limit exceeded"
- Используй кэширование (экономит токены)
- Оставь промежуток между запросами

## 📈 Метрики производительности

После интеграции ожидается:
- ⚡ **Скорость**: +40-50% быстрее на повторных запросах
- 💰 **Стоимость**: -80-90% на токенах при кэшировании
- 🎯 **Надёжность**: 99.9% uptime с авторетриями

## 🔗 Документация

- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-a-prompt/prompt-caching)
- [Models API Reference](https://docs.anthropic.com/en/api/messages)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)

---

**Вопросы?** Проверь примеры в `app/claude_api.py` или запусти тесты:
```bash
python -m app.claude_api
```
