#!/usr/bin/env python3
"""
UNITPLAST BOT - Flask Web Server
Serves: Landing Page + Mini App + API Endpoints
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
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
