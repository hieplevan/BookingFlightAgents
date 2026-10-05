"""
trace.py - Ghi vết thực thi (TraceEvent) và kết quả lượt chạy (RunResult)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from harness.handoff import Handoff


@dataclass
class TraceEvent:
    """
    Sự kiện ghi vết thực thi (call, observation, stop, replan) phục vụ Agent Debugging.
    """
    step: int
    event_type: str  # "call" | "observation" | "stop" | "replan" | "permission_blocked"
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    content: Any = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "event_type": self.event_type,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "content": self.content,
            "timestamp": self.timestamp
        }


@dataclass
class RunResult:
    """
    Kết quả tổng kết của một lượt thực thi theo mẫu thiết kế và kịch bản.
    Khớp với các cột trong Bảng kết quả đối chiếu 3 mẫu thiết kế.
    """
    pattern: str                 # "ReAct" | "Plan-then-Execute" | "Lai (Hybrid)"
    scenario: str                # "happy" | "budget_exceeded" | "needs_approval"
    stop_type: str               # "goal_reached" | "budget_exceeded" | "plan_invalidated" | "needs_approval" | ...
    goal_reached: bool           # True / False
    steps: int                   # Tổng số bước thực hiện
    tool_calls: int              # Tổng số lệnh tool đã thực thi
    replans: int                 # Số lần lập lại kế hoạch (đặc biệt cho mẫu Hybrid)
    estimated_tokens: int        # Ước lượng token tiêu thụ (~Token)
    trace: List[TraceEvent] = field(default_factory=list)
    handoff: Optional[Handoff] = None
    last_booking: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern,
            "scenario": self.scenario,
            "stop_type": self.stop_type,
            "goal_reached": "có" if self.goal_reached else "không",
            "steps": self.steps,
            "tool_calls": self.tool_calls,
            "replans": self.replans,
            "estimated_tokens": self.estimated_tokens,
            "handoff": self.handoff.to_dict() if self.handoff else None,
            "trace_count": len(self.trace)
        }
