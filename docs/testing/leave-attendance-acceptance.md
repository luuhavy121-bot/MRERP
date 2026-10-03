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
# Nhập bảng công Excel — bổ sung ADR-0019

Trạng thái: **In progress / Chờ nghiệm thu**. Fixture phải tổng hợp, không dùng file HR thật.

- HR preview → ghép mã → commit → xem từng ngày; Leader chỉ thấy Team, Staff chỉ thấy bản thân; HR/CEO thấy toàn công ty.
- Không capability, account khóa, employment không hợp lệ, preview của HR khác đều bị chặn; dữ liệu response không lộ trường nội bộ hoặc hồ sơ nhạy cảm.
- Mã có số 0 đầu, ngày/giờ, công lẻ, blank khác zero và kết quả đã tính được giữ nguyên.
- File hỏng/sai mẫu/quá lớn, công thức, số âm/sai định dạng, nhiều tháng, ngày/mã trùng, mapping thiếu/trùng không thể nhập.
- Preview không ghi công. Nhập lại phải xác nhận thay thế; retry cùng commit không ghi thêm; preview cũ trả 409 sau khi một import khác commit. Snapshot đợt cũ và audit vẫn còn.
- Công dự kiến/Leave cũ không bị thay đổi hoặc trừ lần hai. File thật chỉ đọc để đối chiếu parser, không import tự động.
- Backend test, frontend lint/build, E2E xuyên HR/Leader/Staff, OpenAPI, docs checker và diff check phải đạt trước bàn giao.

## Bằng chứng nhập Excel ngày 01/10/2026

- Parser đọc mẫu người dùng: 15 khối, 450 dòng ngày, không lỗi; chỉ đọc, không nhập dữ liệu thật.
- `docker compose run --rm --no-deps backend python manage.py test people_domain mock_identity leave_domain performance_domain recruitment_domain --noinput`: 102 tests đạt trên PostgreSQL, gồm 33 Leave/Attendance và cạnh tranh hai import trả 200/409.
- Playwright attendance-import và leave-attendance đạt với DB test riêng; fixture tổng hợp. Kiểm tra HR import, scope Leader/Staff, chi tiết công, focus bàn phím và mobile không tràn ngang trang.
- Frontend build, OpenAPI validate, migration drift, docs checker và diff check đạt. Lint không có lỗi; còn warning có sẵn ở PerformanceWorkspace ngoài phạm vi.
- Docker local được backup DB trước migration bổ sung. Đây là bằng chứng kỹ thuật, trạng thái vẫn chờ người sở hữu sản phẩm nghiệm thu.

## Demo 06/10 — bổ sung ADR-0021

Trạng thái: Implementation / Chờ nghiệm thu sản phẩm.

- Xin nghỉ sáng/chiều = 0,5; cùng ngày sáng→chiều = 1; legacy payload giữ nguyên ngày. pm→am cùng ngày bị chặn.
- Hai đơn khác buổi được phép; cùng buổi bị chặn khi create/update. Qua tháng/ngày lễ/Chủ nhật tính đúng. Thứ Bảy cả ngày tính công chuẩn.
- Leader duyệt đúng Team; không tự duyệt, không xem nhân sự đã chuyển khỏi Team gắn với đơn. Từ chối cần lý do.
- Lịch nghỉ chỉ approved theo own/Team, không reason/review_note; thiếu capability/account khóa/employment ended bị từ chối.
- Công thực tế Excel không bị trừ phép hoặc đổi khi thay lịch; công dự kiến là số lẻ và có nhãn lịch thứ Hai–thứ Bảy.
- Migration bảo toàn đơn cũ am→pm; backup trước migrate, rollback không reverse dữ liệu mới.

Bằng chứng tự động ngày 03/10: backend suite PostgreSQL và tests nửa ngày/phạm vi/lịch nghỉ đạt; E2E nhập Excel, nghỉ cả ngày và nghỉ nửa ngày thứ Bảy đạt trên DB giả riêng. Luồng nửa ngày chạy lại sau sửa control mobile đạt; Docker đã backup và migrate, không còn migration chờ. Công Excel không bị tính lại. Xem [runbook demo](../operations/local-pilot.md#kịch-bản-demo-hr-ngày-0610); vẫn chờ HR/Leader nghiệm thu.
