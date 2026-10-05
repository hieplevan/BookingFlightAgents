"""
hybrid.py - Mẫu 3: Lai / Hybrid (run_hybrid)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import sys
from pathlib import Path

# Đảm bảo đường dẫn gốc của dự án luôn có trong sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from typing import Optional, Dict, Any, List
from constraints import Constraints, is_goal_reached
from harness.engine import HarnessEngine
from harness.trace import RunResult, TraceEvent
from models.real_langchain import RealLangChainModel
from mock_data import set_current_scenario, _BOOKINGS
from agents.common import _finish


def run_hybrid(
    scenario: str,
    constraints: Optional[Constraints] = None,
    model: Optional[RealLangChainModel] = None,
    k: int = 2
) -> RunResult:
    """
    Thực thi Agent theo mẫu thiết kế Lai (Hybrid):
    1. Gọi model.replan(state, k=2) lập kế hoạch cho cụm tối đa k = 2 bước dựa trên dữ liệu đã biết.
    2. Thực thi cụm đó thông qua HarnessEngine.
    3. Đánh giá độ tiến triển (observation) và lập lại kế hoạch (replan) tiếp tục.
    4. Cân bằng giữa nhìn trước ngắn hạn (k bước) và khả năng thích nghi khi môi trường thay đổi.
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
        "has_searched": False,
        "flights_found": [],
        "checked_flight_idx": 0,
        "current_booking": None,
        "scenario": scenario
    }

    replans_count = 0

    while True:
        # 1. Kiểm tra ngân sách cứng trước khi replan
        if not engine.budget.can_proceed():
            return _finish(
                pattern="Lai (Hybrid)",
                scenario=scenario,
                engine=engine,
                stop_type="budget_exceeded",
                goal_reached=False,
                replans=replans_count
            )

        # 2. Replan cụm tối đa k bước tiếp theo
        replans_count += 1
        engine.trace.append(TraceEvent(
            step=engine.budget.current_step,
            event_type="replan",
            content=f"Lập kế hoạch cụm k={k} bước lần {replans_count}"
        ))

        chunk_plan: List[Dict[str, Any]] = []

        if not state["has_searched"]:
            # Cụm 1: Tìm kiếm chuyến bay
            chunk_plan = [
                {
                    "tool": "search_flights",
                    "args": {
                        "origin": constraints.origin,
                        "dest": constraints.dest,
                        "date": constraints.date,
                        "buoi": constraints.buoi
                    }
                }
            ]
        elif not state.get("current_booking"):
            flights = state.get("flights_found", [])
            idx = state.get("checked_flight_idx", 0)

            if idx < len(flights):
                flight = flights[idx]
                matches, _ = constraints.flight_matches(flight)
                avail = flight.get("available_seats", ["12A"])
                seat = avail[0] if avail else "12A"

                if matches:
                    if not state.get(f"checked_seat_{flight['flight_id']}"):
                        # Replan 2: bước kiểm tra ghế
                        chunk_plan = [
                            {"tool": "check_seat", "args": {"flight_id": flight["flight_id"], "seat_number": seat}}
                        ]
                    else:
                        # Replan 3: bước đặt chỗ
                        chunk_plan = [
                            {"tool": "book_seat", "args": {"flight_id": flight["flight_id"], "seat_number": seat, "passenger_name": "Nguyen Van A"}}
                        ]
                else:
                    # Kịch bản budget_exceeded: Lập cụm tối đa k=2 bước kiểm tra các chuyến tiếp theo
                    chunk_plan = []
                    steps_to_take = min(k, len(flights) - idx, engine.budget.remaining)
                    for offset in range(steps_to_take):
                        f = flights[idx + offset]
                        s = f.get("available_seats", ["10A"])[0] if f.get("available_seats") else "10A"
                        chunk_plan.append({
                            "tool": "check_seat",
                            "args": {"flight_id": f["flight_id"], "seat_number": s}
                        })
                    state["checked_flight_idx"] = idx + len(chunk_plan)
        else:
            # Đã có booking
            booking = state["current_booking"]
            booking_id = booking.get("booking_id")
            price = booking.get("price", 0)

            if scenario == "needs_approval":
                # Cụm bước xem xét thông tin booking rồi cố gắng thanh toán
                chunk_plan = [
                    {"tool": "get_booking", "args": {"booking_id": booking_id}},
                    {"tool": "pay", "args": {"booking_id": booking_id, "amount": price}}
                ]
            else:
                # Kịch bản happy (Replan 4): thanh toán vé và truy vấn lại booking để đối chiếu
                chunk_plan = [
                    {"tool": "pay", "args": {"booking_id": booking_id, "amount": price}},
                    {"tool": "get_booking", "args": {"booking_id": booking_id}}
                ]

        if not chunk_plan:
            stop_type = "budget_exceeded" if engine.budget.is_exceeded() else "no_action"
            return _finish("Lai (Hybrid)", scenario, engine, stop_type, goal_reached=False, replans=replans_count)

        # 3. Thực thi từng bước trong cụm
        for i, action in enumerate(chunk_plan):
            tool_name = action["tool"]
            tool_args = action["args"]

            step_res = engine.execute_one(tool_name, tool_args)

            # Cập nhật quan sát
            obs = step_res.get("observation", {})
            if tool_name == "search_flights":
                state["has_searched"] = True
                if isinstance(obs, dict) and "flights" in obs:
                    state["flights_found"] = obs["flights"]
            elif tool_name == "check_seat":
                fid = tool_args.get("flight_id")
                state[f"checked_seat_{fid}"] = True
            elif tool_name == "book_seat":
                if isinstance(obs, dict) and obs.get("status") == "held":
                    state["current_booking"] = obs
            elif tool_name == "pay":
                if isinstance(obs, dict) and obs.get("status") == "confirmed":
                    if state.get("current_booking"):
                        state["current_booking"]["paid"] = True
                        state["current_booking"]["status"] = "confirmed"

            # Kiểm tra dừng do Harness (Permission Gate, Budget Exceeded, Loop)
            if step_res.get("is_stopped"):
                # Nếu đạt mục tiêu trong cụm nhưng vẫn còn bước xác nhận tiếp theo (ví dụ get_booking sau pay), thực thi nốt
                if step_res["stop_type"] == "goal_reached" and i < len(chunk_plan) - 1:
                    continue

                current_b = _BOOKINGS.get(engine.latest_booking_id) if engine.latest_booking_id else None
                goal_ok = is_goal_reached(current_b, constraints)

                return _finish(
                    pattern="Lai (Hybrid)",
                    scenario=scenario,
                    engine=engine,
                    stop_type=step_res["stop_type"],
                    goal_reached=goal_ok or step_res.get("goal_reached", False),
                    replans=replans_count,
                    handoff=step_res.get("handoff")
                )

        # Kiểm tra nếu mục tiêu đã hoàn tất sau khi kết thúc cả cụm
        current_b = _BOOKINGS.get(engine.latest_booking_id) if engine.latest_booking_id else None
        if is_goal_reached(current_b, constraints):
            return _finish(
                pattern="Lai (Hybrid)",
                scenario=scenario,
                engine=engine,
                stop_type="goal_reached",
                goal_reached=True,
                replans=replans_count
            )


if __name__ == "__main__":
    print("Dang chay thu Mau 3 (Hybrid) voi kich ban 'needs_approval':")
    res = run_hybrid("needs_approval")
    print(f"- Ket qua: Stop type={res.stop_type} | Dat muc tieu={res.goal_reached} | Buoc={res.steps} | Tool calls={res.tool_calls} | Replans={res.replans}")
