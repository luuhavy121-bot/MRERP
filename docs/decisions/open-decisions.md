# Open decisions

Mọi mục trong phần **Đang mở** có trạng thái **Chưa quyết định**. AI và developer không được tự lựa chọn. Mỗi quyết định ảnh hưởng production phải đi qua ADR và cập nhật source of truth liên quan.

## Đang mở

| ID | Quyết định cần chốt | Tài liệu bị ảnh hưởng |
|---|---|---|
| OD-01 | Identity Provider cụ thể và mô hình vận hành/backup | Identity, deployment |
| OD-02 | Hành vi của phiên đang hoạt động khi IdP ngừng | Identity, operations |
| OD-03 | Break-glass ASSETCONTROL và thời gian giữ login cũ | Identity, integration, operations |
| OD-04 | Ranh giới Captain, Leader và Manager | Product requirements, authorization |
| OD-05 | Ai quản trị Rewards và quyền Admin Panel ngoài phạm vi People | Product requirements, authorization |
| OD-06 | CRM field-level matrix cho Sales, Marketing/Ads, Kế toán và nhóm liên quan | CRM requirements, authorization |
| OD-07 | Mapping Ads với Marketing trong cơ cấu MRE | Organization configuration |
| OD-08 | Retire MREKANBAN hay giữ làm client/view chuyên sâu dài hạn | Product boundary, integration, roadmap |
| OD-09 | Database riêng hay schema riêng cho MRERP/CRM trên cùng PostgreSQL instance | Data ownership, deployment |
| OD-10 | Stale threshold, timeout, retry và SLA cho Dashboard snapshot | Integration, operations |
| OD-11 | Service-to-service authentication và rotation | Identity, integration, operations |
| OD-12 | Ngưỡng tải, SLA và ngân sách để tách CRM sang VPS riêng | Deployment |
| OD-13 | Công thức lương, chấm công, phép và reward policy | Business requirements |
| OD-14 | Object storage production dài hạn cho attachment/Documents; local-media Feed/Task hiện chỉ là baseline VPS | Data ownership, deployment |
| OD-15 | Reverse proxy, error tracking và monitoring product cụ thể | Deployment |
| OD-16 | Danh sách Team, cấp bậc và capability chính thức; MRE hiện không dùng Phòng ban | Company configuration, authorization |
| OD-17 | Quan hệ codebase ASSETCONTROL Nhà ZUZU với ASSETCONTROL MRE | Product boundary, migration, security |
| OD-18 | Có mở quyền ASSETCONTROL cho đối tượng ngoài CEO và Leader hay không, và theo policy nào | Product boundary, authorization |
| OD-19 | Ranh giới thao tác giữa Admin Panel MRERP và IdP: provisioning, deprovisioning, approval và audit | Identity, Admin Panel, operations |
| OD-21 | Secret manager, config delivery, certificate automation và rotation cho production | Security, deployment, operations |

## Chi tiết các nhóm cần duyệt sớm

### Identity và khẩn cấp

OD-01, OD-02 và OD-03 cần được giải quyết trước khi migration login thật hoặc tắt cơ chế đăng nhập cũ. Không tự thiết kế backdoor.

### Permission và dữ liệu nhạy cảm

OD-04 đến OD-07, OD-16, OD-18 và OD-19 cần được chốt đủ cho vertical slice bị ảnh hưởng trước khi hiện thực endpoint nghiệp vụ. Không hard-code giả định vào lõi platform.

**Đã chốt cục bộ cho Task Phase 1 qua [ADR-0002](0002-task-authorization-baseline.md):** Captain có permission nền như Staff; Leader có scope các team mình quản lý; Manager tương lai có scope phòng ban nhưng ban đầu không có user Manager; CEO có scope toàn công ty nhưng từng hành động vẫn cần capability. Các quyết định này không tự áp dụng sang CRM, HR, Rewards, Admin Panel hoặc product khác.

**Đã chốt bổ sung qua [ADR-0011](0011-dashboard-feed-task-operational-baseline.md):** Staff/HR đọc Task mình tạo hoặc được giao; Leader thêm Team lãnh đạo; CEO company scope. **Chưa quyết định:** OD-04 vẫn mở cho ranh giới Captain/Leader/Manager ngoài Task; policy Task ngoài phạm vi hiện tại chưa được chốt.

### Topology và vận hành

OD-09 đến OD-12, OD-14, OD-15 và OD-21 cần ADR trước khi lựa chọn production topology/tool. Có thể thiết kế interface/contract mà chưa chọn product cụ thể.

**Đã chốt cục bộ qua [ADR-0012](0012-phase-2-leave-attendance-foundation.md):** Leave nguyên ngày, Leader duyệt một cấp, holiday calendar Việt Nam và HR adjustment được phép trong foundation Phase 2. OD-13 vẫn mở cho loại phép, entitlement, nửa ngày/theo giờ, máy chấm công và công thức lương.

**Đã chốt cục bộ qua [ADR-0013](0013-phase-3-culture-operations-baseline.md):** Recruitment scope/pipeline, Documents local-media/version/retention, Recognition scope, Star ledger không hết hạn, leaderboard và notification preference. OD-05 vẫn mở cho người quản trị catalog/duyệt đổi thưởng; OD-13 vẫn mở cho redemption hold/refund và policy reward còn lại; OD-14 vẫn mở cho object storage production.

### Phase 1 People/HR readiness

OD-22 đến OD-26 đã được giải quyết cho phạm vi People/HR Foundation bằng ADR-0003 đến ADR-0009. ADR-0009 chốt cấu hình MRE phẳng `CEO → Team → Employee`; danh sách Team thực tế trong OD-16 vẫn mở. CEO toàn quyền People không tự áp dụng sang module/product khác. Mock Identity không chọn IdP production và không đóng OD-01/OD-19.

**Đã chốt cục bộ qua [ADR-0010](0010-people-account-and-employment-lifecycle.md):** chỉ CEO vào phần Admin access bundle của People; HR quản lý account/employment toàn công ty; Leader reset mật khẩu trong Team lãnh đạo; Staff tự sửa allow-list của hồ sơ. Quyết định này không chốt IdP production, Rewards hoặc quyền Admin của module khác nên OD-01, OD-05 và OD-19 vẫn mở ở các phần còn lại.

**Đã chốt cục bộ ngày 28/08/2026:** HR tạo Employee với initial status `Thử việc`; Leader quyết định `Thử việc → Chính thức` trong Team mình lãnh đạo; CEO có toàn bộ capability People và company scope. HR nhập tự do mã nhân sự duy nhất và chọn có tạo account hay không. Khi chọn tạo account, account và Employee phải cùng thành công; khi không chọn, Employee được phép chưa có account. Credential và workflow cấp account production về sau vẫn thuộc IdP/OD-19.

### Migration product hiện hữu

OD-08 và OD-17 yêu cầu audit code, workflow, dữ liệu và deployment thực tế. Không import hoặc di chuyển dữ liệu chỉ vì codebase có sẵn. OD-18 chỉ được giải quyết bằng policy được người dùng duyệt; hiện không được mở cho đối tượng khác.

### Repository baseline

OD-20 đã được giải quyết bằng ADR-0001. Baseline này không lựa chọn Identity Provider, secret manager production hoặc policy nghiệp vụ.

## Đã giải quyết

| ID | Kết quả | ADR |
|---|---|---|
| OD-20 | Repository conventions, CI tối thiểu và secret-handling baseline được chấp nhận | [ADR-0001](0001-repository-governance-baseline.md) |
| OD-22 | Actor/scope quản trị People và organization trong slice được chốt | [ADR-0005](0005-people-authorization-and-field-policy.md) |
| OD-23 | Projection `basic`/`hr_detail` và scope đọc trong slice được chốt | [ADR-0005](0005-people-authorization-and-field-policy.md) |
| OD-24 | Promotion/cardinality/code rule tối thiểu của slice được chốt | [ADR-0005](0005-people-authorization-and-field-policy.md) |
| OD-25 | Mock Identity dev/test và production guard được chốt | [ADR-0004](0004-mock-identity-context.md) |
| OD-26 | Stack Phase 1 được chấp nhận | [ADR-0003](0003-phase-1-application-stack.md) |
| People account/lifecycle | Policy account, self-service, employment lifecycle và Admin access bundle cục bộ được chấp nhận | [ADR-0010](0010-people-account-and-employment-lifecycle.md) |
| Dashboard/Feed/Task baseline | Audience, moderation, Task read scope, Goal, recurrence, local-media và retention cục bộ được chấp nhận; OD-14 không đóng | [ADR-0011](0011-dashboard-feed-task-operational-baseline.md) |
| Phase 3 baseline | Recruitment, Documents, Recognition/Stars và Personal Settings baseline được chấp nhận; redemption/catalog approval và object storage production vẫn mở | [ADR-0013](0013-phase-3-culture-operations-baseline.md) |

## Những nội dung không còn mở

Các ràng buộc sau là **Đã chốt**, không được biến thành open decision:

- MRERP là nguồn Employee/Team và Task dài hạn.
- CRM sở hữu Customer/Order/Product/Channel/FFM.
- ASSETCONTROL sở hữu Resource/Grant/Vault.
- Hiện chỉ CEO và Leader được cấp quyền truy cập ASSETCONTROL.
- Product không đọc database chéo.
- Frontend không phải hàng rào authorization.
- Dashboard không gọi CRM trực tiếp trong request tải trang.
- MRERP không được phát triển trong repo/permanent worktree ASSETCONTROL.
