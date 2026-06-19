"""
UNITPLAST Knowledge Engine
Manages AI learning from documents, emails, and catalogs
"""

import logging
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "knowledge"


class KnowledgeEngine:
    """Central AI knowledge management system"""

    def __init__(self):
        self.kb_path = KNOWLEDGE_BASE_PATH
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load or create knowledge index"""
        index_file = self.kb_path / "index.json"

        if index_file.exists():
            try:
                with open(index_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading index: {e}")

        return self._create_empty_index()

    def _create_empty_index(self) -> Dict:
        """Create empty knowledge index"""
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "categories": {
                "materials": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
                "machines": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
                "sales": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
                "production": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
                "catalog": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
                "documents": {
                    "count": 0,
                    "files": [],
                    "last_updated": None,
                },
            },
            "learning_log": [],
            "ai_insights": [],
        }

    def add_material(self, name: str, description: str, properties: Dict) -> bool:
        """Add material to knowledge base"""
        try:
            material_file = self.kb_path / "materials" / f"{name.lower()}.json"

            material_data = {
                "name": name,
                "description": description,
                "properties": properties,
                "added": datetime.now().isoformat(),
                "used_in_orders": 0,
            }

            with open(material_file, "w") as f:
                json.dump(material_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Material added: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding material: {e}")
            return False

    def learn_from_email(self, email_data: Dict) -> Dict:
        """Learn from processed email"""
        insight = {
            "timestamp": datetime.now().isoformat(),
            "email": {
                "company": email_data.get("client_name"),
                "material": email_data.get("material"),
                "quantity": email_data.get("quantity"),
            },
            "insights": [],
        }

        # Extract learnings
        if email_data.get("material"):
            insight["insights"].append(
                f"Customer {email_data.get('client_name')} interested in {email_data.get('material')}"
            )

        if email_data.get("quantity"):
            try:
                qty = int(
                    "".join(filter(str.isdigit, str(email_data.get("quantity"))))
                )
                if qty >= 500:
                    insight["insights"].append(f"Large order: {qty} units")
            except:
                pass

        # Store learning
        self.index["learning_log"].append(insight)
        self._save_index()

        return insight

    def search(self, query: str) -> List[Dict]:
        """Search knowledge base"""
        results = []

        for category, data in self.index["categories"].items():
            for file_info in data.get("files", []):
                if query.lower() in file_info.lower():
                    results.append(
                        {
                            "category": category,
                            "file": file_info,
                            "relevance": 0.8,
                        }
                    )

        return results

    def get_ai_insights(self) -> List[Dict]:
        """Get AI-generated insights"""
        insights = []

        # Analyze learning patterns
        if len(self.index["learning_log"]) > 0:
            materials = {}
            for log_entry in self.index["learning_log"]:
                mat = log_entry.get("email", {}).get("material")
                if mat:
                    materials[mat] = materials.get(mat, 0) + 1

            # Top materials
            if materials:
                top_material = max(materials, key=materials.get)
                insights.append(
                    {
                        "type": "trend",
                        "insight": f"Most requested material: {top_material} ({materials[top_material]} orders)",
                        "confidence": 0.9,
                    }
                )

        # Add default insights if empty
        if not insights:
            insights = [
                {
                    "type": "info",
                    "insight": "Knowledge base actively learning from customer emails",
                    "confidence": 1.0,
                }
            ]

        return insights

    def _save_index(self):
        """Save index to file"""
        try:
            index_file = self.kb_path / "index.json"
            self.index["updated"] = datetime.now().isoformat()

            with open(index_file, "w") as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        total_files = sum(
            len(cat.get("files", [])) for cat in self.index["categories"].values()
        )

        return {
            "total_documents": total_files,
            "learning_events": len(self.index["learning_log"]),
            "categories": self.index["categories"],
            "ai_insights": self.get_ai_insights(),
        }
