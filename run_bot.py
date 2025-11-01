"""
Athena v2 Trading Bot Launcher
Runs the automated trading bot from src/ directory
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the bot
from auto_trader import main

if __name__ == "__main__":
    main()
