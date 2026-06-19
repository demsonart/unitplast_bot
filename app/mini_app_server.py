"""
AI FACTORY OS - Multi-Industry Mini App & API Server
Serves mini apps, dashboards, and APIs for any factory
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify
from .factory_api import create_factory_api


def get_landing_page() -> str:
    """Get landing page listing all available factories"""
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏭 AI Factory OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header-icon {
            font-size: 64px;
            margin-bottom: 16px;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
            color: #111827;
        }
        .header p {
            color: #6b7280;
            font-size: 14px;
        }
        .factories {
            display: grid;
            gap: 16px;
            margin-bottom: 20px;
        }
        .factory-card {
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            color: #111827;
        }
        .factory-card:hover {
            border-color: #667eea;
            background: #f0f4ff;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
        }
        .factory-icon {
            font-size: 28px;
            margin-right: 12px;
        }
        .factory-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        .factory-desc {
            font-size: 13px;
            color: #6b7280;
        }
        .loading {
            text-align: center;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-icon">🏭</div>
            <h1>AI Factory OS</h1>
            <p>Platform for manufacturing sales systems</p>
        </div>
        <div class="factories" id="factories-list">
            <div class="loading">Loading factories...</div>
        </div>
    </div>
    <script>
        fetch('/api/factories')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('factories-list');
                if (!data.factories || data.factories.length === 0) {
                    list.innerHTML = '<p class="loading">No factories configured</p>';
                    return;
                }
                list.innerHTML = data.factories.map(f => `
                    <a href="/app/${f.industry}" class="factory-card">
                        <div>
                            <div class="factory-icon">${f.icon}</div>
                            <div class="factory-name">${f.name}</div>
                            <div class="factory-desc">${f.materials} materials • ${f.modules} production modules</div>
                        </div>
                    </a>
                `).join('');
            })
            .catch(e => {
                document.getElementById('factories-list').innerHTML = '<p class="loading">Error loading factories</p>';
                console.error(e);
            });
    </script>
</body>
</html>"""


def create_app():
    """Create Flask application with Factory OS"""
    try:
        app = Flask(__name__)

        # Initialize Factory API
        factory_api = create_factory_api(app)

        @app.route("/")
        def index():
            """Landing page with factory list"""
            return get_landing_page()

        @app.route("/app/<industry>")
        def get_app(industry: str):
            """Serve mini app for specific industry"""
            system = factory_api.factory_os.get_system(industry)
            if not system:
                return f"<h1>Factory not found: {industry}</h1>", 404

            html = system.generate_mini_app_html()
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}

        @app.route("/health")
        def health():
            factories = len(factory_api.factory_os.systems)
            return {
                "status": "OK",
                "version": "3.0",
                "factories": factories,
                "mode": "FactoryOS"
            }, 200

        return app

    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return None


if __name__ == "__main__":
    app = create_app()
    if app:
        print("=" * 60)
        print("🏭 AI FACTORY OS - Multi-Industry Server")
        print("=" * 60)
        print("📱 Web: http://localhost:5000")
        print("🎯 API: http://localhost:5000/api/factories")
        print("\nPress Ctrl+C to stop\n")
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print("❌ Cannot start server without Flask")
