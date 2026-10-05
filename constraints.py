"""
constraints.py - Lớp Ràng buộc là dữ liệu (Constraints) & hàm kiểm hoàn thành is_goal_reached()
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional


@dataclass
class Constraints:
    """
    Ràng buộc là dữ liệu (Data Constraints).
    Lưu origin, dest, date, buoi, tran_gia ở một cấu trúc dữ liệu cố định.
    flight_matches() kiểm tra mọi chuyến bay để ngăn Agent 'quên yêu cầu ban đầu'.
    """
    origin: str = "SGN"
    dest: str = "DAD"
    date: str = "2026-10-15"
    buoi: str = "sang"         # "sang" (morning) hoặc "chieu" (afternoon)
    tran_gia: int = 2_000_000   # Hạn mức giá tối đa người dùng chấp nhận

    def flight_matches(self, flight: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Kiểm tra xem một chuyến bay có thỏa mãn toàn bộ ràng buộc ban đầu hay không.
        Trả về (True, 'OK') hoặc (False, lý do vi phạm).
        """
        if flight.get("origin") != self.origin:
            return False, f"Sai điểm khởi hành: mong đợi {self.origin}, thực tế {flight.get('origin')}"
        if flight.get("dest") != self.dest:
            return False, f"Sai điểm đến: mong đợi {self.dest}, thực tế {flight.get('dest')}"
        if flight.get("date") != self.date:
            return False, f"Sai ngày bay: mong đợi {self.date}, thực tế {flight.get('date')}"
        if flight.get("buoi") != self.buoi:
            return False, f"Sai buổi trong ngày: mong đợi buổi {self.buoi}, thực tế {flight.get('buoi')}"
        if flight.get("price", 0) > self.tran_gia:
            return False, f"Vượt trần giá: {flight.get('price'):,}đ > {self.tran_gia:,}đ"
        return True, "OK"


def is_goal_reached(booking: Optional[Dict[str, Any]], constraints: Constraints) -> bool:
    """
    Tiêu chí hoàn thành kiểm bằng code độc lập hoàn toàn với LLM.
    Kiểm tra:
    - status == 'confirmed'
    - paid == True
    - giá <= trần giá trong constraints
    - đúng buổi yêu cầu
    Chặn lỗi: 'Dừng sớm sai' khi LLM tưởng đã xong nhưng thực tế chưa hoàn tất.
    """
    if not booking:
        return False

    status_ok = booking.get("status") == "confirmed"
    paid_ok = booking.get("paid") is True
    price_ok = booking.get("price", 0) <= constraints.tran_gia
    buoi_ok = booking.get("buoi") == constraints.buoi

    return bool(status_ok and paid_ok and price_ok and buoi_ok)
