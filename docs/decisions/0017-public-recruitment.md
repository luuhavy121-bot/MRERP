# ADR-0017: Tuyển dụng công khai và Leader quản lý ứng viên

- Status: `Accepted`
- Date: `2026-10-01`
- Deciders: Người sở hữu sản phẩm
- Related source of truth: [Yêu cầu HR mở rộng](../product/hr-expansion-requirements.md)
- Related open decision: Không đóng các open decision production hiện hữu
- Supersedes: Phần Recruitment của ADR-0013 trong phạm vi thay đổi; các miền khác giữ nguyên
- Superseded by: Không có
- Status rationale: Người dùng yêu cầu “PLEASE IMPLEMENT THIS PLAN” với kế hoạch đầy đủ trong task ngày 01/10/2026.

## Context

Triển khai Tuyển dụng và Đánh giá trước MKTLogin; tái sử dụng MRERP modular monolith.

## Decision

Leader tạo bản nháp, gửi HR/CEO duyệt; duyệt tự công khai. Leader quản lý liên hệ/CV và pipeline trong Team; chỉ HR/CEO convert Employee. Public form nhận một CV PDF/DOC/DOCX tối đa 10 MB, một kênh liên hệ, introduction và consent. Tin cũ không tự công khai. Giữ retention từ chối sáu tháng.

## Options considered

Giữ baseline cũ không đáp ứng yêu cầu. Tích hợp hệ thống HR bên ngoài tăng phụ thuộc; chọn module nội bộ theo kế hoạch được duyệt.

## Security and authorization impact

Capability độc lập với scope; account/employment gate tại server. File tải có ACL, PII không vào log. Các hành động nội bộ có audit.

## Data and contract impact

Migration thêm dữ liệu; không tự công khai bản ghi cũ. Contract OpenAPI và ma trận quyền được cập nhật.

## Rollout and rollback

Backup database và media trước migrate. Khi cần rollback, quay về build trước và giữ cột/bảng mới; không reverse migration xóa dữ liệu nếu đã có phát sinh. Mock Identity vẫn chỉ dùng local/test.

## Validation

Theo [nghiệm thu HR mở rộng](../testing/hr-expansion-acceptance.md), backend tests và E2E. Test đạt không tự thay thế nghiệm thu sản phẩm.

## Approval record

Người sở hữu sản phẩm chấp nhận kế hoạch và yêu cầu hiện thực trong task ngày 2026-10-01.
