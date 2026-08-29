# ADR-0011: Tổng quan, Bảng tin và Công việc operational baseline

- Status: `Accepted`
- Date: `2026-08-29`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/product/dashboard-feed-task-requirements.md`, `docs/architecture/dashboard-feed-task-contract.md`
- Related open decision: `OD-14 (không đóng)`
- Supersedes: `Phần baseline tasks.read còn mở của ADR-0002`
- Superseded by: `Không có`

## Context

Người sở hữu sản phẩm yêu cầu mở lại Task và triển khai đồng thời Dashboard nội bộ cùng Newsfeed. Các quyết định về audience, moderation, recurrence, file local-media, notification retention và Goal progress đã được xác nhận trực tiếp trước khi yêu cầu triển khai.

## Decision

**Đã chốt trong phạm vi ba module:**

- Dashboard tách `Thông báo chung` và `Thông báo riêng`; chỉ đọc dữ liệu nội bộ MRERP trong request.
- Mọi employment đang hoạt động có capability Feed được đăng tới company, một hoặc nhiều Team hoặc một hoặc nhiều Employee. Company scope không kết hợp audience khác.
- Chỉ HR/CEO đánh dấu thông báo company là chính thức. Tác giả soft-delete nội dung của mình; HR/CEO moderation có audit.
- Comment có một cấp reply. Reaction cố định gồm Like, Love, Celebrate, Support và Insightful; mỗi actor có một reaction trên mỗi nội dung.
- Share tham chiếu bài gốc, không sao chép file và chỉ được thu hẹp audience. Người đọc phải đồng thời còn quyền đọc share và bài gốc.
- Staff/HR đọc Task mình tạo hoặc được giao; Leader đọc Task cá nhân và Team đang lãnh đạo; CEO đọc company scope nhưng hành động vẫn cần capability.
- Task giữ state machine ADR-0002. Goal Team/company tính progress bằng trung bình progress Task liên kết; Task hoàn thành là 100 và Goal chưa có Task là 0.
- Recurrence daily/weekly/monthly có interval, end date tùy chọn, backfill đầy đủ và idempotency theo series + scheduled time. Celery Beat dùng Redis, không lưu result backend.
- Feed/Task file tối đa 5 file, 10 MB/file, lưu local-media server bằng UUID và chỉ download qua endpoint có ACL. File soft-delete giữ 30 ngày; notification giữ 30 ngày.
- Local-media trên VPS nằm trong persistent volume và backup. Object storage production dài hạn vẫn **Chưa quyết định** theo OD-14.

## Consequences

- MRERP có thêm ba module nội bộ `dashboard_domain`, `feed_domain`, `task_domain`; không tạo microservice mới.
- Redis lỗi không làm hỏng request Feed/Task; recurrence, deadline notification và purge chậm lại rồi catch-up.
- Membership Team hiện tại quyết định audience Team; direct audience là danh sách tĩnh.
- Không có edit/pin/ranking/mention tự do, notification ngoài app, Task cancel/delete hoặc attachment tự sao chép giữa occurrence trong phạm vi này.

## Security and authorization impact

- Mọi endpoint nhạy cảm đi qua account/employment, capability, scope, object và field rule ở server.
- File không public media path; response có `nosniff`, private/no-store và safe attachment filename.
- Security/audit log không lưu token, mật khẩu hoặc payload nhạy cảm.

## Validation

- Backend authorization/API tests cho audience, share, moderation, Task scope/state, recurrence, retention và protected download.
- OpenAPI validation, migration forward/reverse/forward, frontend lint/build và ba E2E trọng yếu.
- Implementation giữ `In progress / Chờ nghiệm thu`; ADR Accepted không có nghĩa UI đã được nghiệm thu.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-29.
- Bằng chứng: yêu cầu `PLEASE IMPLEMENT THIS PLAN: Tổng quan, Newsfeed và Công việc MRERP` trong task hiện tại cùng các lựa chọn policy đã xác nhận trước đó.
