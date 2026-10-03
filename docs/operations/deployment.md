# Deployment và vận hành

Tài liệu này là source of truth chịu trách nhiệm chính cho topology mục tiêu, khả năng tách CRM, backup và observability. Bản đọc ngắn nằm tại [05 — Hướng dẫn và vận hành](../05-huong-dan-va-van-hanh.md).

## 1. Nguyên tắc triển khai

**Đã chốt về ranh giới:**

- MRERP và CRM không đọc database của nhau.
- ASSETCONTROL giữ deployment riêng.
- PostgreSQL không public ra Internet.
- Public traffic chỉ qua HTTPS.
- CRM worker không được làm nghẽn MRERP.
- Backup phải có khả năng phục hồi khi mất VPS chính.

## 2. Topology giai đoạn đầu

**Đề xuất mục tiêu cần ADR.** Một VPS Platform có thể chạy:

```text
VPS Platform
├─ Reverse proxy
├─ Identity integration (không chốt nơi chạy Identity Provider)
├─ MRERP Web/API
├─ MRECRM Web/API
├─ CRM sync/import/report workers
├─ Redis/queue
└─ PostgreSQL 16
   ├─ MRERP logical data ownership
   └─ CRM logical data ownership

VPS/Deployment ASSETCONTROL
├─ ASSETCONTROL Web
└─ ASSETCONTROL data
```

MRERP và CRM phải có credential riêng/tối thiểu. Cùng PostgreSQL instance không cho phép cross-read/cross-write.

**Chưa quyết định.** MRERP/CRM dùng database riêng hay schema riêng trong cùng instance.

Vị trí triển khai và mô hình HA/backup của Identity Provider bị cố ý để mở theo OD-01; sơ đồ trên không được dùng để kết luận IdP chạy cùng VPS Platform.

### Runtime MRERP đã chốt cho baseline hiện tại

Theo ADR-0011, Docker Compose local và topology VPS mục tiêu của MRERP có thêm:

```text
MRERP backend/web
├─ PostgreSQL 16
├─ Redis broker
├─ Celery worker
├─ Celery Beat
└─ persistent media volume (Feed, Task, Documents, Recruitment)
```

Redis/Celery phục vụ recurring Task, deadline notification và retention purge; không dùng result backend. Redis lỗi không được làm hỏng request CRUD Feed/Task. Media volume phải vào backup; binary chỉ tải qua API có ACL. Object storage production vẫn **Chưa quyết định** theo OD-14.

## 3. Khả năng tách CRM

**Đề xuất mục tiêu.** CRM được thiết kế thành deployable riêng ngay từ đầu để có thể chuyển VPS mà không tái thiết kế product boundary.

Không tách chỉ vì số nhân sự hoặc số dòng. Xem xét tách khi monitoring/load test cho thấy:

- Worker CRM gây CPU/RAM saturation hoặc swap.
- I/O, lock hoặc connection contention ảnh hưởng MRERP.
- Latency Dashboard/HR/Task tăng theo job/report CRM.
- CRM cần SLA hoặc lịch deploy độc lập.
- Đã tối ưu query/index/pagination/cache/queue mà cô lập máy vẫn có lợi.

**Chưa quyết định.** Ngưỡng đo cụ thể, SLA và ngân sách.

## 4. Worker và dữ liệu CRM lớn

**Đề xuất mục tiêu dựa trên tải thật:**

- Pagination/filter/sort phía server.
- Index theo query thật.
- Worker riêng cho adapter, import, sync và report.
- Job idempotent; retry giới hạn; failure visibility.
- Báo cáo/export lớn chạy nền.
- Cache aggregate có TTL, không cache bừa dữ liệu nhạy cảm.
- Tránh N+1 và full-table count không cần thiết.
- Resource/concurrency limit cho worker.
- Structured log, query metrics và load test.

CDN chỉ dành cho static asset phù hợp; không sửa database query hoặc report chậm.

## 5. Dashboard resilience

**Đã chốt.** Dashboard đọc MRERP read model, không gọi CRM/ASSETCONTROL trực tiếp trong request. Source product lỗi không được làm treo HR, Task hoặc leave.

**Chưa quyết định.** Stale threshold, timeout, retry và SLA.

## 6. Backup và restore

**Đề xuất mục tiêu bắt buộc.**

- Backup nằm ngoài VPS chính.
- Quyền truy cập backup rõ ràng và tối thiểu.
- Có lịch retention sau khi được quyết định.
- Phải diễn tập restore, không chỉ kiểm tra file backup tồn tại.
- Restore drill phải xác minh database/application có thể khởi động và dữ liệu quan trọng đọc được.

**Chưa quyết định.** Công cụ backup, retention, RPO và RTO cụ thể.

## 7. Observability

**Đề xuất mục tiêu.**

- Structured logs có correlation identifier phù hợp.
- Error tracking.
- Uptime checks.
- Metrics CPU, RAM, I/O, DB connection/lock/query và queue depth.
- Job failure/dead-letter visibility.
- Integration health và snapshot freshness.

**Chưa quyết định.** Product/tool cụ thể cho reverse proxy, error tracking và monitoring.

## 8. Security vận hành

**Đã chốt về nguyên tắc:**

- HTTPS cho public traffic.
- Không public PostgreSQL.
- Không commit secret/dữ liệu production.
- Không dùng static shared service token trong production.
- Không chuyển access token qua query string.

Chi tiết secret manager, certificate automation và service authentication là **Chưa quyết định**.

Baseline repository được mô tả tại [Quản lý cấu hình và secret](configuration-and-secrets.md). Secret manager/config delivery production vẫn mở theo OD-21.

## 9. Readiness trước production

**Cập nhật xác nhận 03/10/2026:** người dùng chọn hoàn thiện/kiểm tra local trước, tài khoản công ty cấp riêng và hướng dùng chung VPS ASSETCONTROL sau đó. Công cụ và quy trình local nằm tại [local pilot](local-pilot.md). Chọn trải nghiệm tài khoản riêng không chọn IdP hoặc cho phép Mock Identity production. Chọn hướng chung VPS không chứng minh đủ tải; topology cần đánh giá/ADR trước implementation production. Chưa deploy VPS trong đợt này.

Trước khi mở production phải có tối thiểu:

- Topology và credential boundary được ADR chấp nhận.
- HTTPS và database network exposure được kiểm tra.
- Backup ngoài VPS và restore drill thành công.
- Runbook deploy/rollback và integration outage.
- Metrics/alert đủ để nhận biết CRM ảnh hưởng MRERP.
- Break-glass chỉ khi OD-03 đã được chốt và kiểm thử.
- Không có secret hoặc dữ liệu production trong Git.

## 10. Tài liệu liên quan

- [Identity và phân quyền](../architecture/identity-and-authorization.md)
- [Tích hợp hệ sinh thái](../architecture/ecosystem-integration.md)
- [Test strategy](../testing/test-strategy.md)
- [Open decisions](../decisions/open-decisions.md)

## 11. Tính phương án hosting toàn hệ sinh thái — 02/10/2026

**Đã xác nhận trực tiếp bởi người sở hữu sản phẩm:** VPS hiện tại đang host ASSETCONTROL; ERP tổng thể bao gồm MRERP Core, ASSETCONTROL, Kanban (MREKANBAN) và CRM (MRECRM). Phải tính tài nguyên, vận hành và backup cho cả bốn thành phần. Phạm vi hệ sinh thái không thay đổi data ownership, không tự chốt việc gom repository/database hoặc tương lai dài hạn MREKANBAN.

**Đề xuất để đánh giá, chưa chốt production topology:**

| Phương án | Bố trí | Đánh đổi |
|---|---|---|
| A — Tận dụng một VPS | Giữ deployment ASSETCONTROL; bổ sung deployment MRERP và dự trù CRM/Kanban trên cùng host | Tiết kiệm chi phí máy; cùng chịu sự cố host và tranh chấp CPU/RAM/I/O |
| B — Hai VPS | VPS hiện tại giữ ASSETCONTROL; VPS Platform mới chạy MRERP và dự trù CRM/Kanban | Giảm tác động lên ASSETCONTROL đang chạy; thêm chi phí và vận hành liên máy |
| C — Tách khi tải tăng | Từ A/B, chuyển CRM và worker sang VPS riêng khi số liệu chứng minh cần thiết | Cô lập tải import/report; cần contract, đo tải và runbook chuyển đổi |

Phương án A chỉ là lựa chọn đang khảo sát so với sơ đồ mục 2. Deployment riêng của ASSETCONTROL không tự đồng nghĩa phải có VPS vật lý riêng, nhưng cũng không cho phép thay đổi runtime, dữ liệu hoặc login hiện tại khi chưa kiểm kê. Chưa có dữ liệu VPS thực tế để kết luận A đủ tải hoặc rẻ hơn nâng cấp/tách máy.

### Dữ liệu cần có trước khi tính cấu hình và chi phí

**Cấu hình do người dùng cung cấp:** VPS ASSETCONTROL hiện tại tại inet.vn có 2 Core, 4 GB RAM, 40 GB SSD, giá đang trả 300.000 đồng/tháng. Đây là thông tin người dùng cung cấp, không phải báo giá mới đã kiểm chứng; chưa có dung lượng trống hoặc số liệu tải thực tế.

**Nhận định thiết kế, chưa có benchmark:** không nên lập kế hoạch production đầy đủ bốn thành phần dựa trên cấu hình này. RAM phải chia cho ASSETCONTROL, MRERP web/worker/Beat, database, Redis và OS; CRM import/report còn chưa được đo. 40 GB phải chứa cả dữ liệu, media, log, image và phần trống cho vận hành. Không khẳng định máy không chạy được MRERP tải nhẹ; cần đo tải để xét staging hoặc thử nghiệm giới hạn.

**Phương án ưu tiên để khảo sát:** B, giữ VPS hiện tại cho ASSETCONTROL và dùng VPS Platform mới cho MRERP, dự trù CRM/Kanban. Mức 4 vCPU/8 GB RAM là điểm khởi đầu để lập dự toán và load test, không phải cấu hình bảo đảm đủ tải. Nếu muốn một VPS, khảo sát nâng cấp lên cùng mức khởi đầu này rồi đo tổng tải; dung lượng SSD phải tính từ dữ liệu/trống/tăng trưởng thực tế trước khi mua. Chưa chốt cấu hình, nhà cung cấp, chi phí hoặc mua/nâng cấp VPS.

- Nhà cung cấp, gói/giá hiện tại, vCPU, RAM, SSD, OS và khả năng nâng cấp.
- CPU/RAM/swap/I/O/ổ đĩa trong giờ cao điểm và khi backup của ASSETCONTROL; tăng trưởng database/media/log.
- Cách deploy, reverse proxy/domain/TLS, database và backup/restore ASSETCONTROL hiện có; chỉ kiểm kê metadata vận hành, không ghi credential/Vault.
- Số người dùng đồng thời, tải upload CV/tài liệu; dự kiến đơn hàng, sync/import/report CRM và runtime Kanban sau audit.
- SLA, ngân sách và RPO/RTO; dung lượng backup ngoài VPS và chi phí lưu trữ/băng thông.

Ước lượng phải tính OS/proxy + tổng mức sử dụng đỉnh của từng app/database/worker + phần dự phòng; dung lượng đĩa tính database, media, log, image, file tạm và tăng trưởng. Không suy cấu hình chỉ từ số nhân sự hoặc menu. CRM hiện chỉ có khung frontend local tại `/crm`, chưa có API/database nghiệp vụ; chưa thể benchmark runtime CRM hoàn chỉnh.

### Thiết kế triển khai để đánh giá

- HTTPS đi qua reverse proxy; tên miền/subdomain cụ thể và proxy vẫn cần duyệt theo OD-15.
- Mỗi product giữ cấu hình, credential, mạng nội bộ, persistent volume và lịch deploy/rollback riêng. Database/schema topology MRERP–CRM vẫn theo OD-09; không cấp quyền đọc chéo.
- Worker CRM có giới hạn tài nguyên/concurrency và queue riêng theo thiết kế được duyệt, tránh gây nghẽn HR/Task. Container có thể giới hạn CPU/RAM nhưng không cô lập được sự cố host hoặc toàn bộ I/O contention; phải xác minh bằng load test.
- Backup database và media ngoài VPS, diễn tập restore từng product; lưu/khôi phục khóa cần thiết của ASSETCONTROL theo quy trình của product đó, không đưa secret sang MRERP.
- Chuẩn bị health check, log rotation, cảnh báo tài nguyên, dung lượng và job failure; công cụ cụ thể chưa được chọn.

Tham khảo kỹ thuật: [Docker Compose production](https://docs.docker.com/compose/how-tos/production/) và [giới hạn tài nguyên container](https://docs.docker.com/engine/containers/resource_constraints/). Các tài liệu này không chứng minh VPS hiện tại đủ tải.

### Trình tự đề xuất

1. Kiểm kê chỉ đọc VPS và ASSETCONTROL, xác minh backup/restore trước thay đổi.
2. So sánh A/B theo tải và giá thật; ghi ADR Proposed cho topology, làm rõ OD-01/09/12/15/21 trong phạm vi production cần dùng.
3. Chuẩn bị cấu hình production và môi trường staging được bảo vệ; kiểm thử tải, rollback và ảnh hưởng tới ASSETCONTROL.
4. Mở MRERP production sau khi Identity thật và các cổng readiness đạt; triển khai/tích hợp Kanban và CRM theo readiness riêng.

**Bằng chứng code hiện tại:** `compose.yaml` dành cho local, bật mock Identity, dùng Django `runserver`/Vite dev server và publish cổng database. Không đưa nguyên cấu hình này lên Internet. ADR-0004 yêu cầu production từ chối mock Identity; chọn và hiện thực Identity production vẫn là bước cần giải quyết, không được bỏ guard để host bản local.

Đây là bản tính phương án, không phải ADR Accepted hoặc xác nhận đã deploy/tích hợp đủ bốn product. Các mục Chưa quyết định tiếp tục giữ trạng thái riêng trong [Open decisions](../decisions/open-decisions.md).

### Kiến trúc hai VPS và khả năng chuyển dữ liệu

**Đề xuất đang đánh giá:**

```text
Người dùng → HTTPS → MRERP (điểm vào hệ sinh thái)
                         │
                         ├─ VPS Platform mới
                         │  ├─ MRERP Core + dữ liệu nhân sự/Task/media
                         │  ├─ MRERP Redis/worker/Beat
                         │  ├─ CRM + dữ liệu/worker CRM (dự trù)
                         │  └─ Kanban + cấu hình board/view (sau audit)
                         │
                         └─ VPS inet.vn hiện tại
                            └─ ASSETCONTROL + database/Vault/media của nó

Product ↔ API/event theo contract và xác thực được duyệt
Từng product → backup ngoài host chính
Identity chung: provider/vị trí vận hành vẫn chưa được chọn
```

Sơ đồ là bố trí logic, không yêu cầu traffic ASSETCONTROL đi qua MRERP. Trình duyệt có thể truy cập endpoint HTTPS riêng của từng product. MRERP và ASSETCONTROL kết nối qua API/event có authorization, không qua database; kết nối mạng riêng/tunnel hay HTTPS giữa server phải được thiết kế và duyệt cùng OD-11/21. Employee/Team/Task giữ UUID ổn định; metadata/snapshot được đồng bộ theo contract, Vault không sang MRERP. Chạy hai VPS không tự tạo SSO hoặc tích hợp API.

**Khả năng di chuyển:** có thể chuyển một product sang host mới bằng cách chuyển runtime tương thích, database, media và cấu hình/khóa cần thiết của chính product đó. Đây là chuyển nơi lưu trữ/vận hành, không phải nhập dữ liệu ASSETCONTROL vào MRERP hoặc nhập dữ liệu Nhà ZUZU vào MRE. Phải xác minh tenant/codebase ASSETCONTROL theo OD-17 trước khi đụng dữ liệu. Giữ UUID, storage key và khóa mã hóa cần thiết để liên kết và Vault tiếp tục dùng được. Công cụ backup/restore cụ thể phụ thuộc database/runtime thực tế đã audit.

Quy trình chuyển đề xuất cho quy mô ban đầu:

1. Kiểm kê phiên bản/schema, dung lượng, file, khóa cần thiết và mọi nguồn ghi (web/API/worker/scheduler/integration).
2. Dựng bản đích cô lập, restore thử từ backup và kiểm tính toàn vẹn, quyền, file và khả năng giải mã theo quy trình product.
3. Chọn cửa sổ bảo trì, dừng mọi nguồn ghi ở bản cũ, hoàn tất/drain hoặc xử lý job đang chạy theo runbook; tạo database/media backup nhất quán cuối cùng rồi restore bản đích. Không chạy scheduler/job hai nơi gây tác dụng kép.
4. Kiểm bản đích, chuyển routing/DNS với HTTPS phù hợp; bản cũ tiếp tục chặn ghi trong thời gian DNS cache còn tồn tại. Mở nguồn ghi tại bản đích sau kiểm tra và giám sát.
5. Giữ bản cũ và backup trong thời hạn được duyệt. Rollback trước khi bản đích nhận ghi có thể quay lại bản cũ; sau khi bản đích đã nhận dữ liệu mới, cần dừng ghi và đồng bộ/restore ngược có kiểm chứng, không chỉ đổi DNS.

Chưa cam kết migration không downtime hoặc thời lượng downtime. Hai VPS theo bố trí trên tách tải và phạm vi sự cố, không phải HA: mất VPS ASSETCONTROL thì ASSETCONTROL ngừng; MRERP giữ nghiệp vụ lõi nhờ snapshot/fallback theo contract. Chi phí phương án B là 300.000 đồng/tháng hiện tại cộng VPS mới và các khoản backup/domain/dịch vụ cần dùng; chưa có báo giá VPS mới để tính tổng.
