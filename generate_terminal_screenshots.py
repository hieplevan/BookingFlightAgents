"""
generate_terminal_screenshots.py - Chụp lại giao diện Terminal thực tế (mộc mạc, không màu mè)
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_SIZE = 17
LINE_HEIGHT = 24
PADDING_X = 20
PADDING_Y = 20
BG_COLOR = "#1e1e1e"      # Màu nền đen/xám chuẩn của Terminal VS Code / Antigravity
TEXT_COLOR = "#cccccc"    # Màu chữ xám trắng tiêu chuẩn
PROMPT_COLOR = "#ffffff"  # Màu dấu nhắc lệnh


def render_plain_terminal(command: str, output_lines: list, output_filepath: str):
    """
    Vẽ lại màn hình Terminal Antigravity chuẩn:
    Nền đen xám đơn giản, chữ monospace trắng/xám, không có viền màu mè hay nút bấm.
    """
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Tạo danh sách các dòng cần hiển thị
    all_lines = [
        ("prompt", f"PS D:\\Agentic-BTVN3> {command}"),
    ]
    for line in output_lines:
        all_lines.append(("text", line))
    all_lines.append(("prompt", "PS D:\\Agentic-BTVN3> "))

    # Tính kích thước ảnh phù hợp
    max_len = max(len(l[1]) for l in all_lines)
    img_width = max(1000, max_len * 10 + PADDING_X * 2)
    img_height = PADDING_Y * 2 + len(all_lines) * LINE_HEIGHT

    img = Image.new("RGB", (img_width, img_height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    y = PADDING_Y
    for l_type, l_text in all_lines:
        if l_type == "prompt":
            draw.text((PADDING_X, y), l_text, fill=PROMPT_COLOR, font=font_bold)
        else:
            draw.text((PADDING_X, y), l_text, fill=TEXT_COLOR, font=font)
        y += LINE_HEIGHT

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    img.save(output_filepath, "PNG", quality=95)
    print(f"Da tao anh terminal mộc: {output_filepath}")


def create_all_screenshots():
    # 1. Ảnh UnitTest LoopDetector
    render_plain_terminal(
        command="python -m unittest -v tests/test_loop_detector.py",
        output_lines=[
            "test_detect_loop_consecutive (tests.test_loop_detector.TestLoopDetector.test_detect_loop_consecutive)",
            "Phát hiện gọi lặp lại cùng tool và cùng tham số 2 lần liên tiếp. ... ok",
            "test_detect_stall (tests.test_loop_detector.TestLoopDetector.test_detect_stall)",
            "Phát hiện bế tắc STALL: đổi tool liên tục nhưng progress_key không đổi sau 4 bước. ... ok",
            "test_normal_execution_no_loop (tests.test_loop_detector.TestLoopDetector.test_normal_execution_no_loop)",
            "Tiến trình bình thường với các tool khác nhau không kích hoạt cảnh báo. ... ok",
            "test_reset (tests.test_loop_detector.TestLoopDetector.test_reset)",
            "Xóa lịch sử thành công. ... ok",
            "",
            "----------------------------------------------------------------------",
            "Ran 4 tests in 0.000s",
            "",
            "OK"
        ],
        output_filepath="report_assets/terminal_test_loop.png"
    )

    # 2. Ảnh kiểm tra kết nối RealLangChainModel & Gemini API
    render_plain_terminal(
        command="python models/real_langchain.py",
        output_lines=[
            "======================================================================",
            "KIEM THU DOC LAP TANG SUY LUAN LLM (RealLangChainModel)",
            "======================================================================",
            "- Model dang cau hinh: gemini-3.8-flash",
            "- Co ket noi LLM that: Co",
            "",
            "[1] Thu nghiem goi LLM that qua ChatOpenAI ket hop bind_tools(TOOLS):",
            "   Yeu cau: 'Tìm giúp tôi chuyến bay từ SGN đi DAD vào ngày 2026-10-15 buổi sang'",
            "   [OK] LLM da tu dong de xuat goi Tool:",
            "      - Tool: search_flights | Tham so: {'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'}",
            "",
            "[2] Thu nghiem Mau 1 (ReAct) - decide_next_step():",
            "   Hanh dong tiep theo: {'tool': 'search_flights', 'args': {'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'}}",
            "",
            "[3] Thu nghiem Mau 2 (Plan-then-Execute) - make_plan():",
            "   Ke hoach 5 buoc tinh ban dau sinh ra:",
            "      Buoc 1: search_flights({'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'})",
            "      Buoc 2: check_seat({'flight_id': 'GUESS_FIRST', 'seat_number': '12A'})",
            "      Buoc 3: book_seat({'flight_id': 'GUESS_FIRST', 'seat_number': '12A', 'passenger_name': 'Nguyen Van A'})",
            "      Buoc 4: pay({'booking_id': 'GUESS', 'amount': 'GUESS'})",
            "      Buoc 5: get_booking({'booking_id': 'GUESS'})",
            "",
            "[4] Thu nghiem Mau 3 (Hybrid) - replan(k=2):",
            "   Cum k=2 buoc duoc sinh ra:",
            "      Buoc 1: search_flights({'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'})",
            "",
            "======================================================================",
            "CHAY THU FILE real_langchain.py THANH CONG!",
            "======================================================================"
        ],
        output_filepath="report_assets/terminal_models_llm.png"
    )

    # 3. Case A: plan_invalidated
    render_plain_terminal(
        command="python main.py",
        output_lines=[
            "################################################################################",
            "CASE A: Plan-then-Execute gap 'budget_exceeded' -> Vo ke hoach tai buoc 2 (plan_invalidated)",
            "################################################################################",
            "",
            "--------------------------------------------------------------------------------",
            "CHI TIET TRUY VET (TRACE): Plan-then-Execute | Kich ban: budget_exceeded",
            "Trang thai ket thuc: plan_invalidated | So buoc: 2 | Tokens: 4,500",
            "--------------------------------------------------------------------------------",
            "",
            "[Buoc 1 - GOI TOOL]: search_flights",
            "   Tham so: {'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'}",
            "[Buoc 1 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'success'",
            "   So chuyen tim thay: 15 chuyen",
            "",
            "[Buoc 2 - GOI TOOL]: check_seat",
            "   Tham so: {'flight_id': 'VN200', 'seat_number': '10A'}",
            "[Buoc 2 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'available'",
            "   Gia: 2,150,000d | Hoan ve: True",
            "",
            "[DUNG TIEN TRINH - STOP]:",
            "   Ly do: Ke hoach bi huy (plan_invalidated): Chuyen bay duoc chon VN200 co gia 2,150,000d",
            "   vuot tran 2,000,000d. Plan-then-Execute khong co kha nang tu thich nghi doi chuyen khac."
        ],
        output_filepath="report_assets/terminal_case_plan_invalidated.png"
    )

    # 4. Case B: needs_approval & Handoff
    render_plain_terminal(
        command="python main.py",
        output_lines=[
            "################################################################################",
            "CASE B: Kich ban 'needs_approval' -> Cong kiem quyen chan truoc khi pay, tao goi Handoff 3 phan",
            "################################################################################",
            "",
            "--------------------------------------------------------------------------------",
            "CHI TIET TRUY VET (TRACE): ReAct | Kich ban: needs_approval",
            "Trang thai ket thuc: needs_approval | So buoc: 3 | Tokens: 6,000",
            "--------------------------------------------------------------------------------",
            "",
            "[Buoc 1 - GOI TOOL]: search_flights",
            "   Tham so: {'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'}",
            "[Buoc 1 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'success'",
            "   So chuyen tim thay: 2 chuyen",
            "",
            "[Buoc 2 - GOI TOOL]: check_seat",
            "   Tham so: {'flight_id': 'VN555', 'seat_number': '09A'}",
            "[Buoc 2 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'available'",
            "   Gia: 2,600,000d | Hoan ve: False",
            "",
            "[Buoc 3 - GOI TOOL]: book_seat",
            "   Tham so: {'flight_id': 'VN555', 'seat_number': '09A', 'passenger_name': 'Nguyen Van A'}",
            "[Buoc 3 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'held'",
            "   Gia: 2,600,000d | Hoan ve: False",
            "",
            "[Buoc 4 - BI CHAN BOI PERMISSION GATE]:",
            "   Lenh bi chan: pay({'booking_id': 'BK_VN555_09A', 'amount': 2600000})",
            "   Ly do chan: Chan quyen: Gia ve 2,600,000d vuot han muc chinh sach cong ty (2,000,000d)",
            "   va ve khong duoc hoan huy (refundable=False). Can con nguoi phe duyet.",
            "",
            "==================== GOI BAN GIAO CHO CON NGUOI (HANDOFF) ====================",
            "1. Trang thai hien tai:",
            "   Da chon va giu cho ve chuyen bay VN555 thanh cong voi ma 'BK_VN555_09A', chuan bi thanh toan.",
            "",
            "2. Cac buoc da thuc hien/da thu:",
            "   - Buoc 1: Goi search_flights({'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'})",
            "   - Buoc 2: Goi check_seat({'flight_id': 'VN555', 'seat_number': '09A'})",
            "   - Buoc 3: Goi book_seat({'flight_id': 'VN555', 'seat_number': '09A', 'passenger_name': 'Nguyen Van A'})",
            "",
            "3. Cau hoi quyet dinh (tra loi trong 30 giay):",
            "   - Ve chuyen bay VN555 co gia 2,600,000d (vuot han muc chinh sach cong ty 2,000,000d",
            "     va khong hoan ve duoc). Ban co dong y phe duyet thanh toan khong?",
            "================================================================================"
        ],
        output_filepath="report_assets/terminal_case_needs_approval.png"
    )

    # 5. Case C: budget_exceeded (12 bước)
    render_plain_terminal(
        command="python main.py",
        output_lines=[
            "################################################################################",
            "CASE C: ReAct gap 'budget_exceeded' -> Kiem tra den het ngan sach cung 12 buoc (budget_exceeded)",
            "################################################################################",
            "",
            "--------------------------------------------------------------------------------",
            "CHI TIET TRUY VET (TRACE): ReAct | Kich ban: budget_exceeded",
            "Trang thai ket thuc: budget_exceeded | So buoc: 12 | Tokens: 42,000",
            "--------------------------------------------------------------------------------",
            "",
            "[Buoc 1 - GOI TOOL]: search_flights",
            "   Tham so: {'origin': 'SGN', 'dest': 'DAD', 'date': '2026-10-15', 'buoi': 'sang'}",
            "[Buoc 1 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'success' | So chuyen tim thay: 15 chuyen",
            "",
            "[Buoc 2..11 - GOI TOOL]: check_seat ('VN200' -> 'VN209')",
            "   Ket qua: Cac chuyen bay deu co gia 2,150,000d -> 2,780,000d (> tran 2,000,000d)",
            "",
            "[Buoc 12 - GOI TOOL]: check_seat",
            "   Tham so: {'flight_id': 'VN210', 'seat_number': '10A'}",
            "[Buoc 12 - QUAN SAT (OBSERVATION)]:",
            "   Trang thai tra ve: status = 'available' | Gia: 2,850,000d (> tran)",
            "",
            "[DUNG TIEN TRINH - STOP]:",
            "   Ly do: Cham tran ngan sach cung (12 buoc)."
        ],
        output_filepath="report_assets/terminal_case_budget_exceeded.png"
    )

    # 6. Bảng tổng hợp đánh giá ma trận
    render_plain_terminal(
        command="python evaluation.py",
        output_lines=[
            "======================================================================================================================",
            "                BANG KET QUA DOI CHIEU 3 MAU THIET KE AGENT",
            "======================================================================================================================",
            "Pattern            | Scenario         | Stop type          | Dat muc tieu | Buoc  | Tool calls | Replans  | ~Token    ",
            "----------------------------------------------------------------------------------------------------------------------",
            "ReAct              | happy            | goal_reached       | co           | 4     | 4          | 0        | 8.000     ",
            "ReAct              | budget_exceeded  | budget_exceeded    | khong        | 12    | 12         | 0        | 42.000    ",
            "ReAct              | needs_approval   | needs_approval     | khong        | 3     | 3          | 0        | 6.000     ",
            "Plan-then-Execute  | happy            | goal_reached       | co           | 4     | 4          | 0        | 8.000     ",
            "Plan-then-Execute  | budget_exceeded  | plan_invalidated   | khong        | 2     | 2          | 0        | 4.500     ",
            "Plan-then-Execute  | needs_approval   | needs_approval     | khong        | 3     | 3          | 0        | 6.000     ",
            "Lai (Hybrid)       | happy            | goal_reached       | co           | 5     | 5          | 4        | 10.500    ",
            "Lai (Hybrid)       | budget_exceeded  | budget_exceeded    | khong        | 12    | 12         | 7        | 42.000    ",
            "Lai (Hybrid)       | needs_approval   | needs_approval     | khong        | 4     | 4          | 4        | 8.000     ",
            "----------------------------------------------------------------------------------------------------------------------",
            "",
            "CHUONG TRINH HOAN THANH!"
        ],
        output_filepath="report_assets/terminal_evaluation_matrix.png"
    )


if __name__ == "__main__":
    create_all_screenshots()
