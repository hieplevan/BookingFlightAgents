"""
react.py - Mẫu 1: ReAct (run_react)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import sys
from pathlib import Path

# Đảm bảo đường dẫn gốc của dự án luôn có trong sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from typing import Optional, Dict, Any
from constraints import Constraints
from harness.engine import HarnessEngine
from harness.trace import RunResult
from models.real_langchain import RealLangChainModel
from mock_data import set_current_scenario
from agents.common import _finish


def run_react(
    scenario: str,
    constraints: Optional[Constraints] = None,
    model: Optional[RealLangChainModel] = None
) -> RunResult:
    """
    Thực thi Agent theo mẫu thiết kế ReAct (Reasoning + Acting).
    Vòng lặp while True, mỗi bước gọi model.decide_next_step(state) để LLM chọn
    1 tool duy nhất dựa trên trạng thái quan sát mới nhất.
    """
    set_current_scenario(scenario)

    if constraints is None:
        # Nếu kịch bản là needs_approval, người dùng nới trần giá lên 3.000.000đ
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

    while True:
        # 1. LLM quyết định bước tiếp theo dựa trên trạng thái hiện thời
        action = model.decide_next_step(state)

        if not action:
            stop_type = "budget_exceeded" if engine.budget.is_exceeded() else "no_action"
            return _finish("ReAct", scenario, engine, stop_type, goal_reached=False)

        tool_name = action["tool"]
        tool_args = action["args"]

        # 2. Chạy qua HarnessEngine để kiểm soát an toàn và thực thi
        step_res = engine.execute_one(tool_name, tool_args)

        # 3. Cập nhật trạng thái Agent từ observation
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

        # 4. Kiểm tra điều kiện dừng từ Harness
        if step_res.get("is_stopped"):
            return _finish(
                pattern="ReAct",
                scenario=scenario,
                engine=engine,
                stop_type=step_res["stop_type"],
                goal_reached=step_res.get("goal_reached", False),
                replans=0,
                handoff=step_res.get("handoff")
            )


if __name__ == "__main__":
    print("Dang chay thu Mau 1 (ReAct) voi kich ban 'happy':")
    res = run_react("happy")
    print(f"- Ket qua: Stop type={res.stop_type} | Dat muc tieu={res.goal_reached} | Buoc={res.steps} | Tool calls={res.tool_calls}")
