import imaplib
import email
from email.header import decode_header
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class EmailReader:
    def __init__(self, email_addr, password, imap_server="imap.yandex.ru", imap_port=993):
        self.email = email_addr
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.mail = None

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email, self.password)
            logger.info(f"Connected to {self.imap_server}")
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            raise

    def disconnect(self):
        if self.mail:
            self.mail.close()
            self.mail.logout()

    def decode_str(self, s):
        """Properly decode email headers with UTF-8 support"""
        if isinstance(s, bytes):
            s = s.decode('utf-8', errors='ignore')

        if not isinstance(s, str):
            return str(s)

        try:
            # Decode RFC 2047 encoded words
            result = decode_header(s)
            decoded_str = ""

            for text, encoding in result:
                if isinstance(text, bytes):
                    # Try specified encoding first, fallback to UTF-8
                    if encoding:
                        try:
                            decoded_str += text.decode(encoding, errors='replace')
                        except (LookupError, TypeError):
                            decoded_str += text.decode('utf-8', errors='replace')
                    else:
                        decoded_str += text.decode('utf-8', errors='replace')
                else:
                    decoded_str += str(text) if text else ""

            return decoded_str.strip()
        except Exception as e:
            logger.warning(f"Failed to decode string: {e}")
            return str(s) if s else ""

    def get_email_body(self, msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    body = payload.decode('utf-8', errors='ignore')
                    break
                elif content_type == "text/html" and not body:
                    payload = part.get_payload(decode=True)
                    body = payload.decode('utf-8', errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload()
        return body

    def get_new_emails(self, limit=10) -> List[Tuple[str, str, str, str]]:
        """Returns list of (message_id, subject, from_email, body)"""
        try:
            self.mail.select('INBOX')
            status, messages = self.mail.search(None, 'ALL')
            email_ids = messages[0].split()[-limit:]

            emails = []
            for email_id in email_ids:
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                message_id = msg.get('Message-ID', '')
                subject = self.decode_str(msg.get('Subject', ''))
                from_email = self.decode_str(msg.get('From', ''))
                body = self.get_email_body(msg)

                emails.append((message_id, subject, from_email, body))

            return emails
        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []

    def get_unread_emails(self) -> List[Tuple[str, str, str, str]]:
        """Returns list of unread emails (message_id, subject, from_email, body)"""
        try:
            self.mail.select('INBOX')
            status, messages = self.mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()

            emails = []
            for email_id in email_ids:
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                message_id = msg.get('Message-ID', '')
                subject = self.decode_str(msg.get('Subject', ''))
                from_email = self.decode_str(msg.get('From', ''))
                body = self.get_email_body(msg)

                emails.append((message_id, subject, from_email, body))

            return emails
        except Exception as e:
            logger.error(f"Error getting unread emails: {e}")
            return []
