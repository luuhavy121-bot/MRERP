# Phase 1 — Task vertical slice stories

Tài liệu này chi tiết hóa EPIC-03 trong [Product backlog](../backlog.md). Nó không định nghĩa API URL, database schema hoặc frontend stack.

## 1. Outcome của slice

**Đề xuất mục tiêu.** Chứng minh một luồng Task nhỏ chạy xuyên:

```text
Identity context giả lập
    → account/employment gate
    → UI tạo và giao Task
    → API kiểm capability/scope/object/field
    → PostgreSQL lưu Task
    → audit hành động
    → UI đọc trạng thái mới
    → test allowed và denied
```

## 2. Ngoài phạm vi slice đầu tiên

**Không làm trong slice đầu:**

- Xóa/hủy Task.
- Recurring Task, dependency, checklist và attachment.
- Notification đa kênh.
- Calendar/Kanban production hoàn chỉnh.
- CRM, ASSETCONTROL hoặc MREKANBAN integration.
- Chọn Identity Provider thật.
- Tự chốt cơ cấu MRE chính thức.

## 3. Story prerequisites

### P1-PLAT-01 — Identity context giả lập

**Là một** backend MRERP, **tôi muốn** nhận identity context giả lập theo contract được duyệt **để** kiểm thử account, employment, capability và scope mà chưa chọn IdP.

Trạng thái: `Blocked` — cần ADR Identity contract.

### P1-PEOPLE-01 — Organization fixture được kiểm soát

**Là một** policy engine, **tôi muốn** có Employee, Team và quan hệ quản lý tối thiểu **để** đánh giá scope của Task.

Trạng thái: `Refining` — fixture phải được ghi là test data, không trở thành cơ cấu MRE chính thức.

## 4. Story nghiệp vụ Task

### P1-TASK-01 — Xem Task trong scope

**Là một** nhân sự đang hoạt động, **tôi muốn** xem Task thuộc scope của mình **để** biết việc cần thực hiện hoặc quản lý.

Acceptance criteria dự thảo:

- Server lấy actor và scope từ identity context đã xác thực.
- Không tin `employee_uuid`, `team_uuid` hoặc capability do client tự gửi.
- Record ngoài scope không xuất hiện trong kết quả.
- Account khóa hoặc employment không hợp lệ bị từ chối.

Trạng thái: `Refining` — baseline `tasks.read` cho Staff/Captain chưa được xác nhận riêng; chưa đạt `Ready`.

### P1-TASK-02 — Tạo Task

**Là một** nhân sự có `tasks.create`, **tôi muốn** tạo Task **để** ghi nhận một công việc có người tạo, người nhận, deadline và trạng thái.

Acceptance criteria:

- Nhân sự đang hoạt động nhận `tasks.create` qua gói capability cơ bản của MRE.
- Backend từ chối khi thiếu capability hoặc employment không hợp lệ.
- Task có UUID và audit actor do server xác định.
- Tạo Task không tự cấp quyền đọc record ngoài scope.

Trạng thái: `Refining`.

### P1-TASK-03 — Giao Task đúng scope

**Là một** người có `tasks.assign`, **tôi muốn** giao Task trong scope được phép **để** phân công công việc mà không vượt ranh giới quản lý.

Acceptance criteria:

- Staff/Captain chỉ giao cho chính mình.
- Leader giao cho thành viên team mình phụ trách.
- Manager tương lai giao trong phòng ban phụ trách; Phase 1 ban đầu không có user Manager.
- CEO có company scope nhưng vẫn phải có action capability.
- Giao ngoài scope bị từ chối và được test.

Trạng thái: `Refining`.

### P1-TASK-04 — Cập nhật theo trách nhiệm

**Là một** người tham gia Task, **tôi muốn** chỉ sửa phần thuộc trách nhiệm của mình **để** dữ liệu không bị thay đổi trái phép.

Acceptance criteria:

- Người tạo sửa tiêu đề, mô tả, deadline và người nhận trong scope.
- Người nhận sửa trạng thái thực hiện, tiến độ, bình luận và bằng chứng hoàn thành.
- Người có `tasks.manage` quản lý Task trong scope tương ứng.
- Server áp dụng field policy; payload từ client không thể mở rộng quyền.

Trạng thái: `Refining`.

### P1-TASK-05 — Gửi hoàn thành và xác nhận

**Là một** người nhận Task, **tôi muốn** gửi Task sang `Chờ xác nhận` **để** người giao kiểm tra kết quả.

**Là một** người tạo hoặc người có `tasks.accept`, **tôi muốn** chọn `Đã hoàn thành` hoặc `Yêu cầu làm lại` **để** kết thúc hoặc tiếp tục công việc.

Acceptance criteria:

- Người nhận không đóng trực tiếp Task do người khác tạo.
- Người tạo hoặc `tasks.accept` trong scope được xác nhận hoặc yêu cầu làm lại.
- Mỗi state transition ghi audit actor, thời điểm, trạng thái trước và sau.
- UI có thể dùng status dropdown nhưng backend mới quyết định transition có hợp lệ hay không.

Trạng thái: `Refining`.

### P1-TASK-06 — Task tự giao

**Là một** nhân sự tự giao Task, **tôi muốn** có người quản lý xác nhận **để** tránh tự tạo và tự công nhận kết quả.

Acceptance criteria:

- Staff/Captain tự giao → Leader có `tasks.accept` và team scope xác nhận.
- Leader tự giao → CEO có `tasks.accept` và company scope xác nhận.
- CEO không tạo Task tự giao trong workflow cần xác nhận.
- Người tạo/người nhận không được tự xác nhận Task này.

Trạng thái: `Refining`.

### P1-TASK-07 — Audit và bằng chứng từ chối

**Là một** người vận hành, **tôi muốn** hành động nhạy cảm và lần từ chối quan trọng có bằng chứng **để** điều tra lỗi quyền và thay đổi Task.

Acceptance criteria:

- Tạo, giao, thay đổi field nhạy cảm, submit, accept và request-rework có audit.
- Test bao phủ allowed, thiếu capability, ngoài scope, object state, field denial và employment không hợp lệ.
- Audit không lưu secret hoặc payload nhạy cảm không cần thiết.

Trạng thái: `Refining`.

## 5. Điều kiện chuyển story sang Ready

Áp dụng [Definition of Ready](../../testing/definition-of-ready.md). Toàn bộ story hiện chưa được đánh dấu `Ready` vì còn thiếu stack ADR, mock Identity contract và API/data contract tối thiểu.

## 6. Tài liệu liên quan

- [Ma trận quyền Task](../../architecture/task-authorization-matrix.md)
- [Acceptance scenarios](../../testing/phase-1-task-acceptance.md)
- [ADR-0002](../../decisions/0002-task-authorization-baseline.md)
- [Data ownership](../../architecture/data-ownership.md)
