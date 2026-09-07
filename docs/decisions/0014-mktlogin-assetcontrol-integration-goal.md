# ADR-0014: Mục tiêu tích hợp MKTLogin với ASSETCONTROL

- Status: `Accepted`
- Date: `2026-09-03`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/product/product-overview.md`, `docs/architecture/data-ownership.md`, `docs/architecture/ecosystem-integration.md`, `docs/product/roadmap.md`
- Related open decision: `OD-27 (không đóng)`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu sản phẩm xác nhận trực tiếp phạm vi sản phẩm và đích tích hợp; chi tiết contract vẫn chưa được quyết định.`

## Context

Công ty hiện dùng MKTLogin trong hoạt động Marketing và xác nhận MKTLogin có API. Mục tiêu không phải xây lại sản phẩm này mà là làm cho tài nguyên được quản lý trong ASSETCONTROL liên kết thực sự với tài nguyên tương ứng trong MKTLogin.

- **Đã chốt:** ASSETCONTROL sở hữu Resource, Grant, Vault và audit; MRERP sở hữu Employee, Team và capability cấp hệ sinh thái; không product nào đọc database chéo.
- **Đã chốt trong task hiện tại:** chỉ MKTLogin thuộc phạm vi; không cần quan tâm MKT City; MKTLogin có API; không clone đầy đủ MKTLogin.
- **Chưa quyết định:** chi tiết API, resource mapping, quyền thao tác, đồng bộ, security, failure handling và rollback.

## Decision drivers

- Người quản lý cần biết Resource ASSETCONTROL tương ứng với resource thật nào trong MKTLogin.
- Không tạo một sản phẩm cạnh tranh hoặc nguồn dữ liệu vận hành thứ hai.
- Giữ secret/session khỏi MRERP và tôn trọng data ownership hiện có.
- Có thể cấp, kiểm tra và thu hồi quyền với audit sau khi contract được duyệt.
- Integration phải thất bại an toàn khi MKTLogin không phản hồi.

## Options considered

### Option A — Clone đầy đủ MKTLogin vào hệ sinh thái

- Ưu điểm: kiểm soát toàn bộ giao diện và code.
- Nhược điểm: trùng sản phẩm đang dùng, phạm vi rất lớn, phải tự duy trì trình duyệt và cơ chế vận hành nhạy cảm.
- Kết quả: không chọn.

### Option B — Chỉ lưu đường link hoặc tên thủ công

- Ưu điểm: triển khai nhanh.
- Nhược điểm: không chứng minh resource còn tồn tại hoặc đúng đối tượng; không đồng bộ lifecycle; dễ lệch dữ liệu.
- Kết quả: có thể dùng làm bước điều hướng tạm thời nhưng không đạt mục tiêu cuối.

### Option C — ASSETCONTROL liên kết MKTLogin qua API

- Ưu điểm: giữ đúng product boundary, dùng sản phẩm hiện có và tạo quan hệ kiểm chứng được.
- Nhược điểm: phụ thuộc contract, giới hạn và độ ổn định của API nhà cung cấp.
- Kết quả: được chọn làm mục tiêu.

## Decision

Chọn Option C:

- Chỉ MKTLogin thuộc integration scope; MKT City nằm ngoài phạm vi hiện tại.
- Không clone đầy đủ MKTLogin vào MRERP hoặc ASSETCONTROL.
- MKTLogin sở hữu môi trường/tài nguyên vận hành thực tế của nó.
- ASSETCONTROL sở hữu Resource/Grant/Vault/audit và giữ mapping có định danh tới resource MKTLogin.
- MRERP chỉ chia sẻ Employee/Team/capability tối thiểu theo contract; không lưu cookie, session, password hoặc API credential MKTLogin.
- Implementation production chỉ bắt đầu sau khi OD-27 được refinement đủ và contract/security được duyệt.

## Remaining open questions

- MKTLogin API hỗ trợ resource và thao tác cụ thể nào trong gói công ty đang dùng?
- Identifier nào ổn định để mapping và unique rule là gì?
- API authentication, secret storage và rotation thực hiện thế nào?
- Đồng bộ theo chiều nào, tần suất nào và cách đối soát dữ liệu lệch?
- Ai được link/unlink/sync/cấp/thu hồi và audit lưu gì?
- Hành vi timeout/retry/rate-limit/idempotency/degraded mode/rollback là gì?
- API có hỗ trợ SSO/deep link cho người dùng hay chỉ service integration?

Tất cả được theo dõi bằng OD-27. OD-01, OD-03, OD-11, OD-17, OD-18 và OD-21 vẫn giữ nguyên phạm vi riêng.

## Consequences

### Positive

- ASSETCONTROL không còn chỉ giữ một bản ghi thủ công tách rời MKTLogin.
- Không phải xây và vận hành lại chức năng của nhà cung cấp.
- Giữ ranh giới Employee/Team ở MRERP và Resource/Grant/audit ở ASSETCONTROL.

### Negative / trade-offs

- Chất lượng integration phụ thuộc khả năng API và gói MKTLogin thực tế.
- Cần xử lý dữ liệu lệch và gián đoạn của hệ thống bên ngoài.

### Risks and mitigations

- API thay đổi: version adapter/contract và có compatibility test.
- Gọi nhầm resource: mapping bằng identifier ổn định, unique constraint và màn hình xác nhận.
- Lộ credential: secret ngoài Git/frontend/log, quyền tối thiểu và rotation sau khi OD-27/OD-21 được duyệt.
- MKTLogin lỗi: không giả trạng thái thành công; hiển thị lần đồng bộ gần nhất và trạng thái lỗi.

## Security and authorization impact

- Không suy ra quyền MKTLogin chỉ từ việc người dùng nhìn thấy nút ở MRERP.
- ASSETCONTROL phải kiểm account/employment, capability, scope, object và field policy tại server.
- Link/unlink/sync/lifecycle command phải có audit nhưng không ghi secret hoặc payload nhạy cảm.
- API credential không được gửi xuống frontend.

## Data and contract impact

- MKTLogin là nguồn của resource/session vận hành thực tế.
- ASSETCONTROL giữ external identifier, mapping, trạng thái/snapshot tối thiểu và audit theo contract được duyệt.
- MRERP chỉ nhận metadata/notification cần thiết; không nhận cookie, session hoặc secret.
- Không đọc database chéo và không dùng tên hiển thị làm khóa liên kết duy nhất.

## Rollout and rollback

- Kiểm kê tài khoản/gói API và resource MKTLogin bằng dữ liệu an toàn.
- Định nghĩa contract, mapping và authorization trước khi migration.
- Bắt đầu read-only/discovery và dual-run trước mọi command thay đổi trạng thái.
- Xác minh đối soát, audit và failure behavior trước khi cho phép lifecycle command.
- Rollback bằng cách tắt adapter/command và giữ dữ liệu ASSETCONTROL hiện có; không xóa mapping hoặc audit khi chưa có kế hoạch migration được duyệt.

## Validation

- Contract test với API/sandbox hoặc test double bám contract đã kiểm chứng.
- Test allowed, thiếu capability, ngoài scope, object rule, field absence và account/employment không hợp lệ.
- Test identifier uniqueness, idempotency, timeout, retry, rate limit và reconciliation.
- Test không rò cookie, session, password, API credential hoặc Vault content qua API/log/audit.
- Nghiệm thu không chỉ dựa trên deep link; phải chứng minh mapping đọc được từ MKTLogin và xử lý lỗi đúng.

## Documentation updates

- Cập nhật product overview, business requirements, data ownership, ecosystem integration, roadmap, backlog, open decisions và đường đọc `01–06`.

## Approval record

- Người chấp nhận: Người sở hữu sản phẩm MRERP.
- Ngày chấp nhận: 2026-09-03.
- Bằng chứng/xác nhận: “công ty dùng MKT login, không cần quan tâm MKT city”; “MKT login có API (không cần clone lại full)”; và “mục tiêu cuối cùng ... tài nguyên được ghi trên Assetcontrol thực sự liên kết với MKT login”.
