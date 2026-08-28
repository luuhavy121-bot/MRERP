# Open decisions

Mọi mục trong phần **Đang mở** có trạng thái **Chưa quyết định**. AI và developer không được tự lựa chọn. Mỗi quyết định ảnh hưởng production phải đi qua ADR và cập nhật source of truth liên quan.

## Đang mở

| ID | Quyết định cần chốt | Tài liệu bị ảnh hưởng |
|---|---|---|
| OD-01 | Identity Provider cụ thể và mô hình vận hành/backup | Identity, deployment |
| OD-02 | Hành vi của phiên đang hoạt động khi IdP ngừng | Identity, operations |
| OD-03 | Break-glass ASSETCONTROL và thời gian giữ login cũ | Identity, integration, operations |
| OD-04 | Ranh giới Captain, Leader và Manager | Product requirements, authorization |
| OD-05 | Ai được vào Admin Panel và ai quản trị Rewards | Product requirements, authorization |
| OD-06 | CRM field-level matrix cho Sales, Marketing/Ads, Kế toán và nhóm liên quan | CRM requirements, authorization |
| OD-07 | Mapping Ads với Marketing trong cơ cấu MRE | Organization configuration |
| OD-08 | Retire MREKANBAN hay giữ làm client/view chuyên sâu dài hạn | Product boundary, integration, roadmap |
| OD-09 | Database riêng hay schema riêng cho MRERP/CRM trên cùng PostgreSQL instance | Data ownership, deployment |
| OD-10 | Stale threshold, timeout, retry và SLA cho Dashboard snapshot | Integration, operations |
| OD-11 | Service-to-service authentication và rotation | Identity, integration, operations |
| OD-12 | Ngưỡng tải, SLA và ngân sách để tách CRM sang VPS riêng | Deployment |
| OD-13 | Công thức lương, chấm công, phép và reward policy | Business requirements |
| OD-14 | Object storage và retention cho Documents | Data ownership, deployment |
| OD-15 | Reverse proxy, error tracking và monitoring product cụ thể | Deployment |
| OD-16 | Danh sách phòng ban, team, cấp bậc và capability chính thức | Company configuration, authorization |
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

**Chưa quyết định:** OD-04 vẫn mở cho ranh giới Captain/Leader/Manager ngoài Task; quyền đọc Task nền của Staff/Captain và policy hủy/xóa Task cũng chưa được chốt.

### Topology và vận hành

OD-09 đến OD-12, OD-14, OD-15 và OD-21 cần ADR trước khi lựa chọn production topology/tool. Có thể thiết kế interface/contract mà chưa chọn product cụ thể.

### Phase 1 People/HR readiness

OD-22 đến OD-26 đã được giải quyết cho phạm vi People/HR Foundation bằng ADR-0003 đến ADR-0008. CEO đã được chốt toàn quyền trong People nhưng quyết định này không tự áp dụng sang module/product khác. Mock Identity không chọn IdP production và không đóng OD-01/OD-19 ngoài phạm vi slice.

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
