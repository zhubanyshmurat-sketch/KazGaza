import os
import sys
from pathlib import Path

os.environ.setdefault("BOT_TOKEN", "123456:test-token")
os.environ.setdefault("BOT_INTERNAL_TOKEN", "test-bot-secret")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
