"""
Flask роуты для работы с Claude API через веб-интерфейс
Предоставляет REST API для калькулятора и управления заказами
"""

from flask import Blueprint, request, jsonify
from .claude_api import ClaudeAPIClient
import logging

logger = logging.getLogger(__name__)

claude_bp = Blueprint('claude', __name__, url_prefix='/api/claude')
claude_client = ClaudeAPIClient()


@claude_bp.route('/calculate', methods=['POST'])
def calculate_price():
    """
    POST /api/claude/calculate
    Расчет стоимости материала

    Request JSON:
    {
        "material": "plastic|furniture|metal",
        "params": {
            "height": 200,
            "width": 150,
            "thickness": 2,
            "quantity": 100
        },
        "use_cache": true
    }
    """
    try:
        data = request.get_json()
        material = data.get('material')
        params = data.get('params', {})
        use_cache = data.get('use_cache', True)

        if not material or not params:
            return jsonify({
                "status": "error",
                "message": "Укажите material и params"
            }), 400

        result = claude_client.calculate_price(material, params, use_cache)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Ошибка в /calculate: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@claude_bp.route('/analyze-order', methods=['POST'])
def analyze_order():
    """
    POST /api/claude/analyze-order
    Анализ текста заказа

    Request JSON:
    {
        "order_text": "Нужно 500 коробок...",
        "order_history": [...],
        "use_cache": true
    }
    """
    try:
        data = request.get_json()
        order_text = data.get('order_text')
        order_history = data.get('order_history')
        use_cache = data.get('use_cache', True)

        if not order_text:
            return jsonify({
                "status": "error",
                "message": "Укажите order_text"
            }), 400

        result = claude_client.analyze_order(order_text, order_history, use_cache)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Ошибка в /analyze-order: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@claude_bp.route('/generate-proposal', methods=['POST'])
def generate_proposal():
    """
    POST /api/claude/generate-proposal
    Генерация коммерческого предложения

    Request JSON:
    {
        "order_data": {
            "material": "metal",
            "price": 150000
        },
        "company_info": {
            "company": "UNITGROUP",
            "email": "sales@unitgroup.tech"
        },
        "use_cache": true
    }
    """
    try:
        data = request.get_json()
        order_data = data.get('order_data')
        company_info = data.get('company_info')
        use_cache = data.get('use_cache', True)

        if not order_data or not company_info:
            return jsonify({
                "status": "error",
                "message": "Укажите order_data и company_info"
            }), 400

        result = claude_client.generate_proposal(order_data, company_info, use_cache)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Ошибка в /generate-proposal: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@claude_bp.route('/health', methods=['GET'])
def health():
    """Проверка доступности Claude API"""
    try:
        # Простой тест подключения
        return jsonify({
            "status": "ok",
            "service": "claude-api",
            "model": claude_client.model
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
