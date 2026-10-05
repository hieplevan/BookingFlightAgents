"""
loop_detector.py - Bộ phát hiện lặp (LOOP) và bế tắc (STALL)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import json
from typing import List, Dict, Any, Tuple, Optional


class LoopDetector:
    """
    Bộ phát hiện lặp (LOOP) và bế tắc (STALL):
    - LOOP: Phát hiện gọi lặp cùng cặp (tool, args).
    - STALL: Phát hiện đổi tool liên tục nhưng đại lượng tiến triển (progress) đứng yên.
    """

    def __init__(self, loop_threshold: int = 2, stall_threshold: int = 4):
        self.loop_threshold = loop_threshold
        self.stall_threshold = stall_threshold
        self.history: List[Dict[str, Any]] = []

    def record(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        observation: Optional[Any] = None,
        progress_key: Optional[str] = None
    ) -> None:
        """Ghi nhận một lượt gọi tool và kết quả quan sát."""
        args_str = json.dumps(tool_args, sort_keys=True, ensure_ascii=False)
        self.history.append({
            "tool_name": tool_name,
            "tool_args": tool_args,
            "args_hash": f"{tool_name}:{args_str}",
            "observation": observation,
            "progress_key": progress_key
        })

    def detect_loop(self) -> Tuple[bool, str]:
        """
        Phát hiện gọi lặp lại cùng tool và cùng bộ tham số.
        Nếu cùng 1 lệnh xuất hiện >= loop_threshold lần liên tiếp hoặc lặp nhiều lần trong lịch sử gần.
        """
        if len(self.history) < self.loop_threshold:
            return False, ""

        recent = self.history[-self.loop_threshold:]
        first_hash = recent[0]["args_hash"]
        if all(item["args_hash"] == first_hash for item in recent):
            return True, f"LOOP: Gọi lặp lại '{recent[0]['tool_name']}' với cùng tham số {self.loop_threshold} lần liên tiếp."

        # Kiểm tra tổng số lần gọi cùng (tool, args) trong 6 bước gần nhất
        last_item = self.history[-1]
        count = sum(1 for item in self.history[-6:] if item["args_hash"] == last_item["args_hash"])
        if count >= 3:
            return True, f"LOOP: Gọi lại lệnh '{last_item['tool_name']}' {count} lần trong các bước gần đây."

        return False, ""

    def detect_stall(self) -> Tuple[bool, str]:
        """
        Phát hiện bế tắc (STALL): Agent liên tục đổi tool nhưng trạng thái tiến triển
        (ví dụ: tìm thấy chuyến bay, chọn ghế, tạo booking) không hề thay đổi sau stall_threshold bước.
        """
        if len(self.history) < self.stall_threshold:
            return False, ""

        recent = self.history[-self.stall_threshold:]
        # Kiểm tra nếu progress_key không đổi trong suốt window
        progress_keys = [item.get("progress_key") for item in recent]
        if all(k is not None and k == progress_keys[0] for k in progress_keys):
            return True, f"STALL: Đổi tool liên tục nhưng tiến trình '{progress_keys[0]}' không thay đổi sau {self.stall_threshold} bước."

        return False, ""

    def check(self) -> Tuple[bool, str]:
        """Kiểm tra tổng hợp cả LOOP và STALL."""
        is_loop, msg = self.detect_loop()
        if is_loop:
            return True, msg
        is_stall, msg = self.detect_stall()
        if is_stall:
            return True, msg
        return False, ""

    def reset(self) -> None:
        """Xóa lịch sử kiểm tra."""
        self.history.clear()
