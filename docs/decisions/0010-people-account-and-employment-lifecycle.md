# ADR-0010: People account và employment lifecycle

- Status: `Accepted`
- Date: `2026-08-29`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/people-data-contract.md`, `docs/architecture/people-authorization-matrix.md`
- Related open decision: `OD-04`, `OD-05`, `OD-19`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người dùng xác nhận gói quyền và yêu cầu triển khai toàn bộ trong task ngày 29/08/2026.`

## Context

- **Đã chốt:** People Foundation có Employee tùy chọn account, Team và promotion nhưng chưa có account/employment lifecycle hoàn chỉnh.
- **Đã chốt mới:** cần cấp/khóa/mở/reset account, offboarding, self profile, history, audit, import/export và quản trị access.
- **Chưa quyết định:** Identity Provider production; adapter mock không được biến thành IdP production.

## Decision drivers

- Ngăn account còn quyền sau khi nhân sự nghỉ việc.
- Giữ credential ngoài Employee và ngoài audit/log.
- Áp dụng least privilege theo company/managed-team/self scope.
- Có lịch sử thay vì ghi đè không dấu vết.

## Decision

- CEO có toàn quyền People, account, access bundle và audit.
- HR quản lý Employee; cấp/khóa/mở/reset account toàn công ty; thay đổi employment lifecycle; import/export và xem audit Employee/account.
- Leader tiếp tục quản lý Team, promotion và được reset mật khẩu account của nhân sự trong Team mình lãnh đạo; không cấp/khóa account hoặc sửa access bundle.
- Staff tự sửa tên hiển thị, ngày sinh và địa chỉ; không sửa CCCD, mã nhân sự, Team, employment hoặc capability. Phần tài khoản/bảo mật nằm trong trang `Hồ sơ của tôi`.
- `Nghỉ việc` khóa account, thu hồi group/capability và giữ Employee/history; kích hoạt lại phục hồi bundle đã lưu. `Tạm nghỉ` khóa account nhưng giữ bundle.
- Mật khẩu tạm do server tạo, chỉ trả trong response thành công một lần và không được lưu vào Employee/audit/log.
- Import/export dùng CSV, không nhận/xuất password.
- Admin access bundle chỉ dành cho CEO; scope Team vẫn lấy từ organization relation phía server.
- Credential operation đi qua Identity adapter. Adapter hiện tại chỉ hoạt động khi Mock Identity development/test được bật; production provider vẫn bị fail-closed.

## Remaining open questions

- IdP production, provisioning/deprovisioning contract và account recovery production vẫn thuộc OD-19.
- MFA, session revocation liên product, retention/anonymization và HR data catalog mở rộng chưa quyết định.
- Reward administration trong OD-05 không được giải quyết bởi ADR này.

## Security and authorization impact

- Account/employment gate, action capability, data scope, object rule và field policy chạy tại server.
- Leader reset password chỉ với target trong Team đang lãnh đạo; không được tự reset qua endpoint quản trị.
- Access bundle không nhận capability tùy ý từ client và CEO không được tự hạ quyền chính mình.
- Password không xuất hiện trong audit, structured log, CSV hoặc payload đọc lại.

## Data and contract impact

- Mở rộng employment status bằng `Tạm nghỉ` và `Nghỉ việc`.
- Thêm lịch sử membership và trạng thái account cần cho offboarding/restore.
- Employee vẫn là nguồn chuẩn hồ sơ; Identity adapter vẫn sở hữu thao tác credential.

## Rollout and rollback

- Migration additive; backfill lịch sử không giả định dữ liệu production.
- Kiểm tra forward → reverse → forward trên database tạm.
- Rollback schema sau khi có lifecycle data cần backup và đánh giá riêng.

## Validation

- Test allowed, thiếu capability, ngoài scope, self/object rule, invalid employment và field absence.
- E2E cho self profile, HR account lifecycle, Leader team password reset và offboarding.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 29/08/2026.
- Bằng chứng/xác nhận: người dùng xác nhận gói quyền được đề xuất, bổ sung Leader/HR reset password, đặt tài khoản cá nhân bên trong `Hồ sơ của tôi`, sau đó yêu cầu “triển khai”.
