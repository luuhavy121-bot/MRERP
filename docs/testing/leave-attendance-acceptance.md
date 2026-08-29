# Acceptance — Leave ticket và bảng công

## Trạng thái

- **Đã chốt:** nhân sự gửi đơn, Leader duyệt theo Team, HR xem bảng công.
- **Đề xuất mục tiêu:** tự động hóa bằng API tests và một E2E trọng yếu.
- **Chưa quyết định:** policy phép/lương ngoài phạm vi được liệt kê trong yêu cầu.

## Scenarios tối thiểu

1. Staff đang hoạt động tạo đơn hợp lệ và thấy ticket `Chờ duyệt`.
2. Server từ chối ngày kết thúc trước ngày bắt đầu và đơn trùng ngày.
3. Leader của Team xem và duyệt ticket; audit chứa status trước/sau nhưng không chứa dữ liệu nhạy cảm.
4. Leader Team khác không thấy và không review được ticket.
5. Người gửi không tự review ticket.
6. HR xem bảng công theo tháng và thấy ngày nghỉ đã duyệt làm giảm công dự kiến.
7. Staff không truy cập được bảng công toàn công ty.
8. Account khóa hoặc employment không hợp lệ bị từ chối ở mọi endpoint bảo vệ.
9. Payload không thể tự đặt requester, reviewer, status hoặc audit actor.
10. Staff sửa đơn pending của mình; server từ chối đơn đã xử lý, sai owner, stale version và khoảng ngày trùng.
11. Ngày lễ Việt Nam đang hoạt động không được tính vào công chuẩn hoặc ngày nghỉ duyệt bị trừ lặp.
12. HR/CEO adjustment có lý do và audit; Staff/Leader bị từ chối; HR không nhận quyền duyệt Leave.

## Không đạt

- Frontend ẩn nút nhưng API vẫn cho review ngoài Team.
- Đơn đã review bị review lần hai.
- Bảng công rò CCCD, địa chỉ, username hoặc dữ liệu lương.
- Delivery tự thêm loại phép hoặc công thức lương.
