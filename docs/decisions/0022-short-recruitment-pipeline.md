# ADR-0022: Pipeline tuyển dụng gọn và kế hoạch sử dụng nhân sự

- Status: `Accepted`
- Date: `2026-10-03`
- Deciders: Người sở hữu sản phẩm MRERP
- Related source of truth: [HR requirements](../product/hr-expansion-requirements.md)
- Supersedes: Bước Đề nghị trong pipeline ADR-0013; không thay quyền duyệt tin ADR-0017
- Status rationale: Người dùng xác nhận nhu cầu nằm trong tin tuyển, kế hoạch là công việc dự kiến giao cho nhân sự và yêu cầu “đúng, rút ngắn đi”.

## Decision

Pipeline là Mới → Sàng lọc → Phỏng vấn → Đã tuyển; có thể Từ chối từ mỗi bước đang xử lý. Bỏ bước Đề nghị. Chuyển Đã tuyển trực tiếp từ Phỏng vấn; quyền chuyển thành Employee vẫn chỉ HR/CEO. Quy trình bản nháp → gửi → HR/CEO duyệt và xuất bản giữ nguyên.

HiringRequest thêm `utilization_plan`, văn bản nội bộ tối đa 3.000 ký tự: công việc, phần phụ trách và mục tiêu dự kiến giao cho người được tuyển. Không có bước hoặc entity kế hoạch riêng. Trường tùy chọn để bảo toàn tin cũ; chỉ sửa khi bản nháp, cùng ACL tin tuyển. Không trả trường này qua API công khai hoặc bản xem trước public.

## Migration and rollback

Backup database/media trước migrate. Hồ sơ đang Đề nghị chuyển về Phỏng vấn, tăng version để tránh lưu lịch/ghi chú từ phiên cũ. Giữ nguyên lịch sử transition, ghi chú và CV; lịch sử vẫn đọc được nhãn Đề nghị cũ. Không nhận stage offer mới qua API. Migration ngược không tự đoán hồ sơ nào từng ở Đề nghị; rollback ứng dụng giữ schema và dữ liệu bổ sung, hoặc phục hồi backup cùng mốc sau đối chiếu dữ liệu phát sinh.

## Validation

Test đường Phỏng vấn → Đã tuyển, chặn offer/nhảy bước, giữ ACL/account/employment và giới hạn convert Employee. Test lưu kế hoạch nội bộ, public redaction và migration bảo toàn lịch sử. Build, OpenAPI, docs/diff và E2E theo [acceptance](../testing/hr-expansion-acceptance.md); test xanh không thay nghiệm thu sản phẩm.
