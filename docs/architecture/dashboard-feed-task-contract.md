# Contract Tổng quan, Bảng tin và Công việc

Tài liệu này chịu trách nhiệm chính cho data/API/authorization contract của Dashboard, Feed và Task/Goal theo [ADR-0011](../decisions/0011-dashboard-feed-task-operational-baseline.md).

## Data ownership

**Đã chốt.** MRERP sở hữu Post, audience, Comment, Reaction, Notification, Goal, Task, Recurrence và metadata attachment của ba module. Identity vẫn sở hữu credential/session; People vẫn sở hữu Employee/Team/employment.

Các domain nằm trong cùng Django deployable và chỉ tham chiếu model qua ranh giới đã biết; không tạo database/product riêng.

## Authorization

- Gate chung: authenticated account hoạt động + Employee liên kết + employment `Thử việc` hoặc `Chính thức`.
- Feed: `view/add/comment/react/share`; official và moderation là capability riêng. Read query áp audience ở database. Share cần ACL của cả share và original.
- Task: áp [ma trận Task](task-authorization-matrix.md). Progress chỉ assignee sửa; definition do creator hoặc manager đúng scope sửa; transition fail-closed.
- Goal/Recurrence: Leader giới hạn Team đang lãnh đạo; CEO company scope với action capability.
- File download luôn đánh giá ACL của parent Post/Task; metadata API không chứa filesystem path.

## API v1

- Dashboard: `GET /api/v1/dashboard/`, `POST /notifications/{uuid}/read/`, `POST /notifications/read-all/`.
- App shell tái sử dụng chính các endpoint Dashboard trên cho notification center toàn cục; không thêm endpoint hoặc bảng notification thứ hai.
- Feed: list/create/retrieve/delete Post; comment, reaction, share, audience options và protected attachment download dưới `/api/v1/feed/`.
- Task: list/create/patch Task, transition, attachment, Goal và Recurrence commands dưới `/api/v1/tasks/`.
- Contract chi tiết được sinh và validate tại `apps/mrerp/backend/openapi.yaml`.
- Error dùng envelope `code`, `detail`, `correlation_id`, `errors` tùy chọn và response header `X-Correlation-ID`.

## File contract

- Tối đa 5 file/parent, 10 MB/file.
- Cho JPEG, PNG, WebP, GIF, PDF, TXT, CSV, DOCX, XLSX, PPTX và ZIP.
- Chặn path traversal, extension/MIME mismatch, HTML, SVG, script, executable và signature cơ bản không hợp lệ.
- File lưu bằng UUID ngoài static root. Download dùng authenticated `FileResponse`, `Content-Disposition` an toàn, `nosniff` và `private, no-store`.
- Soft-deleted file purge sau 30 ngày. Persistent media volume phải nằm trong backup.

## Background processing

- Celery Beat phát lịch recurrence mỗi phút, deadline notification mỗi 15 phút và retention purge hằng ngày.
- Redis chỉ là broker; không cấu hình Celery result backend.
- Occurrence unique theo `(recurrence, scheduled_for)`. Monthly giữ anchor day và co về cuối tháng.
- Worker phục hồi backfill toàn bộ kỳ hợp lệ bị lỡ. Redis outage không chặn request CRUD.

## Data model chính

- Feed: `Post`, `PostAttachment`, `Comment`, `PostReaction`, `CommentReaction`.
- Dashboard: `Notification` với recipient, kind, target, read state và deduplication key.
- Work: `Goal`, `Task`, `TaskAttachment`, `Recurrence`; Task occurrence giữ series + scheduled time.
- Audit dùng `people_domain.AuditEvent` hiện hữu với before/after tối thiểu, không lưu file path hoặc nội dung file.
