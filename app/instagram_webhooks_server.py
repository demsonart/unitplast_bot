import logging
import json
import hmac
import hashlib
from typing import Dict, Optional
from flask import Flask, request
from functools import wraps

logger = logging.getLogger(__name__)

class InstagramWebhookServer:
    """
    Flask server for receiving Meta Webhooks from Instagram
    Handles webhook verification and message processing
    """

    def __init__(self, verify_token: str, app_secret: str, host: str = "0.0.0.0", port: int = 5000):
        self.verify_token = verify_token
        self.app_secret = app_secret
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.message_handlers = {}

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for webhooks"""
        @self.app.route("/webhook", methods=["GET"])
        def verify_webhook():
            """Verify webhook with Meta"""
            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")

            if token == self.verify_token:
                logger.info("Webhook verification successful")
                return challenge
            else:
                logger.error("Webhook verification failed")
                return "Forbidden", 403

        @self.app.route("/webhook", methods=["POST"])
        def receive_webhook():
            """Receive messages from Meta"""
            try:
                # Verify request signature
                if not self._verify_signature(request):
                    logger.warning("Invalid webhook signature")
                    return "Invalid signature", 403

                data = request.get_json()

                if not data:
                    return "No data", 400

                # Process webhook
                self._process_webhook(data)

                return "ok", 200

            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return "Error", 500

    def _verify_signature(self, req) -> bool:
        """Verify webhook signature from Meta"""
        try:
            signature = req.headers.get("X-Hub-Signature-256", "")
            body = req.get_data(as_text=True)

            expected_signature = f"sha256={hmac.new(
                self.app_secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()}"

            return signature == expected_signature

        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    def _process_webhook(self, data: Dict):
        """Process incoming webhook data"""
        try:
            if "entry" not in data:
                return

            for entry in data.get("entry", []):
                for messaging in entry.get("messaging", []):
                    sender_id = messaging.get("sender", {}).get("id")
                    recipient_id = messaging.get("recipient", {}).get("id")
                    timestamp = messaging.get("timestamp")

                    # Process message
                    if "message" in messaging:
                        self._handle_message(sender_id, messaging.get("message"), timestamp)

                    # Process postback (button clicks)
                    elif "postback" in messaging:
                        self._handle_postback(sender_id, messaging.get("postback"), timestamp)

        except Exception as e:
            logger.error(f"Error processing webhook data: {e}")

    def _handle_message(self, sender_id: str, message: Dict, timestamp: int):
        """Handle incoming message"""
        try:
            logger.info(f"Message from {sender_id}: {message}")

            # Call registered handler
            if "message" in self.message_handlers:
                handler = self.message_handlers["message"]
                handler(sender_id, message, timestamp)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _handle_postback(self, sender_id: str, postback: Dict, timestamp: int):
        """Handle postback (button clicks)"""
        try:
            payload = postback.get("payload")
            logger.info(f"Postback from {sender_id}: {payload}")

            if "postback" in self.message_handlers:
                handler = self.message_handlers["postback"]
                handler(sender_id, postback, timestamp)

        except Exception as e:
            logger.error(f"Error handling postback: {e}")

    def register_handler(self, event_type: str, handler):
        """Register message/postback handler"""
        self.message_handlers[event_type] = handler
        logger.info(f"Handler registered for {event_type}")

    def send_message(self, recipient_id: str, text: str) -> bool:
        """
        Send message to Instagram user
        In production, this would use the Instagram Graph API
        """
        try:
            logger.info(f"Sending message to {recipient_id}: {text}")
            # In production, call Instagram Graph API
            # endpoint = f"https://graph.instagram.com/{recipient_id}/messages"
            # requests.post(endpoint, ...)
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_template(self, recipient_id: str, template_name: str) -> bool:
        """Send template message to Instagram user"""
        try:
            logger.info(f"Sending template {template_name} to {recipient_id}")
            # In production, call Instagram Graph API with template
            return True
        except Exception as e:
            logger.error(f"Error sending template: {e}")
            return False

    def start(self, debug: bool = False):
        """Start webhook server"""
        logger.info(f"Starting webhook server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug)

    def get_app(self):
        """Get Flask app instance"""
        return self.app
