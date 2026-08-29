# Yêu cầu Tổng quan, Bảng tin và Công việc

Tài liệu này là source of truth nghiệp vụ cho ba module được mở cùng nhau theo [ADR-0011](../decisions/0011-dashboard-feed-task-operational-baseline.md). Contract kỹ thuật nằm tại [Dashboard–Feed–Task contract](../architecture/dashboard-feed-task-contract.md).

## Trạng thái

- **Đã chốt:** yêu cầu và policy trong ADR-0011.
- **In progress / Chờ nghiệm thu:** implementation hiện tại.
- **Chưa quyết định:** object storage production dài hạn theo OD-14.

## Tổng quan

- Sau đăng nhập mở Tổng quan mặc định.
- `Thông báo chung` chứa hướng dẫn dùng app và bài company-scope; thông báo chính thức HR/CEO được làm nổi bật.
- `Thông báo riêng` chứa bài Team/direct, tương tác Feed, Task/Goal, kết quả đơn nghỉ và cảnh báo account của chính actor.
- Trung tâm thông báo nằm ở app shell để người dùng xem số chưa đọc và mở thông báo từ mọi tab; Dashboard và app shell dùng cùng nguồn dữ liệu, không tạo notification store cạnh tranh.
- Personal Settings trên app shell cho phép đổi nền sáng/tối cục bộ và đăng xuất. Theme là preference trình bày trên thiết bị, không ảnh hưởng authorization hoặc dữ liệu server.
- Người dùng xem unread count, đánh dấu từng item hoặc tất cả đã đọc. Notification lưu 30 ngày.
- Dashboard không gọi CRM hoặc ASSETCONTROL đồng bộ.

## Bảng tin

- Employment đang hoạt động được đăng text/file tới company, Team hoặc Employee theo capability.
- Company scope độc lập; Team và Employee có thể kết hợp. Team dùng membership hiện tại; Employee direct là danh sách tĩnh.
- Chỉ HR/CEO đánh dấu thông báo chính thức.
- Feed mới nhất trước và phân trang phía server; không ranking thuật toán.
- Post phải có text hoặc file; tối đa 5 file, 10 MB/file. Allow-list và quy tắc MIME nằm trong contract kỹ thuật.
- Comment có một cấp reply. Reaction cố định và duy nhất theo actor/content.
- Share giữ tham chiếu bài gốc và audience chỉ được thu hẹp. Bài gốc bị xóa hiển thị tombstone và file không tải được.
- Tác giả soft-delete nội dung của mình; HR/CEO moderation mọi nội dung có audit. Comment đã xóa giữ tombstone cho reply.

## Công việc và mục tiêu

- Staff/HR đọc Task mình tạo hoặc được giao; Leader thêm Team đang lãnh đạo; CEO company scope.
- Staff/HR chỉ tự giao; Leader giao trong Team; CEO giao toàn công ty nhưng không tạo self-task.
- Task có title, description, creator, assignee, Team, deadline ngày+giờ, progress 0–100, Goal tùy chọn và audit metadata.
- State machine và self-task áp dụng ADR-0002; người nhận submit, actor có `tasks.accept` đúng scope accept/rework.
- Goal scope Team/company, period ngày/tuần/tháng/quý. Leader quản lý Goal Team; CEO quản lý Goal company và mọi Team.
- Goal progress là trung bình Task liên kết cùng scope/timebox; completed luôn 100, không có Task là 0.
- Recurrence daily/weekly/monthly có interval, start time, deadline offset, end date tùy chọn và pause/resume/stop. Worker backfill đủ kỳ bị lỡ và không sinh trùng.
- Attachment là brief hoặc evidence, có cùng giới hạn và ACL download với Feed. File không tự sao chép sang occurrence sau.

## Không làm trong phạm vi này

- Edit/pin/ranking Feed, mention tự do hoặc notification ngoài app.
- Task cancel/delete, dependency, checklist hoặc Kanban production.
- Object storage production, antivirus product cụ thể hoặc CDN media.
- CRM/ASSETCONTROL integration hoặc lựa chọn Identity Provider.
