# MRERP Platform

MRERP là repository mới cho nền tảng làm việc chung của MRE. Repository dự kiến chứa MRERP Core và MRECRM dưới dạng các deployable có ranh giới riêng, đồng thời cung cấp contract và design system dùng chung. ASSETCONTROL và repository MREKANBAN hiện tại tiếp tục nằm ngoài repository này trong giai đoạn đầu.

Repository GitHub: [luuhavy121-bot/MRERP](https://github.com/luuhavy121-bot/MRERP)

## Trạng thái hiện tại

Repository đang ở **Phase 0 — khóa context và nền tài liệu**.

Hiện chưa có frontend/backend production, database migration hoặc dependency ứng dụng. Repository có một [visual prototype không dependency](prototype/README.md) để duyệt hướng giao diện; prototype này không phải application scaffold hay bằng chứng backend/authorization đã tồn tại. Phần tài liệu của Phase 0 đã được thiết lập nhưng Phase 0 chỉ được đóng khi đạt cổng trong [04 — Tiêu chí nghiệm thu](docs/04-tieu-chi-nghiem-thu.md). Các tài liệu kiến trúc có nhãn **Đề xuất mục tiêu** chưa phải là quyết định production cuối cùng nếu chưa có ADR được chấp nhận.

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

## Cấu trúc Phase 0

```text
MRERP/
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
   │  └─ roadmap.md
   ├─ architecture/
   │  ├─ technical-architecture.md
   │  ├─ data-ownership.md
   │  ├─ identity-and-authorization.md
   │  └─ ecosystem-integration.md
   ├─ operations/
   │  ├─ deployment.md
   │  └─ configuration-and-secrets.md
   ├─ testing/
   │  └─ test-strategy.md
   └─ decisions/
      ├─ README.md
      ├─ ADR-TEMPLATE.md
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
