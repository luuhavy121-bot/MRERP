# 03 — Thiết kế kỹ thuật

Tài liệu này mô tả kiến trúc bằng ngôn ngữ ngắn gọn. Mỗi chủ đề kỹ thuật có một tài liệu chuyên sâu chịu trách nhiệm chính và được dẫn bên dưới.

## Bức tranh tổng thể

```text
Nhân sự MRE
    │
    ▼
Identity Provider
    │
    ├──────────────┬──────────────────┐
    ▼              ▼                  ▼
MRERP Core       MRECRM          ASSETCONTROL
    │
    ▼
MREKANBAN tham chiếu Task trong giai đoạn chuyển tiếp

ASSETCONTROL ── API ──▶ MKTLogin (hệ thống bên ngoài)
```

**Đã chốt.** MRERP, CRM và ASSETCONTROL giữ data ownership riêng. Chạy cùng VPS không cho phép đọc database của nhau.

Sơ đồ chỉ thể hiện quan hệ logic. Nó không chốt nơi triển khai Identity Provider hoặc tương lai dài hạn của MREKANBAN.

## Kiến trúc ứng dụng

- **Đã chốt:** MRERP Core là modular monolith.
- **Đề xuất mục tiêu cần ADR:** MRECRM là modular monolith deploy độc lập trong cùng monorepo mới.
- **Đã chốt về hiện trạng:** ASSETCONTROL là Django monolith và giữ repo/deployment riêng.
- **Chưa quyết định:** kiến trúc dài hạn và việc retire/giữ MREKANBAN.

Chi tiết: [Kiến trúc kỹ thuật](architecture/technical-architecture.md).

## Dữ liệu

Mỗi miền có đúng một nguồn chuẩn. Product khác chỉ nhận UUID, snapshot hoặc aggregate tối thiểu theo quyền.

Chi tiết: [Data ownership](architecture/data-ownership.md).

## Identity và quyền

**Đề xuất mục tiêu.** Các product dùng OIDC/OAuth 2.0 với Identity Provider chuẩn. Provider cụ thể chưa được chọn.

**Đã chốt.** Product đích tự kiểm sáu lớp quyền tại server: account/employment, product, action, scope, object và field.

Task Phase 1 đã có [ma trận quyền chuyên biệt](architecture/task-authorization-matrix.md). Ma trận này không tự áp dụng sang CRM, HR, Rewards hoặc Admin Panel.

People/HR Phase 1 có [data/API contract](architecture/people-data-contract.md) và [ma trận quyền riêng](architecture/people-authorization-matrix.md). Stack, mock Identity, People policy, account tùy chọn, bundle CEO và cơ cấu phẳng theo Team đã được chấp nhận trong ADR-0003 đến ADR-0009. Identity Provider production vẫn **Chưa quyết định**.

Chi tiết: [Identity và phân quyền](architecture/identity-and-authorization.md).

## Liên kết product

Hệ sinh thái dùng đúng công cụ theo mục đích: deep link để điều hướng, REST khi cần phản hồi ngay, event/queue cho thông báo bất đồng bộ và snapshot/read model cho Dashboard.

**Đã chốt qua ADR-0014.** MKTLogin giữ chức năng vận hành thực tế của nó; ASSETCONTROL quản lý Resource/Grant/audit và liên kết resource qua API. MKT City không thuộc phạm vi. API authentication, mapping và failure contract chi tiết vẫn **Chưa quyết định**.

Chi tiết: [Tích hợp hệ sinh thái](architecture/ecosystem-integration.md).

## Triển khai

**Đề xuất mục tiêu.** MRERP và CRM có thể bắt đầu trên cùng VPS Platform nhưng là deployable và logical data owner riêng. CRM chỉ chuyển VPS khi monitoring/load test chứng minh cần thiết.

Chi tiết: [Deployment và vận hành](operations/deployment.md).

## Stack mục tiêu

**Đã chốt cho Phase 1 theo ADR-0003 và ADR-0011.** React/TypeScript/Vite cho frontend; Python 3.12, Django 5.2 và DRF cho backend; PostgreSQL 16; OpenAPI và Docker Compose. Celery/Redis đã được thêm cho recurring Task, deadline notification và retention; không dùng result backend. Reverse proxy và HTTPS production vẫn theo kế hoạch deployment.

Contract mới: [Dashboard–Feed–Task](architecture/dashboard-feed-task-contract.md).

**Đã chốt cục bộ qua ADR-0013.** Phase 3 thêm bốn module trong MRERP modular monolith: `preferences_domain`, `recruitment_domain`, `documents_domain` và `rewards_domain`. File vẫn qua protected download và local-media persistent volume; API không trả storage path. Chi tiết tại [contract Phase 3](architecture/phase-3-contract.md) và [ma trận quyền Phase 3](architecture/phase-3-authorization-matrix.md).

Chi tiết và giới hạn prototype: [Kiến trúc kỹ thuật](architecture/technical-architecture.md).

## Những điều chưa được chọn

Identity Provider, database/schema topology, service authentication, monitoring stack, break-glass và ngưỡng tách CRM đều **Chưa quyết định**.

Danh sách đầy đủ: [Open decisions](decisions/open-decisions.md).

Tiếp theo: [04 — Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md).
