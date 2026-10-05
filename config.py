"""
config.py - Cấu hình tuyến bay hỗ trợ & hạn mức chính sách
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Tuyến bay được hỗ trợ
SUPPORTED_ORIGIN = "SGN"
SUPPORTED_DEST = "DAD"
DEFAULT_DATE = "2026-10-15"

# Hạn mức chính sách công ty (Permission Gate)
# Mọi giao dịch vé có giá > APPROVAL_PRICE_LIMIT và không hoàn được sẽ bị chặn trước khi pay
APPROVAL_PRICE_LIMIT = 2_000_000  # 2.000.000 VNĐ

# Ngân sách số bước tối đa của Harness
DEFAULT_MAX_STEPS = 12

# Cấu hình LLM từ biến môi trường
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
