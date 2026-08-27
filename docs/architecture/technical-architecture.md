# Kiến trúc kỹ thuật MRERP

Tài liệu này là source of truth chịu trách nhiệm chính cho architectural drivers, kiến trúc product, stack và cấu trúc monorepo mục tiêu. Bản đọc ngắn nằm tại [03 — Thiết kế kỹ thuật](../03-thiet-ke-ky-thuat.md).

## 1. Architectural drivers

**Đã chốt.** Kiến trúc phải:

- Cung cấp một hệ sinh thái thống nhất mà không gom mọi dữ liệu/process vào một app.
- Giữ data ownership và authorization tại product sở hữu dữ liệu.
- Đủ đơn giản để một developer cùng AI vận hành.
- Cô lập tải CRM khỏi nghiệp vụ MRERP.
- Dữ liệu hóa cấu hình tổ chức để có thể tái sử dụng platform.
- Chịu được lỗi integration mà không làm hỏng nghiệp vụ lõi.

## 2. Kiến trúc product

### MRERP Core

**Đã chốt.** Modular monolith.

Module giao tiếp qua service/use-case contract rõ ràng; không import view hoặc sửa bảng của nhau tùy tiện.

### MRECRM

**Đề xuất mục tiêu cần ADR.** Modular monolith có thể build/test/deploy độc lập, nằm cùng monorepo mới với MRERP.

Không chia thành microservice theo Customer, Order, Product hoặc Channel ở giai đoạn đầu.

### ASSETCONTROL

**Đã chốt về hiện trạng và ranh giới.** Product/repository/deployment riêng; codebase hiện tại là Django monolith có service layer.

**Chưa quyết định.** Hình thức tái sử dụng cho MRE.

### MREKANBAN

**Đã chốt theo hướng chuyển tiếp.** Repository/product hiện tại giữ riêng và dùng `task_uuid` từ MRERP.

**Chưa quyết định.** Retire hay giữ làm client/view chuyên sâu dài hạn; kiến trúc nội bộ cần audit.

## 3. Tech stack

Toàn bộ mục này là **Đề xuất mục tiêu cần ADR** trước khi scaffold production:

- Frontend: React, TypeScript và Vite bản ổn định.
- Backend: Python 3.12, Django 5.2 và Django REST Framework.
- Database: PostgreSQL 16.
- Background processing khi có use case: Celery và Redis.
- API contract: OpenAPI; frontend client sinh hoặc được kiểm soát từ contract.
- SSO: OpenID Connect/OAuth 2.0 với Identity Provider chuẩn.
- Deployment: Docker Compose, reverse proxy và HTTPS.
- Observability: structured logs, error tracking, uptime và metrics cần thiết.

**Không làm.** Không chọn Next/Vinext beta của prototype làm production chỉ vì prototype dùng stack đó.

## 4. Kiến trúc ba tầng tái sử dụng

### Platform

**Đề xuất mục tiêu.**

- Identity integration.
- Employee identity và organization model đa chiều.
- Permission guard fail-closed.
- Module registry.
- Audit foundation.
- API contract, shared identifier và event envelope.
- Design system và API client.

### Company Configuration

**Đề xuất mục tiêu bắt buộc.** Cấp bậc, phòng ban, team, cây tổ chức, capability mặc định, scope policy, branding, feature flags, cultural values và reward catalog phải là dữ liệu/configuration.

### Business Modules

**Đề xuất mục tiêu.** Task, leave, attendance, approval, recognition, recruitment, documents và CRM dùng Platform nhưng giữ workflow/data ownership riêng.

Không tạo abstraction chung quá sớm. Chỉ trích xuất platform package khi có ít nhất hai use case thật chứng minh phần dùng chung.

## 5. Cấu trúc monorepo mục tiêu

**Đề xuất mục tiêu cần ADR.**

```text
mre-platform/
├─ apps/
│  ├─ mrerp/
│  │  ├─ frontend/
│  │  └─ backend/
│  └─ mrecrm/
│     ├─ frontend/
│     └─ backend/
├─ packages/
│  ├─ contracts/
│  ├─ api-client/
│  ├─ design-system/
│  └─ shared-types/
├─ infra/
│  ├─ docker/
│  ├─ reverse-proxy/
│  ├─ identity/
│  ├─ monitoring/
│  └─ backup/
├─ docs/
├─ tests/
│  ├─ contract/
│  ├─ integration/
│  └─ e2e/
├─ AGENTS.md
└─ README.md
```

ASSETCONTROL và repository MREKANBAN hiện tại không nằm làm source subfolder trong monorepo giai đoạn đầu. Không dùng Git submodule khi chưa có nhu cầu được chứng minh.

## 6. Backend modular monolith

**Đề xuất mục tiêu.** Mỗi Django module giữ model, service/use case, selector/query, API và test của mình.

```text
backend/
├─ config/
├─ platform/
│  ├─ identity/
│  ├─ organizations/
│  ├─ permissions/
│  ├─ audit/
│  └─ modules/
├─ modules/
│  ├─ people/
│  ├─ attendance/
│  ├─ approvals/
│  ├─ tasks/
│  ├─ recognition/
│  ├─ recruitment/
│  ├─ documents/
│  └─ reporting/
└─ tests/
```

Đây là gợi ý cấu trúc, không phải yêu cầu tạo package chung giả tạo.

## 7. Frontend

**Đề xuất mục tiêu.**

- Route/navigation phản ánh module nghiệp vụ.
- Design system không chứa business permission logic.
- API client dựa trên OpenAPI.
- Route guard và ẩn menu chỉ phục vụ UX.
- CRM table dùng server-side pagination/filter/sort.
- Thiết kế rõ loading, empty, error, stale và forbidden state.
- Không đưa toàn bộ ứng dụng vào một component lớn.

## 8. Prototype

**Đã chốt về phạm vi sử dụng.** Prototype Codex chỉ là UI end-state với dữ liệu minh họa; chưa có backend, PostgreSQL, OIDC hoặc authorization production. Prototype Claude chỉ là tham khảo về fail-closed, configuration, contract, snapshot và ghi khoảng trống.

Mỗi phần prototype phải được phân loại: dùng trực tiếp, dùng ý tưởng/UX, viết lại production hoặc loại bỏ.

## 9. Ranh giới quyết định

| Nội dung | Trạng thái | Open decision/ADR cần có |
|---|---|---|
| MRERP modular monolith | **Đã chốt** | Không |
| CRM modular monolith deploy độc lập | **Đề xuất mục tiêu** | ADR trước khi scaffold CRM |
| Stack mục tiêu | **Đề xuất mục tiêu** | ADR stack/baseline trước scaffold |
| Database hay schema riêng | **Chưa quyết định** | OD-09 |
| Identity Provider | **Chưa quyết định** | OD-01 |
| Service authentication | **Chưa quyết định** | OD-11 |
| Tool monitoring/reverse proxy | **Chưa quyết định** | OD-15 |

## 10. Tài liệu liên quan

- [Data ownership](data-ownership.md)
- [Identity và phân quyền](identity-and-authorization.md)
- [Tích hợp hệ sinh thái](ecosystem-integration.md)
- [Deployment](../operations/deployment.md)
