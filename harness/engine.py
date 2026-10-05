"""
engine.py - Bộ máy thực thi trung tâm (HarnessEngine.execute_one)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import json
from typing import Dict, Any, Tuple, Optional, List
from config import DEFAULT_MAX_STEPS, APPROVAL_PRICE_LIMIT
from constraints import Constraints, is_goal_reached
from tools import TOOL_MAP
from harness.budget import Budget
from harness.loop_detector import LoopDetector
from harness.permission import check_permission
from harness.handoff import Handoff
from harness.trace import TraceEvent
from mock_data import _BOOKINGS


class HarnessEngine:
    """
    Bộ máy thực thi trung tâm của Harness:
    - Kiểm soát ngân sách cứng (Budget).
    - Cổng kiểm quyền (Permission Gate).
    - Phát hiện lặp/bế tắc (LoopDetector).
    - Xác thực tiêu chí hoàn thành bằng code (is_goal_reached).
    - Ghi vết toàn bộ hành trình (TraceEvent).
    - Tạo gói bàn giao (Handoff) khi cần con người can thiệp.
    """

    def __init__(self, constraints: Constraints, max_steps: int = DEFAULT_MAX_STEPS):
        self.constraints = constraints
        self.budget = Budget(max_steps=max_steps)
        self.loop_detector = LoopDetector()
        self.trace: List[TraceEvent] = []
        self.attempted_actions: List[str] = []
        self.tool_calls_count = 0
        self.latest_booking_id: Optional[str] = None

    def execute_one(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Thực thi một bước công cụ dưới sự giám sát nghiêm ngặt của Harness.
        Trả về kết quả có cấu trúc gồm: status, observation, stop_type, handoff, is_stopped.
        """
        # 1. Kiểm tra ngân sách cứng trước khi thực thi
        if not self.budget.can_proceed():
            self.trace.append(TraceEvent(
                step=self.budget.current_step,
                event_type="stop",
                tool_name=tool_name,
                content="Ngân sách bước chạy đã hết (max_steps reached)"
            ))
            return {
                "status": "stopped",
                "stop_type": "budget_exceeded",
                "is_stopped": True,
                "message": f"Dừng do vượt ngân sách tối đa ({self.budget.max_steps} bước)."
            }

        # 2. Cổng kiểm quyền (Permission Gate) - Đặc biệt trước khi gọi pay
        booking_info = _BOOKINGS.get(tool_args.get("booking_id") or self.latest_booking_id)
        is_permitted, perm_reason = check_permission(tool_name, tool_args, booking_info)
        
        if not is_permitted:
            # Chặn lại và tạo gói Handoff 3 phần
            ticket_price = booking_info.get("price", 0) if booking_info else tool_args.get("amount", 0)
            flight_id = booking_info.get("flight_id", "N/A") if booking_info else "N/A"
            
            handoff = Handoff(
                status_reached=(
                    f"Đã chọn và giữ chỗ vé chuyến bay {flight_id} thành công với mã "
                    f"'{tool_args.get('booking_id', self.latest_booking_id)}', chuẩn bị thanh toán."
                ),
                attempted_actions=list(self.attempted_actions),
                specific_question=(
                    f"Vé chuyến bay {flight_id} có giá {ticket_price:,}đ (vượt hạn mức chính sách công ty "
                    f"{APPROVAL_PRICE_LIMIT:,}đ và không hoàn vé được). Bạn có đồng ý phê duyệt thanh toán không?"
                )
            )

            self.trace.append(TraceEvent(
                step=self.budget.current_step + 1,
                event_type="permission_blocked",
                tool_name=tool_name,
                tool_args=tool_args,
                content=perm_reason
            ))

            return {
                "status": "blocked",
                "stop_type": "needs_approval",
                "is_stopped": True,
                "handoff": handoff,
                "message": perm_reason
            }

        # 3. Bộ phát hiện lặp (LoopDetector) trước khi gọi
        is_loop, loop_msg = self.loop_detector.detect_loop()
        if is_loop:
            self.trace.append(TraceEvent(
                step=self.budget.current_step + 1,
                event_type="stop",
                tool_name=tool_name,
                tool_args=tool_args,
                content=loop_msg
            ))
            return {
                "status": "stopped",
                "stop_type": "loop_detected",
                "is_stopped": True,
                "message": loop_msg
            }

        # 4. Tiêu thụ 1 bước ngân sách & ghi nhận gọi tool
        step_num = self.budget.consume_step()
        self.tool_calls_count += 1
        self.trace.append(TraceEvent(
            step=step_num,
            event_type="call",
            tool_name=tool_name,
            tool_args=tool_args
        ))
        self.attempted_actions.append(f"Bước {step_num}: Gọi {tool_name}({tool_args})")

        # 5. Thực thi công cụ thực tế
        tool_func = TOOL_MAP.get(tool_name)
        if not tool_func:
            observation_raw = json.dumps({"status": "error", "message": f"Công cụ {tool_name} không tồn tại."})
        else:
            try:
                observation_raw = tool_func.invoke(tool_args)
            except Exception as e:
                observation_raw = json.dumps({"status": "error", "message": str(e)})

        # Parse observation
        try:
            observation_data = json.loads(observation_raw) if isinstance(observation_raw, str) else observation_raw
        except Exception:
            observation_data = {"raw": observation_raw}

        # Lưu lại booking id nếu có
        if isinstance(observation_data, dict):
            if "booking_id" in observation_data:
                self.latest_booking_id = observation_data["booking_id"]
            elif "booking" in observation_data and isinstance(observation_data["booking"], dict):
                self.latest_booking_id = observation_data["booking"].get("booking_id")

        # 6. Ghi nhận observation vào trace và loop detector
        self.trace.append(TraceEvent(
            step=step_num,
            event_type="observation",
            tool_name=tool_name,
            content=observation_data
        ))
        
        # Đánh giá khóa tiến trình để phát hiện STALL
        progress_key = f"booked:{self.latest_booking_id}" if self.latest_booking_id else f"step:{tool_name}"
        self.loop_detector.record(tool_name, tool_args, observation_data, progress_key=progress_key)

        # 7. Kiểm tra tiêu chí hoàn thành bằng code (is_goal_reached)
        current_booking = _BOOKINGS.get(self.latest_booking_id) if self.latest_booking_id else None
        goal_done = is_goal_reached(current_booking, self.constraints)

        if goal_done:
            self.trace.append(TraceEvent(
                step=step_num,
                event_type="stop",
                content="Mục tiêu đặt vé đã hoàn thành thành công theo tiêu chí kiểm bằng code."
            ))
            return {
                "status": "success",
                "stop_type": "goal_reached",
                "is_stopped": True,
                "goal_reached": True,
                "observation": observation_data,
                "booking": current_booking
            }

        # 8. Kiểm tra lại ngân sách sau khi thực thi bước
        if self.budget.is_exceeded():
            self.trace.append(TraceEvent(
                step=step_num,
                event_type="stop",
                content="Chạm trần ngân sách cứng (12 bước)."
            ))
            return {
                "status": "stopped",
                "stop_type": "budget_exceeded",
                "is_stopped": True,
                "goal_reached": False,
                "observation": observation_data,
                "booking": current_booking
            }

        return {
            "status": "running",
            "stop_type": None,
            "is_stopped": False,
            "goal_reached": False,
            "observation": observation_data,
            "booking": current_booking
        }
