# ADR-0006: Employee và Identity account provisioning

- Status: `Superseded`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/identity-and-authorization.md`, `docs/architecture/people-data-contract.md`
- Related open decision: `OD-19`
- Supersedes: `Không có`
- Superseded by: `ADR-0007`
- Status rationale: `ADR-0007 cho phép HR tạo Employee mà chưa tạo account; phần compensation khi có chọn tạo account vẫn được giữ lại.`

## Context

- **Đã chốt:** HR nhập mã nhân sự, tài khoản, mật khẩu khởi tạo và trạng thái; HR chỉ tạo `Thử việc`.
- **Đã chốt:** IdP sở hữu credential; MRERP sở hữu Employee và không được lưu password.
- **Đã chốt:** khi HR bấm Lưu, account và Employee phải được tạo/liên kết trong cùng thao tác nghiệp vụ; chỉ báo thành công khi cả hai sẵn sàng.
- **Đã chốt:** nếu một bước thất bại, không tạo Employee và không báo thành công.
- **Chưa quyết định:** thứ tự gọi, idempotency, xử lý account đã tạo dở và password delivery/reset khi có lỗi một phần.

## Decision drivers

- Không lưu/log/audit password trong MRERP.
- Không để account IdP hoặc Employee mồ côi âm thầm khi một bước lỗi.
- Retry không tạo trùng account/Employee.
- HR nhận kết quả rõ nhưng không thấy credential sau khi submit ngoài policy được duyệt.
- Không khóa implementation vào IdP cụ thể trước OD-01.

## Options considered

### Option A — MRERP orchestration tạo account rồi Employee

- Mô tả: backend MRERP nhận command, gọi IdP provisioning adapter và tạo Employee/mapping theo workflow idempotent.
- Ưu điểm: một thao tác cho HR, phù hợp trải nghiệm form được yêu cầu.
- Nhược điểm: không có distributed transaction; cần compensation/orphan reconciliation.
- Rủi ro: IdP thành công nhưng database MRERP lỗi, hoặc ngược lại.
- Migration/rollback: disable/reconcile account theo command ID và audit, không rollback bằng cách lưu password.

### Option B — Tạo Employee trước, account provisioning riêng

- Mô tả: HR tạo Employee `Thử việc`; account được tạo/mapping ở bước sau bởi workflow được ủy quyền.
- Ưu điểm: tách lỗi, MRERP People không giữ password trong request chính.
- Nhược điểm: hai bước, Employee có thể chưa đăng nhập ngay.
- Rủi ro: hồ sơ chờ mapping lâu hoặc mapping nhầm subject.
- Migration/rollback: trạng thái provisioning rõ và reconciliation queue/manual workflow.

## Decision

Chọn Option A cho mock Identity Phase 1:

1. Backend kiểm HR capability và validate payload.
2. Mock Identity tạo account đang active bằng username/password HR nhập.
3. MRERP tạo Employee `Thử việc` và mapping subject trong database transaction.
4. Chỉ trả thành công khi cả account và Employee đã tạo/liên kết.
5. Nếu tạo Employee thất bại, xóa account vừa tạo; nếu cleanup lỗi, ghi critical audit/log không chứa password và không tạo Employee.
6. Retry dùng idempotency/unique constraint để không tạo trùng.
7. Không bắt buộc đổi password lần đăng nhập đầu trong slice này.

## Remaining open questions

- Username format, uniqueness và recovery policy.
- Ai được retry, disable hoặc sửa mapping.

## Consequences

### Positive

- Khi Accepted, P1-PPL-04 có contract rõ để chuyển gần `Ready`.

### Negative / trade-offs

- Orchestration an toàn phức tạp hơn một database transaction.

### Risks and mitigations

- Password leak: dùng secret-safe request handling, redaction và không persistence/logging.
- Duplicate provisioning: idempotency key và uniqueness ở cả adapter/data layer.
- Orphan state: trạng thái provisioning, audit và reconciliation/compensation.

## Security and authorization impact

- Chỉ HR có capability create được gọi workflow; server không tin chức danh từ client.
- Credential chỉ đi tới IdP adapter qua kênh được bảo vệ; không trả lại trong API response/log.
- ADR không chọn IdP cụ thể.

## Data and contract impact

- Employee có mapping subject hoặc provisioning state tối thiểu theo phương án được chọn.
- Password không phải Employee field.
- API cần idempotency và error envelope không lộ credential.

## Rollout and rollback

- Dev/test dùng mock adapter sau ADR-0004.
- Có test từng failure point trước khi nối IdP thật.
- Không bật production provisioning cho tới khi OD-01/OD-19 và runbook liên quan được chốt.

## Validation

- Success, duplicate retry, IdP fail, MRERP fail-after-IdP, redacted logs/audit và unauthorized actor tests.

## Documentation updates

- Khi Accepted, cập nhật People data contract, Identity source, operations runbook và readiness register.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: người dùng xác nhận account tạo ngay, account dang dở bị xóa, không bắt buộc đổi password và account thử việc hoạt động ngay.
