# Open decisions

**Cập nhật được duyệt 01/10/2026:** ưu tiên [Tuyển dụng công khai và đánh giá KPI](../product/hr-expansion-requirements.md) trước MKTLogin theo ADR-0017/0018. Quyền Leader với CV/pipeline và quy trình draft → gửi duyệt thay thế baseline tuyển dụng cũ ở phần bên dưới. Các phần khác giữ trạng thái riêng.

Mọi mục trong phần **Đang mở** có trạng thái **Chưa quyết định**. AI và developer không được tự lựa chọn. Mỗi quyết định ảnh hưởng production phải đi qua ADR và cập nhật source of truth liên quan.

## Đang mở

| ID | Quyết định cần chốt | Tài liệu bị ảnh hưởng |
|---|---|---|
| OD-01 | Identity Provider cụ thể và mô hình vận hành/backup | Identity, deployment |
| OD-02 | Hành vi của phiên đang hoạt động khi IdP ngừng | Identity, operations |
| OD-03 | Break-glass ASSETCONTROL và thời gian giữ login cũ | Identity, integration, operations |
| OD-04 | Ranh giới Captain, Leader và Manager | Product requirements, authorization |
| OD-05 | Quyền Admin Panel ngoài phạm vi đã duyệt; quản trị Rewards đã chốt cục bộ qua ADR-0020 | Product requirements, authorization |
| OD-06 | CRM field-level matrix cho Sales, Marketing/Ads, Kế toán và nhóm liên quan | CRM requirements, authorization |
| OD-07 | Mapping Ads với Marketing trong cơ cấu MRE | Organization configuration |
| OD-08 | Retire MREKANBAN hay giữ làm client/view chuyên sâu dài hạn | Product boundary, integration, roadmap |
| OD-09 | Database riêng hay schema riêng cho MRERP/CRM trên cùng PostgreSQL instance | Data ownership, deployment |
| OD-10 | Stale threshold, timeout, retry và SLA cho Dashboard snapshot | Integration, operations |
| OD-11 | Service-to-service authentication và rotation | Identity, integration, operations |
| OD-12 | Ngưỡng tải, SLA và ngân sách để tách CRM sang VPS riêng | Deployment |
| OD-13 | Công thức lương, chấm công, phép và reward policy còn lại, gồm ngân sách tiền mặt CEO; catalog/hold/refund/hạn mức sao đã chốt qua ADR-0020 | Business requirements |
| OD-14 | Object storage production dài hạn cho attachment/Documents; local-media Feed/Task hiện chỉ là baseline VPS | Data ownership, deployment |
| OD-15 | Reverse proxy, error tracking và monitoring product cụ thể | Deployment |
| OD-16 | Danh sách Team, cấp bậc và capability chính thức; MRE hiện không dùng Phòng ban | Company configuration, authorization |
| OD-17 | Quan hệ codebase ASSETCONTROL Nhà ZUZU với ASSETCONTROL MRE | Product boundary, migration, security |
| OD-18 | Có mở quyền ASSETCONTROL cho đối tượng ngoài CEO và Leader hay không, và theo policy nào | Product boundary, authorization |
| OD-19 | Ranh giới thao tác giữa Admin Panel MRERP và IdP: provisioning, deprovisioning, approval và audit | Identity, Admin Panel, operations |
| OD-21 | Secret manager, config delivery, certificate automation và rotation cho production | Security, deployment, operations |
| OD-27 | Contract ASSETCONTROL–MKTLogin: resource mapping, API authentication, permission, sync/reconciliation, failure handling và rollback | Product boundary, data ownership, integration, security, operations, testing |
| OD-28 | Policy bàn giao máy công ty và xử lý thu hồi: actor, quyền Windows/remote, bằng chứng, tài nguyên dùng chung, ngoại lệ và tiêu chí hoàn tất | Integration, authorization, operations, testing |

## Chi tiết các nhóm cần duyệt sớm

### Identity và khẩn cấp

OD-01, OD-02 và OD-03 cần được giải quyết trước khi migration login thật hoặc tắt cơ chế đăng nhập cũ. Không tự thiết kế backdoor.

**Xác nhận trực tiếp ngày 03/10/2026:** người dùng chọn hoàn thiện/kiểm tra local trước và tài khoản do công ty cấp riêng. Điều này chốt trải nghiệm cấp tài khoản, chưa chọn IdP hoặc contract provisioning/reset/revoke; OD-01/02/19 vẫn mở. Hướng hosting sau là dùng chung VPS ASSETCONTROL, cần kiểm kê tải và ADR topology trước triển khai; không tự đóng OD-09/12/15/21. [Runbook pilot local](../operations/local-pilot.md) chỉ hiện thực kiểm tra và backup/restore thử trên development.

### Permission và dữ liệu nhạy cảm

OD-04 đến OD-07, OD-16, OD-18 và OD-19 cần được chốt đủ cho vertical slice bị ảnh hưởng trước khi hiện thực endpoint nghiệp vụ. Không hard-code giả định vào lõi platform.

**Đã chốt cục bộ cho Task Phase 1 qua [ADR-0002](0002-task-authorization-baseline.md):** Captain có permission nền như Staff; Leader có scope các team mình quản lý; Manager tương lai có scope phòng ban nhưng ban đầu không có user Manager; CEO có scope toàn công ty nhưng từng hành động vẫn cần capability. Các quyết định này không tự áp dụng sang CRM, HR, Rewards, Admin Panel hoặc product khác.

**Đã chốt bổ sung qua [ADR-0011](0011-dashboard-feed-task-operational-baseline.md):** Staff/HR đọc Task mình tạo hoặc được giao; Leader thêm Team lãnh đạo; CEO company scope. **Chưa quyết định:** OD-04 vẫn mở cho ranh giới Captain/Leader/Manager ngoài Task; policy Task ngoài phạm vi hiện tại chưa được chốt.

### Topology và vận hành

OD-09 đến OD-12, OD-14, OD-15 và OD-21 cần ADR trước khi lựa chọn production topology/tool. Có thể thiết kế interface/contract mà chưa chọn product cụ thể.

**Đã chốt cục bộ qua [ADR-0012](0012-phase-2-leave-attendance-foundation.md):** Leave nguyên ngày, Leader duyệt một cấp, holiday calendar Việt Nam và HR adjustment được phép trong foundation Phase 2. OD-13 vẫn mở cho loại phép, entitlement, nửa ngày/theo giờ, máy chấm công và công thức lương.

**Đã chốt cục bộ qua [ADR-0013](0013-phase-3-culture-operations-baseline.md):** Recruitment scope/pipeline, Documents local-media/version/retention, Recognition scope, Star ledger không hết hạn, leaderboard và notification preference. **Bổ sung [ADR-0020](0020-stars-redemption-and-recognition.md):** HR/CEO quản trị catalog/duyệt đổi, hạn mức sao Team/tháng, hold/refund/tồn/snapshot và Recognition trong Đánh giá nhân sự. OD-05 chỉ còn phần Admin chưa duyệt; OD-13 giữ các policy còn lại và ngân sách tiền mặt tổng CEO được hoãn. OD-14 vẫn mở cho object storage production.

### Phase 1 People/HR readiness

OD-22 đến OD-26 đã được giải quyết cho phạm vi People/HR Foundation bằng ADR-0003 đến ADR-0009. ADR-0009 chốt cấu hình MRE phẳng `CEO → Team → Employee`; danh sách Team thực tế trong OD-16 vẫn mở. CEO toàn quyền People không tự áp dụng sang module/product khác. Mock Identity không chọn IdP production và không đóng OD-01/OD-19.

**Đã chốt cục bộ qua [ADR-0010](0010-people-account-and-employment-lifecycle.md):** chỉ CEO vào phần Admin access bundle của People; HR quản lý account/employment toàn công ty; Leader reset mật khẩu trong Team lãnh đạo; Staff tự sửa allow-list của hồ sơ. Quyết định này không chốt IdP production, Rewards hoặc quyền Admin của module khác nên OD-01, OD-05 và OD-19 vẫn mở ở các phần còn lại.

**Đã chốt cục bộ ngày 28/08/2026:** HR tạo Employee với initial status `Thử việc`; Leader quyết định `Thử việc → Chính thức` trong Team mình lãnh đạo; CEO có toàn bộ capability People và company scope. HR nhập tự do mã nhân sự duy nhất và chọn có tạo account hay không. Khi chọn tạo account, account và Employee phải cùng thành công; khi không chọn, Employee được phép chưa có account. Credential và workflow cấp account production về sau vẫn thuộc IdP/OD-19.

### Migration product hiện hữu

OD-08 và OD-17 yêu cầu audit code, workflow, dữ liệu và deployment thực tế. Không import hoặc di chuyển dữ liệu chỉ vì codebase có sẵn. OD-18 chỉ được giải quyết bằng policy được người dùng duyệt; hiện không được mở cho đối tượng khác.

**Đã chốt qua [ADR-0014](0014-mktlogin-assetcontrol-integration-goal.md):** công ty dùng MKTLogin, MKT City không thuộc phạm vi hiện tại, không clone đầy đủ MKTLogin và đích cuối là resource ASSETCONTROL liên kết với resource thật trong MKTLogin qua API. OD-27 vẫn mở cho contract/security/permission/failure semantics trước implementation production.

**Bổ sung bằng chứng cho OD-27 ngày 03/09/2026:** đã nhận tài liệu API trong ứng dụng MKTLogin 2.1.3; người dùng xác nhận mỗi máy cài app riêng và phân quyền theo Team. **Đã chốt cục bộ qua [ADR-0015](0015-mktlogin-workspace-per-team.md):** các Team sẽ có workspace riêng. OD-27 vẫn mở cho quy tắc định danh/liên kết Team–workspace cụ thể, quyền API theo tài khoản, định danh giữa nhiều máy và kết nối tới API `localhost:4980` khi máy/ứng dụng bật hoặc tắt. [Kết quả đọc tài liệu](../architecture/ecosystem-integration.md#53-kết-quả-đọc-tài-liệu-mktlogin-được-cung-cấp) chưa chốt kiến trúc kết nối hoặc chứng minh API cấp/thu hồi quyền tồn tại.

**Bằng chứng bổ sung cho OD-27:** nhà cung cấp trả lời qua người dùng rằng gỡ quyền không đóng hồ sơ đang mở; thành viên vẫn dùng được. Khi được hỏi API gỡ quyền/buộc đóng trên máy thành viên, nhà cung cấp trả lời không thực hiện được vì khác máy. [Giới hạn thu hồi](../architecture/ecosystem-integration.md#54-giới-hạn-thu-hồi-được-nhà-cung-cấp-trả-lời) phải được tính vào contract: gỡ quyền không phải bằng chứng chấm dứt phiên. Khả năng mở lại/offline và phạm vi API vẫn chưa kiểm chứng; không hứa remote revoke qua API được hỏi.

**Làm rõ mới nhất từ người dùng:** gói công ty/tài khoản con, MRERP → MKTLogin không nhập lại credential và mất quyền dùng khi nghỉ việc là phương án công ty họp bàn, không phải tính năng MKT xác nhận. Tài khoản/profile/tài nguyên công ty phải được giữ nguyên. [Mục 5.6 tài liệu tích hợp](../architecture/ecosystem-integration.md#56-bổ-sung-từ-người-dùng-gói-công-ty-và-tài-khoản-thành-viên) ghi nguồn và giới hạn. OD-27 bổ sung Employee–quyền sử dụng/thành viên, cơ chế đăng nhập và nơi thực thi chặn. Nếu thực thi tại máy thì cần policy OD-28. Chỉ khóa MRERP, giữ nguyên cả quyền MKTLogin và quyền dùng máy thì chưa đạt; phản hồi trước về profile đang mở vẫn có hiệu lực. ADR-0016 bản 02 giữ Proposed.

### Máy công ty và bằng chứng thu hồi

**OD-28 vẫn Chưa quyết định.** Người dùng muốn giữ MKTLogin trên máy công ty cho khoảng 50–60 nhân sự và tính trước bước thu hồi. Cần chốt ai kiểm soát quyền sử dụng Windows/remote, ai thu và kiểm tra máy, ai xác nhận bằng chứng, thời điểm hiệu lực, trường hợp chưa lấy được máy, tài nguyên dùng chung và người có quyền duyệt ngoại lệ. Sở hữu máy không tự bảo đảm đã ngắt quyền truy cập; bàn giao máy không vô hiệu hóa phiên ở nơi khác hoặc thu lại dữ liệu đã sao chép.

[Bản vẽ và kiến trúc máy công ty](../architecture/mktlogin-company-device-proposal.md) và [ADR-0016](0016-mktlogin-company-device-integration-proposal.md) là **Proposed**, chưa được chấp nhận: kiểm kê API chỉ đọc, liên kết/cấp phát rồi theo dõi từng phần thu hồi. OD-27 giữ contract kỹ thuật; OD-28 giữ policy vận hành/bằng chứng. Không tự mở ASSETCONTROL cho IT/HR/Staff (OD-18), không chọn service authentication (OD-11/OD-21) hoặc codebase ASSETCONTROL MRE (OD-17).

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
| Phase 3 baseline | Recruitment, Documents, Recognition/Stars và Personal Settings baseline được chấp nhận; object storage production vẫn mở, catalog/redemption được mở rộng qua ADR-0020 | [ADR-0013](0013-phase-3-culture-operations-baseline.md) |
| Rewards mở rộng (OD-05/OD-13 một phần) | HR/CEO quản trị/duyệt, hạn mức Team/tháng, giữ/hoàn sao và tồn được chốt; ngân sách tiền mặt CEO hoãn | [ADR-0020](0020-stars-redemption-and-recognition.md) |
| MKTLogin integration goal | Chỉ tích hợp MKTLogin; không clone; ASSETCONTROL resource phải liên kết resource thật qua API. Contract chi tiết vẫn mở ở OD-27 | [ADR-0014](0014-mktlogin-assetcontrol-integration-goal.md) |

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
- MKT City không thuộc phạm vi dự án hiện tại và không clone đầy đủ MKTLogin.

## Phần OD-13 chốt thêm ngày 01/10/2026

Nhập kết quả Excel HR được chốt theo [ADR-0019](0019-attendance-excel-import.md). OD-13 tiếp tục mở cho công thức ca/công/lương, khóa kỳ, sửa mapping mã chấm công và retention/xóa lịch sử nhập. Không mặc định bảng xuất là công đã duyệt.

## Bổ sung OD-13 ngày 03/10/2026

[ADR-0021](0021-hr-demo-half-day-and-workflow.md) giải quyết nghỉ nửa ngày và công chuẩn thứ Hai–thứ Bảy cả ngày cho demo local. Loại phép/hạn mức/lương/theo giờ/hủy đơn/duyệt thay/khóa kỳ và máy chấm công vẫn Chưa quyết định. Không mở production từ xác nhận demo.
