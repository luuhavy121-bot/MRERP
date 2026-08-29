# 06 — Kế hoạch triển khai

Roadmap chi tiết được quản lý tại [Roadmap chuyên sâu](product/roadmap.md). Tài liệu này cho biết đang ở đâu, cổng chuyển phase và bước tiếp theo.

## Trạng thái hiện tại

**Hiện tại: Phase 2 — đang triển khai nền Leave/Attendance đơn giản theo ADR-0012. People/HR Foundation đã được nghiệm thu; các gói Phase 1 khác vẫn giữ trạng thái chờ nghiệm thu riêng.**

Đã có:

- `AGENTS.md` và README.
- Đường đọc chính `01–06`.
- Source of truth chuyên sâu theo miền.
- Danh sách open decisions.
- ADR template và quy trình ADR.
- Glossary và test strategy ban đầu.
- Governance baseline: `.gitignore`, `.gitattributes`, CONTRIBUTING, PR template và CI repository checker.
- Workflow `Repository quality` đã chạy thành công trên GitHub sau khi baseline được push.
- ADR-0002 và ADR-0011 đã chốt permission/policy cục bộ cho Task, Goal, Feed, Dashboard, recurrence và local-media.
- Task stories và acceptance ba module ở trạng thái `In progress / Chờ nghiệm thu`.
- Gói refinement People/HR Foundation đã có stories, field/data/API draft, permission matrix, migration approach, acceptance scenarios và readiness register.
- ADR-0003 đến ADR-0009 đã được chấp nhận cho People/HR Foundation; ADR-0009 thay mô hình Department → Team bằng cơ cấu phẳng CEO → Team → Employee.
- React/Vite frontend, Django/DRF API, migration, mock Identity development/test, authorization, audit và automated tests của slice đã được tạo.
- People UI có Danh bạ, sơ đồ `CEO → Team → Employee` và split-view Team → nhân sự; mọi view dùng cùng server authorization/projection đã chốt.
- Danh bạ dùng pagination/search/filter phía server; có hồ sơ cá nhân, correlation ID, error envelope và object rule chống Leader tự đổi scope.
- Bộ kiểm thử local hiện có 87 backend tests và 6 luồng Playwright E2E; số liệu cuối cùng phải lấy từ CI và không thay thế nghiệm thu.
- People/HR Foundation được người sở hữu sản phẩm nghiệm thu `Accepted` ngày 29/08/2026; trạng thái này không bao gồm các nghiệp vụ People ngoài slice.
- Phần mở rộng People có trang `Hồ sơ của tôi` gồm thông tin cá nhân và account, provision/reset/lock account, employment pause/terminate/reactivate, lịch sử, CSV, People audit và Admin access bundle. Phần này giữ trạng thái `In progress / Chờ nghiệm thu`.
- Leave/Attendance có UI tạo/sửa đơn pending, Leader duyệt một cấp, holiday calendar Việt Nam, HR adjustment, API, migration, authorization, audit, 17 backend tests và một E2E xuyên ba persona.
- Repository CI chạy docs/secret hygiene, backend tests trên PostgreSQL 16, OpenAPI validation và frontend lint/build.
- App React có màn hình Tiến độ tạm thời cho phase/module/gate; màn hình tự ẩn khi tổng tiến độ đạt 100% và không được dùng thay bằng chứng nghiệm thu.

Chưa có:

- Identity Provider production được chọn.
- Deployment production, HTTPS/reverse proxy và runbook production hoàn chỉnh.
- Identity production, payroll và các module ngoài People/HR Foundation cùng baseline Leave/Attendance hiện tại.
- Bằng chứng load/restore production.

Đã có thêm một [visual prototype không dependency](../prototype/README.md) để duyệt hướng thiết kế và minh họa trạng thái màn hình. Đây không phải scaffold production và không thay đổi trạng thái các quyết định kiến trúc.

## Các phase mục tiêu

1. Phase 0: context, tài liệu, conventions và ADR.
2. Phase 1: nền Identity contract, People/HR Foundation, Leave/Attendance baseline và Tổng quan–Bảng tin–Công việc.
3. Phase 2: policy Leave/Attendance mở rộng, approval, Kanban view và Dashboard snapshot/fallback ngoài dữ liệu nội bộ.
4. Phase 3: recognition/rewards, recruitment, documents và settings.
5. Phase 4: tích hợp ASSETCONTROL và MREKANBAN hiện hữu.
6. Phase 5: CRM tối thiểu, field policy, channel worker, reporting read model và load test.

Toàn bộ roadmap là **Đề xuất mục tiêu**; phạm vi từng phase phải được xác nhận trước khi triển khai.

**Đã chốt trong task ngày 29/08/2026:** ưu tiên triển khai Phase 3 trước phần còn lại của Phase 2. Phạm vi baseline nằm tại [Yêu cầu Phase 3](product/phase-3-requirements.md) và [ADR-0013](decisions/0013-phase-3-culture-operations-baseline.md).

## Cổng chuyển sang Phase 1

Chỉ chuyển phase khi:

- Người sở hữu sản phẩm duyệt source of truth Phase 0.
- Phạm vi vertical slice đầu tiên được xác nhận; hiện gói đề xuất là People/HR Foundation.
- Identity contract giả lập được chấp nhận mà không chọn IdP thật.
- Permission semantics tối thiểu cho slice được chốt.
- Data ownership trong slice không còn mơ hồ.
- Definition of Done và test strategy được duyệt.

## Bước tiếp theo đề xuất

1. Nghiệm thu Phase 3 baseline đã triển khai: Settings → Recruitment → Documents → Recognition/Stars.
2. Giữ reward catalog/redemption ngoài implementation tới khi OD-05/OD-13 được duyệt phần còn lại.
3. Không trộn trạng thái nghiệm thu Phase 1–2 với Phase 3.
4. Khi quay lại Payroll hoặc máy chấm công, giải quyết phần tương ứng của OD-13 trước.

## Đọc sâu hơn

- [Roadmap chi tiết](product/roadmap.md)
- [Open decisions](decisions/open-decisions.md)
- [ADR process](decisions/README.md)
- [Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md)
