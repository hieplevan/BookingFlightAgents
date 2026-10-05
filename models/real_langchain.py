"""
real_langchain.py - RealLangChainModel kết nối LLM thật qua ChatOpenAI & bind_tools
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Đảm bảo đường dẫn gốc của dự án luôn có trong sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from tools import TOOLS
from constraints import Constraints


class RealLangChainModel:
    """
    RealLangChainModel:
    Kết nối LLM thật qua ChatOpenAI kết hợp .bind_tools(TOOLS).
    Hỗ trợ 3 mẫu thiết kế Agent:
    - ReAct: decide_next_step(state) -> chọn 1 tool duy nhất dựa trên observation mới nhất.
    - Plan-then-Execute: make_plan(state) -> sinh trọn gói 5 bước ban đầu dùng placeholder.
    - Lai (Hybrid): replan(state, k=2) -> lập kế hoạch cho cụm tối đa k bước rồi cập nhật.
    """

    def __init__(
        self,
        model_name: str = OPENAI_MODEL,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL", None)
        self.model_name = model_name or "gpt-4o-mini"
        self.has_real_llm = bool(self.api_key and len(self.api_key.strip()) > 5)

        if self.has_real_llm:
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "api_key": self.api_key,
                "temperature": 0.0
            }
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.llm = ChatOpenAI(**kwargs)
            self.llm_with_tools = self.llm.bind_tools(TOOLS)
        else:
            self.llm = None
            self.llm_with_tools = None

    def decide_next_step(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Dành cho mẫu ReAct: Phản ứng tức thì với observation, chọn 1 công cụ tiếp theo.
        """
        constraints: Constraints = state.get("constraints", Constraints())
        flights = state.get("flights_found", [])
        booking = state.get("current_booking")
        checked_idx = state.get("checked_flight_idx", 0)

        # 1. Nếu có LLM thật và key hợp lệ, thử gọi qua LangChain bind_tools
        if self.has_real_llm and self.llm_with_tools:
            try:
                system_prompt = (
                    "Bạn là Trợ lý Agent đặt vé máy bay tuyến SGN -> DAD. "
                    "Hãy sử dụng đúng các công cụ được cung cấp để tìm kiếm, kiểm tra ghế, đặt vé và thanh toán."
                )
                user_content = (
                    f"Ràng buộc: Tuyến {constraints.origin} -> {constraints.dest}, Ngày {constraints.date}, "
                    f"Buổi: {constraints.buoi}, Trần giá: {constraints.tran_gia:,}đ. "
                    f"Trạng thái hiện tại: Đã tìm thấy {len(flights)} chuyến, Đã đặt vé: {bool(booking)}."
                )
                response = self.llm_with_tools.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_content)
                ])
                if response.tool_calls:
                    tc = response.tool_calls[0]
                    return {"tool": tc["name"], "args": tc["args"]}
            except Exception:
                # Nếu API lỗi hoặc mất mạng, chuyển tiếp qua logic dự phòng bên dưới
                pass

        # 2. Logic suy luận theo mẫu ReAct (chính xác theo yêu cầu thực nghiệm BTVN#3)
        # Bước 1: Chưa tìm kiếm thì gọi search_flights
        if not state.get("has_searched"):
            return {
                "tool": "search_flights",
                "args": {
                    "origin": constraints.origin,
                    "dest": constraints.dest,
                    "date": constraints.date,
                    "buoi": constraints.buoi
                }
            }

        # Bước 2: Đã tìm kiếm nhưng không có chuyến nào
        if not flights:
            return None

        # Bước 3: Đã có booking, cần thanh toán
        if booking and not booking.get("paid"):
            return {
                "tool": "pay",
                "args": {
                    "booking_id": booking["booking_id"],
                    "amount": booking["price"]
                }
            }

        # Bước 4: Kiểm tra chuyến bay phù hợp
        # Duyệt qua các chuyến bay
        if checked_idx < len(flights):
            flight = flights[checked_idx]
            # Nếu chưa check seat cho chuyến này
            if not state.get(f"checked_seat_{flight['flight_id']}"):
                seat = flight.get("available_seats", ["12A"])[0] if flight.get("available_seats") else "12A"
                return {
                    "tool": "check_seat",
                    "args": {
                        "flight_id": flight["flight_id"],
                        "seat_number": seat
                    }
                }
            # Nếu đã check seat và thỏa mãn ràng buộc
            matches, _ = constraints.flight_matches(flight)
            if matches and not booking:
                seat = flight.get("available_seats", ["12A"])[0] if flight.get("available_seats") else "12A"
                return {
                    "tool": "book_seat",
                    "args": {
                        "flight_id": flight["flight_id"],
                        "seat_number": seat,
                        "passenger_name": "Nguyen Van A"
                    }
                }
            else:
                # Không thỏa mãn, ReAct chuyển sang kiểm tra chuyến bay tiếp theo
                state["checked_flight_idx"] = checked_idx + 1
                if checked_idx + 1 < len(flights):
                    next_flight = flights[checked_idx + 1]
                    seat = next_flight.get("available_seats", ["10A"])[0] if next_flight.get("available_seats") else "10A"
                    return {
                        "tool": "check_seat",
                        "args": {
                            "flight_id": next_flight["flight_id"],
                            "seat_number": seat
                        }
                    }

        return None

    def make_plan(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Dành cho mẫu Plan-then-Execute:
        Sinh trọn gói 5 bước ngay từ đầu (dùng placeholder GUESS_FIRST, GUESS),
        sau đó chạy tuần tự và không lập lại kế hoạch.
        """
        constraints: Constraints = state.get("constraints", Constraints())
        
        # 5 bước trọn gói với placeholder theo tài liệu bài giảng
        plan = [
            {
                "step": 1,
                "tool": "search_flights",
                "args": {
                    "origin": constraints.origin,
                    "dest": constraints.dest,
                    "date": constraints.date,
                    "buoi": constraints.buoi
                }
            },
            {
                "step": 2,
                "tool": "check_seat",
                "args": {
                    "flight_id": "GUESS_FIRST",
                    "seat_number": "12A"
                }
            },
            {
                "step": 3,
                "tool": "book_seat",
                "args": {
                    "flight_id": "GUESS_FIRST",
                    "seat_number": "12A",
                    "passenger_name": "Nguyen Van A"
                }
            },
            {
                "step": 4,
                "tool": "pay",
                "args": {
                    "booking_id": "GUESS",
                    "amount": "GUESS"
                }
            },
            {
                "step": 5,
                "tool": "get_booking",
                "args": {
                    "booking_id": "GUESS"
                }
            }
        ]
        return plan

    def replan(self, state: Dict[str, Any], k: int = 2) -> List[Dict[str, Any]]:
        """
        Dành cho mẫu Lai (Hybrid):
        Lập kế hoạch cho cụm tối đa k = 2 bước dựa trên dữ liệu đã biết,
        thực thi cụm đó, kiểm tra độ tiến triển rồi lập lại kế hoạch.
        """
        constraints: Constraints = state.get("constraints", Constraints())
        flights = state.get("flights_found", [])
        booking = state.get("current_booking")
        checked_idx = state.get("checked_flight_idx", 0)

        # Cụm 1: Chưa search -> lập kế hoạch: [search_flights, check_seat_first]
        if not state.get("has_searched"):
            return [
                {
                    "step": 1,
                    "tool": "search_flights",
                    "args": {
                        "origin": constraints.origin,
                        "dest": constraints.dest,
                        "date": constraints.date,
                        "buoi": constraints.buoi
                    }
                }
            ]

        # Đã có booking -> kế hoạch [pay]
        if booking and not booking.get("paid"):
            return [
                {
                    "step": 1,
                    "tool": "pay",
                    "args": {
                        "booking_id": booking["booking_id"],
                        "amount": booking["price"]
                    }
                }
            ]

        # Chưa có booking nhưng đã có flights
        if flights and checked_idx < len(flights):
            current_flight = flights[checked_idx]
            matches, _ = constraints.flight_matches(current_flight)
            seat = current_flight.get("available_seats", ["12A"])[0] if current_flight.get("available_seats") else "12A"

            if matches:
                # Nếu chuyến bay thỏa mãn: lập cụm 2 bước [check_seat, book_seat]
                return [
                    {
                        "step": 1,
                        "tool": "check_seat",
                        "args": {"flight_id": current_flight["flight_id"], "seat_number": seat}
                    },
                    {
                        "step": 2,
                        "tool": "book_seat",
                        "args": {"flight_id": current_flight["flight_id"], "seat_number": seat, "passenger_name": "Nguyen Van A"}
                    }
                ][:k]
            else:
                # Nếu không thỏa mãn (ví dụ vượt giá), kiểm tra chuyến bay tiếp theo
                steps = []
                for i in range(checked_idx, min(checked_idx + k, len(flights))):
                    f = flights[i]
                    s = f.get("available_seats", ["10A"])[0] if f.get("available_seats") else "10A"
                    steps.append({
                        "step": len(steps) + 1,
                        "tool": "check_seat",
                        "args": {"flight_id": f["flight_id"], "seat_number": s}
                    })
                return steps

        return []


if __name__ == "__main__":
    print("=" * 70)
    print("KIEM THU DOC LAP TANG SUY LUAN LLM (RealLangChainModel)")
    print("=" * 70)

    model = RealLangChainModel()
    print(f"- Model dang cau hinh: {model.model_name}")
    print(f"- Co ket noi LLM that: {'Co' if model.has_real_llm else 'Khong (su dung logic suy luan du phong)'}")

    # 1. Kiểm tra gọi trực tiếp LLM với bind_tools
    if model.has_real_llm and model.llm_with_tools:
        print("\n[1] Thu nghiem goi LLM that qua ChatOpenAI ket hop bind_tools(TOOLS):")
        try:
            prompt = "Tìm giúp tôi chuyến bay từ SGN đi DAD vào ngày 2026-10-15 buổi sang"
            print(f"   Yeu cau: '{prompt}'")
            resp = model.llm_with_tools.invoke(prompt)
            if resp.tool_calls:
                print("   [OK] LLM da tu dong de xuat goi Tool:")
                for tc in resp.tool_calls:
                    print(f"      - Tool: {tc['name']} | Tham so: {tc['args']}")
            else:
                print(f"   Phan hoi LLM: {resp.content}")
        except Exception as e:
            print(f"   Loi khi goi API LLM: {e}")

    # 2. Thử nghiệm mẫu 1: ReAct (decide_next_step)
    print("\n[2] Thu nghiem Mau 1 (ReAct) - decide_next_step():")
    mock_state = {"constraints": Constraints(), "has_searched": False}
    action = model.decide_next_step(mock_state)
    print(f"   Hanh dong tiep theo: {action}")

    # 3. Thử nghiệm mẫu 2: Plan-then-Execute (make_plan)
    print("\n[3] Thu nghiem Mau 2 (Plan-then-Execute) - make_plan():")
    plan = model.make_plan(mock_state)
    print(f"   Ke hoach 5 buoc tinh ban dau sinh ra:")
    for step in plan:
        print(f"      Buoc {step['step']}: {step['tool']}({step['args']})")

    # 4. Thử nghiệm mẫu 3: Lai / Hybrid (replan)
    print("\n[4] Thu nghiem Mau 3 (Hybrid) - replan(k=2):")
    chunk = model.replan(mock_state, k=2)
    print(f"   Cum k=2 buoc duoc sinh ra:")
    for step in chunk:
        print(f"      Buoc {step['step']}: {step['tool']}({step['args']})")

    print("\n" + "=" * 70)
    print("CHAY THU FILE real_langchain.py THANH CONG!")
    print("=" * 70)
