#!/usr/bin/env python3
"""
UNITPLAST AI FACTORY OS - Production Mini App Server
Serves the Mini App and APIs for production deployment
"""

from flask import Flask, jsonify, render_template_string, send_file
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Get Mini App HTML
MINI_APP_PATH = Path(__file__).parent / "web" / "unitplast_app.html"

@app.route('/')
def index():
    """Serve Mini App"""
    try:
        with open(MINI_APP_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Mini App not found"}), 404

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "OK",
        "service": "UNITPLAST API",
        "version": "1.0"
    })

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

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
