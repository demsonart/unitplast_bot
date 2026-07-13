"""
UNITPLAST API Server
Connects frontend app to backend services
"""

from flask import Flask, jsonify, request
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    # Import backend modules
    from .ai_consultant import AIConsultant
    from .lead_scorer import LeadScorer
    from .email_reader import EmailReader
    from .config import YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT
    from .claude_routes import claude_bp

    consultant = AIConsultant()
    scorer = LeadScorer()

    # Register Claude API blueprint
    app.register_blueprint(claude_bp)

    # ============ MATERIALS API ============

    @app.route('/api/materials', methods=['GET'])
    def get_materials():
        """Get all materials with specs"""
        materials = consultant.knowledge_base['materials']
        return jsonify({
            'success': True,
            'materials': [
                {
                    'id': key,
                    'name': val['name'],
                    'price_range': f"{val['price_per_kg'][0]}-{val['price_per_kg'][1]} ₽/кг",
                    'properties': val['properties'],
                    'uses': val['best_for'],
                    'min_volume': val['min_volume'],
                    'lead_time': f"{val['lead_time_days'][0]}-{val['lead_time_days'][1]} дней"
                }
                for key, val in materials.items()
            ]
        })

    @app.route('/api/materials/<material_id>', methods=['GET'])
    def get_material(material_id):
        """Get specific material details"""
        materials = consultant.knowledge_base['materials']
        if material_id.upper() not in materials:
            return jsonify({'error': 'Material not found'}), 404

        mat = materials[material_id.upper()]
        return jsonify({
            'success': True,
            'material': {
                'id': material_id.upper(),
                'name': mat['name'],
                'price_range': mat['price_per_kg'],
                'properties': mat['properties'],
                'uses': mat['best_for'],
                'alternatives_cheaper': mat.get('alternatives_cheaper', []),
                'min_volume': mat['min_volume'],
                'lead_time': mat['lead_time_days']
            }
        })

    # ============ AI CONSULTANT API ============

    @app.route('/api/ai/consult', methods=['POST'])
    def ai_consult():
        """AI Consultant - answer question"""
        data = request.json
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'Question required'}), 400

        response = consultant.answer_question(question)
        return jsonify({
            'success': True,
            'answer': response
        })

    # ============ EMAIL API ============

    @app.route('/api/emails', methods=['GET'])
    def get_emails():
        """Get emails from inbox"""
        try:
            reader = EmailReader(YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT)
            reader.connect()
            reader.mail.select('INBOX')

            # Get last 10 emails
            status, messages = reader.mail.search(None, 'ALL')
            email_ids = messages[0].split()[-10:]

            import email
            emails = []

            for email_id in reversed(email_ids):
                try:
                    status, msg_data = reader.mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])

                    subject = reader.decode_str(msg.get('Subject', ''))
                    from_email = reader.decode_str(msg.get('From', ''))
                    body = reader.get_email_body(msg)

                    emails.append({
                        'id': email_id.decode(),
                        'from': from_email.split('<')[0].strip(),
                        'subject': subject,
                        'preview': body[:100] + '...' if len(body) > 100 else body,
                        'time': '∼ now',
                        'unread': False
                    })
                except Exception as e:
                    logger.error(f"Error processing email: {e}")
                    continue

            reader.disconnect()
            return jsonify({'success': True, 'emails': emails})

        except Exception as e:
            logger.error(f"Email fetch error: {e}")
            return jsonify({'error': str(e)}), 500

    # ============ ORDERS API ============

    @app.route('/api/orders', methods=['POST'])
    def create_order():
        """Create new order"""
        data = request.json

        order = {
            'id': datetime.now().isoformat(),
            'material': data.get('material'),
            'quantity': data.get('quantity'),
            'size': data.get('size'),
            'company': data.get('company'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }

        # Score the order
        score_result = scorer.score_lead({
            'material': order['material'],
            'quantity': order['quantity'],
            'client_name': order['company'],
            'client_phone': order['phone']
        })

        order['score'] = score_result['score']
        order['priority'] = score_result['priority']['level']

        # TODO: Save to database
        logger.info(f"Order created: {order['id']}")

        return jsonify({
            'success': True,
            'order': order,
            'message': f"✅ Order created! Priority: {order['priority']} (Score: {order['score']}/100)"
        }), 201

    @app.route('/api/orders', methods=['GET'])
    def get_orders():
        """Get recent orders"""
        # TODO: Fetch from database
        orders = [
            {
                'id': '1',
                'material': 'ABS',
                'quantity': 2000,
                'company': 'Казаков Р.',
                'priority': 'critical',
                'score': 90,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': '2',
                'material': 'PP',
                'quantity': 5000,
                'company': 'ООО Тест',
                'priority': 'high',
                'score': 75,
                'created_at': datetime.now().isoformat()
            }
        ]

        return jsonify({'success': True, 'orders': orders})

    # ============ DASHBOARD API ============

    @app.route('/api/dashboard/stats', methods=['GET'])
    def get_stats():
        """Get dashboard statistics"""
        return jsonify({
            'success': True,
            'stats': {
                'orders_this_week': 5,
                'conversion_rate': 0.35,
                'avg_response_time_minutes': 15,
                'critical_orders': 1,
                'high_orders': 2,
                'total_revenue': 125000
            }
        })

    # ============ HEALTH CHECK ============

    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check"""
        return jsonify({
            'status': 'OK',
            'service': 'UNITPLAST API',
            'version': '1.0',
            'timestamp': datetime.now().isoformat()
        })

    # ============ 404 HANDLER ============

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("🚀 UNITPLAST API Server")
    print("📡 Running on: http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/materials")
    print("   GET  /api/materials/{id}")
    print("   POST /api/ai/consult")
    print("   GET  /api/emails")
    print("   POST /api/orders")
    print("   GET  /api/orders")
    print("   GET  /api/dashboard/stats")
    app.run(host='0.0.0.0', port=5000, debug=False)
