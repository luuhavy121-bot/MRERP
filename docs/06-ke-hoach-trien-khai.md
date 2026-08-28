# 06 — Kế hoạch triển khai

Roadmap chi tiết được quản lý tại [Roadmap chuyên sâu](product/roadmap.md). Tài liệu này cho biết đang ở đâu, cổng chuyển phase và bước tiếp theo.

## Trạng thái hiện tại

**Hiện tại: Phase 1 — People/HR Foundation đang được hiện thực và kiểm chứng.**

Đã có:

- `AGENTS.md` và README.
- Đường đọc chính `01–06`.
- Source of truth chuyên sâu theo miền.
- Danh sách open decisions.
- ADR template và quy trình ADR.
- Glossary và test strategy ban đầu.
- Governance baseline: `.gitignore`, `.gitattributes`, CONTRIBUTING, PR template và CI repository checker.
- Workflow `Repository quality` đã chạy thành công trên GitHub sau khi baseline được push.
- Backlog cấp Epic cho toàn roadmap và story chi tiết của Task vertical slice Phase 1 ở trạng thái `Refining`.
- ADR-0002 và ma trận quyền đã chốt phần permission semantics của Task được người dùng xác nhận.
- Definition of Ready và acceptance scenarios cho Task đã có bản đề xuất để duyệt.
- Gói refinement People/HR Foundation đã có stories, field/data/API draft, permission matrix, migration approach, acceptance scenarios và readiness register.
- ADR-0003 đến ADR-0008 đã được người sở hữu sản phẩm chấp nhận cho People/HR Foundation; ADR-0007 điều chỉnh account tùy chọn và ADR-0008 chốt CEO toàn quyền People.
- React/Vite frontend, Django/DRF API, migration, mock Identity development/test, authorization, audit và automated tests của slice đã được tạo.
- People UI có Danh bạ, sơ đồ Department → Team → Leader/thành viên và Team management; mọi view dùng cùng server authorization/projection đã chốt.
- Repository CI chạy docs/secret hygiene, backend tests trên PostgreSQL 16, OpenAPI validation và frontend lint/build.
- App React có màn hình Tiến độ tạm thời cho phase/module/gate; màn hình tự ẩn khi tổng tiến độ đạt 100% và không được dùng thay bằng chứng nghiệm thu.

Chưa có:

- Identity Provider production được chọn.
- Deployment production, HTTPS/reverse proxy và runbook production hoàn chỉnh.
- Các module ngoài People/HR Foundation.
- Bằng chứng load/restore production.

Đã có thêm một [visual prototype không dependency](../prototype/README.md) để duyệt hướng thiết kế và minh họa trạng thái màn hình. Đây không phải scaffold production và không thay đổi trạng thái các quyết định kiến trúc.

## Các phase mục tiêu

1. Phase 0: context, tài liệu, conventions và ADR.
2. Phase 1: nền Identity contract, People/HR Foundation và permission trước; shell và Task vertical slice theo sau khi dependency sẵn sàng.
3. Phase 2: leave/attendance, approval, Task views và Dashboard fallback.
4. Phase 3: recognition/rewards, recruitment, documents và settings.
5. Phase 4: tích hợp ASSETCONTROL và MREKANBAN hiện hữu.
6. Phase 5: CRM tối thiểu, field policy, channel worker, reporting read model và load test.

Toàn bộ roadmap là **Đề xuất mục tiêu**; phạm vi từng phase phải được xác nhận trước khi triển khai.

## Cổng chuyển sang Phase 1

Chỉ chuyển phase khi:

- Người sở hữu sản phẩm duyệt source of truth Phase 0.
- Phạm vi vertical slice đầu tiên được xác nhận; hiện gói đề xuất là People/HR Foundation.
- Identity contract giả lập được chấp nhận mà không chọn IdP thật.
- Permission semantics tối thiểu cho slice được chốt.
- Data ownership trong slice không còn mơ hồ.
- Definition of Done và test strategy được duyệt.

## Bước tiếp theo đề xuất

1. Hoàn tất kiểm chứng People slice trên PostgreSQL, migration/rollback, frontend build và authorization tests.
2. Người sở hữu sản phẩm nghiệm thu luồng local theo [People acceptance scenarios](testing/phase-1-people-acceptance.md).
3. Refinement slice tiếp theo; Task vẫn là ứng viên theo roadmap nhưng không tự động bắt đầu.
4. Giải quyết OD-19 bằng ADR riêng trước khi kết nối Identity production.

## Đọc sâu hơn

- [Roadmap chi tiết](product/roadmap.md)
- [Open decisions](decisions/open-decisions.md)
- [ADR process](decisions/README.md)
- [Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md)
