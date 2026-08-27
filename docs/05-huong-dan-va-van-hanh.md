# 05 — Hướng dẫn và vận hành

Ứng dụng chưa được triển khai ở Phase 0, vì vậy hiện chưa có hướng dẫn thao tác màn hình, tài khoản production hoặc runbook sự cố có thể thực thi. Tài liệu này ghi khung vận hành cần hoàn thiện dần; chi tiết hạ tầng thuộc [Deployment và vận hành](operations/deployment.md).

## Dành cho người sử dụng

**Yêu cầu trải nghiệm đã chốt:**

1. Nhân sự mở MRERP và đăng nhập qua Identity chung.
2. Dashboard hiển thị không gian cá nhân theo quyền.
3. Người dùng mở CRM/ASSETCONTROL/MREKANBAN được cấp quyền mà không nhập lại mật khẩu.
4. Product đích vẫn tự kiểm quyền trước khi trả dữ liệu.

**Đề xuất mục tiêu:** thực hiện đăng nhập chung bằng OIDC/OAuth 2.0. Identity Provider và chi tiết session vẫn chưa quyết định.

**Chưa có ở Phase 0:** URL production đã duyệt, màn hình thật, tài khoản thật, hướng dẫn khôi phục mật khẩu và quy trình hỗ trợ người dùng.

## Dành cho người vận hành

Các runbook cần được tạo trước khi mở production:

- Deploy và rollback từng product.
- Backup và restore drill.
- IdP outage và session degradation.
- ASSETCONTROL emergency access sau khi policy được duyệt.
- CRM worker overload/queue backlog.
- Dashboard snapshot stale hoặc sync thất bại.
- Secret rotation và service credential rotation.
- Điều tra audit và sự cố lộ dữ liệu.

## Hành vi khi integration lỗi

**Đã chốt.** Dashboard vẫn hiển thị HR, Task và nghiệp vụ nội bộ; vùng dữ liệu CRM/ASSETCONTROL dùng snapshot gần nhất, timestamp và cảnh báo stale.

**Chưa quyết định.** Timeout, retry, stale threshold, SLA và escalation path cụ thể.

Không được tạo runbook break-glass có thể thực thi trước khi OD-03 được người có thẩm quyền quyết định và ADR được chấp nhận.

## Backup và phục hồi

**Đề xuất mục tiêu bắt buộc.** Backup phải nằm ngoài VPS và phải diễn tập restore. Chỉ có snapshot hoặc file backup chưa chứng minh hệ thống phục hồi được.

**Chưa quyết định.** Công cụ, retention, RPO và RTO.

## Quan sát hệ thống

**Đề xuất mục tiêu.** Cần structured logs, error tracking, uptime, resource/database/queue metrics và integration freshness.

**Chưa quyết định.** Công cụ monitoring/error tracking/reverse proxy cụ thể.

## Đọc sâu hơn

- [Deployment và vận hành](operations/deployment.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [Tích hợp hệ sinh thái](architecture/ecosystem-integration.md)
- [Open decisions](decisions/open-decisions.md)

Tiếp theo: [06 — Kế hoạch triển khai](06-ke-hoach-trien-khai.md).
