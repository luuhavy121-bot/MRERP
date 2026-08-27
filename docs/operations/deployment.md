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
