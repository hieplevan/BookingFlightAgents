# BookingFlightAgents - Safety Harness Engine with LangChain

Hệ thống Agent đặt vé máy bay tuyến **SGN -> DAD** áp dụng cơ chế giám sát an toàn (**Safety Harness Engine**) và kiểm chứng trên 3 mẫu thiết kế Agent (**ReAct**, **Plan-then-Execute**, **Hybrid/Lai**).

Môn học: **SE373 – Agentic AI Engineering**

---

## 1. Triết lý thiết kế (Core Principle)

> **"Model chỉ có quyền đề xuất hành động. Harness Engine mới là bên có thẩm quyền cao nhất quyết định Agent thực sự được làm gì, khi nào phải chặn lại và khi nào cần bàn giao cho con người."**

Hệ thống không phụ thuộc vào lời hứa của mô hình ngôn ngữ lớn (LLM), mà đặt LLM dưới sự giám sát độc lập của các lớp kiểm soát bằng mã nguồn (code-level enforcement).

---

## 2. Cấu trúc thư mục

```text
├── config.py             # Cấu hình tuyến SGN -> DAD, hạn mức APPROVAL_PRICE_LIMIT = 2.000.000đ
├── mock_data.py          # Dữ liệu giả lập 3 kịch bản thực nghiệm & quản lý _BOOKINGS
├── constraints.py        # Class Constraints & hàm kiểm tra hoàn thành is_goal_reached()
├── tools.py              # 5 @tool LangChain: search_flights, check_seat, book_seat, pay, get_booking
├── harness/              # Bộ máy kiểm soát an toàn (Safety Harness)
│   ├── budget.py         # Ngân sách cứng (max_steps = 12)
│   ├── loop_detector.py  # Bộ phát hiện lặp (LOOP) và bế tắc (STALL)
│   ├── permission.py     # Cổng kiểm quyền (check_permission) trước khi thanh toán
│   ├── handoff.py        # Cấu trúc bàn giao 3 phần cho con người (Handoff)
│   ├── trace.py          # Ghi vết thực thi (TraceEvent) & kết quả lượt chạy (RunResult)
│   └── engine.py         # Bộ máy điều phối trung tâm (HarnessEngine.execute_one)
├── models/               # Tầng suy luận LLM
│   └── real_langchain.py # RealLangChainModel kết nối Google Gemini API (gemini-3.8-flash)
├── agents/               # 3 Mẫu thiết kế Agent đối chứng
│   ├── common.py         # Tổng hợp kết quả (_finish) & ước lượng chi phí token
│   ├── react.py          # Mẫu 1: ReAct (run_react)
│   ├── plan_execute.py   # Mẫu 2: Plan-then-Execute (run_plan_then_execute)
│   └── hybrid.py         # Mẫu 3: Lai / Hybrid (run_hybrid)
├── tests/                # Kiểm thử tự động độc lập
│   └── test_loop_detector.py # 4 Unit tests cho thuật toán Loop/Stall
├── evaluation.py         # Đánh giá ma trận 3 mẫu x 3 kịch bản
├── main.py               # Điểm khởi chạy chính toàn bộ quy trình
├── .env.example          # Mẫu cấu hình môi trường
└── requirements.txt      # Thư viện phụ thuộc
```

---

## 3. Cài đặt & Khởi chạy

### Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

### Cấu hình file `.env`:
Tạo file `.env` từ `.env.example`:
```env
OPENAI_API_KEY=your_gemini_api_key_here
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-3.8-flash
```

### Chạy kiểm thử độc lập (Unit Tests):
```bash
python -m unittest -v tests/test_loop_detector.py
```

### Chạy chương trình chính (Hiển thị Unit Tests + Trace 3 Cases + Ma trận):
```bash
python main.py
```

### Chạy ma trận đánh giá đối chiếu (Evaluation Matrix):
```bash
python evaluation.py
```

---

## 4. Kết quả thực nghiệm đối chiếu (Evaluation Matrix)

| Pattern | Scenario | Stop type | Đạt mục tiêu | Bước | Tool calls | Replans | ~Token |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **ReAct** | `happy` | `goal_reached` | có | 4 | 4 | 0 | 8.000 |
| **Plan-then-Execute** | `happy` | `goal_reached` | có | 4 | 4 | 0 | 8.000 |
| **Lai (Hybrid)** | `happy` | `goal_reached` | có | 5 | 5 | 4 | 10.500 |
| **ReAct** | `budget_exceeded` | `budget_exceeded` | không | 12 | 12 | 0 | 42.000 |
| **Plan-then-Execute** | `budget_exceeded` | `plan_invalidated` | không | 2 | 2 | 0 | 4.500 |
| **Lai (Hybrid)** | `budget_exceeded` | `budget_exceeded` | không | 12 | 12 | 7 | 42.000 |
| **ReAct** | `needs_approval` | `needs_approval` | không | 3 | 3 | 0 | 6.000 |
| **Plan-then-Execute** | `needs_approval` | `needs_approval` | không | 3 | 3 | 0 | 6.000 |
| **Lai (Hybrid)** | `needs_approval` | `needs_approval` | không | 4 | 4 | 4 | 8.000 |
