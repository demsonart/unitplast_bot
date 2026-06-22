#!/usr/bin/env python3
"""
UNITPLAST BOT - Flask Server
Entry point for web server (delegates to app/app.py)
"""

import os
from app.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
