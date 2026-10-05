"""
handoff.py - Cấu trúc bàn giao 3 phần cho con người (Handoff)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Handoff:
    """
    Cấu trúc bàn giao 3 phần cho con người:
    1. Trạng thái đã làm tới đâu (status_reached)
    2. Đã thử những gì (attempted_actions)
    3. Câu hỏi cụ thể có thể trả lời trong 30 giây (specific_question)

    Chặn lỗi: Bàn giao mơ hồ khiến người nhận không thể ra quyết định ngay.
    """
    status_reached: str
    attempted_actions: List[str] = field(default_factory=list)
    specific_question: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành từ điển có cấu trúc."""
        return {
            "status_reached": self.status_reached,
            "attempted_actions": self.attempted_actions,
            "specific_question": self.specific_question,
        }

    def format_report(self) -> str:
        """Định dạng báo cáo bàn giao rõ ràng, súc tích cho người duyệt."""
        actions_str = "\n".join([f"   - {act}" for act in self.attempted_actions]) or "   - Không có"
        return (
            "==================== GÓI BÀN GIAO CHO CON NGƯỜI (HANDOFF) ====================\n"
            f"1. Trạng thái hiện tại:\n   {self.status_reached}\n\n"
            f"2. Các bước đã thực hiện/đã thử:\n{actions_str}\n\n"
            f"3. Câu hỏi quyết định (trả lời trong 30 giây):\n   - {self.specific_question}\n"
            "================================================================================"
        )
