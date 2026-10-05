"""
test_loop_detector.py - Kiểm thử độc lập bộ phát hiện lặp LoopDetector
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import unittest
from harness.loop_detector import LoopDetector


class TestLoopDetector(unittest.TestCase):
    """Bộ kiểm thử độc lập cho LoopDetector (LOOP & STALL)."""

    def setUp(self):
        self.detector = LoopDetector(loop_threshold=2, stall_threshold=4)

    def test_normal_execution_no_loop(self):
        """Tiến trình bình thường với các tool khác nhau không kích hoạt cảnh báo."""
        self.detector.record("search_flights", {"origin": "SGN", "dest": "DAD"}, progress_key="p1")
        self.detector.record("check_seat", {"flight_id": "VN123", "seat": "12A"}, progress_key="p2")
        self.detector.record("book_seat", {"flight_id": "VN123", "seat": "12A"}, progress_key="p3")

        is_stopped, msg = self.detector.check()
        self.assertFalse(is_stopped)
        self.assertEqual(msg, "")

    def test_detect_loop_consecutive(self):
        """Phát hiện gọi lặp lại cùng tool và cùng tham số 2 lần liên tiếp."""
        self.detector.record("check_seat", {"flight_id": "VN123", "seat": "12A"})
        self.detector.record("check_seat", {"flight_id": "VN123", "seat": "12A"})

        is_loop, msg = self.detector.detect_loop()
        self.assertTrue(is_loop)
        self.assertIn("LOOP", msg)
        self.assertIn("check_seat", msg)

    def test_detect_stall(self):
        """Phát hiện bế tắc STALL: đổi tool liên tục nhưng progress_key không đổi sau 4 bước."""
        self.detector.record("search_flights", {"page": 1}, progress_key="no_ticket")
        self.detector.record("check_seat", {"flight_id": "VN201"}, progress_key="no_ticket")
        self.detector.record("check_seat", {"flight_id": "VN202"}, progress_key="no_ticket")
        self.detector.record("check_seat", {"flight_id": "VN203"}, progress_key="no_ticket")

        is_stall, msg = self.detector.detect_stall()
        self.assertTrue(is_stall)
        self.assertIn("STALL", msg)

    def test_reset(self):
        """Xóa lịch sử thành công."""
        self.detector.record("check_seat", {"flight_id": "VN123"})
        self.detector.record("check_seat", {"flight_id": "VN123"})
        self.assertTrue(self.detector.detect_loop()[0])

        self.detector.reset()
        self.assertFalse(self.detector.detect_loop()[0])


if __name__ == "__main__":
    unittest.main()
