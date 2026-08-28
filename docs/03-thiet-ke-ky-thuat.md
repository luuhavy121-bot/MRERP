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

People/HR Phase 1 có [data/API contract](architecture/people-data-contract.md) và [ma trận quyền riêng](architecture/people-authorization-matrix.md). Stack, mock Identity development/test, People policy và account provisioning đã được chấp nhận trong ADR-0003 đến ADR-0006 cho slice này. Việc chọn Identity Provider production vẫn **Chưa quyết định**.

Chi tiết: [Identity và phân quyền](architecture/identity-and-authorization.md).

## Liên kết product

Hệ sinh thái dùng đúng công cụ theo mục đích: deep link để điều hướng, REST khi cần phản hồi ngay, event/queue cho thông báo bất đồng bộ và snapshot/read model cho Dashboard.

Chi tiết: [Tích hợp hệ sinh thái](architecture/ecosystem-integration.md).

## Triển khai

**Đề xuất mục tiêu.** MRERP và CRM có thể bắt đầu trên cùng VPS Platform nhưng là deployable và logical data owner riêng. CRM chỉ chuyển VPS khi monitoring/load test chứng minh cần thiết.

Chi tiết: [Deployment và vận hành](operations/deployment.md).

## Stack mục tiêu

**Đã chốt cho Phase 1 theo ADR-0003.** React/TypeScript/Vite cho frontend; Python 3.12, Django 5.2 và DRF cho backend; PostgreSQL 16; OpenAPI và Docker Compose. Celery/Redis chỉ được thêm khi có use case background job được duyệt; reverse proxy và HTTPS production vẫn theo kế hoạch deployment.

Chi tiết và giới hạn prototype: [Kiến trúc kỹ thuật](architecture/technical-architecture.md).

## Những điều chưa được chọn

Identity Provider, database/schema topology, service authentication, monitoring stack, break-glass và ngưỡng tách CRM đều **Chưa quyết định**.

Danh sách đầy đủ: [Open decisions](decisions/open-decisions.md).

Tiếp theo: [04 — Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md).
