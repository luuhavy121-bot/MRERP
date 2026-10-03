# Contract Leave và Attendance hiện tại

Tài liệu này chuyên biệt hóa contract nội bộ của MRERP cho [yêu cầu Leave/Attendance](../product/leave-attendance-requirements.md).

## 1. Ownership

**Đã chốt.** MRERP sở hữu đơn nghỉ và bảng công. Leave ghi workflow đơn; Attendance chỉ đọc đơn đã duyệt để tạo projection theo tháng. Leave không ghi trực tiếp dữ liệu lương.

## 2. Capability và scope

| Capability | Phạm vi |
|---|---|
| `leave_domain.submit_leave_request` | Actor đang hoạt động tạo đơn cho chính mình |
| `leave_domain.view_own_leave_request` | Đọc đơn của chính actor |
| `leave_domain.review_team_leave_request` | Leader đọc/review đơn của thành viên Team mình lãnh đạo |
| `leave_domain.view_company_attendance` | HR đọc projection bảng công toàn công ty |
| `leave_domain.adjust_company_attendance` | HR/CEO ghi adjustment theo nhân sự/tháng, bắt buộc lý do |

**Đã chốt.** Capability được lấy từ server. Client không gửi role, Team hoặc employee UUID để tự mở scope.

## 3. Data model

`LeaveRequest` gồm UUID, requester Employee, start/end date, reason, status, reviewer, review note, reviewed time, version và timestamp. `PublicHoliday` giữ ngày lễ theo năm. `AttendanceAdjustment` giữ duy nhất một adjustment Employee/tháng, số ngày, lý do và actor. Audit dùng `AuditEvent` hiện hữu.

## 4. API v1

- `GET /api/v1/leave/requests/`: đơn của actor và, nếu có capability review, ticket thuộc Team actor lãnh đạo.
- `POST /api/v1/leave/requests/`: tạo đơn cho chính actor.
- `PATCH /api/v1/leave/requests/{uuid}/`: requester sửa ngày/lý do khi đơn còn pending, có optimistic version.
- `POST /api/v1/leave/requests/{uuid}/review/`: Leader chọn `approved` hoặc `rejected` và ghi chú tùy chọn.
- `GET /api/v1/leave/attendance/?month=YYYY-MM`: HR đọc projection bảng công.
- `POST /api/v1/leave/attendance/adjust/`: HR/CEO upsert adjustment theo Employee/tháng.

Mọi lỗi dùng error envelope chung có `code`, `detail` và `correlation_id`.

## 5. Projection bảng công

**Đã chốt theo ADR-0012.** Mỗi dòng chỉ trả Employee UUID/code/name/Team, tháng, công chuẩn sau ngày lễ, số ngày lễ, ngày nghỉ đã duyệt, adjustment và công dự kiến. Không trả field HR nhạy cảm hoặc tiền lương.

## 6. Chưa quyết định

Contract không chọn loại phép, entitlement, ca làm, nguồn máy chấm công, payroll calculation hoặc cơ chế khóa kỳ. Cách quản trị holiday calendar production theo năm vẫn cần refinement vận hành.

## 7. Contract nhập Excel theo ADR-0019

**Đã chốt:** dữ liệu thuộc `leave_domain`, độc lập với projection hiện hữu.

| Capability | Actor/scope |
|---|---|
| `leave_domain.import_attendance` | HR upload, xem trước, ghép mã, xác nhận và xem lịch sử |
| `leave_domain.view_own_actual_attendance` | Staff/Leader/HR/CEO xem bản thân |
| `leave_domain.view_team_actual_attendance` | Leader đọc nhân sự thuộc Team hiện tại mình lãnh đạo |
| `leave_domain.view_company_attendance` | HR/CEO đọc toàn công ty như baseline |

- `AttendanceImport`: UUID, filename, SHA-256, month, source JSON, baseline versions, mappings, imported_by, committed_at, replaced_count. Giữ snapshot bản nhập cũ, preview chỉ người tạo được commit.
- `AttendanceEmployeeMapping`: source_code dạng chuỗi unique, Employee one-to-one; bản đầu không đổi mapping đã lưu.
- `AttendanceRecord`: Employee/date unique, data nguồn, batch, version; row hiện hành tham chiếu đợt nhập mới nhất.
- POST `/api/v1/leave/attendance-imports/preview/`: multipart `file`; 201 trả source/errors, employee_options chỉ UUID/code/name/Team, mappings và existing_days. Không ghi bản công khi preview.
- POST `/api/v1/leave/attendance-imports/{uuid}/commit/`: `{mappings: {source_code: employee_uuid}, replace_existing: boolean}`. 200 summary; 400 validation, 403 capability, 404 preview người khác, 409 dữ liệu stale/mapping xung đột/chưa xác nhận thay thế.
- GET `/api/v1/leave/attendance-imports/`: tối đa 100 đợt đã commit mới nhất, summary HR.
- GET `/api/v1/leave/actual-attendance/?month=YYYY-MM`: danh sách Employee cơ bản, days và totals; không trả source_code/name, mapping, filename, importer hoặc hồ sơ nhạy cảm. Scope theo capability và Team hiện tại.
- Decimal nguồn lưu chuỗi hoặc null; giờ vào/ra giữ chuỗi hoặc null. Không đổi `3.48` thành giờ:phút; không có quy tắc diễn giải giờ mới.
- Commit khóa batch và Employee theo thứ tự UUID, so sánh version đã chụp khi preview. Chỉ thay ngày xuất hiện trong file; không xóa ngày khác. Audit chỉ số dòng/thay thế, không log nội dung công/PII.
- Migration thêm bảng/quyền cho group chuẩn đang có, không seed lại user và không đổi mật khẩu.

## Bổ sung ADR-0021

LeaveRequest có start_period/end_period am/pm, mặc định am→pm. API create/update giữ tương thích payload cũ, cùng ngày không cho pm→am, giới hạn 366 ngày/đơn. Overlap kiểm khoảng buổi pending/approved; create/update khóa Employee để chống đua tạo khoảng trùng. Các trường ngày công projection trả số lẻ theo 0,5 ngày. review rejected bắt buộc note; không thay ACL của HR.

GET `/api/v1/leave/requests/calendar/?month=YYYY-MM` trả uuid/name/employee_code/team_name/start_date/end_date/start_period/end_period chỉ approved trong own hoặc Team đang lãnh đạo; không reason/review_note. Employee phải còn ở Team gắn với đơn để Leader xem/duyệt. Công chuẩn thứ Hai–thứ Bảy cả ngày trừ holiday theo ADR-0021; không cập nhật AttendanceRecord.
