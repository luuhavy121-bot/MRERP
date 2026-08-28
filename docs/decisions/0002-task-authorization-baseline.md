# ADR-0002: Task authorization baseline cho Phase 1

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/identity-and-authorization.md`, `docs/architecture/task-authorization-matrix.md`
- Related open decision: `OD-04 (một phần)`, `OD-16 (không giải quyết danh mục chính thức)`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người dùng trực tiếp chọn từng phương án về cấp bậc, scope, capability, field responsibility và Task completion trong task ngày 28/08/2026.`

## Context

- **Đã chốt:** MRERP sở hữu Task và mọi endpoint nhạy cảm kiểm sáu lớp authorization ở server.
- **Đã chốt:** permission không được rút gọn thành một cột role hoặc việc ẩn nút frontend.
- **Chưa quyết định trước ADR:** capability/scope tối thiểu cho Task vertical slice.

## Decision drivers

- Đủ rõ để viết story và test permission cho một vertical slice.
- Không hard-code cấu trúc MRE vào permission core.
- Tách action capability khỏi data scope.
- Tránh CEO trở thành superuser ngầm cho mọi action.
- Cho phép Manager xuất hiện về sau mà không tạo user Manager giả ở giai đoạn đầu.

## Options considered

### Option A — Capability + scope + object/field rule

- Mô tả: cấp bậc cấu hình default bundle/scope; server kiểm capability và scope thực tế.
- Ưu điểm: phù hợp authorization model đã chốt, test được và không tin client.
- Nhược điểm: cần ma trận và policy test rõ.
- Rủi ro: cấu hình sai organization có thể tạo scope sai.
- Migration/rollback: sửa company configuration/assignment có audit; không đổi permission core tùy tiện.

### Option B — Một role quyết định toàn bộ quyền

- Mô tả: Staff/Leader/CEO được hard-code trực tiếp trong endpoint.
- Ưu điểm: ít cấu hình ban đầu.
- Nhược điểm: mâu thuẫn mô hình capability đa chiều và khó tái sử dụng.
- Rủi ro: privilege escalation, policy phân tán và khó test.
- Migration/rollback: không được chọn.

## Decision

Chọn Option A trong phạm vi Task Phase 1:

- Captain có permission nền giống Staff.
- Leader có team scope cho Task.
- Manager tương lai có department scope; giai đoạn đầu không có user Manager và Leader không bị tự nâng cấp.
- CEO có company data scope nhưng từng action vẫn cần capability.
- `tasks.create` thuộc gói capability cơ bản của employment đang hoạt động.
- Staff/Captain chỉ tự giao; Leader giao trong team; Manager tương lai trong department; CEO trong company scope.
- Creator sửa definition fields; assignee sửa execution fields; `tasks.manage` chỉ có hiệu lực trong scope.
- Assignee submit `Chờ xác nhận`; creator hoặc người có `tasks.accept` trong scope chọn hoàn thành/rework.
- Self-task không được tự accept: Staff/Captain do Leader xác nhận, Leader do CEO xác nhận; CEO self-task không thuộc workflow slice.

Core authorization phải đánh giá capability/scope từ server data. Tên cấp bậc chỉ là company configuration cho default assignment.

## Remaining open questions

- Baseline `tasks.read` đầy đủ cho Staff/Captain.
- Hủy/xóa, reopen, overdue escalation, delegation và comment visibility.
- OD-04 vẫn mở cho ranh giới cấp bậc ngoài Task.
- OD-16 vẫn mở cho danh sách organization/capability chính thức.
- OD-05 và OD-19 không được giải quyết bởi ADR này.

## Consequences

### Positive

- Có permission baseline đủ để viết story và scenario cụ thể.
- CEO scope và action capability được tách rõ.
- Captain không tạo nhánh quyền không cần thiết.
- Manager có thể được thêm sau mà không tạo dữ liệu giả ban đầu.

### Negative / trade-offs

- Cần organization mapping và relationship data chính xác.
- Self-task có thêm bước xác nhận quản lý.
- Story read-list chưa Ready cho đến khi baseline `tasks.read` được xác nhận.

### Risks and mitigations

- Scope sai do client gửi: server bỏ qua client role/team/scope.
- Capability còn khi employment kết thúc: account/employment gate chạy trước action check.
- UI dropdown gửi transition sai: server state machine fail-closed.

## Security and authorization impact

- Áp dụng account/employment, action, scope, object và field check cho Task.
- Tạo/giao/sửa/submit/accept/rework phải có audit phù hợp.
- Không truyền hoặc lưu credential/token mới.

## Data and contract impact

- MRERP tiếp tục sở hữu Task UUID và workflow state.
- Cần server-owned creator/assignee/audit actor identifiers.
- API/schema cụ thể chưa được ADR này chọn.

## Rollout and rollback

- Chỉ hiện thực sau khi story đạt Definition of Ready và Phase 1 được mở.
- Dùng fixture organization được duyệt cho test; không import data production.
- Nếu matrix chưa đủ, giữ story `Blocked/Refining`; không nới quyền để chạy demo.

## Validation

- Áp dụng toàn bộ scenario tại `docs/testing/phase-1-task-acceptance.md`.
- Endpoint nhạy cảm có allowed, thiếu capability, ngoài scope, field denial, object state và invalid employment test.

## Documentation updates

- Thêm backlog, Task stories, Definition of Ready, Task authorization matrix và acceptance scenarios.
- Cập nhật identity/authorization, business requirements, roadmap, open decisions và docs index.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: người dùng trực tiếp chọn backlog theo Epic toàn roadmap và story chi tiết Phase 1; xác nhận Captain bằng Staff, Leader theo team, Manager tương lai theo phòng ban nhưng ban đầu không có user Manager, CEO theo toàn công ty nhưng vẫn cần capability; đồng thời chọn policy tạo/giao/sửa/xác nhận/self-task được mô tả trong ADR này.
