# Phase 1 — Task acceptance scenarios

Tài liệu này giữ đường dẫn tương thích cho Task acceptance. Bộ scenario hiện hành nằm tại [Acceptance Tổng quan, Bảng tin và Công việc](dashboard-feed-task-acceptance.md) và ma trận quyền tại [Task authorization matrix](../architecture/task-authorization-matrix.md).

Trạng thái implementation: `In progress / Chờ nghiệm thu`.

Task chỉ đạt khi chứng minh được read/assignment scope, field/object rule, state transition, self-task, Goal progress, recurrence idempotency/backfill/month-end, attachment ACL và audit bằng automated tests. Không đánh dấu `Accepted` trước nghiệm thu của người sở hữu sản phẩm.
