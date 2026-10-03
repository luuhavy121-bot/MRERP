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

## Sao & Đổi thưởng — ADR-0020

**Trạng thái: Implementation hoàn tất / Chờ nghiệm thu sản phẩm.** Bằng chứng baseline ngày 29/08 không thay thế kiểm tra phần mở rộng này.

- Ghi nhận nằm trong pane nhân sự/tháng tại Đánh giá nhân sự; đổi nhân sự/tháng không giữ nhầm nội dung cũ; không đổi KPI hoặc tự cộng sao. Navigation hiển thị Sao & Đổi thưởng.
- HR/CEO ghi nhận theo capability riêng, kể cả không được sửa KPI và nhân sự chưa có phiếu. Staff chưa có phiếu vẫn xem ghi nhận own theo tháng. Danh sách yêu cầu đổi thưởng tải đủ các trang, không âm thầm bỏ yêu cầu sau giới hạn trang đầu.
- HR/CEO tạo/sửa/ngừng quà, đặt hạn mức Team; Staff/Leader bị từ chối endpoint quản trị. Mẫu gợi ý không tự kích hoạt quà/tồn/giá tiền.
- Leader chỉ cấp dương cho người khác trong Team có hạn mức tháng, không vượt quota kể cả hai request đồng thời. Hạ quota dưới số đã dùng bị từ chối; HR/CEO giảm sao không làm âm số dư.
- Nhân sự đủ sao/tồn gửi yêu cầu, số dư khả dụng giảm và held tăng; tên/chi phí snapshot đúng. Không đủ sao, hết tồn, quà ngừng hoạt động hoặc chi phí đã thay đổi bị từ chối mà không để lại hold/tồn lệch.
- Retry cùng request key không giữ sao/tồn lần hai; key khác nội dung bị từ chối. Cạnh tranh đổi quà không gây âm số dư/tồn.
- HR/CEO khác duyệt → xác nhận trao; held về 0 mà không trừ lần hai. Không tự duyệt/từ chối/trao, không sai state hoặc xử lý ngoài scope.
- Hủy pending/approved bởi own hoặc manager, từ chối pending bởi manager khác: bắt buộc lý do và hoàn sao/tồn đúng một lần kể cả retry; không hủy fulfilled.
- Staff/Leader chỉ nhận yêu cầu own, HR/CEO nhận company; ledger vẫn own và leaderboard không bị hold/refund làm thay đổi điểm. Account khóa/employment không hợp lệ bị chặn ở mọi endpoint nhạy cảm.
- Có evidence migration forward/reverse/forward trên DB tạm, contract validation, backend authorization/concurrency, lint/build và E2E tạo quà → đổi → duyệt → trao/hủy. Rollback dữ liệu thật giữ schema hoặc restore backup, không reverse xóa yêu cầu/ledger mới.

## Bằng chứng chung cho mọi slice

- PostgreSQL tests, migration forward/reverse/forward, OpenAPI validation, frontend lint/build và Playwright.
- Audit cho hành động nhạy cảm và không có password/token/PII payload/file path trong audit.
- UI có loading, empty, error, forbidden và trạng thái đang lưu.

## Bằng chứng implementation ngày 29/08/2026

- 100 backend tests toàn MRERP; riêng `preferences_domain`, `recruitment_domain`, `documents_domain`, `rewards_domain` có 13 tests xanh.
- 3 Playwright E2E Phase 3 xanh: pipeline/convert Employee, Documents Team ACL và Recognition/Star/notification preference.
- OpenAPI sinh và validate không có error/warning; migration Phase 3 đã chạy forward → reverse → forward trên database tạm.
- Frontend lint/build xanh. Trạng thái vẫn là `Chờ người sở hữu sản phẩm nghiệm thu`, không tự chuyển `Accepted`.

## Bằng chứng mở rộng ngày 02/10/2026

- Hai Playwright E2E dùng backend thực trên SQLite cô lập đạt: HR cấu hình quà/hạn mức → Leader cấp sao/ghi nhận → Staff đổi quà → HR duyệt/trao; luồng Recognition/preferences hiện có đã cập nhật và đạt.
- PostgreSQL: lượt cuối đạt 18/18 test Rewards, không bỏ qua test; gồm cạnh tranh hạn mức và đơn vị tồn cuối. SQLite E2E không thay thế kiểm chứng khóa đồng thời PostgreSQL.
- Frontend build đạt. Finish review desktop/mobile đạt sau sửa quyền Recognition độc lập KPI và đọc đủ trang yêu cầu đổi quà.
- Docker local đã cập nhật sau backup và migration.
- Đây là bằng chứng kỹ thuật trong task, không tự chuyển sang nghiệm thu sản phẩm `Accepted`.
