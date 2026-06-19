"""
AI Consultant - Intelligent product and process recommendations
Learns from company data, provides expert advice
"""

import json
from typing import Dict, List, Tuple


class AIConsultant:
    """Smart AI Consultant for manufacturing processes and material selection"""

    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        self.learning_history = []

    def _build_knowledge_base(self) -> Dict:
        """Build comprehensive knowledge base from material data"""
        return {
            'materials': {
                'ABS': {
                    'name': 'ABS (Акрилонитрил-бутадиен-стирол)',
                    'price_per_kg': (350, 500),
                    'properties': {
                        'impact_resistance': 'очень высокая',
                        'processing_ease': 'легко обрабатывается',
                        'color_options': 'все цвета',
                        'temperature_range': '-40°C до +80°C',
                        'uv_resistance': 'плохая (нужна защита)',
                        'durability': 'высокая'
                    },
                    'alternatives_cheaper': ['PP', 'PS'],
                    'alternatives_better': ['PC', 'PA'],
                    'best_for': ['электроинструменты', 'корпусы', 'игрушки', 'автомобильные детали'],
                    'avoid_for': ['прямой УФ', 'агрессивные химикаты'],
                    'min_volume': 1000,
                    'lead_time_days': (14, 21)
                },
                'PP': {
                    'name': 'PP (Полипропилен)',
                    'price_per_kg': (200, 350),
                    'properties': {
                        'impact_resistance': 'средняя',
                        'weight': 'легкий',
                        'chemical_resistance': 'высокая',
                        'temperature_range': '-20°C до +120°C',
                        'cost': 'самый дешевый',
                        'flexibility': 'гибкий'
                    },
                    'alternatives_cheaper': ['PE'],
                    'alternatives_better': ['ABS', 'PC'],
                    'best_for': ['контейнеры', 'трубы', 'упаковка', 'пищевое'],
                    'avoid_for': ['высокие нагрузки', 'ударостойкость'],
                    'min_volume': 500,
                    'lead_time_days': (10, 14)
                },
                'PET': {
                    'name': 'PET (Полиэтилентерефталат)',
                    'price_per_kg': (300, 450),
                    'properties': {
                        'transparency': 'полная',
                        'food_safe': 'да, разрешено',
                        'strength': 'хорошая',
                        'chemical_resistance': 'хорошая',
                        'temperature_range': '-40°C до +70°C',
                        'recyclable': 'да'
                    },
                    'alternatives_cheaper': ['PP', 'PS'],
                    'alternatives_better': ['PC'],
                    'best_for': ['бутылки', 'контейнеры напитков', 'пищевая упаковка'],
                    'avoid_for': ['высокие температуры'],
                    'min_volume': 500,
                    'lead_time_days': (7, 14)
                },
                'PC': {
                    'name': 'PC (Поликарбонат)',
                    'price_per_kg': (800, 1200),
                    'properties': {
                        'impact_resistance': 'экстремальная',
                        'transparency': 'как стекло',
                        'weight': 'очень легкий',
                        'temperature_range': '-40°C до +120°C',
                        'uv_resistance': 'высокая',
                        'cost': 'дорогой'
                    },
                    'alternatives_cheaper': ['ABS', 'PS'],
                    'alternatives_lighter': 'нет, это самый легкий прочный',
                    'best_for': ['защитные окна', 'авиация', 'автомобили', 'экстремальное'],
                    'avoid_for': ['бюджет'],
                    'min_volume': 500,
                    'lead_time_days': (21, 28)
                },
                'PVC': {
                    'name': 'PVC (Поливинилхлорид)',
                    'price_per_kg': (250, 400),
                    'properties': {
                        'chemical_resistance': 'очень высокая',
                        'flame_resistance': 'хорошая',
                        'rigidity': 'жесткий',
                        'temperature_range': '-20°C до +70°C',
                        'durability': 'долговечный'
                    },
                    'alternatives_cheaper': ['PE'],
                    'alternatives_better': ['PP для трубопроводов'],
                    'best_for': ['трубы', 'химические контейнеры', 'кабельные каналы'],
                    'avoid_for': ['пищевое контактное использование'],
                    'min_volume': 500,
                    'lead_time_days': (10, 14)
                }
            },
            'processes': {
                'injection_molding': {
                    'name': 'Литье под давлением',
                    'best_materials': ['ABS', 'PP', 'PA', 'PC'],
                    'min_volume': 1000,
                    'tolerance': '±0.1-0.2 mm',
                    'lead_time': '14-21 дней',
                    'cost_factor': 1.0,
                    'best_for': ['сложные формы', 'массовое производство', 'тонкие стенки'],
                    'avoid_for': ['очень большие детали', 'простые изделия']
                },
                'thermoforming': {
                    'name': 'Термоформовка',
                    'best_materials': ['ABS', 'PP', 'PVC'],
                    'min_volume': 500,
                    'tolerance': '±0.3 mm',
                    'lead_time': '7-14 дней',
                    'cost_factor': 0.8,
                    'best_for': ['полупрозрачные детали', 'быстрое производство', 'среднее количество'],
                    'avoid_for': ['очень тонкие стенки']
                },
                'extrusion': {
                    'name': 'Экструзия',
                    'best_materials': ['PP', 'PE', 'PVC'],
                    'min_volume': '100 м',
                    'tolerance': '±1 mm',
                    'lead_time': '10-15 дней',
                    'cost_factor': 0.6,
                    'best_for': ['профили', 'трубы', 'длинные детали'],
                    'avoid_for': ['сложные формы']
                }
            },
            'questions': {
                'для улицы': {
                    'answer': 'Для улицы рекомендуем UV-стабилизированный материал.',
                    'recommendations': ['PC (экстремальная ударостойкость)', 'ABS (с UV защитой)', 'PVC (химически стойкий)'],
                    'warning': 'Обычный пластик быстро потускнеет. Нужна UV защита.'
                },
                'пищевой': {
                    'answer': 'Для пищевого контакта разрешены только определенные материалы.',
                    'recommendations': ['PET (стандарт для напитков)', 'PP пищевой (контейнеры)'],
                    'warning': 'Требуется сертификат пищевой безопасности. PVC категорически запрещен.'
                },
                'ударостойкий': {
                    'answer': 'Выберите материал с высокой ударостойкостью.',
                    'recommendations': ['PC (экстремальная)', 'ABS (высокая)', 'PA (гибкий)'],
                    'warning': 'PC самый прочный, но дороже. ABS - хороший компромисс цена/свойства.'
                },
                'дешевый': {
                    'answer': 'Самые бюджетные варианты:',
                    'recommendations': ['PE (самый дешевый)', 'PP (дешевый + функциональный)', 'PS (если прозрачность важна)'],
                    'warning': 'Дешевизна часто означает потерю прочности или долговечности.'
                },
                'прозрачный': {
                    'answer': 'Для прозрачности выбирайте между:',
                    'recommendations': ['PC (как стекло, дорогой)', 'PET (пищевой, дешевле)', 'PS (хрупкий, дешевый)', 'PMMA (акрил, если нужна оптика)'],
                    'warning': 'Прозрачность часто влияет на цену. PC в 3-4 раза дороже PS.'
                },
                'гибкий': {
                    'answer': 'Для гибкости выбирайте эластичные материалы.',
                    'recommendations': ['PE (самый гибкий)', 'PP (гибче ABS)', 'TPE (резиноподобный)'],
                    'warning': 'Гибкость часто означает меньшую жесткость конструкции.'
                }
            }
        }

    def answer_question(self, question: str) -> Dict:
        """Answer user question with intelligent response"""
        question_lower = question.lower()

        # Direct knowledge base match
        for key, kb_item in self.knowledge_base['questions'].items():
            if key in question_lower:
                return {
                    'question': question,
                    'answer': kb_item['answer'],
                    'recommendations': kb_item['recommendations'],
                    'warning': kb_item['warning'],
                    'type': 'material_advice'
                }

        # Material selection logic
        if 'выбрать' in question_lower or 'какой материал' in question_lower:
            return self._material_selection_logic(question)

        # Process recommendation
        if 'процесс' in question_lower or 'способ' in question_lower or 'производство' in question_lower:
            return self._process_recommendation(question)

        # Cost optimization
        if 'дешев' in question_lower or 'стоим' in question_lower or 'цена' in question_lower:
            return self._cost_optimization(question)

        # Default fallback
        return {
            'question': question,
            'answer': 'Отличный вопрос! Для точного ответа нужны подробности.',
            'follow_up': [
                'Какой размер изделия?',
                'Какое количество?',
                'Какие требования к прочности?',
                'Будет ли на улице?'
            ],
            'type': 'clarification'
        }

    def _material_selection_logic(self, question: str) -> Dict:
        """Recommend material based on question context"""
        question_lower = question.lower()

        # Detect requirements
        is_outdoor = 'улиц' in question_lower or 'уф' in question_lower or 'солнц' in question_lower
        is_food = 'пищ' in question_lower or '食' in question_lower or 'напит' in question_lower
        needs_impact = 'удар' in question_lower or 'проч' in question_lower or 'падение' in question_lower
        needs_cheap = 'дешев' in question_lower or 'экономи' in question_lower or 'минимум' in question_lower
        needs_transparent = 'прозрач' in question_lower or 'видно' in question_lower

        if is_outdoor:
            recommendations = ['PC', 'ABS с UV', 'PVC']
            reason = 'Для уличного использования нужна UV устойчивость'
        elif is_food:
            recommendations = ['PET', 'PP пищевой']
            reason = 'Только материалы с пищевым сертификатом'
        elif needs_impact:
            recommendations = ['PC', 'ABS', 'PA']
            reason = 'Выбираем материал с высокой ударостойкостью'
        elif needs_cheap:
            recommendations = ['PE', 'PP', 'PS']
            reason = 'Бюджетные варианты с адекватной функциональностью'
        elif needs_transparent:
            recommendations = ['PC', 'PET', 'PMMA']
            reason = 'Прозрачные материалы для оптических требований'
        else:
            recommendations = ['ABS', 'PP']
            reason = 'Универсальные материалы для большинства применений'

        return {
            'question': question,
            'answer': f'Рекомендуемые материалы для вашего случая:',
            'recommendations': recommendations,
            'reason': reason,
            'next_step': 'Скажите количество и сроки - рассчитаем полную цену',
            'type': 'material_recommendation'
        }

    def _process_recommendation(self, question: str) -> Dict:
        """Recommend production process"""
        return {
            'question': question,
            'answer': 'Выбор процесса зависит от сложности детали и количества.',
            'recommendations': {
                'Если 1000+ шт и сложная форма': 'Литье под давлением (точность ±0.1 мм)',
                'Если 500-1000 шт и простая форма': 'Термоформовка (быстрее и дешевле)',
                'Если 100+ метров профиля': 'Экструзия (дешево за метр)'
            },
            'type': 'process_recommendation'
        }

    def _cost_optimization(self, question: str) -> Dict:
        """Recommend cost-saving options"""
        return {
            'question': question,
            'answer': 'Способы снизить стоимость:',
            'options': [
                {'change': 'ABS → PP', 'savings': '30-40%', 'trade_off': 'Меньше ударостойкость'},
                {'change': 'Первичный → Переработанный пластик', 'savings': '20-30%', 'trade_off': 'Могут быть дефекты цвета'},
                {'change': 'Увеличить объем заказа', 'savings': '5-15%', 'trade_off': 'Нужно место для хранения'},
                {'change': 'Упростить геометрию', 'savings': '10-25%', 'trade_off': 'Изменение дизайна'},
            ],
            'warning': 'Экономия должна быть безопасной - не теряйте качество критических характеристик',
            'type': 'cost_optimization'
        }

    def learn_from_interaction(self, user_question: str, user_response: str, material_selected: str):
        """Learn from customer interactions"""
        self.learning_history.append({
            'user_question': user_question,
            'user_response': user_response,
            'material_selected': material_selected,
            'timestamp': str(__import__('datetime').datetime.now())
        })

    def get_insights(self) -> Dict:
        """Get insights from learning history"""
        if not self.learning_history:
            return {'message': 'No learning data yet'}

        material_count = {}
        for entry in self.learning_history:
            mat = entry['material_selected']
            material_count[mat] = material_count.get(mat, 0) + 1

        most_popular = max(material_count, key=material_count.get) if material_count else None

        return {
            'total_interactions': len(self.learning_history),
            'most_popular_material': most_popular,
            'material_distribution': material_count,
            'recommendation': f'Consider stocking more {most_popular} based on customer preferences'
        }


# Example usage
if __name__ == '__main__':
    consultant = AIConsultant()

    # Test questions
    test_questions = [
        'Какой пластик выбрать для улицы?',
        'Нужен для пищевого контакта',
        'Материал должен быть очень ударостойким',
        'Хочу дешевый вариант',
        'Какой способ производства выбрать?'
    ]

    for q in test_questions:
        response = consultant.answer_question(q)
        print(f"\n❓ Q: {q}")
        print(f"✅ A: {response['answer']}")
        if 'recommendations' in response:
            print(f"   → {response['recommendations']}")
