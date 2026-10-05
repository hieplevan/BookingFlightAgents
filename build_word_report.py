"""
build_word_report.py - Tạo báo cáo Word (.docx) chuẩn TRẮNG ĐEN (Black & White / Monochrome)
Định dạng: Nét liền đơn giản (Table Grid nét liền đen), không dùng khung viền cho chữ,
không dùng màu mè hay icon, tuân thủ chặt chẽ thể thức báo cáo học thuật.
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

DOCX_OUTPUT_PATH = "d:/Agentic-BTVN3/BAO_CAO_BTVN3_SE373_TrangDen.docx"
DOCX_DEFAULT_PATH = "d:/Agentic-BTVN3/BAO_CAO_BTVN3_SE373.docx"

# Màu đen thuần 100% cho toàn bộ văn bản
COLOR_BLACK = RGBColor(0, 0, 0)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Thiết lập khoảng đệm (padding) trong ô."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders_basic_grid(table):
    """
    Thiết lập đường viền bảng nét liền đơn màu đen cơ bản nhất (Table Grid chuẩn):
    Tất cả các cạnh trên, dưới, trái, phải và đường ngang/dọc bên trong đều là nét liền đen 0.5pt.
    """
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)


def create_report():
    doc = Document()

    # Thiết lập lề trang tiêu chuẩn A4 (1 inch = 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # =========================================================================
    # 1. TRANG BÌA (COVER PAGE) - HOÀN TOÀN TRẮNG ĐEN, NÉT LIỀN ĐƠN GIẢN
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(20)
    p_inst.paragraph_format.space_after = Pt(2)
    run_inst = p_inst.add_run("ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN")
    run_inst.bold = True
    run_inst.font.name = "Times New Roman"
    run_inst.font.size = Pt(13)
    run_inst.font.color.rgb = COLOR_BLACK

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(60)
    run_line = p_line.add_run("----------------------------------------")
    run_line.font.name = "Times New Roman"
    run_line.font.color.rgb = COLOR_BLACK

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run("BÁO CÁO BÀI TẬP VỀ NHÀ #03")
    run_title.bold = True
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(22)
    run_title.font.color.rgb = COLOR_BLACK

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(50)
    run_sub = p_sub.add_run("DỰNG AGENT ĐẶT VÉ MÁY BAY BẰNG LANGCHAIN\nVÀ CƠ CHẾ KIỂM SOÁT AN TOÀN (HARNESS ENGINE)")
    run_sub.bold = True
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = COLOR_BLACK

    # Bảng thông tin sinh viên & học phần (kẻ nét liền basic)
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False
    set_table_borders_basic_grid(info_table)
    col_widths = [Inches(2.3), Inches(3.9)]
    
    info_data = [
        ("Môn học:", "SE373 – Agentic AI Engineering"),
        ("Nội dung bài tập:", "BTVN#03: Giám sát & Kiểm soát An toàn Agent"),
        ("Chặng bay thực nghiệm:", "Sài Gòn (SGN) -> Đà Nẵng (DAD)"),
        ("Mô hình suy luận LLM:", "Google Gemini API (gemini-3.8-flash)"),
        ("Điểm khởi chạy chính:", "main.py & evaluation.py")
    ]

    for idx, (label, val) in enumerate(info_data):
        row = info_table.rows[idx]
        cell_lbl, cell_val = row.cells[0], row.cells[1]
        cell_lbl.width, cell_val.width = col_widths[0], col_widths[1]
        set_cell_margins(cell_lbl, top=100, bottom=100, left=120, right=120)
        set_cell_margins(cell_val, top=100, bottom=100, left=120, right=120)

        p_lbl = cell_lbl.paragraphs[0]
        p_lbl.paragraph_format.space_before = Pt(2)
        p_lbl.paragraph_format.space_after = Pt(2)
        r_lbl = p_lbl.add_run(label)
        r_lbl.bold = True
        r_lbl.font.name = "Times New Roman"
        r_lbl.font.size = Pt(11.5)
        r_lbl.font.color.rgb = COLOR_BLACK

        p_val = cell_val.paragraphs[0]
        p_val.paragraph_format.space_before = Pt(2)
        p_val.paragraph_format.space_after = Pt(2)
        r_val = p_val.add_run(val)
        r_val.font.name = "Times New Roman"
        r_val.font.size = Pt(11.5)
        r_val.font.color.rgb = COLOR_BLACK

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(120)
    run_date = p_date.add_run("Tháng 10 / 2026")
    run_date.font.name = "Times New Roman"
    run_date.font.size = Pt(12)
    run_date.font.color.rgb = COLOR_BLACK

    doc.add_page_break()

    # =========================================================================
    # PHẦN 1: TỔNG QUAN BÀI TOÁN & KIẾN TRÚC HỆ THỐNG
    # =========================================================================
    h1 = doc.add_heading("1. TỔNG QUAN BÀI TOÁN & KIẾN TRÚC HỆ THỐNG", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(
        "Trong các hệ thống Agentic AI hiện đại, việc để Large Language Model (LLM) tự do ra quyết định "
        "và hành động độc lập luôn tiềm ẩn những rủi ro nghiêm trọng như: tin dữ liệu sai (hallucination), "
        "quên ràng buộc ban đầu sau hội thoại dài, dừng sớm khi chưa hoàn thành, hoặc lặp vô tận tiêu tốn ngân sách. "
        "Bài tập về nhà số 03 (SE373) tập trung xây dựng một hệ sinh thái Agent đặt vé máy bay tuyến "
    )
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.font.color.rgb = COLOR_BLACK
    
    run_bold = p.add_run("SGN -> DAD")
    run_bold.bold = True
    run_bold.font.name = "Times New Roman"
    run_bold.font.size = Pt(12)
    run_bold.font.color.rgb = COLOR_BLACK
    
    run2 = p.add_run(
        " với 5 công cụ chuẩn của LangChain, đặt dưới sự kiểm soát chặt chẽ của bộ máy "
    )
    run2.font.name = "Times New Roman"
    run2.font.size = Pt(12)
    run2.font.color.rgb = COLOR_BLACK

    run_harness = p.add_run("Harness Engine")
    run_harness.bold = True
    run_harness.font.name = "Times New Roman"
    run_harness.font.size = Pt(12)
    run_harness.font.color.rgb = COLOR_BLACK

    run_rest = p.add_run(
        " nhằm hiện thực hóa nguyên tắc sống còn trong kỹ nghệ Agent:"
    )
    run_rest.font.name = "Times New Roman"
    run_rest.font.size = Pt(12)
    run_rest.font.color.rgb = COLOR_BLACK

    # Viết đoạn nguyên tắc bình thường, không bọc trong khung
    p_rule = doc.add_paragraph()
    p_rule.paragraph_format.space_before = Pt(6)
    p_rule.paragraph_format.space_after = Pt(10)
    p_rule.paragraph_format.left_indent = Inches(0.4)
    p_rule.paragraph_format.line_spacing = 1.2
    r_rt = p_rule.add_run("Nguyên tắc cốt lõi: ")
    r_rt.bold = True
    r_rt.font.name = "Times New Roman"
    r_rt.font.size = Pt(12)
    r_rt.font.color.rgb = COLOR_BLACK

    r_rc = p_rule.add_run(
        "Model chỉ có quyền đề xuất hành động. Harness Engine mới là bên có thẩm quyền cao nhất quyết định "
        "Agent thực sự được làm gì, khi nào phải chặn lại và khi nào cần bàn giao cho con người."
    )
    r_rc.font.name = "Times New Roman"
    r_rc.font.size = Pt(12)
    r_rc.font.italic = True
    r_rc.font.color.rgb = COLOR_BLACK

    # Cấu trúc thư mục
    h2 = doc.add_heading("1.1 Cấu trúc thư mục dự án", level=2)
    h2.runs[0].font.name = "Times New Roman"
    h2.runs[0].font.color.rgb = COLOR_BLACK

    p_tree = doc.add_paragraph()
    p_tree.paragraph_format.space_after = Pt(8)
    run_tree = p_tree.add_run(
        "Dự án được tổ chức phân tầng rõ ràng theo đúng chuẩn kiến trúc của môn học:\n"
        "├── config.py             # Cấu hình tuyến SGN -> DAD, hạn mức APPROVAL_PRICE_LIMIT = 2.000.000đ\n"
        "├── mock_data.py          # Dữ liệu giả lập 3 kịch bản thực nghiệm & quản lý _BOOKINGS\n"
        "├── constraints.py        # Class Constraints & hàm kiểm tra hoàn thành is_goal_reached()\n"
        "├── tools.py              # 5 @tool LangChain: search_flights, check_seat, book_seat, pay, get_booking\n"
        "├── harness/              # Bộ máy kiểm soát an toàn (Safety Harness)\n"
        "│   ├── budget.py         # Ngân sách cứng (max_steps = 12)\n"
        "│   ├── loop_detector.py  # Bộ phát hiện lặp (LOOP) và bế tắc (STALL)\n"
        "│   ├── permission.py     # Cổng kiểm quyền (check_permission) trước khi thanh toán\n"
        "│   ├── handoff.py        # Cấu trúc bàn giao 3 phần cho con người (Handoff)\n"
        "│   ├── trace.py          # Ghi vết thực thi (TraceEvent) & kết quả lượt chạy (RunResult)\n"
        "│   └── engine.py         # Bộ máy điều phối trung tâm (HarnessEngine.execute_one)\n"
        "├── models/               # Tầng suy luận LLM\n"
        "│   └── real_langchain.py # RealLangChainModel kết nối Google Gemini API (gemini-3.8-flash)\n"
        "├── agents/               # 3 Mẫu thiết kế Agent đối chứng\n"
        "│   ├── common.py         # Tổng hợp kết quả (_finish) & ước lượng chi phí token\n"
        "│   ├── react.py          # Mẫu 1: ReAct (run_react)\n"
        "│   ├── plan_execute.py   # Mẫu 2: Plan-then-Execute (run_plan_then_execute)\n"
        "│   └── hybrid.py         # Mẫu 3: Lai / Hybrid (run_hybrid)\n"
        "├── tests/                # Kiểm thử tự động độc lập\n"
        "│   └── test_loop_detector.py # 4 Unit tests cho thuật toán Loop/Stall\n"
        "├── evaluation.py         # Đánh giá ma trận 3 mẫu x 3 kịch bản\n"
        "├── main.py               # Điểm khởi chạy chính toàn bộ quy trình\n"
        "└── .env                  # Cấu hình OPENAI_API_KEY, BASE_URL, MODEL"
    )
    run_tree.font.name = "Consolas"
    run_tree.font.size = Pt(9.5)
    run_tree.font.color.rgb = COLOR_BLACK

    # 5 công cụ
    h2 = doc.add_heading("1.2 Bộ 5 công cụ có cấu trúc JSON (LangChain Tools)", level=2)
    h2.runs[0].font.name = "Times New Roman"
    h2.runs[0].font.color.rgb = COLOR_BLACK

    p_tools = doc.add_paragraph()
    p_tools.paragraph_format.line_spacing = 1.2
    run_tools = p_tools.add_run(
        "Cả 5 công cụ đều được gắn decorator @tool của langchain_core và bắt buộc trả về dữ liệu có cấu trúc "
        "(JSON có thuộc tính status rõ ràng) nhằm tránh hiện tượng Agent suy đoán mò:"
    )
    run_tools.font.name = "Times New Roman"
    run_tools.font.size = Pt(12)
    run_tools.font.color.rgb = COLOR_BLACK

    tools_bullets = [
        ("search_flights(origin, dest, date, buoi)", "Tìm chuyến bay phù hợp, trả về danh sách kèm giá, giờ bay, điều kiện hoàn vé."),
        ("check_seat(flight_id, seat_number)", "Kiểm tra tình trạng ghế trống trên chuyến bay cụ thể."),
        ("book_seat(flight_id, seat_number, passenger_name)", "Thực hiện giữ chỗ, lưu vào biến toàn cục _BOOKINGS với status = 'held'."),
        ("pay(booking_id, amount)", "Thanh toán giao dịch, cập nhật status sang 'confirmed' và paid = True."),
        ("get_booking(booking_id)", "Tra cứu đối chiếu trạng thái đặt vé theo mã đặt chỗ.")
    ]
    for name, desc in tools_bullets:
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Inches(0.3)
        bp.paragraph_format.space_before = Pt(2)
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.line_spacing = 1.15
        r_dash = bp.add_run("- ")
        r_dash.font.name = "Times New Roman"
        r_dash.font.size = Pt(11.5)
        r_dash.font.color.rgb = COLOR_BLACK
        r_name = bp.add_run(name + ": ")
        r_name.bold = True
        r_name.font.name = "Consolas"
        r_name.font.size = Pt(10.5)
        r_name.font.color.rgb = COLOR_BLACK
        r_desc = bp.add_run(desc)
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(11.5)
        r_desc.font.color.rgb = COLOR_BLACK

    # =========================================================================
    # PHẦN 2: CÁC LỚP KIỂM SOÁT AN TOÀN (HARNESS ENGINE)
    # =========================================================================
    h1 = doc.add_heading("2. CÁC LỚP KIỂM SOÁT AN TOÀN (HARNESS ENGINE)", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    p_harness = doc.add_paragraph()
    p_harness.paragraph_format.line_spacing = 1.2
    run_harness_desc = p_harness.add_run(
        "Hệ thống cài đặt đầy đủ 4 lớp kiểm soát an toàn cốt lõi cùng 3 cơ chế đảm bảo điểm dừng (Termination):"
    )
    run_harness_desc.font.name = "Times New Roman"
    run_harness_desc.font.size = Pt(12)
    run_harness_desc.font.color.rgb = COLOR_BLACK

    table_harness = doc.add_table(rows=5, cols=4)
    table_harness.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_harness.autofit = False
    set_table_borders_basic_grid(table_harness)
    
    t_widths = [Inches(1.5), Inches(1.4), Inches(2.1), Inches(1.8)]
    headers = ["Lớp Harness", "File cài đặt", "Cơ chế hoạt động", "Chặn được lỗi gì"]
    
    # Tiêu đề bảng: Chữ in đậm, viền đen nét liền basic
    hdr_row = table_harness.rows[0]
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = t_widths[idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(heading)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BLACK

    harness_rows = [
        ("1. Ràng buộc là dữ liệu", "constraints.py\n(class Constraints)", "Lưu origin, dest, date, buoi, tran_gia ở cấu trúc cố định; flight_matches() kiểm tra mọi chuyến bay.", "'Quên yêu cầu ban đầu' — Agent không bị trôi khỏi ràng buộc khi hội thoại dài."),
        ("2. Tiêu chí hoàn thành kiểm bằng code", "constraints.py\n(is_goal_reached)", "Kiểm tra status == 'confirmed', paid == True, giá <= trần, đúng buổi — độc lập hoàn toàn với LLM.", "Dừng sớm sai (Model tưởng đã xong nhưng thực tế chưa hoàn tất)."),
        ("3. Kiểm quyền (Permission Gate)", "harness/permission.py\n(check_permission)", "Chạy trước khi thực thi tool pay; chặn lại nếu giá vé > 2.000.000đ và vé không hoàn được.", "Agent tự ý thanh toán các giao dịch vượt thẩm quyền."),
        ("4. Bàn giao (Handoff)", "harness/handoff.py\n(class Handoff)", "Đóng gói đủ 3 phần: Trạng thái đã làm tới đâu, đã thử những gì, câu hỏi cụ thể trong 30 giây.", "Bàn giao mơ hồ khiến người nhận không thể ra quyết định ngay.")
    ]

    for row_idx, data in enumerate(harness_rows, start=1):
        row = table_harness.rows[row_idx]
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.width = t_widths[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_BLACK

    # 3 cơ chế đảm bảo điểm dừng
    h2 = doc.add_heading("2.1 Ba cơ chế đảm bảo vòng lặp luôn dừng (Termination Guarantees)", level=2)
    h2.runs[0].font.name = "Times New Roman"
    h2.runs[0].font.color.rgb = COLOR_BLACK

    term_items = [
        ("Ngân sách cứng (harness/budget.py - Budget):", "Giới hạn max_steps = 12 bước gọi công cụ. Chặn đứng tình trạng Agent chạy tràn lan tốn kém chi phí token."),
        ("Phát hiện lặp & bế tắc (harness/loop_detector.py - LoopDetector):", "Phát hiện gọi lặp cùng cặp (tool, args) liên tiếp (LOOP) hoặc liên tục đổi tool nhưng chỉ số tiến trình đứng yên (STALL)."),
        ("Ghi vết thực thi (harness/trace.py - TraceEvent & RunResult):", "Lưu lại nhật ký chi tiết từng bước (call, observation, stop, replan) phục vụ Agent Debugging.")
    ]
    for term_title, term_desc in term_items:
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Inches(0.3)
        bp.paragraph_format.space_before = Pt(2)
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.line_spacing = 1.15
        r_dash = bp.add_run("- ")
        r_dash.font.name = "Times New Roman"
        r_dash.font.size = Pt(11.5)
        r_dash.font.color.rgb = COLOR_BLACK
        r_t = bp.add_run(term_title + " ")
        r_t.bold = True
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(11.5)
        r_t.font.color.rgb = COLOR_BLACK
        r_d = bp.add_run(term_desc)
        r_d.font.name = "Times New Roman"
        r_d.font.size = Pt(11.5)
        r_d.font.color.rgb = COLOR_BLACK

    # =========================================================================
    # PHẦN 3: BA MẪU THIẾT KẾ AGENT
    # =========================================================================
    h1 = doc.add_heading("3. BA MẪU THIẾT KẾ AGENT (ReAct, Plan-then-Execute, Lai/Hybrid)", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    p_agents = doc.add_paragraph()
    p_agents.paragraph_format.line_spacing = 1.2
    run_agents_desc = p_agents.add_run(
        "Cả 3 mẫu thiết kế trong thư mục agents/ đều dùng chung bộ TOOLS, cùng gọi RealLangChainModel "
        "(kết nối Google Gemini qua ChatOpenAI & bind_tools) và đều đi qua HarnessEngine. "
        "Sự khác biệt cốt lõi nằm ở cách thức tổ chức ra quyết định cho bước tiếp theo:"
    )
    run_agents_desc.font.name = "Times New Roman"
    run_agents_desc.font.size = Pt(12)
    run_agents_desc.font.color.rgb = COLOR_BLACK

    table_patterns = doc.add_table(rows=4, cols=4)
    table_patterns.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_patterns.autofit = False
    set_table_borders_basic_grid(table_patterns)
    
    p_widths = [Inches(1.5), Inches(1.4), Inches(2.2), Inches(1.7)]
    p_headers = ["Mẫu thiết kế", "File cài đặt", "Cách tổ chức trong code", "Đặc điểm vận hành"]
    
    hdr_row = table_patterns.rows[0]
    for idx, heading in enumerate(p_headers):
        cell = hdr_row.cells[idx]
        cell.width = p_widths[idx]
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(heading)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BLACK

    pattern_rows = [
        ("ReAct", "agents/react.py\n(run_react)", "Vòng lặp while True, mỗi bước gọi model.decide_next_step(state) để LLM chọn 1 tool duy nhất dựa trên observation mới nhất.", "Phản ứng tức thì với mọi observation, linh hoạt nhất."),
        ("Plan-then-Execute", "agents/plan_execute.py\n(run_plan_then_execute)", "Gọi model.make_plan(state) sinh trọn gói 5 bước ngay từ đầu (dùng placeholder GUESS_FIRST, GUESS), chạy tuần tự và không lập lại kế hoạch.", "Tiết kiệm số lần gọi LLM, dễ duyệt trước, nhưng vỡ ngay khi giả định bước đầu sai."),
        ("Lai (Hybrid)", "agents/hybrid.py\n(run_hybrid)", "Gọi model.replan(state, k=2) lập kế hoạch cho cụm tối đa k = 2 bước dựa trên dữ liệu đã biết, thực thi cụm đó, kiểm tra tiến triển rồi replan.", "Cân bằng giữa nhìn trước ngắn hạn và khả năng thích nghi khi môi trường thay đổi.")
    ]

    for row_idx, data in enumerate(pattern_rows, start=1):
        row = table_patterns.rows[row_idx]
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.width = p_widths[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_BLACK

    # =========================================================================
    # PHẦN 4: KẾT QUẢ THỰC NGHIỆM & PHÂN TÍCH MA TRẬN ĐÁNH GIÁ
    # =========================================================================
    doc.add_page_break()
    h1 = doc.add_heading("4. KẾT QUẢ THỰC NGHIỆM & MA TRẬN ĐỐI CHIẾU", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    p_sc = doc.add_paragraph()
    p_sc.paragraph_format.line_spacing = 1.2
    run_sc_desc = p_sc.add_run(
        "Ba kịch bản trong mock_data.py được thiết kế để kiểm chứng đầy đủ các điều kiện dừng của Harness:\n"
        "1. happy: Có chuyến bay sáng, giá <= 2.000.000đ, hoàn vé được -> Agent đặt và thanh toán thành công (goal_reached).\n"
        "2. budget_exceeded: 15 chuyến bay sáng nhưng tất cả đều vượt trần giá 2.000.000đ -> Agent dừng khi chạm ngân sách 12 bước hoặc vỡ kế hoạch (plan_invalidated).\n"
        "3. needs_approval: Người dùng nới trần giá lên 3.000.000đ, có chuyến phù hợp (2.600.000đ) nhưng không hoàn được và vượt hạn mức công ty 2.000.000đ -> Cổng kiểm quyền chặn trước khi pay (needs_approval)."
    )
    run_sc_desc.font.name = "Times New Roman"
    run_sc_desc.font.size = Pt(11.5)
    run_sc_desc.font.color.rgb = COLOR_BLACK

    # Bảng kết quả đối chiếu
    h2 = doc.add_heading("4.1 Bảng kết quả đối chiếu 3 mẫu thiết kế (Ma trận 9 lượt chạy)", level=2)
    h2.runs[0].font.name = "Times New Roman"
    h2.runs[0].font.color.rgb = COLOR_BLACK

    table_results = doc.add_table(rows=10, cols=8)
    table_results.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_results.autofit = False
    set_table_borders_basic_grid(table_results)

    res_widths = [Inches(1.4), Inches(1.1), Inches(1.2), Inches(0.7), Inches(0.5), Inches(0.7), Inches(0.6), Inches(0.7)]
    res_headers = ["Pattern", "Scenario", "Stop type", "Đạt mục tiêu", "Bước", "Tool calls", "Replans", "~Token"]

    hdr_row = table_results.rows[0]
    for idx, heading in enumerate(res_headers):
        cell = hdr_row.cells[idx]
        cell.width = res_widths[idx]
        set_cell_margins(cell, top=100, bottom=100, left=60, right=60)
        p = cell.paragraphs[0]
        r = p.add_run(heading)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_BLACK

    results_data = [
        ("ReAct", "happy", "goal_reached", "có", "4", "4", "0", "8.000"),
        ("Plan-then-Execute", "happy", "goal_reached", "có", "4", "4", "0", "8.000"),
        ("Lai (Hybrid)", "happy", "goal_reached", "có", "5", "5", "4", "10.500"),
        ("ReAct", "budget_exceeded", "budget_exceeded", "không", "12", "12", "0", "42.000"),
        ("Plan-then-Execute", "budget_exceeded", "plan_invalidated", "không", "2", "2", "0", "4.500"),
        ("Lai (Hybrid)", "budget_exceeded", "budget_exceeded", "không", "12", "12", "7", "42.000"),
        ("ReAct", "needs_approval", "needs_approval", "không", "3", "3", "0", "6.000"),
        ("Plan-then-Execute", "needs_approval", "needs_approval", "không", "3", "3", "0", "6.000"),
        ("Lai (Hybrid)", "needs_approval", "needs_approval", "không", "4", "4", "4", "8.000")
    ]

    for row_idx, data in enumerate(results_data, start=1):
        row = table_results.rows[row_idx]
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.width = res_widths[col_idx]
            set_cell_margins(cell, top=80, bottom=80, left=60, right=60)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_BLACK

    # =========================================================================
    # PHẦN 5: CÁC HÌNH ẢNH CHỤP TERMINAL THỰC TẾ (SCREENSHOTS)
    # =========================================================================
    doc.add_page_break()
    h1 = doc.add_heading("5. MINH CHỨNG THỰC THI TRÊN TERMINAL (ẢNH CHỤP THỰC TẾ)", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    p_img_intro = doc.add_paragraph()
    p_img_intro.paragraph_format.line_spacing = 1.2
    r_intro = p_img_intro.add_run(
        "Dưới đây là các hình ảnh chụp lại màn hình Terminal thực tế trong quá trình chạy kiểm thử độc lập, "
        "kết nối LLM Google Gemini thật, cũng như truy vết (trace) chi tiết các trường hợp lỗi và ma trận đối chiếu:"
    )
    r_intro.font.name = "Times New Roman"
    r_intro.font.size = Pt(12)
    r_intro.font.color.rgb = COLOR_BLACK

    screenshots_info = [
        (
            "Hình 1: Kiểm thử độc lập bộ phát hiện lặp LoopDetector",
            "report_assets/terminal_test_loop.png",
            "Chạy lệnh: python -m unittest -v tests/test_loop_detector.py. Cả 4 test case độc lập cho thuật toán LOOP (lặp lại tool & args liên tiếp) và STALL (đổi tool liên tục nhưng chỉ số tiến trình đứng yên) đều đạt trạng thái OK."
        ),
        (
            "Hình 2: Kiểm tra kết nối LLM Google Gemini (RealLangChainModel) & bind_tools",
            "report_assets/terminal_models_llm.png",
            "Chạy lệnh: python models/real_langchain.py. Mô hình gemini-3.8-flash phản hồi trực tiếp qua API, tự động nhận diện yêu cầu và phát lệnh gọi tool search_flights cùng bộ tham số chuẩn xác."
        ),
        (
            "Hình 3: Chi tiết Trace Case A – Plan-then-Execute vỡ kế hoạch (plan_invalidated)",
            "report_assets/terminal_case_plan_invalidated.png",
            "Minh chứng vỡ kế hoạch tại bước 2: Sau khi search_flights thấy 15 chuyến bay nhưng giá đều > 2.000.000đ, Plan-then-Execute cố định chọn chuyến đầu tiên VN200. Khi check_seat phát hiện giá 2.150.000đ vượt trần, kế hoạch tĩnh lập tức bị hủy."
        ),
        (
            "Hình 4: Chi tiết Trace Case B – Cổng kiểm quyền chặn trước pay & Gói Handoff 3 phần",
            "report_assets/terminal_case_needs_approval.png",
            "Minh chứng cơ chế kiểm quyền (Permission Gate): Chuyến bay VN555 giá 2.600.000đ thỏa trần người dùng nhưng vượt hạn mức công ty 2.000.000đ và không hoàn được. Cổng kiểm quyền lập tức chặn lệnh pay và xuất gói bàn giao Handoff 3 phần."
        ),
        (
            "Hình 5: Chi tiết Trace Case C – ReAct chạm trần ngân sách cứng (budget_exceeded)",
            "report_assets/terminal_case_budget_exceeded.png",
            "Minh chứng cơ chế ngân sách cứng: Agent ReAct kiên trì kiểm tra lần lượt 12 chuyến bay từ VN200 đến VN210. Khi chạm ngưỡng max_steps = 12, lớp Budget kích hoạt dừng cưỡng chế để bảo vệ tài nguyên."
        ),
        (
            "Hình 6: Toàn cảnh ma trận đánh giá tự động 9 lượt chạy (Matrix Evaluation)",
            "report_assets/terminal_evaluation_matrix.png",
            "Chạy lệnh: python evaluation.py. Ma trận đối chiếu 3 mẫu thiết kế x 3 kịch bản hiển thị đầy đủ, chính xác tuyệt đối từng số bước, tool calls, replans và số lượng token tiêu thụ theo đúng tài liệu bài giảng."
        )
    ]

    for title, img_path, caption in screenshots_info:
        p_cap_title = doc.add_paragraph()
        p_cap_title.paragraph_format.space_before = Pt(14)
        p_cap_title.paragraph_format.space_after = Pt(4)
        r_ct = p_cap_title.add_run(title)
        r_ct.bold = True
        r_ct.font.name = "Times New Roman"
        r_ct.font.size = Pt(11.5)
        r_ct.font.color.rgb = COLOR_BLACK

        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=Inches(6.2))
        else:
            p_warn = doc.add_paragraph()
            p_warn.add_run(f"[Không tìm thấy ảnh: {img_path}]").italic = True

        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(12)
        p_desc.paragraph_format.line_spacing = 1.15
        r_desc = p_desc.add_run("Mô tả: " + caption)
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(10.5)
        r_desc.font.color.rgb = COLOR_BLACK

    # =========================================================================
    # PHẦN 6: KẾT LUẬN & BÀI HỌC KINH NGHIỆM
    # =========================================================================
    doc.add_page_break()
    h1 = doc.add_heading("6. KẾT LUẬN & BÀI HỌC KINH NGHIỆM", level=1)
    h1.runs[0].font.name = "Times New Roman"
    h1.runs[0].font.color.rgb = COLOR_BLACK

    conclusions = [
        ("Về chi phí vận hành (Token Cost):", "Chi phí tỉ lệ thuận với số vòng lặp hội thoại. Ở kịch bản budget_exceeded, ReAct và Hybrid tiêu thụ tới ~42.000 token do kiên trì tìm kiếm đến bước thứ 12, trong khi Plan-then-Execute chỉ tiêu thụ ~4.500 token do vỡ kế hoạch sớm. Điều này chứng minh việc kiểm soát ngân sách cứng là tối quan trọng để tránh thất thoát tài nguyên."),
        ("Về khả năng thích nghi môi trường:", "Plan-then-Execute thành công ở kịch bản happy chỉ vì chuyến bay hợp lệ nằm ngay đầu danh sách. Nếu chuyến hợp lệ ở vị trí thứ 2 hoặc thứ 3, Plan-then-Execute sẽ thất bại hoàn toàn trong khi ReAct và Hybrid thích nghi tuyệt vời."),
        ("Về tính độc lập và uy quyền của Harness:", "Ở kịch bản needs_approval, bất kể Agent thông minh hay sử dụng mẫu thiết kế nào, HarnessEngine đều chặn chính xác lệnh pay vi phạm chính sách và tạo gói Handoff chuyển giao quyền quyết định cho con người. Điều này tái khẳng định chân lý: Trong kỹ nghệ Agentic AI thực tế, không bao giờ trao toàn quyền không kiểm soát cho mô hình ngôn ngữ lớn.")
    ]

    for c_title, c_text in conclusions:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.left_indent = Inches(0.3)
        p_c.paragraph_format.space_before = Pt(3)
        p_c.paragraph_format.space_after = Pt(8)
        p_c.paragraph_format.line_spacing = 1.2
        r_dash = p_c.add_run("- ")
        r_dash.font.name = "Times New Roman"
        r_dash.font.size = Pt(11.5)
        r_dash.font.color.rgb = COLOR_BLACK
        r_ct = p_c.add_run(f"{c_title} ")
        r_ct.bold = True
        r_ct.font.name = "Times New Roman"
        r_ct.font.size = Pt(11.5)
        r_ct.font.color.rgb = COLOR_BLACK
        r_cx = p_c.add_run(c_text)
        r_cx.font.name = "Times New Roman"
        r_cx.font.size = Pt(11.5)
        r_cx.font.color.rgb = COLOR_BLACK

    doc.save(DOCX_OUTPUT_PATH)
    print(f"Bao cao Word TRANG DEN da duoc luu thanh cong tai: {DOCX_OUTPUT_PATH}")
    try:
        doc.save(DOCX_DEFAULT_PATH)
        print(f"Da dong bo vao: {DOCX_DEFAULT_PATH}")
    except Exception:
        print(f"(Luu y: {DOCX_DEFAULT_PATH} dang duoc mo boi ung dung khac nen da luu vao {DOCX_OUTPUT_PATH})")


if __name__ == "__main__":
    create_report()
