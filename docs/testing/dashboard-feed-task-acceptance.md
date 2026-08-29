# Acceptance — Tổng quan, Bảng tin và Công việc

Trạng thái implementation: `In progress / Chờ nghiệm thu`.

## Điều kiện đạt

- Dashboard tách đúng general/private, unread/read-all không tác động recipient khác và không gọi integration ngoài MRERP.
- Feed không rò post ngoài audience; share không mở rộng; official/moderation đúng HR/CEO; comment/reaction/delete và tombstone đúng policy.
- File vượt count/size, sai MIME/signature, HTML/SVG/path traversal bị từ chối; download ngoài ACL trả 403/404 và không lộ storage path.
- Task đúng scope Staff/HR/Leader/CEO; progress/definition/transition/self-task fail-closed; Goal progress tính đúng.
- Recurrence daily/weekly/monthly backfill đủ, idempotent, clamp month-end và pause/stop đúng.
- Notification và soft-deleted file purge sau 30 ngày.
- Migration forward → reverse → forward chạy trên database tạm; OpenAPI, backend test, frontend lint/build và E2E đều qua.

## E2E tối thiểu

1. Staff đăng company post có ảnh; actor khác comment/reaction/share; HR moderation.
2. Leader tạo Goal + recurring Task + attachment; Staff cập nhật/submit; Leader accept; Goal đạt 100%.
3. Hai persona thấy đúng general/private Dashboard và không rò direct/team notification.
4. Notification center hiển thị trên mọi tab, dùng đúng unread count/scope phía server; theme sáng/tối được giữ sau reload và không thay đổi quyền.

## Điều kiện không đạt

- Frontend ẩn nút nhưng API vẫn cho phép hành động ngoài capability/scope.
- Share mở rộng audience, direct/team item xuất hiện sai persona hoặc file tải bằng URL public.
- Worker sinh occurrence trùng, bỏ kỳ khi phục hồi hoặc Redis outage làm hỏng request Feed/Task.
- Đánh dấu story `Accepted`/100% khi chưa có nghiệm thu của người sở hữu sản phẩm.
