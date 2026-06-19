#!/usr/bin/env python3
"""
Unitplast Order Bot - Entry point
Run: python -m unitplast_bot or python __main__.py
"""
import asyncio
from app.main import main

if __name__ == "__main__":
    asyncio.run(main())
