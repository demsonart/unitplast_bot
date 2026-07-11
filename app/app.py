#!/usr/bin/env python3
"""
UNITPLAST BOT - Flask Web Server
Serves: Landing Page + Mini App + API Endpoints
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from datetime import datetime
from app.api_v1 import api as api_v1

def create_app():
    """Create and configure Flask application"""
    WEB_DIR = Path(__file__).parent.parent / "web"

    app = Flask(__name__,
                static_folder=str(WEB_DIR / "assets"),
                static_url_path="/assets")
    CORS(app)

    # Paths
    LANDING_PATH = WEB_DIR / "landing.html"  # New landing page with 9 sections
    INDEX_PATH = WEB_DIR / "index.html"  # Old landing (fallback)
    MINIAPP_PATH = WEB_DIR / "miniapp.html"  # Mini app with loyalty system

    # ═══════════════════════════════════════════════════════════════════════════════
    # ROUTES
    # ═══════════════════════════════════════════════════════════════════════════════

    @app.route('/')
    def landing():
        """Landing page"""
        try:
            with open(LANDING_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return jsonify({"error": "Landing page not found"}), 404

    @app.route('/app/miniapp')
    def miniapp():
        """Telegram Mini App"""
        try:
            with open(MINIAPP_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return jsonify({"error": "Mini App not found"}), 404

    @app.route('/health')
    @app.route('/api/health')
    def health():
        """Health check - used by Railway and monitoring"""
        return jsonify({
            "status": "OK",
            "service": "UNITPLAST BOT",
            "version": "2.0",
            "timestamp": str(datetime.now()),
            "endpoints": {
                "landing": "/",
                "miniapp": "/app/miniapp",
                "materials": "/api/materials",
                "health": "/health"
            }
        }), 200

    @app.route('/api/materials')
    def get_materials():
        """Get materials catalog"""
        return jsonify({
            "success": True,
            "materials": [
                {"id": "abs", "name": "ABS", "price": "350-500 ₽/кг", "icon": "🧴"},
                {"id": "pp", "name": "PP", "price": "200-350 ₽/кг", "icon": "🧴"},
                {"id": "pet", "name": "PET", "price": "300-450 ₽/кг", "icon": "🧴"},
                {"id": "pvc", "name": "PVC", "price": "250-400 ₽/кг", "icon": "🧴"},
                {"id": "pc", "name": "PC", "price": "800-1200 ₽/кг", "icon": "🧴"},
            ]
        })

    @app.route('/api/emails')
    def get_emails():
        """Get recent emails"""
        return jsonify({
            "success": True,
            "emails": [
                {
                    "id": 1,
                    "from": "Казаков Р.",
                    "subject": "Крышки ABS 110х120мм 2000шт",
                    "time": "5 мин",
                    "unread": True
                },
                {
                    "id": 2,
                    "from": "ООО Тест",
                    "subject": "КП на PP контейнеры 5000шт",
                    "time": "15 мин",
                    "unread": True
                },
            ]
        })

    @app.route('/api/dashboard/stats')
    def dashboard_stats():
        """Get dashboard statistics"""
        return jsonify({
            "success": True,
            "stats": {
                "total_orders": 23,
                "critical_orders": 3,
                "response_time_minutes": 12,
                "conversion_rate": 0.35
            }
        })

    @app.route('/robots.txt')
    def robots():
        """SEO robots.txt"""
        try:
            robots_path = WEB_DIR / "robots.txt"
            with open(robots_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except FileNotFoundError:
            return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    @app.route('/sitemap.xml')
    def sitemap():
        """SEO sitemap.xml"""
        try:
            sitemap_path = WEB_DIR / "sitemap.xml"
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'application/xml; charset=utf-8'}
        except FileNotFoundError:
            return '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', 200, {'Content-Type': 'application/xml; charset=utf-8'}

    @app.route('/og-image.svg')
    def og_image():
        """Open Graph preview image"""
        try:
            og_path = WEB_DIR / "og-image.svg"
            with open(og_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'image/svg+xml; charset=utf-8'}
        except FileNotFoundError:
            return '', 404

    @app.route('/data/<filename>')
    def serve_data(filename):
        """Serve catalog data files (JSON)"""
        try:
            if not filename.endswith('.json') and not filename.endswith('.md'):
                return jsonify({"error": "Invalid file type"}), 403
            data_path = WEB_DIR / "data" / filename
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content_type = 'application/json' if filename.endswith('.json') else 'text/markdown'
                return content, 200, {'Content-Type': f'{content_type}; charset=utf-8'}
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/js/<filename>')
    def serve_js(filename):
        """Serve JavaScript files"""
        try:
            if not filename.endswith('.js'):
                return jsonify({"error": "Invalid file type"}), 403
            js_path = WEB_DIR / "js" / filename
            with open(js_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'application/javascript; charset=utf-8'}
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ═══════════════════════════════════════════════════════════════════════════════
    # AGENTS API (Autonomous agents monitoring)
    # ═══════════════════════════════════════════════════════════════════════════════

    @app.route('/api/agents/status')
    def agents_status():
        """Get current status of all agents (read-only)"""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            status_file = data_dir / "agents_status.json"

            if status_file.exists():
                with open(status_file, 'r') as f:
                    data = jsonify(json.load(f))
                    return data, 200

            return jsonify({"error": "Agent status file not found", "status": "initializing"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/agents/health')
    def agents_health():
        """Get health check history from monitor agent"""
        try:
            log_dir = Path(__file__).parent.parent / "logs"
            health_file = log_dir / "health_monitor.log"

            if not health_file.exists():
                return jsonify({"error": "Health log not found"}), 404

            # Return last 20 health check entries
            with open(health_file, 'r') as f:
                lines = f.readlines()[-20:]

            entries = []
            for line in lines:
                try:
                    entries.append(json.loads(line.strip()))
                except:
                    pass

            return jsonify({"history": entries, "count": len(entries)}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/agents/logs/<agent_name>')
    def agents_logs(agent_name):
        """Get logs for specific agent"""
        try:
            # Whitelist agent names to prevent path traversal
            allowed_agents = ['health_monitor', 'agent_status', 'system_monitor', 'unitplast']
            if agent_name not in allowed_agents:
                return jsonify({"error": "Invalid agent name"}), 403

            log_dir = Path(__file__).parent.parent / "logs"
            log_file = log_dir / f"{agent_name}.log"

            if not log_file.exists():
                return jsonify({"error": f"Log for {agent_name} not found"}), 404

            # Return last 50 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()[-50:]

            return jsonify({"agent": agent_name, "lines": lines}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ═══════════════════════════════════════════════════════════════════════════════
    # ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════════

    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return jsonify({"error": "Endpoint not found", "status": 404}), 404

    @app.errorhandler(500)
    def server_error(error):
        """500 error handler"""
        return jsonify({"error": "Internal server error", "status": 500}), 500

    # ═══════════════════════════════════════════════════════════════════════════════
    # REGISTER BLUEPRINTS
    # ═══════════════════════════════════════════════════════════════════════════════

    app.register_blueprint(api_v1)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
