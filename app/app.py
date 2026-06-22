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

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Paths
    WEB_DIR = Path(__file__).parent.parent / "web"
    LANDING_PATH = WEB_DIR / "index.html"
    MINIAPP_PATH = WEB_DIR / "unitplast_app.html"

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

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
