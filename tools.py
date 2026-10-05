"""
tools.py - 5 LangChain @tool trả về dữ liệu có cấu trúc JSON
Môn: SE373 – Agentic AI Engineering · BTVN#3
"""

import json
from typing import Dict, Any, List
from langchain_core.tools import tool
from mock_data import get_current_flights, _BOOKINGS


@tool
def search_flights(origin: str, dest: str, date: str, buoi: str = "sang") -> str:
    """
    Tìm kiếm các chuyến bay theo điểm khởi hành, điểm đến, ngày và buổi (sang/chieu).
    Trả về dữ liệu có cấu trúc JSON với danh sách chuyến bay kèm giá, giờ bay và điều kiện hoàn vé.
    """
    flights = get_current_flights()
    matched = []
    for f in flights:
        if (f.get("origin") == origin and 
            f.get("dest") == dest and 
            f.get("date") == date and 
            f.get("buoi") == buoi):
            matched.append({
                "flight_id": f["flight_id"],
                "airline": f.get("airline", ""),
                "origin": f["origin"],
                "dest": f["dest"],
                "date": f["date"],
                "departure_time": f["departure_time"],
                "buoi": f["buoi"],
                "price": f["price"],
                "refundable": f["refundable"],
                "available_seats": f.get("available_seats", [])
            })
    
    return json.dumps({
        "status": "success",
        "count": len(matched),
        "flights": matched
    }, ensure_ascii=False)


@tool
def check_seat(flight_id: str, seat_number: str) -> str:
    """
    Kiểm tra tình trạng ghế trên chuyến bay cụ thể.
    Trả về JSON với status: 'available' hoặc 'unavailable'.
    """
    flights = get_current_flights()
    flight = next((f for f in flights if f["flight_id"] == flight_id), None)
    
    if not flight:
        return json.dumps({
            "status": "error",
            "message": f"Không tìm thấy chuyến bay {flight_id}"
        }, ensure_ascii=False)
        
    available_seats = flight.get("available_seats", [])
    if seat_number in available_seats:
        return json.dumps({
            "status": "available",
            "flight_id": flight_id,
            "seat_number": seat_number,
            "price": flight["price"],
            "refundable": flight["refundable"],
            "buoi": flight["buoi"]
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "unavailable",
            "flight_id": flight_id,
            "seat_number": seat_number,
            "message": f"Ghế {seat_number} đã được đặt hoặc không tồn tại."
        }, ensure_ascii=False)


@tool
def book_seat(flight_id: str, seat_number: str, passenger_name: str = "Nguyen Van A") -> str:
    """
    Tạo yêu cầu giữ chỗ (booking) cho chuyến bay và ghế đã chọn.
    Trả về JSON với status: 'held' cùng booking_id và thông tin vé.
    """
    flights = get_current_flights()
    flight = next((f for f in flights if f["flight_id"] == flight_id), None)
    
    if not flight:
        return json.dumps({
            "status": "error",
            "message": f"Không tìm thấy chuyến bay {flight_id}"
        }, ensure_ascii=False)

    booking_id = f"BK_{flight_id}_{seat_number}"
    booking_record = {
        "booking_id": booking_id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "passenger_name": passenger_name,
        "price": flight["price"],
        "refundable": flight["refundable"],
        "buoi": flight["buoi"],
        "origin": flight["origin"],
        "dest": flight["dest"],
        "date": flight["date"],
        "status": "held",
        "paid": False
    }
    _BOOKINGS[booking_id] = booking_record

    return json.dumps({
        "status": "held",
        "booking_id": booking_id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "price": flight["price"],
        "refundable": flight["refundable"],
        "buoi": flight["buoi"]
    }, ensure_ascii=False)


@tool
def pay(booking_id: str, amount: int) -> str:
    """
    Thực hiện thanh toán giao dịch đặt vé sau khi đã kiểm tra quyền hạn.
    Cập nhật status sang 'confirmed' và paid = True.
    """
    booking = _BOOKINGS.get(booking_id)
    if not booking:
        return json.dumps({
            "status": "error",
            "message": f"Không tìm thấy mã đặt chỗ {booking_id}"
        }, ensure_ascii=False)
        
    if amount < booking["price"]:
        return json.dumps({
            "status": "error",
            "message": f"Số tiền thanh toán {amount:,}đ không đủ cho vé {booking['price']:,}đ"
        }, ensure_ascii=False)

    booking["paid"] = True
    booking["status"] = "confirmed"
    
    return json.dumps({
        "status": "confirmed",
        "booking_id": booking_id,
        "paid": True,
        "amount": amount
    }, ensure_ascii=False)


@tool
def get_booking(booking_id: str) -> str:
    """
    Tra cứu thông tin trạng thái đặt vé hiện tại theo mã booking_id.
    """
    booking = _BOOKINGS.get(booking_id)
    if not booking:
        return json.dumps({
            "status": "not_found",
            "message": f"Không tìm thấy mã đặt chỗ {booking_id}"
        }, ensure_ascii=False)

    return json.dumps({
        "status": "success",
        "booking": booking
    }, ensure_ascii=False)


# Danh sách 5 công cụ dùng chung cho toàn bộ dự án
TOOLS = [search_flights, check_seat, book_seat, pay, get_booking]
TOOL_MAP = {t.name: t for t in TOOLS}
