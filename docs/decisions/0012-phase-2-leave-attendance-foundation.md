# ADR-0012: Nền Leave và Attendance đơn giản cho Phase 2

- Status: `Accepted`
- Date: `2026-08-29`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/product/leave-attendance-requirements.md`
- Related open decision: `OD-13 (chỉ giải quyết một phần; payroll và policy phép chi tiết vẫn mở)`
- Supersedes: `Không có`
- Superseded by: `ADR-0021 chỉ ở giới hạn nguyên ngày và lịch thứ Hai–thứ Sáu; các policy khác giữ nguyên`
- Status rationale: `Người sở hữu sản phẩm xác nhận trực tiếp phạm vi nền trong task ngày 29/08/2026.`

## Context

- **Đã chốt:** Nhân sự gửi đơn xin nghỉ; Leader duyệt một cấp; đơn được duyệt thì ngày đó được tính là nghỉ. HR giám sát và điều chỉnh bảng công. Ngày lễ theo lịch Việt Nam. Tích hợp máy chấm công làm sau.
- **Đề xuất mục tiêu của foundation:** Chỉ cho sửa đơn khi `Chờ duyệt`; adjustment theo tháng là số ngày nguyên có thể âm/dương và bắt buộc lý do.
- **Chưa quyết định:** Loại phép, hạn mức, nửa ngày/theo giờ, có lương/không lương, công thức lương và dữ liệu máy chấm công.

## Decision drivers

- Có nền UI → API → database → authorization → audit → test trước khi mở policy chi tiết.
- Không xây approval engine tổng quát khi mới chỉ có một workflow thực tế.
- Giữ Attendance là projection vận hành, không biến thành Payroll.

## Options considered

### Option A — Nền Leave/Attendance cục bộ, đơn giản

- Mô tả: Mở rộng module hiện tại bằng edit pending, holiday calendar và HR adjustment.
- Ưu điểm: Ít model, dễ test, phù hợp quy trình hiện tại.
- Nhược điểm: Chưa xử lý ca làm, entitlement hoặc payroll.
- Rủi ro: Lịch ngày lễ thay đổi theo năm; cần nạp baseline hằng năm.
- Migration/rollback: Hai bảng mới, có reverse migration; không thay đổi LeaveRequest cũ.

### Option B — Approval/Attendance engine tổng quát

- Mô tả: Xây workflow nhiều cấp, policy engine, ca làm và payroll input đầy đủ ngay.
- Ưu điểm: Nhiều khả năng mở rộng.
- Nhược điểm: Chưa có policy thực tế; tăng rủi ro xây sai.
- Rủi ro: Overengineering và tạo abstraction không có consumer.
- Migration/rollback: Phức tạp, không phù hợp giai đoạn nền.

## Decision

Chọn Option A. Leave giữ state machine `Chờ duyệt → Đã duyệt/Từ chối`; chỉ requester được sửa đơn `Chờ duyệt`. Attendance loại ngày lễ đang hoạt động khỏi công chuẩn, trừ ngày nghỉ đã duyệt và cộng adjustment HR. HR không nhận capability duyệt Leave.

Baseline 2026 dùng lịch nghỉ do Chính phủ/Bộ Nội vụ công bố; doanh nghiệp có thể có phương án liền kề/hoán đổi khác nên adjustment giữ vai trò bù sai khác trong foundation.

## Remaining open questions

- OD-13 vẫn mở cho policy phép và lương.
- Lịch làm việc theo ca và tích hợp máy chấm công làm sau.
- Cơ chế quản trị holiday calendar hằng năm sẽ refinement khi cần vận hành production.

## Consequences

### Positive

- Có luồng nghỉ → duyệt → công dự kiến đơn giản và giải thích được.
- HR điều chỉnh có lý do/audit mà không sửa record nguồn.

### Negative / trade-offs

- Chỉ hỗ trợ ngày nguyên và một cấp duyệt.
- Holiday calendar cần được nạp theo năm.

## Security and authorization impact

- Requester chỉ sửa đơn của mình khi pending.
- Leader chỉ duyệt Team lãnh đạo; không tự duyệt.
- HR/CEO có capability adjustment; Staff/Leader không có.
- Audit không lưu reason nội dung của Leave/adjustment.

## Data and contract impact

- Thêm `PublicHoliday` và `AttendanceAdjustment` trong `leave_domain`.
- Thêm PATCH Leave pending và POST Attendance adjustment.
- Projection thêm holiday days, adjustment days/reason và công dự kiến sau adjustment.

## Rollout and rollback

- Migration forward tạo bảng và seed baseline 2026.
- Reverse xóa chỉ holiday seed do migration sở hữu rồi gỡ hai bảng.
- LeaveRequest hiện hữu không bị rewrite.

## Validation

- Test edit allowed/denied/object state/version/overlap.
- Test holiday giảm công chuẩn.
- Test HR adjustment, Staff denial và audit data minimization.
- E2E Staff sửa đơn → Leader duyệt → HR xem/điều chỉnh.

## Approval record

- Người chấp nhận: Người sở hữu sản phẩm MRERP
- Ngày chấp nhận: 29/08/2026
- Bằng chứng/xác nhận: Task hiện tại — các xác nhận 1–6 về Leave, ngày lễ, HR, một cấp duyệt, edit và máy chấm công.
