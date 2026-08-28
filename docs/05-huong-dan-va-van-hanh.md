# 05 — Hướng dẫn và vận hành

Repository đã có bản chạy local của People/HR Foundation trong Phase 1. Chưa có môi trường hoặc tài khoản production. Tài liệu này ghi phần có thể vận hành ở local và khung production cần hoàn thiện; chi tiết hạ tầng thuộc [Deployment và vận hành](operations/deployment.md).

## Dành cho người sử dụng

**Yêu cầu trải nghiệm đã chốt:**

1. Nhân sự mở MRERP và đăng nhập qua Identity chung.
2. Dashboard hiển thị không gian cá nhân theo quyền.
3. Người dùng mở CRM/ASSETCONTROL/MREKANBAN được cấp quyền mà không nhập lại mật khẩu.
4. Product đích vẫn tự kiểm quyền trước khi trả dữ liệu.

**Đề xuất mục tiêu:** thực hiện đăng nhập chung bằng OIDC/OAuth 2.0. Identity Provider và chi tiết session vẫn chưa quyết định.

**Đã có ở local:** đăng nhập mock bằng session cookie, danh sách/hồ sơ nhân sự theo scope, HR quick-create và chỉnh hồ sơ, Leader quản lý cơ cấu/team và xác nhận nhân sự chính thức.

Mục **Tiến độ** trong thanh điều hướng là bề mặt quản trị tạm thời: hiển thị phase, module, bằng chứng chất lượng, open decisions và cổng tiếp theo. Chỉ số lấy từ roadmap/source of truth và phải cập nhật cùng bằng chứng thực tế; mục này tự ẩn khi tổng tiến độ đạt 100%.

**Chưa có:** URL production đã duyệt, Identity production, tài khoản thật, hướng dẫn khôi phục mật khẩu và quy trình hỗ trợ người dùng.

## Chạy local

1. Backend: tạo Python 3.12 virtual environment, cài `apps/mrerp/backend/requirements.txt`, migrate và chạy server cổng 8000.
2. Seed tài khoản giả bằng lệnh `python manage.py seed_demo --password <mật-khẩu-local>`; không commit mật khẩu.
3. Frontend: cài đúng dependency từ lockfile bằng `npm ci`, sau đó `npm run dev`; Vite chạy cổng 4173 và proxy `/api` tới backend.
4. Có thể dùng `docker compose up --build` sau khi cấp `POSTGRES_PASSWORD` và `MRERP_SECRET_KEY` trong môi trường local.

Chi tiết câu lệnh nằm tại README của [backend](../apps/mrerp/backend/README.md) và [frontend](../apps/mrerp/frontend/README.md).

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
- [Quản lý cấu hình và secret](operations/configuration-and-secrets.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [Tích hợp hệ sinh thái](architecture/ecosystem-integration.md)
- [Open decisions](decisions/open-decisions.md)

Tiếp theo: [06 — Kế hoạch triển khai](06-ke-hoach-trien-khai.md).
