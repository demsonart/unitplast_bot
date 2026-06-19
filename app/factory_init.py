"""
AI Factory OS Initialization
Sets up Factory OS with registered templates
"""

import json
import os
from pathlib import Path
from .factory_template import FactoryOS, FactoryTemplate, FactorySystem

def initialize_factory_os() -> FactoryOS:
    """Initialize FactoryOS with all available templates"""
    os.makedirs('config/templates', exist_ok=True)

    factory_os = FactoryOS()

    # Load Plastics Factory Template
    plastics_config = load_template_config('config/templates/plastics_factory.json')
    plastics_template = FactoryTemplate(
        name=plastics_config['name'],
        industry=plastics_config['industry'],
        icon=plastics_config['icon'],
        color=plastics_config['color'],
        materials=plastics_config['materials'],
        production_modules=plastics_config['production_modules'],
        knowledge_base=plastics_config['knowledge_base'],
        email_rules=plastics_config['email_rules'],
        manager_kpis=plastics_config['manager_kpis'],
    )
    factory_os.register_template(plastics_template)

    # TODO: Load other factory templates
    # - Furniture Factory
    # - Metal Processing Factory
    # - Packaging Factory
    # - Logistics Factory

    return factory_os


def load_template_config(config_path: str) -> dict:
    """Load template config from JSON file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Template config not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_mini_app_for_factory(industry: str, output_path: str) -> bool:
    """Generate Mini App HTML for a factory industry"""
    factory_os = initialize_factory_os()
    system = factory_os.get_system(industry)

    if not system:
        print(f"❌ Factory system not found: {industry}")
        return False

    html = system.generate_mini_app_html()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Generated Mini App: {output_path}")
    return True


def generate_all_factory_mini_apps() -> None:
    """Generate Mini Apps for all registered factories"""
    factory_os = initialize_factory_os()

    for industry, system in factory_os.systems.items():
        output_path = f"web/{industry}_factory.html"
        html = system.generate_mini_app_html()

        os.makedirs("web", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generated: {output_path}")


if __name__ == "__main__":
    print("🏭 Initializing AI Factory OS...")
    generate_all_factory_mini_apps()
    print("✅ Factory OS initialized successfully!")
