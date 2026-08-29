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
