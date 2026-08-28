# ADR-0004: Mock Identity context cho Phase 1

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/identity-and-authorization.md`
- Related open decision: `OD-25`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project duyệt mock Identity chỉ dùng dev/test và không dùng login ASSETCONTROL cho Phase 1.`

## Context

- **Đã chốt:** IdP sở hữu credential/login/subject/session; MRERP ánh xạ subject với Employee và kiểm authorization ở server.
- **Đề xuất mục tiêu:** dùng Identity context giả lập có contract ổn định để phát triển People/Task mà không chọn IdP.
- **Chưa quyết định:** cách tạo actor cục bộ, cách vô hiệu hóa mock ngoài môi trường cho phép và shape contract.

## Decision drivers

- Không khóa vào một IdP cụ thể.
- Test được account/employment/capability/scope và actor audit.
- Không cho client production giả header/claim để mở quyền.
- Cùng business code nhận một interface Identity context khi đổi từ mock sang OIDC.

## Options considered

### Option A — Development/test identity adapter trong backend

- Mô tả: adapter chỉ bật trong môi trường dev/test, chọn actor từ fixture server-side và tạo normalized Identity context.
- Ưu điểm: nhẹ, deterministic, phù hợp automated test.
- Nhược điểm: cần guard cấu hình chặt để không bật nhầm production.
- Rủi ro: debug header/cookie bị tin ngoài môi trường cho phép.
- Migration/rollback: thay adapter bằng OIDC adapter, giữ normalized context contract.

### Option B — Mock OIDC Provider cục bộ

- Mô tả: chạy một IdP giả tuân OIDC cho dev/test.
- Ưu điểm: gần flow redirect/token thực tế hơn.
- Nhược điểm: thêm service/dependency và vận hành sớm.
- Rủi ro: test business chậm/phức tạp, vẫn không chứng minh IdP production.
- Migration/rollback: đổi issuer/client config khi IdP thật được chọn.

## Decision

Chọn Option A. Backend có development/test identity adapter và local login bằng session cookie. Mock account lưu password hash, không lưu plaintext; cấu hình production phải fail startup nếu mock Identity được bật. Business code chỉ nhận normalized actor context để có thể thay adapter bằng OIDC sau này. Công cụ debug có thể đổi session giữa một allow-list persona fixture phía server; client không được tự khai báo role, capability hoặc scope.

## Remaining open questions

- Claim mapping và session behavior của IdP production vẫn chưa quyết định.

## Consequences

### Positive

- Cho phép xây authorization trước khi khóa IdP.

### Negative / trade-offs

- Cần thêm contract và test chống bật nhầm mock.

### Risks and mitigations

- Privilege escalation qua header: không tin header trong production; test startup fail-closed.
- Mock khác IdP thật: contract adapter và contract tests tách biệt.

## Security and authorization impact

- Đây là quyết định security-sensitive; phải Accepted trước implementation.
- Không truyền token qua URL, không lưu access token dài hạn ở frontend.
- Actor audit phải đến từ normalized server context.

## Data and contract impact

- `identity_subject` mapping tới `employee_uuid`; không tự tạo Employee khi mapping thiếu.
- Không quyết định provider, claim mapping production hoặc session outage policy.

## Rollout and rollback

- Chỉ bật trong dev/test bằng configuration fail-closed.
- Có automated test chứng minh production configuration từ chối mock.
- Rollback bằng cách tắt adapter; không thay đổi Employee ownership.

## Validation

- Test actor hợp lệ, subject không mapping, account khóa, employment kết thúc, client spoofing và audit actor.
- Test persona switch: phải đăng nhập, chỉ nhận persona trong allow-list, session mới phản ánh đúng actor và endpoint trả `404` ngoài development/test.

## Documentation updates

- Khi Accepted, cập nhật Identity source, People contract, test strategy và local runbook.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: trả lời trực tiếp “rồi” khi được hỏi duyệt Mock Identity chỉ hoạt động dev/test, chưa dùng đăng nhập ASSETCONTROL.
