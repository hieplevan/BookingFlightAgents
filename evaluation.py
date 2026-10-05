"""
evaluation.py - Chạy đánh giá toàn bộ 3 mẫu thiết kế × 3 kịch bản & in báo cáo
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

from typing import List
from agents.react import run_react
from agents.plan_execute import run_plan_then_execute
from agents.hybrid import run_hybrid
from harness.trace import RunResult


def run_full_evaluation() -> List[RunResult]:
    """
    Chạy đánh giá ma trận 3 Mẫu thiết kế Agent × 3 Kịch bản dữ liệu thực nghiệm:
    1. ReAct (happy, budget_exceeded, needs_approval)
    2. Plan-then-Execute (happy, budget_exceeded, needs_approval)
    3. Lai / Hybrid (happy, budget_exceeded, needs_approval)
    """
    scenarios = ["happy", "budget_exceeded", "needs_approval"]
    results: List[RunResult] = []

    print("\n" + "=" * 80)
    print("BAT DAU CHAY DANH GIA MA TRAN 3 MAU THIET KE × 3 KICH BAN (SE373 - BTVN#3)")
    print("=" * 80 + "\n")

    # Mẫu 1: ReAct
    for sc in scenarios:
        print(f"Dang chay: ReAct | Scenario: {sc} ...")
        res = run_react(scenario=sc)
        results.append(res)

    # Mẫu 2: Plan-then-Execute
    for sc in scenarios:
        print(f"Dang chay: Plan-then-Execute | Scenario: {sc} ...")
        res = run_plan_then_execute(scenario=sc)
        results.append(res)

    # Mẫu 3: Lai / Hybrid
    for sc in scenarios:
        print(f"Dang chay: Lai (Hybrid) | Scenario: {sc} ...")
        res = run_hybrid(scenario=sc)
        results.append(res)

    print("\nHoan thanh 9/9 luot thuc nghiem!\n")
    return results


def print_evaluation_report(results: List[RunResult]) -> None:
    """
    In Bảng kết quả đối chiếu 3 mẫu thiết kế theo đúng chuẩn tài liệu BTVN#3.
    """
    header = (
        f"{'Pattern':<18} | {'Scenario':<16} | {'Stop type':<18} | "
        f"{'Đạt mục tiêu':<12} | {'Bước':<5} | {'Tool calls':<10} | {'Replans':<8} | {'~Token':<10}"
    )
    separator = "-" * len(header)

    print("=" * len(header))
    print("                BẢNG KẾT QUẢ ĐỐI CHIẾU 3 MẪU THIẾT KẾ AGENT")
    print("=" * len(header))
    print(header)
    print(separator)

    for r in results:
        goal_text = "có" if r.goal_reached else "không"
        tokens_fmt = f"{r.estimated_tokens:,.0f}".replace(",", ".")
        print(
            f"{r.pattern:<18} | {r.scenario:<16} | {r.stop_type:<18} | "
            f"{goal_text:<12} | {r.steps:<5} | {r.tool_calls:<10} | {r.replans:<8} | {tokens_fmt:<10}"
        )
    print(separator)
    print()


if __name__ == "__main__":
    evaluation_results = run_full_evaluation()
    print_evaluation_report(evaluation_results)
