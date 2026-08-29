# Tiêu chí nghiệm thu Phase 3

Phase 3 chỉ `Accepted` sau khi người sở hữu sản phẩm nghiệm thu. ADR Accepted hoặc test xanh không tự thay thế bước này.

## Personal Settings

- Người dùng bật/tắt social notification và preference được lưu qua API/database.
- Notification bắt buộc vẫn được tạo khi social notification bị tắt.

## Recruitment

- Leader tạo request trong Team → HR duyệt → opening xuất hiện.
- Leader ngoài Team không thấy candidate/application.
- HR chuyển pipeline đúng state và convert application `hired` thành Employee `Thử việc` đúng một lần.
- Candidate rejected quá sáu tháng được ẩn danh bởi worker.

## Documents

- Leader upload document Team; Staff trong Team tải được, người ngoài Team bị từ chối.
- Version history giữ metadata đúng; archive/soft-delete không làm file public.
- Count, size, MIME, filename và protected download đều được test.

## Recognition và Stars

- Leader gửi Recognition/cấp sao trong Team nhưng không thể tự thao tác hoặc vượt scope.
- Recognition không tự cộng sao.
- Ledger append-only, balance đúng và leaderboard không lộ transaction detail.

## Bằng chứng chung

- PostgreSQL tests, migration forward/reverse/forward, OpenAPI validation, frontend lint/build và Playwright.
- Audit cho hành động nhạy cảm và không có password/token/PII payload/file path trong audit.
- UI có loading, empty, error, forbidden và trạng thái đang lưu.

## Bằng chứng implementation ngày 29/08/2026

- 100 backend tests toàn MRERP; riêng `preferences_domain`, `recruitment_domain`, `documents_domain`, `rewards_domain` có 13 tests xanh.
- 3 Playwright E2E Phase 3 xanh: pipeline/convert Employee, Documents Team ACL và Recognition/Star/notification preference.
- OpenAPI sinh và validate không có error/warning; migration Phase 3 đã chạy forward → reverse → forward trên database tạm.
- Frontend lint/build xanh. Trạng thái vẫn là `Chờ người sở hữu sản phẩm nghiệm thu`, không tự chuyển `Accepted`.
