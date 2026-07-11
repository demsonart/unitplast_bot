#!/usr/bin/env python3
"""
UNITPLAST API v1 - Backend Endpoints
Handles calculations, orders, materials, analytics, team management
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

api = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# ═══════════════════════════════════════════════════════════════════════════════
# CALCULATIONS API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/calculations', methods=['GET'])
def get_calculations():
    """Get list of calculations"""
    return jsonify({
        "success": True,
        "calculations": [
            {
                "id": 2506,
                "type": "UP",
                "product": "Пластиковый контейнер",
                "volume": "0.5 м³",
                "material": "ABS",
                "price": 245000,
                "created_at": "2026-07-07T10:30:00",
                "status": "saved"
            },
            {
                "id": 2507,
                "type": "UF",
                "product": "Деревянный шкаф",
                "dimensions": "180x80x40 см",
                "material": "ЛДСП",
                "price": 85000,
                "created_at": "2026-07-06T14:15:00",
                "status": "saved"
            },
            {
                "id": 2508,
                "type": "UM",
                "product": "Металлический каркас",
                "weight": "2.5 т",
                "material": "Сталь",
                "price": 125000,
                "created_at": "2026-07-05T09:45:00",
                "status": "saved"
            }
        ],
        "total": 24
    }), 200

@api.route('/calculations/<int:calc_id>', methods=['GET'])
def get_calculation(calc_id):
    """Get specific calculation"""
    return jsonify({
        "success": True,
        "calculation": {
            "id": calc_id,
            "type": "UP",
            "product": "Пластиковый контейнер",
            "parameters": {
                "material": "ABS пластик",
                "height": 800,
                "width": 600,
                "depth": 400,
                "wall_thickness": 2,
                "quantity": 100
            },
            "pricing": {
                "material_cost": 150000,
                "labor_cost": 50000,
                "markup": 45000,
                "total": 245000
            },
            "timeline": {
                "production_days": 5,
                "delivery_days": 2,
                "total_days": 7
            }
        }
    }), 200

@api.route('/calculations', methods=['POST'])
def create_calculation():
    """Create new calculation"""
    data = request.json
    calc_id = 2600 + random.randint(1, 99)

    return jsonify({
        "success": True,
        "calculation_id": calc_id,
        "price": data.get('quantity', 1) * 2450,
        "message": "Расчет создан успешно"
    }), 201

# ═══════════════════════════════════════════════════════════════════════════════
# ORDERS API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/orders', methods=['GET'])
def get_orders():
    """Get list of orders"""
    status = request.args.get('status', 'all')

    orders = [
        {
            "id": 2506,
            "calculation_id": 2506,
            "product": "Пластиковый контейнер",
            "quantity": 100,
            "price": 245000,
            "status": "in_progress",
            "progress": 60,
            "created_at": "2026-07-07",
            "due_date": "2026-07-12"
        },
        {
            "id": 2505,
            "calculation_id": 2507,
            "product": "Деревянный шкаф",
            "quantity": 50,
            "price": 85000,
            "status": "ready",
            "progress": 100,
            "created_at": "2026-07-05",
            "due_date": "2026-07-10"
        },
        {
            "id": 2504,
            "calculation_id": 2508,
            "product": "Металлический каркас",
            "quantity": 1,
            "price": 125000,
            "status": "delivered",
            "progress": 100,
            "created_at": "2026-07-01",
            "due_date": "2026-07-08"
        }
    ]

    if status != 'all':
        orders = [o for o in orders if o['status'] == status]

    return jsonify({
        "success": True,
        "orders": orders,
        "total": len(orders),
        "statuses": {
            "in_progress": 3,
            "ready": 2,
            "delivered": 1,
            "cancelled": 0
        }
    }), 200

@api.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order details"""
    return jsonify({
        "success": True,
        "order": {
            "id": order_id,
            "calculation_id": 2506,
            "product": "Пластиковый контейнер",
            "quantity": 100,
            "unit_price": 2450,
            "total_price": 245000,
            "status": "in_progress",
            "progress": 60,
            "timeline": {
                "created": "2026-07-07T10:30:00",
                "started": "2026-07-07T14:00:00",
                "due": "2026-07-12T17:00:00",
                "estimated_completion": "2026-07-12"
            },
            "production": {
                "line": "Line A",
                "current_step": 3,
                "total_steps": 5,
                "materials_used": "45 кг"
            }
        }
    }), 200

@api.route('/orders', methods=['POST'])
def create_order():
    """Create new order from calculation"""
    data = request.json
    order_id = 2500 + random.randint(1, 99)

    return jsonify({
        "success": True,
        "order_id": order_id,
        "message": "Заказ создан и добавлен в очередь производства"
    }), 201

# ═══════════════════════════════════════════════════════════════════════════════
# MATERIALS API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/materials', methods=['GET'])
def get_materials_v1():
    """Get materials inventory"""
    return jsonify({
        "success": True,
        "materials": {
            "UP": [
                {
                    "name": "ABS пластик",
                    "quantity": 450,
                    "unit": "кг",
                    "price_per_unit": 425,
                    "status": "in_stock",
                    "reorder_level": 100
                },
                {
                    "name": "PP пластик",
                    "quantity": 35,
                    "unit": "кг",
                    "price_per_unit": 275,
                    "status": "low_stock",
                    "reorder_level": 100
                }
            ],
            "UF": [
                {
                    "name": "Фанера 18мм",
                    "quantity": 820,
                    "unit": "листов",
                    "price_per_unit": 450,
                    "status": "in_stock",
                    "reorder_level": 200
                }
            ],
            "UM": [
                {
                    "name": "Стальной профиль",
                    "quantity": 8,
                    "unit": "т",
                    "price_per_unit": 65000,
                    "status": "critical",
                    "reorder_level": 10
                }
            ]
        }
    }), 200

@api.route('/materials/<material_id>', methods=['PUT'])
def update_material(material_id):
    """Update material inventory"""
    data = request.json

    return jsonify({
        "success": True,
        "message": f"Материал {material_id} обновлен",
        "new_quantity": data.get('quantity')
    }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get dashboard analytics"""
    return jsonify({
        "success": True,
        "period": "month",
        "metrics": {
            "calculations": 24,
            "orders": 7,
            "revenue": 2430000,
            "avg_order_value": 347142,
            "production_efficiency": 76,
            "on_time_delivery": 94
        },
        "by_type": {
            "UP": {"calculations": 8, "orders": 4, "revenue": 980000},
            "UF": {"calculations": 9, "orders": 2, "revenue": 680000},
            "UM": {"calculations": 7, "orders": 1, "revenue": 770000}
        },
        "trends": {
            "last_7_days": [140, 156, 142, 165, 178, 182, 195],
            "growth_rate": 15
        }
    }), 200

@api.route('/analytics/production', methods=['GET'])
def get_production_analytics():
    """Get production line analytics"""
    return jsonify({
        "success": True,
        "lines": [
            {
                "name": "Line A - Plastic",
                "status": "running",
                "load": 87,
                "current_order": 2506,
                "progress": 60,
                "items_per_hour": 125,
                "uptime": 99.5
            },
            {
                "name": "Line B - Furniture",
                "status": "maintenance",
                "load": 0,
                "current_order": None,
                "progress": 0,
                "eta": "2 часа"
            },
            {
                "name": "Line C - Metal",
                "status": "idle",
                "load": 0,
                "ready_for": "next_batch"
            }
        ]
    }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# TEAM API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/team/members', methods=['GET'])
def get_team_members():
    """Get team members list"""
    return jsonify({
        "success": True,
        "team": [
            {
                "id": 1,
                "name": "Иван Петров",
                "role": "Manager",
                "email": "ivan@unitplast.ru",
                "status": "active",
                "permissions": ["read", "write", "admin"]
            },
            {
                "id": 2,
                "name": "Мария Сидорова",
                "role": "Operator",
                "email": "maria@unitplast.ru",
                "status": "active",
                "permissions": ["read", "write"]
            },
            {
                "id": 3,
                "name": "Алексей Козлов",
                "role": "Engineer",
                "email": "alex@unitplast.ru",
                "status": "active",
                "permissions": ["read"]
            }
        ],
        "total": 12
    }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# SYNC API (1C Integration)
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/sync/1c', methods=['POST'])
def sync_1c():
    """Sync with 1C accounting"""
    return jsonify({
        "success": True,
        "synced": {
            "documents": 156,
            "orders": 7,
            "materials": 45,
            "timestamp": datetime.now().isoformat()
        },
        "message": "Синхронизация с 1С завершена успешно"
    }), 200

@api.route('/sync/1c/status', methods=['GET'])
def sync_1c_status():
    """Get 1C sync status"""
    return jsonify({
        "success": True,
        "status": "synced",
        "last_sync": "5 минут назад",
        "next_sync": "за 4 минуты 55 секунд",
        "documents": 156,
        "errors": 0
    }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT API
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/export/orders/<format>', methods=['POST'])
def export_orders(format):
    """Export orders in specified format"""
    if format not in ['xlsx', 'csv', 'pdf', 'xml']:
        return jsonify({"error": "Unsupported format"}), 400

    return jsonify({
        "success": True,
        "format": format,
        "filename": f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
        "records": 24,
        "download_url": f"/downloads/orders_export.{format}"
    }), 200

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH & INFO
# ═══════════════════════════════════════════════════════════════════════════════

@api.route('/status', methods=['GET'])
def api_status():
    """Get API status"""
    return jsonify({
        "success": True,
        "api_version": "1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "calculations": "/api/v1/calculations",
            "orders": "/api/v1/orders",
            "materials": "/api/v1/materials",
            "analytics": "/api/v1/analytics/dashboard",
            "team": "/api/v1/team/members",
            "sync_1c": "/api/v1/sync/1c"
        }
    }), 200
