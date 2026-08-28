# ADR-0005: People authorization và field policy Phase 1

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/identity-and-authorization.md`, `docs/architecture/people-authorization-matrix.md`
- Related open decision: `OD-22`, `OD-23`, `OD-24`, `OD-16`, `OD-05 (không giải quyết toàn bộ)`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project chốt actor, scope, field visibility và organization cardinality cho People slice ngày 28/08/2026.`

## Context

- **Đã chốt:** People data thuộc MRERP; endpoint kiểm sáu lớp quyền; cơ cấu/cấp bậc không hard-code.
- **Đề xuất mục tiêu:** capability riêng cho read/write organization/employment cùng server-owned projection.
- **Đã chốt cục bộ:** HR tạo Employee với initial status `Thử việc`; Leader chuyển `Thử việc → Chính thức`.
- **Chưa quyết định:** scope Leader, quyền People còn lại, field nào được đọc/sửa và transition khác.

## Decision drivers

- Dữ liệu Employee có độ nhạy khác nhau theo field.
- Organization mapping tác động trực tiếp tới authorization module khác.
- Tách quyền quản trị People khỏi việc có cấp bậc cao hoặc truy cập Admin Panel.
- Có thể test allowed, thiếu capability, ngoài scope và field absence.

## Options considered

### Option A — Capability + scope + named field projections

- Mô tả: action capability độc lập, scope từ server data, response dùng projection `basic`/`organization`/`employment` được duyệt.
- Ưu điểm: khớp mô hình authorization đã chốt, data minimization rõ và test được.
- Nhược điểm: cần quyết định matrix và quản trị configuration.
- Rủi ro: projection/config sai có thể lộ field hoặc làm mất quyền hợp lệ.
- Migration/rollback: version capability/projection; thu hồi config có audit.

### Option B — Hard-code quyền theo HR/Leader/CEO và serializer chung

- Mô tả: endpoint kiểm role/cấp bậc và trả một payload chung.
- Ưu điểm: ít policy ban đầu.
- Nhược điểm: mâu thuẫn source of truth, không đủ field-level authorization và khó tái sử dụng.
- Rủi ro: privilege escalation và rò rỉ dữ liệu.
- Migration/rollback: không được khuyến nghị.

## Decision

Chọn Option A trong People slice:

- HR tạo nhanh Employee bằng mã nhân sự, account và password; initial status luôn `Thử việc`.
- HR được xem/sửa hồ sơ chi tiết gồm tên hiển thị, CCCD, ngày sinh, phòng ban và địa chỉ. Field nhạy cảm không xuất hiện trong payload Staff/Leader.
- Staff xem projection cơ bản của Employee thuộc cùng Team.
- Leader xem projection cơ bản của Employee ở mọi Team, nhưng chỉ chuyển `Thử việc → Chính thức` cho Employee cùng Team mình lãnh đạo.
- Leader quản lý Department, Team, membership và Leader–Team; thay đổi organization có audit và không được tin scope do client gửi.
- Một Employee chỉ thuộc một Team tại một thời điểm; một Team có thể có nhiều Leader.
- Promotion có hiệu lực ngay và bắt buộc ghi chú.
- Captain/Manager tồn tại như rank configuration tương lai; giai đoạn đầu không có user và không tự nhận capability.
- Mã nhân sự duy nhất toàn hệ thống, theo dạng ba chữ cái viết hoa và số thứ tự, ví dụ `NDK13`.

## Remaining open questions

- Transition khác ngoài `Thử việc → Chính thức`, self-service edit, audit-reader UI và quyền Captain/Manager tương lai không thuộc slice đầu.

## Consequences

### Positive

- Khi được duyệt, People stories có thể chuyển từ Blocked sang Ready theo từng phần.

### Negative / trade-offs

- Cần nhiều test projection/scope hơn role CRUD đơn giản.

### Risks and mitigations

- Người có quyền cao được suy thành superuser: mọi action vẫn cần capability.
- Organization self-escalation: server từ chối client-provided scope và audit thay đổi mapping.
- Field leak: named projection/allow-list và absence test.

## Security and authorization impact

- Quyết định trực tiếp capability, scope, object và field policy People.
- Không quyết định IdP hoặc Admin Panel/IdP provisioning boundary.

## Data and contract impact

- API response không serialize model chung cho mọi actor.
- Employment/organization mutation cần audit và concurrency behavior.

## Rollout and rollback

- Mở capability theo story nhỏ sau khi test denied/field absence xanh.
- Mặc định không cấp capability mới nếu configuration thiếu.
- Rollback bằng thu hồi capability/projection version; không xóa audit hoặc Employee.

## Validation

- Dùng toàn bộ scenario tại `docs/testing/phase-1-people-acceptance.md`.
- Review contract diff mỗi khi thêm field.

## Documentation updates

- Khi Accepted, cập nhật People matrix, data contract, business requirements, open decisions và readiness register.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: câu trả lời trực tiếp cho 12 câu hỏi chặn People/HR trong task hiện tại.
