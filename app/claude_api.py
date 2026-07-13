"""
Claude API клиент с prompt caching для оптимизации токенов и скорости
Используется для расчетов, анализа заказов и генерации КП
"""

import os
import json
import logging
from typing import Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeAPIClient:
    """
    Клиент для работы с Claude API с поддержкой prompt caching
    Кэширует длинные системные контексты для ускорения и экономии токенов
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-opus-4-5"  # Используем Opus для лучшей точности расчётов

    def calculate_price(
        self,
        material: str,
        params: dict,
        use_cache: bool = True
    ) -> dict:
        """
        Расчет стоимости материала с кэшированием системного контекста
        Args:
            material: 'plastic', 'furniture', 'metal'
            params: параметры расчета (высота, ширина, толщина и т.д.)
            use_cache: использовать ли prompt caching
        """
        system_context = self._get_material_system_context(material)

        try:
            if use_cache:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=[
                        {
                            "type": "text",
                            "text": system_context,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": f"Рассчитай стоимость для параметров: {json.dumps(params, ensure_ascii=False)}"
                        }
                    ]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_context,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Рассчитай стоимость для параметров: {json.dumps(params, ensure_ascii=False)}"
                        }
                    ]
                )

            result_text = response.content[0].text
            return {
                "status": "success",
                "material": material,
                "params": params,
                "result": result_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_creation_input_tokens": getattr(
                        response.usage, "cache_creation_input_tokens", 0
                    ),
                    "cache_read_input_tokens": getattr(
                        response.usage, "cache_read_input_tokens", 0
                    )
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при расчете стоимости: {e}")
            return {
                "status": "error",
                "material": material,
                "error": str(e)
            }

    def analyze_order(
        self,
        order_text: str,
        order_history: Optional[list] = None,
        use_cache: bool = True
    ) -> dict:
        """
        Анализ и парсинг заказа с кэшированием контекста истории
        Args:
            order_text: текст заказа
            order_history: история предыдущих заказов (для контекста)
            use_cache: использовать ли prompt caching
        """
        system_context = self._get_order_analysis_context(order_history)

        try:
            if use_cache:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=[
                        {
                            "type": "text",
                            "text": system_context,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": f"Проанализируй заказ:\n{order_text}"
                        }
                    ]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=system_context,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Проанализируй заказ:\n{order_text}"
                        }
                    ]
                )

            result_text = response.content[0].text
            return {
                "status": "success",
                "analysis": result_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_read_input_tokens": getattr(
                        response.usage, "cache_read_input_tokens", 0
                    )
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при анализе заказа: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_proposal(
        self,
        order_data: dict,
        company_info: dict,
        use_cache: bool = True
    ) -> dict:
        """
        Генерация коммерческого предложения с кэшированием шаблонов
        Args:
            order_data: данные заказа (материал, параметры, цена)
            company_info: информация компании (реквизиты, контакты)
            use_cache: использовать ли prompt caching
        """
        system_context = self._get_proposal_generation_context()

        try:
            if use_cache:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=3072,
                    system=[
                        {
                            "type": "text",
                            "text": system_context,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=[
                        {
                            "role": "user",
                            "content": f"Создай КП:\nДанные заказа: {json.dumps(order_data, ensure_ascii=False)}\nРеквизиты: {json.dumps(company_info, ensure_ascii=False)}"
                        }
                    ]
                )
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=3072,
                    system=system_context,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Создай КП:\nДанные заказа: {json.dumps(order_data, ensure_ascii=False)}\nРеквизиты: {json.dumps(company_info, ensure_ascii=False)}"
                        }
                    ]
                )

            result_text = response.content[0].text
            return {
                "status": "success",
                "proposal": result_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cache_read_input_tokens": getattr(
                        response.usage, "cache_read_input_tokens", 0
                    )
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при генерации КП: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def _get_material_system_context(material: str) -> str:
        """Системный контекст для расчетов по материалам"""
        contexts = {
            "plastic": """Ты — профессиональный калькулятор стоимости пластиковых изделий.
Используй следующие формулы расчёта:
- Цена за кг пластика: 150-250 ₽ в зависимости от типа
- Стоимость обработки: (Высота × Ширина × Толщина) × коэффициент сложности
- Минимальный заказ: 1000 ₽
- Скидка от 10 единиц: 5%
- Скидка от 50 единиц: 10%

Всегда указывай:
1. Расчёт по составляющим
2. Итоговую стоимость за единицу
3. Стоимость за партию
4. Срок изготовления (обычно 5-7 дней)
5. Условия доставки""",

            "furniture": """Ты — специалист по расчету стоимости мебельного производства.
Используй следующие параметры:
- Материал: ЛДСП (300₽/м²), МДФ (400₽/м²), Массив (600₽/м²)
- Фурнитура: стандартная (500₽), премиум (1500₽)
- Сборка: 2000₽ за единицу (или 1000₽ если клиент сам собирает)
- Обработка кромок: 50₽ за метр

Расчёт:
1. Материал по площади
2. Фурнитура
3. Работы мастера
4. Доставка и монтаж

Скидки:
- От 3 единиц: 7%
- От 10 единиц: 12%
- От 50 единиц: 15%

Срок: 10-14 дней""",

            "metal": """Ты — инженер-калькулятор металлоконструкций.
Стандарты расчёта:
- Сталь (ГОСТ 1050): 50-70 ₽/кг
- Алюминий: 200-300 ₽/кг
- Нержавейка: 150-200 ₽/кг
- Монтажные работы: 1500-3000 ₽/день
- Доставка: 50 ₽/км + 3000 ₽ база

Расчёт включает:
1. Вес конструкции (кг) × цена материала
2. Обработка (резка, сварка, покраска)
3. Монтажные работы на месте
4. Логистика

Гарантия: 3 года
Сертификаты: ГОСТ, ISO
Сроки: 14-21 день с момента подтверждения"""
        }
        return contexts.get(material, contexts["plastic"])

    @staticmethod
    def _get_order_analysis_context(order_history: Optional[list] = None) -> str:
        """Системный контекст для анализа заказов"""
        base_context = """Ты — специалист по анализу производственных заказов для UNITGROUP.
Твоя задача:
1. Определить тип материала (пластик, мебель, металл)
2. Извлечь все параметры (размеры, количество, требования)
3. Оценить сложность производства
4. Предложить оптимальное решение
5. Вычислить примерную стоимость

Ответ давай в структурированном формате JSON."""

        if order_history:
            history_text = "История последних заказов:\n"
            for order in order_history[-5:]:  # Последние 5 заказов
                history_text += f"- {order.get('date')}: {order.get('material')} на сумму {order.get('amount')}₽\n"
            return base_context + "\n" + history_text

        return base_context

    @staticmethod
    def _get_proposal_generation_context() -> str:
        """Системный контекст для генерации КП"""
        return """Ты — профессиональный писатель коммерческих предложений.
Генерируй КП в формате:

КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ
[Дата и номер]

ПРЕДМЕТ ПРЕДЛОЖЕНИЯ
[Описание изделия]

ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ
[Параметры, материал, допуски]

СТОИМОСТЬ
[Цена за единицу, за партию, условия скидок]

СРОКИ ВЫПОЛНЕНИЯ
[5-7 дней для пластика, 10-14 для мебели, 14-21 для металла]

УСЛОВИЯ
- Оплата: 50% авансом, 50% перед отправкой
- Доставка: за счёт заказчика или по договорённости
- Гарантия: стандартная 12 месяцев
- Форс-мажор: согласно ГК РФ

Подпись, печать, контакты компании"""


def test_claude_api():
    """Тестирование функциональности"""
    client = ClaudeAPIClient()

    # Тест 1: Расчет пластика
    print("🧪 Тест 1: Расчет пластика...")
    result = client.calculate_price(
        "plastic",
        {"height": 200, "width": 150, "thickness": 2, "quantity": 100}
    )
    print(f"✅ Результат: {result['status']}")
    if result['status'] == 'success':
        print(f"📊 Использовано токенов: {result['usage']['input_tokens']}")
        print(f"💾 Кэш прочитано: {result['usage']['cache_read_input_tokens']}")

    # Тест 2: Анализ заказа
    print("\n🧪 Тест 2: Анализ заказа...")
    result = client.analyze_order(
        "Нужно 500 единиц пластиковых коробок размер 300x200x100мм"
    )
    print(f"✅ Результат: {result['status']}")

    # Тест 3: Генерация КП
    print("\n🧪 Тест 3: Генерация КП...")
    result = client.generate_proposal(
        {
            "material": "metal",
            "type": "construction",
            "weight": "500кг",
            "quantity": 1,
            "price": 150000
        },
        {
            "company": "UNITGROUP",
            "email": "sales@unitgroup.tech",
            "phone": "+7 (XXX) XXX-XX-XX"
        }
    )
    print(f"✅ Результат: {result['status']}")


if __name__ == "__main__":
    test_claude_api()
