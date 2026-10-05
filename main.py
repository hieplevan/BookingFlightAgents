"""
main.py - Điểm khởi chạy chính của chương trình BTVN#3
Môn: SE373 – Agentic AI Engineering · Buổi: 03
Đề bài: Dựng Agent Đặt Vé Máy Bay Bằng LangChain (SGN -> DAD)
"""

import sys
import unittest
from evaluation import run_full_evaluation, print_evaluation_report
from agents.react import run_react
from agents.plan_execute import run_plan_then_execute
from agents.hybrid import run_hybrid
from harness.trace import RunResult


def run_tests() -> bool:
    """Chạy kiểm thử độc lập cho LoopDetector."""
    print("=" * 80)
    print("[1/3] KIEM THU DOC LAP BO PHAT HIEN LAP (LOOP DETECTOR)")
    print("=" * 80)
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def print_trace_details(res: RunResult) -> None:
    """In chi tiết từng bước thực thi (call, observation, stop) để Agent Debugging."""
    print("\n" + "-" * 80)
    print(f"CHI TIET TRUY VET (TRACE): {res.pattern} | Kich ban: {res.scenario}")
    print(f"Trang thai ket thuc: {res.stop_type} | So buoc: {res.steps} | Tokens: {res.estimated_tokens:,}")
    print("-" * 80)

    for event in res.trace:
        step_str = f"Buoc {event.step}" if event.step > 0 else "Khoi tao"
        if event.event_type == "call":
            print(f"\n[{step_str} - GOI TOOL]: {event.tool_name}")
            print(f"   Tham so: {event.tool_args}")
        elif event.event_type == "observation":
            print(f"[{step_str} - QUAN SAT (OBSERVATION)]:")
            content = event.content
            if isinstance(content, dict):
                status = content.get("status")
                print(f"   Trang thai tra ve: status = '{status}'")
                if "flights" in content:
                    print(f"   So chuyen tim thay: {len(content['flights'])} chuyen")
                elif "price" in content:
                    print(f"   Gia: {content.get('price'):,}d | Hoan ve: {content.get('refundable')}")
                elif "message" in content:
                    print(f"   Thong bao: {content['message']}")
            else:
                print(f"   Du lieu: {content}")
        elif event.event_type == "permission_blocked":
            print(f"\n[{step_str} - BI CHAN BOI PERMISSION GATE]:")
            print(f"   Lenh bi chan: {event.tool_name}({event.tool_args})")
            print(f"   Ly do chan: {event.content}")
        elif event.event_type == "replan":
            print(f"\n[{step_str} - REPLAN]: {event.content}")
        elif event.event_type == "stop":
            print(f"\n[DUNG TIEN TRINH - STOP]:")
            print(f"   Ly do: {event.content}")

    if res.handoff:
        print("\n" + res.handoff.format_report())


def show_detailed_case_traces() -> None:
    """Hiển thị chi tiết vết từng bước trực tiếp cho các trường hợp điển hình."""
    print("\n" + "=" * 80)
    print("[2/3] CHI TIET TRUY VET TUNG BUOC (TRACE) CUA CAC CASE DIEN HINH")
    print("=" * 80)

    # 1. Case vỡ kế hoạch (plan_invalidated)
    print("\n" + "#" * 80)
    print("CASE A: Plan-then-Execute gap 'budget_exceeded' -> Vo ke hoach tai buoc 2 (plan_invalidated)")
    print("#" * 80)
    res_plan = run_plan_then_execute("budget_exceeded")
    print_trace_details(res_plan)

    # 2. Case bị chặn quyền và bàn giao 3 phần (needs_approval)
    print("\n" + "#" * 80)
    print("CASE B: Kich ban 'needs_approval' -> Cong kiem quyen chan truoc khi pay, tao goi Handoff 3 phan")
    print("#" * 80)
    res_perm = run_react("needs_approval")
    print_trace_details(res_perm)

    # 3. Case chạm trần ngân sách 12 bước (budget_exceeded)
    print("\n" + "#" * 80)
    print("CASE C: ReAct gap 'budget_exceeded' -> Kiem tra den het ngan sach cung 12 buoc (budget_exceeded)")
    print("#" * 80)
    res_budget = run_react("budget_exceeded")
    print_trace_details(res_budget)


def main():
    print("""
================================================================================
          BTVN#3: DUNG AGENT DAT VE MAY BAY BANG LANGCHAIN
          Mon hoc: SE373 – Agentic AI Engineering · Buoi: 03
          Tuyen bay: SGN -> DAD | Han muc chinh sach: 2.000.000d
================================================================================
""")

    # 1. Chạy unit tests độc lập cho LoopDetector
    test_ok = run_tests()
    if not test_ok:
        print("[ERROR] Kiem thu that bai!")
        sys.exit(1)

    # 2. Hiển thị trực tiếp chi tiết vết từng bước của các case (vỡ kế hoạch, chặn quyền handoff, trần ngân sách)
    show_detailed_case_traces()

    # 3. Chạy đánh giá ma trận 3 mẫu × 3 kịch bản và in bảng tổng hợp
    print("\n" + "=" * 80)
    print("[3/3] DANH GIA MA TRAN 3 MAU THIET KE × 3 KICH BAN THUC NGHIEM")
    print("=" * 80)
    results = run_full_evaluation()
    print_evaluation_report(results)

    print("CHUONG TRINH HOAN THANH!")


if __name__ == "__main__":
    main()
