"""
Factory OS API
Serves mini apps, dashboards, and knowledge bases for any factory
"""

from flask import Flask, jsonify, request
from .factory_template import FactoryTemplate, FactorySystem, FactoryOS
import json
import os
import logging

logger = logging.getLogger(__name__)


class FactoryAPI:
    """REST API for Factory OS"""

    def __init__(self, app=None):
        self.app = app
        self.factory_os = self._load_factory_os()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize Flask app with Factory API routes"""
        self.app = app

        @app.route("/api/factories", methods=["GET"])
        def list_factories():
            """List all available factories"""
            templates = self.factory_os.list_available_templates()
            return jsonify({"success": True, "factories": templates})

        @app.route("/api/factories/<industry>", methods=["GET"])
        def get_factory(industry: str):
            """Get factory details"""
            system = self.factory_os.get_system(industry)
            if not system:
                return jsonify({"success": False, "error": "Factory not found"}), 404

            return jsonify(
                {
                    "success": True,
                    "factory": system.template.to_dict(),
                    "kpis": system.template.manager_kpis,
                }
            )

        @app.route("/api/factories/<industry>/mini-app", methods=["GET"])
        def get_mini_app(industry: str):
            """Get mini app HTML for factory"""
            system = self.factory_os.get_system(industry)
            if not system:
                return jsonify({"success": False, "error": "Factory not found"}), 404

            html = system.generate_mini_app_html()
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}

        @app.route("/api/factories/<industry>/dashboard-config", methods=["GET"])
        def get_dashboard_config(industry: str):
            """Get manager dashboard config"""
            system = self.factory_os.get_system(industry)
            if not system:
                return jsonify({"success": False, "error": "Factory not found"}), 404

            config = system.get_manager_dashboard_config()
            return jsonify({"success": True, "config": config})

        @app.route("/api/factories/<industry>/knowledge", methods=["GET"])
        def get_knowledge(industry: str):
            """Get AI consultant knowledge base"""
            system = self.factory_os.get_system(industry)
            if not system:
                return jsonify({"success": False, "error": "Factory not found"}), 404

            knowledge = system.get_ai_consultant_knowledge()
            return jsonify({"success": True, "knowledge": knowledge})

        @app.route("/api/factories/<industry>/email-rules", methods=["GET"])
        def get_email_rules(industry: str):
            """Get email classification rules"""
            system = self.factory_os.get_system(industry)
            if not system:
                return jsonify({"success": False, "error": "Factory not found"}), 404

            rules = system.get_email_classification_rules()
            return jsonify({"success": True, "rules": rules})

    def _load_factory_os(self) -> FactoryOS:
        """Load all available factory templates"""
        factory_os = FactoryOS()

        # Load all JSON template files from config/templates/
        templates_dir = "config/templates"
        if not os.path.exists(templates_dir):
            logger.warning(f"Templates directory not found: {templates_dir}")
            return factory_os

        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                config_path = os.path.join(templates_dir, filename)
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)

                    template = FactoryTemplate(
                        name=config['name'],
                        industry=config['industry'],
                        icon=config['icon'],
                        color=config['color'],
                        materials=config['materials'],
                        production_modules=config['production_modules'],
                        knowledge_base=config['knowledge_base'],
                        email_rules=config['email_rules'],
                        manager_kpis=config['manager_kpis'],
                    )

                    factory_os.register_template(template)
                    logger.info(f"Loaded template: {template.name}")

                except Exception as e:
                    logger.error(f"Failed to load template {config_path}: {e}")
                    continue

        return factory_os


def create_factory_api(app: Flask) -> FactoryAPI:
    """Factory function to create and initialize Factory API"""
    return FactoryAPI(app)
