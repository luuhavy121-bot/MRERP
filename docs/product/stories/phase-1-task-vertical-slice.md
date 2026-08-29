# Phase 1 — Task, Goal và Recurrence stories

Tài liệu này chi tiết hóa EPIC-03 theo [ADR-0002](../../decisions/0002-task-authorization-baseline.md) và [ADR-0011](../../decisions/0011-dashboard-feed-task-operational-baseline.md).

## Outcome

Task, Goal, Recurrence và attachment chạy xuyên UI → API → PostgreSQL → authorization → audit → worker → automated test. Implementation hiện `In progress / Chờ nghiệm thu`.

## Stories

### P1-TASK-01 — Xem Task đúng scope

- Staff/HR thấy Task mình tạo hoặc được giao.
- Leader thêm Task Team đang lãnh đạo; CEO company scope.
- Account/employment không hợp lệ, thiếu capability và record ngoài scope bị từ chối.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-02 — Tạo và giao Task

- Staff/HR chỉ tự giao; Leader giao trong Team; CEO giao toàn công ty nhưng không self-task.
- Server sở hữu creator, Team, audit actor và initial state.
- Definition fields và progress có field/object rule riêng.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-03 — Submit, accept và rework

- Assignee cập nhật progress và submit từ `Đang thực hiện/Yêu cầu làm lại`.
- Actor có `tasks.accept` đúng scope accept hoặc rework; rework cần ghi chú.
- Self-task không được tự accept theo ADR-0002.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-04 — Goal theo timebox

- Leader quản lý Goal Team; CEO quản lý Goal company và mọi Team.
- Nhân sự đọc Goal company và Team hiện tại.
- Progress là trung bình Task liên kết; completed là 100, không có Task là 0.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-05 — Recurring Task

- Daily/weekly/monthly có interval, start, deadline offset, end date tùy chọn.
- Worker backfill đủ kỳ, unique theo series + scheduled time và clamp ngày cuối tháng.
- Pause/resume/stop chỉ ảnh hưởng kỳ tương lai.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-06 — Attachment có ACL

- Brief do creator/manager đúng scope quản lý; evidence do assignee quản lý.
- Tối đa 5 file/Task, 10 MB/file; download luôn kiểm Task ACL.
- File không tự sao chép sang occurrence tiếp theo; soft-delete purge sau 30 ngày.

Trạng thái: `In progress / Chờ nghiệm thu`.

### P1-TASK-07 — Audit, notification và test

- Tạo/sửa/transition/Goal/recurrence/file có audit before/after tối thiểu.
- Assignment, review, deadline và Goal change tạo notification trong app đúng recipient.
- Test bao phủ allowed, thiếu capability, ngoài scope, object/field rule, invalid employment, idempotency và protected download.

Trạng thái: `In progress / Chờ nghiệm thu`.

## Ngoài phạm vi

- Task cancel/delete, dependency, checklist, comment/mention và Kanban production.
- Notification ngoài app.
- CRM, ASSETCONTROL hoặc MREKANBAN integration.
- Object storage production và Identity Provider production.

## Tài liệu liên quan

- [Contract ba module](../../architecture/dashboard-feed-task-contract.md)
- [Ma trận Task](../../architecture/task-authorization-matrix.md)
- [Acceptance](../../testing/dashboard-feed-task-acceptance.md)
