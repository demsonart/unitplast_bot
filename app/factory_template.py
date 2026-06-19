"""
AI Factory OS - Template System
Generates complete sales systems from configurable factory templates
"""

import json
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FactoryTemplate:
    """Base template for generating industry-specific sales systems"""

    name: str  # "Plastics Factory", "Furniture Factory", etc.
    industry: str  # "plastics", "furniture", "metal", "packaging", "logistics"
    icon: str  # 🏭 🪑 ⚙️ 📦 🚚
    color: str  # Primary brand color

    materials: List[str]  # What this factory produces
    production_modules: List[Dict[str, Any]]  # 5 production types with knowledge
    knowledge_base: Dict[str, Any]  # Industry-specific knowledge
    email_rules: Dict[str, Any]  # How to detect orders from this industry
    manager_kpis: List[str]  # Key metrics for managers

    @classmethod
    def from_config(cls, config_path: str) -> "FactoryTemplate":
        """Load template from JSON config"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return cls(
            name=config['name'],
            industry=config['industry'],
            icon=config['icon'],
            color=config['color'],
            materials=config['materials'],
            production_modules=config['production_modules'],
            knowledge_base=config['knowledge_base'],
            email_rules=config['email_rules'],
            manager_kpis=config['manager_kpis']
        )

    def to_dict(self) -> Dict:
        """Export as configuration dictionary"""
        return {
            'name': self.name,
            'industry': self.industry,
            'icon': self.icon,
            'color': self.color,
            'materials': self.materials,
            'production_modules': self.production_modules,
            'knowledge_base': self.knowledge_base,
            'email_rules': self.email_rules,
            'manager_kpis': self.manager_kpis,
        }


class FactorySystem:
    """Complete sales system for a factory"""

    def __init__(self, template: FactoryTemplate):
        self.template = template
        self.logger = logging.getLogger(f"Factory[{template.name}]")

    def generate_mini_app_html(self) -> str:
        """Generate customer-facing Mini App from template"""
        modules_html = self._generate_module_cards()
        knowledge_samples = self._get_knowledge_samples()

        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.template.name} - Заказ продукции</title>
    <style>
        :root {{
            --primary: {self.template.color};
            --light: #f3f4f6;
            --text: #111827;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--light);
        }}

        .header {{
            background: var(--primary);
            color: white;
            padding: 20px;
            text-align: center;
        }}

        .header-icon {{
            font-size: 36px;
            margin-bottom: 8px;
        }}

        .header-title {{
            font-size: 24px;
            font-weight: 700;
        }}

        .content {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}

        .section {{
            margin-bottom: 24px;
        }}

        .section-title {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--primary);
        }}

        .module-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}

        .module-card {{
            background: white;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.3s;
        }}

        .module-card:active {{
            transform: scale(0.98);
            border-color: var(--primary);
        }}

        .module-icon {{
            font-size: 32px;
            margin-bottom: 8px;
        }}

        .module-name {{
            font-size: 13px;
            font-weight: 600;
        }}

        .form-group {{
            margin-bottom: 16px;
        }}

        .form-label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        input, select, textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid var(--light);
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }}

        button {{
            width: 100%;
            padding: 14px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}

        button:active {{
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-icon">{self.template.icon}</div>
        <div class="header-title">{self.template.name}</div>
    </div>

    <div class="content">
        <div class="section">
            <div class="section-title">📦 Направления производства</div>
            <div class="module-grid">
                {modules_html}
            </div>
        </div>

        <div class="section">
            <div class="section-title">📝 Ваша заявка</div>
            <form onsubmit="submitOrder(event)">
                <div class="form-group">
                    <label class="form-label">Материал</label>
                    <select required>
                        <option>Выберите материал</option>
                        {self._generate_material_options()}
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Количество</label>
                    <input type="number" placeholder="1000" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Размеры/Спецификация</label>
                    <input type="text" placeholder="100x50x25 мм" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Ваша компания</label>
                    <input type="text" placeholder="ООО Пример" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Телефон</label>
                    <input type="tel" placeholder="+7 (999) 999-99-99" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" placeholder="info@example.com" required>
                </div>

                <button type="submit">📤 Отправить заявку</button>
            </form>
        </div>

        <div class="section">
            <div class="section-title">💡 Часто спрашивают</div>
            {knowledge_samples}
        </div>
    </div>

    <script>
        function submitOrder(event) {{
            event.preventDefault();
            alert('✅ Заявка принята! Скоро с вами свяжется менеджер.');
            event.target.reset();
        }}
    </script>
</body>
</html>"""

        return html

    def _generate_module_cards(self) -> str:
        """Generate HTML for production module cards"""
        cards = []
        for module in self.template.production_modules:
            cards.append(f"""
                <div class="module-card">
                    <div class="module-icon">{module['icon']}</div>
                    <div class="module-name">{module['name']}</div>
                </div>
            """)
        return ''.join(cards)

    def _generate_material_options(self) -> str:
        """Generate HTML option tags for materials"""
        options = []
        for material in self.template.materials:
            options.append(f"<option>{material}</option>")
        return ''.join(options)

    def _get_knowledge_samples(self) -> str:
        """Get sample Q&A from knowledge base"""
        samples = self.template.knowledge_base.get('faq', [])[:3]
        html = []
        for qa in samples:
            html.append(f"""
                <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                    <strong>{qa['q']}</strong><br>
                    <span style="color: #6b7280; font-size: 13px;">{qa['a']}</span>
                </div>
            """)
        return ''.join(html)

    def get_manager_dashboard_config(self) -> Dict:
        """Get dashboard configuration for managers"""
        return {
            'name': f"{self.template.name} Manager",
            'icon': '👨‍💼',
            'color': self.template.color,
            'kpis': self.template.manager_kpis,
            'production_modules': self.template.production_modules,
        }

    def get_ai_consultant_knowledge(self) -> Dict:
        """Knowledge base for AI consultant"""
        return {
            'factory': self.template.name,
            'industry': self.template.industry,
            'materials': self.template.materials,
            'production_modules': self.template.production_modules,
            'knowledge_base': self.template.knowledge_base,
        }

    def get_email_classification_rules(self) -> Dict:
        """Email processing rules for this factory"""
        return self.template.email_rules


class FactoryOS:
    """Operating system for AI factories - manages multiple templates"""

    def __init__(self):
        self.templates: Dict[str, FactoryTemplate] = {}
        self.systems: Dict[str, FactorySystem] = {}
        self.logger = logging.getLogger("FactoryOS")

    def register_template(self, template: FactoryTemplate) -> None:
        """Register a new factory template"""
        self.templates[template.industry] = template
        self.systems[template.industry] = FactorySystem(template)
        self.logger.info(f"Registered template: {template.name}")

    def get_system(self, industry: str) -> FactorySystem:
        """Get factory system for industry"""
        return self.systems.get(industry)

    def list_available_templates(self) -> List[Dict]:
        """List all available factory templates"""
        return [
            {
                'name': t.name,
                'industry': t.industry,
                'icon': t.icon,
                'materials': len(t.materials),
                'modules': len(t.production_modules),
            }
            for t in self.templates.values()
        ]
