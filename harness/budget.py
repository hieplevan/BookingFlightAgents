"""
budget.py - Ngân sách cứng (Budget: max_steps=12)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""


class Budget:
    """
    Ngân sách cứng (Hard Budget) cho Agent.
    Giới hạn max_steps=12, chặn tình trạng chạy tràn lan tốn chi phí.
    """
    def __init__(self, max_steps: int = 12):
        self.max_steps = max_steps
        self.current_step = 0

    def can_proceed(self) -> bool:
        """Kiểm tra xem ngân sách còn cho phép thực thi bước tiếp theo không."""
        return self.current_step < self.max_steps

    def consume_step(self) -> int:
        """Tiêu thụ 1 bước và trả về số bước hiện tại."""
        self.current_step += 1
        return self.current_step

    def is_exceeded(self) -> bool:
        """Kiểm tra ngân sách đã bị vượt quá hay chưa."""
        return self.current_step >= self.max_steps

    @property
    def remaining(self) -> int:
        """Số bước còn lại."""
        return max(0, self.max_steps - self.current_step)

    def reset(self) -> None:
        """Đặt lại ngân sách về 0."""
        self.current_step = 0
