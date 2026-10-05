"""
plan_execute.py - Mẫu 2: Plan-then-Execute (run_plan_then_execute)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import sys
from pathlib import Path

# Đảm bảo đường dẫn gốc của dự án luôn có trong sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from typing import Optional, Dict, Any, List
from constraints import Constraints
from harness.engine import HarnessEngine
from harness.trace import RunResult, TraceEvent
from models.real_langchain import RealLangChainModel
from mock_data import set_current_scenario
from agents.common import _finish


def run_plan_then_execute(
    scenario: str,
    constraints: Optional[Constraints] = None,
    model: Optional[RealLangChainModel] = None
) -> RunResult:
    """
    Thực thi Agent theo mẫu thiết kế Plan-then-Execute:
    1. Gọi model.make_plan(state) sinh trọn gói 5 bước ngay từ đầu (dùng placeholder GUESS_FIRST, GUESS).
    2. Chạy tuần tự từng bước và KHÔNG lập lại kế hoạch.
    3. Nếu giả định bước đầu sai (ví dụ chuyến bay vượt ngân sách hoặc hết ghế), kế hoạch bị hủy (plan_invalidated) ngay lập tức.
    """
    set_current_scenario(scenario)

    if constraints is None:
        tran_gia = 3_000_000 if scenario == "needs_approval" else 2_000_000
        constraints = Constraints(
            origin="SGN",
            dest="DAD",
            date="2026-10-15",
            buoi="sang",
            tran_gia=tran_gia
        )

    if model is None:
        model = RealLangChainModel()

    engine = HarnessEngine(constraints=constraints)
    state: Dict[str, Any] = {
        "constraints": constraints,
        "scenario": scenario
    }

    # Sinh kế hoạch tĩnh trọn gói 5 bước ban đầu
    plan: List[Dict[str, Any]] = model.make_plan(state)

    first_flight_data: Optional[Dict[str, Any]] = None
    first_flight_id: Optional[str] = None
    first_seat_number = "12A"
    current_booking_id: Optional[str] = None
    current_price: Optional[int] = None

    for item in plan:
        tool_name = item["tool"]
        raw_args = dict(item["args"])

        # Thay thế placeholder GUESS_FIRST và GUESS bằng thông tin tương ứng
        if tool_name in ["check_seat", "book_seat"]:
            if raw_args.get("flight_id") == "GUESS_FIRST":
                raw_args["flight_id"] = first_flight_id or "VN123"
            raw_args["seat_number"] = first_seat_number

        elif tool_name in ["pay", "get_booking"]:
            if raw_args.get("booking_id") == "GUESS":
                raw_args["booking_id"] = current_booking_id
            if raw_args.get("amount") == "GUESS":
                raw_args["amount"] = current_price or 0

        # Thực thi bước qua HarnessEngine
        step_res = engine.execute_one(tool_name, raw_args)

        # Kiểm tra nếu bị chặn dừng từ Harness (ví dụ Permission Gate chặn pay trong needs_approval)
        if step_res.get("is_stopped"):
            return _finish(
                pattern="Plan-then-Execute",
                scenario=scenario,
                engine=engine,
                stop_type=step_res["stop_type"],
                goal_reached=step_res.get("goal_reached", False),
                replans=0,
                handoff=step_res.get("handoff")
            )

        obs = step_res.get("observation", {})

        # Xử lý sau bước 1: search_flights
        if tool_name == "search_flights":
            flights = obs.get("flights", []) if isinstance(obs, dict) else []
            if not flights:
                return _finish("Plan-then-Execute", scenario, engine, "plan_invalidated", goal_reached=False)
            
            # Gán chuyến bay đầu tiên vào kế hoạch tĩnh (giả định chuyến 0)
            first_flight_data = flights[0]
            first_flight_id = first_flight_data["flight_id"]
            avail = first_flight_data.get("available_seats", [])
            first_seat_number = avail[0] if avail else "12A"

        # Xử lý sau bước 2: check_seat
        elif tool_name == "check_seat":
            # Kiểm tra xem chuyến bay đầu tiên được chọn có thực sự thỏa mãn ràng buộc không
            # Trong Plan-then-Execute: nếu chuyến bay vượt trần giá -> vỡ kế hoạch (plan_invalidated)!
            flight_price = first_flight_data.get("price", 0) if first_flight_data else obs.get("price", 0)
            
            if flight_price > constraints.tran_gia or obs.get("status") == "unavailable":
                # Kế hoạch tĩnh vỡ do giả định ban đầu sai ("Lỗi ở bước đầu làm hỏng toàn bộ các bước sau")
                engine.trace.append(TraceEvent(
                    step=engine.budget.current_step,
                    event_type="stop",
                    content=(
                        f"Kế hoạch bị hủy (plan_invalidated): Chuyến bay được chọn {first_flight_id} "
                        f"có giá {flight_price:,}đ vượt trần {constraints.tran_gia:,}đ. "
                        f"Plan-then-Execute không có khả năng tự thích nghi đổi chuyến khác."
                    )
                ))
                return _finish(
                    pattern="Plan-then-Execute",
                    scenario=scenario,
                    engine=engine,
                    stop_type="plan_invalidated",
                    goal_reached=False,
                    replans=0
                )

        # Xử lý sau bước 3: book_seat
        elif tool_name == "book_seat":
            if isinstance(obs, dict) and obs.get("status") == "held":
                current_booking_id = obs.get("booking_id")
                current_price = obs.get("price")
            else:
                return _finish("Plan-then-Execute", scenario, engine, "plan_invalidated", goal_reached=False)

    return _finish("Plan-then-Execute", scenario, engine, "plan_completed", goal_reached=False)


if __name__ == "__main__":
    print("Dang chay thu Mau 2 (Plan-then-Execute) voi kich ban 'budget_exceeded':")
    res = run_plan_then_execute("budget_exceeded")
    print(f"- Ket qua: Stop type={res.stop_type} | Dat muc tieu={res.goal_reached} | Buoc={res.steps} | Tool calls={res.tool_calls}")
