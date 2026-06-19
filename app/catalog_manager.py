import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CatalogManager:
    """Manages product catalog and knowledge base (local, no AI needed)"""

    def __init__(self, catalog_path: str = None):
        if catalog_path is None:
            catalog_path = Path(__file__).parent.parent / "catalog" / "products.json"

        self.catalog_path = Path(catalog_path)
        self.products = self._load_catalog()

    def _load_catalog(self) -> dict:
        """Load product catalog from JSON"""
        try:
            if self.catalog_path.exists():
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Catalog file not found: {self.catalog_path}")
                return {"materials": {}, "faqs": {}}
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
            return {"materials": {}, "faqs": {}}

    def get_material(self, material_name: str) -> Optional[dict]:
        """Get material info by name"""
        materials = self.products.get("materials", {})

        # Try exact match
        if material_name in materials:
            return materials[material_name]

        # Try case-insensitive search
        for key, value in materials.items():
            if key.lower() == material_name.lower():
                return value
            if value.get("name", "").lower() == material_name.lower():
                return value

        return None

    def search_materials(self, query: str) -> List[Dict]:
        """Search materials by name or description"""
        query = query.lower()
        results = []

        materials = self.products.get("materials", {})
        for key, value in materials.items():
            # Search in name and description
            name = value.get("name", "").lower()
            desc = value.get("description", "").lower()

            if query in name or query in desc:
                results.append({
                    "key": key,
                    "name": value.get("name", key),
                    "description": value.get("description", "")[:100] + "..."
                })

        return results

    def get_all_materials(self) -> List[str]:
        """Get list of all available materials"""
        return list(self.products.get("materials", {}).keys())

    def get_material_colors(self, material_name: str) -> List[str]:
        """Get available colors for a material"""
        material = self.get_material(material_name)
        if material:
            return material.get("colors", [])
        return []

    def get_material_thicknesses(self, material_name: str) -> List[str]:
        """Get available thicknesses for a material"""
        material = self.get_material(material_name)
        if material:
            return material.get("thicknesses", [])
        return []

    def get_material_description(self, material_name: str) -> str:
        """Get material description"""
        material = self.get_material(material_name)
        if material:
            return material.get("description", "")
        return "Материал не найден"

    def get_faq(self, question_type: str) -> str:
        """Get FAQ answer (no AI, local knowledge base)"""
        faqs = self.products.get("faqs", {})
        return faqs.get(question_type, "Ответ не найден")

    def search_faq(self, query: str) -> Optional[str]:
        """Search FAQ by keywords"""
        query = query.lower()
        faqs = self.products.get("faqs", {})

        # Keywords mapping to FAQ topics
        keywords_map = {
            "доставка": "shipping",
            "доставить": "shipping",
            "доставка": "shipping",
            "курьер": "shipping",
            "цена": "price_list",
            "прайс": "price_list",
            "сколько стоит": "price_list",
            "стоимость": "price_list",
            "срок": "delivery_time",
            "сколько дней": "delivery_time",
            "как долго": "delivery_time",
            "оплата": "payment",
            "платеж": "payment",
            "как платить": "payment",
            "гарантия": "warranty",
            "гарантию": "warranty",
            "минимум": "min_order",
            "образец": "samples",
            "образцы": "samples",
            "производство": "molding",
            "производим": "molding",
            "что производите": "molding",
        }

        # Find matching FAQ
        for keyword, topic in keywords_map.items():
            if keyword in query:
                return faqs.get(topic, "Ответ не найден")

        return None

    def get_faq_list(self) -> Dict[str, str]:
        """Get all FAQ with titles"""
        faq_titles = {
            "delivery_time": "⏰ Сроки изготовления",
            "price_list": "💰 Прайс-лист",
            "payment": "💳 Способы оплаты",
            "shipping": "🚚 Доставка",
            "warranty": "✅ Гарантия",
            "min_order": "📦 Минимальный заказ",
            "molding": "🔧 Производство",
            "samples": "🎯 Образцы"
        }

        faqs = self.products.get("faqs", {})
        return {
            faq_titles.get(key, key): value
            for key, value in faqs.items()
        }

    def format_material_info(self, material_name: str) -> str:
        """Format material info for display"""
        material = self.get_material(material_name)
        if not material:
            return "Материал не найден"

        info = f"""
📋 {material.get('name', material_name)}

📝 Описание:
{material.get('description', '')}

🎨 Цвета: {', '.join(material.get('colors', []))}

📏 Толщины: {', '.join(material.get('thicknesses', []))}

📐 Макс. размер: {material.get('max_size', 'N/A')}

⚖️ Плотность: {material.get('density', 'N/A')}

🌡️ Диапазон температур: {material.get('temp_range', 'N/A')}

⏰ Срок изготовления: {material.get('lead_time', 'По запросу')}
"""
        return info.strip()
