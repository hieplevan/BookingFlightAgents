"""
permission.py - Cổng kiểm quyền (Permission Gate) trước khi thanh toán
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

from typing import Tuple, Dict, Any, Optional
from config import APPROVAL_PRICE_LIMIT
from mock_data import _BOOKINGS


def check_permission(
    tool_name: str,
    tool_args: Dict[str, Any],
    booking_info: Optional[Dict[str, Any]] = None,
    price_limit: int = APPROVAL_PRICE_LIMIT
) -> Tuple[bool, str]:
    """
    Cổng kiểm quyền (Permission Gate).
    Chạy trước khi thực thi tool pay:
    Chặn lại nếu giá vé > hạn mức công ty (2.000.000đ) và vé không hoàn được.
    Chặn lỗi: Agent tự ý thanh toán các giao dịch vượt thẩm quyền.
    """
    if tool_name != "pay":
        return True, "Hành động không yêu cầu kiểm quyền hạn mức thanh toán."

    # Lấy thông tin booking
    booking_id = tool_args.get("booking_id")
    booking = booking_info or _BOOKINGS.get(booking_id)

    if not booking:
        # Nếu chưa tìm thấy booking, tạm cho qua để tool tự báo lỗi hoặc kiểm tra amount
        amount = tool_args.get("amount", 0)
        if amount > price_limit:
            return False, f"Chặn quyền: Số tiền yêu cầu thanh toán {amount:,}đ vượt hạn mức chính sách công ty {price_limit:,}đ."
        return True, "OK"

    price = booking.get("price", 0)
    refundable = booking.get("refundable", True)

    # Quy tắc kiểm quyền: Giá > 2.000.000đ VÀ không hoàn được
    if price > price_limit and not refundable:
        return False, (
            f"Chặn quyền: Giá vé {price:,}đ vượt hạn mức chính sách công ty ({price_limit:,}đ) "
            f"và vé không được hoàn hủy (refundable=False). Cần con người phê duyệt."
        )

    return True, "OK"
