# Nghiệm thu HR mở rộng

Áp dụng cổng [04](../04-tieu-chi-nghiem-thu.md) và test strategy. Trạng thái chờ nghiệm thu, không tự đánh dấu Accepted khi test xanh.

- Leader tạo/sửa draft → gửi → HR duyệt → public tin → ứng viên nộp CV → Leader xem và chuyển pipeline → HR convert Employee.
- Legacy opening không public; rejected/closed/expired không xuất hiện; không rò justification/requester/storage path.
- CV định dạng/dung lượng sai bị từ chối; tải file phải qua ACL; ngoài Team/thiếu capability/inactive/terminated bị chặn.
- KPI: công thức Decimal, weight 100, thiếu completion/comment không chốt; unique tháng; stale update trả 409.
- Staff không thấy draft hoặc phiếu người khác, chỉ xác nhận own; HR/CEO xem/mở lại nhưng không tự chấm; Leader ngoài Team bị chặn.
- Reopen giữ snapshot và phản hồi cũ; bắt buộc lý do; chốt lại yêu cầu nhân sự xác nhận lại.
- Backend suite, frontend build, E2E hai luồng, docs checker và git diff --check đạt; giao diện kiểm tra desktop/mobile.

## Bằng chứng kỹ thuật 01/10/2026

- Backend suite SQLite: 114 tests đạt; sau đó bổ sung test cạnh tranh dành riêng PostgreSQL.
- PostgreSQL: 20 tests Recruitment/Performance đạt, gồm hai writer cùng version trả 200/409.
- Public CV validation/audit thay đổi cuối: hai test liên quan chạy lại PostgreSQL đạt.
- Playwright: 5 tests HR mở rộng/Phase 3 đạt; hai luồng mới chạy lại sau sửa giao diện đạt.
- Frontend production build, OpenAPI validate, makemigrations --check, docs checker và diff whitespace đạt.
- Migration đã áp dụng Docker local sau backup; /careers và public API trả HTTP 200. Chưa deploy VPS/Internet và chưa thay thế nghiệm thu người sở hữu sản phẩm.
- Giao diện desktop/mobile đã kiểm tra; reviewer độc lập xác nhận hai điểm sửa (lỗi form tại chỗ và selected row) đạt.

## Demo 06/10 — bổ sung ADR-0021

Theo [ADR-0022](../decisions/0022-short-recruitment-pipeline.md), nghiệm thu thêm: UI không có cột Đề nghị; Phỏng vấn→Đã tuyển trực tiếp, không nhảy Mới→Đã tuyển; kế hoạch sử dụng nhân sự chỉ nội bộ/draft, không vào preview/public. Kiểm tra ACL/khóa account/employment ended và convert vẫn chỉ HR/CEO. Migration offer→interview tăng version, giữ notes/history/CV; trạng thái vẫn chờ nghiệm thu sản phẩm.

Bằng chứng ADR-0022 ngày 03/10: 21 Recruitment tests đạt trên PostgreSQL (8,18 giây), gồm kiểm tra migration dữ liệu/history, chuyển trực tiếp hired, từ chối stage offer và scope/redaction của kế hoạch nội bộ. E2E Leader tạo tin có kế hoạch → HR duyệt → public nộp CV → screening → interview → hired đạt trên DB giả riêng. Build đạt; lint không có lỗi, còn warnings React; OpenAPI validate 0 lỗi/6 warnings enum buổi nghỉ. Docs/diff và migration drift đạt. Backup trước migrate được giữ local; Docker đã áp dụng migration 0004. Reviewer giao diện narrow refinement desktop/mobile trả `ship` không có material fixes; không thay nghiệm thu sản phẩm.

Trạng thái: Implementation / Chờ nghiệm thu sản phẩm.

- Leader sao chép cấu trúc KPI tháng trước, completion/comment trống; ngoài scope/Staff/account khóa bị chặn; không tự tạo phiếu. Lịch sử theo ACL, Staff không thấy draft.
- Chốt → nhân sự nhận thông báo → xác nhận → Leader nhận thông báo; HR mở lại có lý do và snapshot còn nguyên.
- Xem trước tin không xuất bản và không có justification; tìm/lọc và zero-result đúng. Hồ sơ mới vào pipeline, mở CV có ACL.
- Lưu lịch/ghi chú trong Team, stale version trả 409; terminal không sửa, timezone đúng, không tự đổi stage. Notes không vào public/projection không quản lý/audit và được xóa khi ẩn danh.
- Demo ba vai trò Leader/HR/Staff theo docs/04 và test strategy, không dùng test xanh để tự đánh dấu Accepted.

Bằng chứng tự động ngày 03/10: 152 backend tests PostgreSQL đạt; 4 Interview tests chạy lại sau sửa phạm vi notification đạt. Các luồng E2E tuyển công khai/CV/pipeline, KPI chốt–xác nhận–mở lại và lưu lịch phỏng vấn/tìm kiếm đã đạt trên DB giả riêng; hai luồng nâng cấp HR chạy lại sau sửa UI mobile đạt. Build/OpenAPI/docs/diff và migration drift đã kiểm tra. Hướng dẫn thao tác/evidence đầy đủ ở [local pilot](../operations/local-pilot.md#kịch-bản-demo-hr-ngày-0610). Trạng thái vẫn chờ nghiệm thu sản phẩm.
