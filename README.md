# MRERP Platform

MRERP là repository mới cho nền tảng làm việc chung của MRE. Repository dự kiến chứa MRERP Core và MRECRM dưới dạng các deployable có ranh giới riêng, đồng thời cung cấp contract và design system dùng chung. ASSETCONTROL và repository MREKANBAN hiện tại tiếp tục nằm ngoài repository này trong giai đoạn đầu.

Repository GitHub: [luuhavy121-bot/MRERP](https://github.com/luuhavy121-bot/MRERP)

## Trạng thái hiện tại

Repository đang ưu tiên **Phase 3 — Văn hóa và vận hành nhân sự** theo ADR-0013; Phase 1–2 chưa nghiệm thu vẫn giữ trạng thái riêng và không được tự coi là hoàn thành.

Phase 0 đã qua cổng duyệt. Slice People/HR Foundation đầu tiên hiện có React/Vite frontend, Django/DRF API, migration, authorization fail-closed, audit và automated tests. App có màn hình Tiến độ quản trị tạm thời, tự ẩn khi tổng tiến độ đạt 100%; phần trăm không thay thế bằng chứng nghiệm thu. Local development dùng SQLite mặc định hoặc PostgreSQL 16 qua Docker Compose. Mock Identity chỉ dành cho development/test và tự từ chối khởi động ở production; Identity Provider production vẫn **Chưa quyết định**.

People/HR Foundation đã được người sở hữu sản phẩm nghiệm thu `Accepted` ngày 29/08/2026. People account/employment lifecycle và gói Tổng quan–Bảng tin–Công việc vẫn `In progress / Chờ nghiệm thu`. Leave/Attendance Phase 2 đang mở rộng theo [ADR-0012](docs/decisions/0012-phase-2-leave-attendance-foundation.md) với edit pending, holiday calendar Việt Nam và HR adjustment; máy chấm công/payroll vẫn ngoài phạm vi.

## Thứ tự đọc bắt buộc

1. [AGENTS.md](AGENTS.md) — quy tắc làm việc và giới hạn chủ động.
2. [01 — Tổng quan sản phẩm](docs/01-tong-quan-san-pham.md).
3. [02 — Yêu cầu sản phẩm](docs/02-yeu-cau-san-pham.md).
4. [03 — Thiết kế kỹ thuật](docs/03-thiet-ke-ky-thuat.md).
5. [04 — Tiêu chí nghiệm thu](docs/04-tieu-chi-nghiem-thu.md).
6. [05 — Hướng dẫn và vận hành](docs/05-huong-dan-va-van-hanh.md).
7. [06 — Kế hoạch triển khai](docs/06-ke-hoach-trien-khai.md).
8. [docs/README.md](docs/README.md) — chọn tài liệu chuyên sâu theo miền.
9. [Thuật ngữ](docs/glossary.md), [Open decisions](docs/decisions/open-decisions.md) và các [ADR](docs/decisions/README.md) liên quan.

Hướng dẫn đóng góp: [CONTRIBUTING.md](CONTRIBUTING.md).

## Cấu trúc repository

```text
MRERP/
├─ apps/
│  └─ mrerp/
│     ├─ backend/       # Django/DRF People API và mock Identity
│     └─ frontend/      # React/Vite MRERP shell và People UI
├─ compose.yaml
├─ .gitattributes
├─ .gitignore
├─ .github/
│  ├─ pull_request_template.md
│  └─ workflows/repository-quality.yml
├─ AGENTS.md
├─ CONTRIBUTING.md
├─ README.md
├─ prototype/
│  ├─ README.md
│  ├─ index.html
│  ├─ project-status.js
│  ├─ styles.css
│  └─ app.js
├─ scripts/
│  └─ check_docs.py
└─ docs/
   ├─ README.md
   ├─ glossary.md
   ├─ 01-tong-quan-san-pham.md
   ├─ 02-yeu-cau-san-pham.md
   ├─ 03-thiet-ke-ky-thuat.md
   ├─ 04-tieu-chi-nghiem-thu.md
   ├─ 05-huong-dan-va-van-hanh.md
   ├─ 06-ke-hoach-trien-khai.md
   ├─ product/
   │  ├─ product-overview.md
   │  ├─ business-requirements.md
   │  ├─ backlog.md
   │  ├─ stories/
   │  │  ├─ phase-1-people-foundation.md
   │  │  └─ phase-1-task-vertical-slice.md
   │  └─ roadmap.md
   ├─ architecture/
   │  ├─ technical-architecture.md
   │  ├─ data-ownership.md
   │  ├─ identity-and-authorization.md
   │  ├─ people-data-contract.md
   │  ├─ people-authorization-matrix.md
   │  ├─ task-authorization-matrix.md
   │  └─ ecosystem-integration.md
   ├─ operations/
   │  ├─ deployment.md
   │  └─ configuration-and-secrets.md
   ├─ testing/
   │  ├─ test-strategy.md
   │  ├─ definition-of-ready.md
   │  ├─ phase-1-people-acceptance.md
   │  ├─ phase-1-people-readiness.md
   │  └─ phase-1-task-acceptance.md
   └─ decisions/
      ├─ README.md
      ├─ ADR-TEMPLATE.md
      ├─ 0001-repository-governance-baseline.md
      ├─ 0002-task-authorization-baseline.md
      ├─ 0003-phase-1-application-stack.md
      ├─ 0004-mock-identity-context.md
      ├─ 0005-people-authorization-and-field-policy.md
      ├─ 0006-employee-account-provisioning.md
      └─ open-decisions.md
```

## Nguyên tắc cốt lõi

- Một danh tính đăng nhập chung, nhưng từng product tự kiểm tra quyền tại server.
- MRERP là nguồn chuẩn của nhân sự, cơ cấu tổ chức và Task.
- CRM và ASSETCONTROL giữ data ownership riêng.
- Không đọc database chéo product.
- Dashboard dùng snapshot/read model và không phụ thuộc trực tiếp vào CRM khi tải trang.
- Không tự quyết những mục được đánh dấu **Chưa quyết định**.

## Prototype

[Prototype giao diện mới](prototype/README.md) minh họa app shell, Dashboard và các bề mặt nghiệp vụ bằng dữ liệu mock. Có thể chạy trực tiếp mà không cài dependency.

Prototype chỉ minh họa giao diện và UX. Không được coi prototype là production backend, database, Identity, authorization hoặc bằng chứng cho một quyết định kiến trúc. Mọi màn hình sẽ được thay dữ liệu mock bằng vertical slice có API contract và kiểm tra quyền ở server sau khi các cổng tương ứng được duyệt.

## Chạy local

Xem [hướng dẫn backend](apps/mrerp/backend/README.md) và [hướng dẫn frontend](apps/mrerp/frontend/README.md). Chế độ nhanh dùng SQLite; Docker Compose dùng PostgreSQL 16. Không dùng mock Identity hoặc credential demo ở production.
