# 06 — Kế hoạch triển khai

Roadmap chi tiết được quản lý tại [Roadmap chuyên sâu](product/roadmap.md). Tài liệu này cho biết đang ở đâu, cổng chuyển phase và bước tiếp theo.

## Trạng thái hiện tại

**Hiện tại: Phase 0 — khóa context và nền tài liệu; chưa đóng phase.**

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

Chưa có:

- Frontend/backend scaffold.
- Database migration.
- Dependency ứng dụng.
- Identity Provider được chọn.
- Tính năng nghiệp vụ.
- Story Phase 1 ở trạng thái `Ready`.

Đã có thêm một [visual prototype không dependency](../prototype/README.md) để duyệt hướng thiết kế và minh họa trạng thái màn hình. Đây không phải scaffold production và không thay đổi trạng thái các quyết định kiến trúc.

## Các phase mục tiêu

1. Phase 0: context, tài liệu, conventions và ADR.
2. Phase 1: nền Identity contract, Employee/Team, permission, shell và một Task vertical slice.
3. Phase 2: leave/attendance, approval, Task views và Dashboard fallback.
4. Phase 3: recognition/rewards, recruitment, documents và settings.
5. Phase 4: tích hợp ASSETCONTROL và MREKANBAN hiện hữu.
6. Phase 5: CRM tối thiểu, field policy, channel worker, reporting read model và load test.

Toàn bộ roadmap là **Đề xuất mục tiêu**; phạm vi từng phase phải được xác nhận trước khi triển khai.

## Cổng chuyển sang Phase 1

Chỉ chuyển phase khi:

- Người sở hữu sản phẩm duyệt source of truth Phase 0.
- Phạm vi Task vertical slice được xác nhận.
- Identity contract giả lập được chấp nhận mà không chọn IdP thật.
- Permission semantics tối thiểu cho slice được chốt.
- Data ownership trong slice không còn mơ hồ.
- Definition of Done và test strategy được duyệt.

## Bước tiếp theo đề xuất

1. Người sở hữu sản phẩm duyệt sáu tài liệu đường đọc chính.
2. Duyệt [backlog](product/backlog.md), [Task stories](product/stories/phase-1-task-vertical-slice.md), [ma trận quyền](architecture/task-authorization-matrix.md) và [Definition of Ready](testing/definition-of-ready.md).
3. Chốt các điểm còn chặn slice: quyền đọc Task nền, API/data contract, Identity contract giả lập và stack qua ADR.
4. Hoàn thiện test cases từ [Task acceptance scenarios](testing/phase-1-task-acceptance.md), rồi đưa từng story đủ điều kiện sang `Ready`.
5. Chỉ sau khi cổng Phase 1 được duyệt và có yêu cầu chuyển phase mới scaffold stack được duyệt.

## Đọc sâu hơn

- [Roadmap chi tiết](product/roadmap.md)
- [Open decisions](decisions/open-decisions.md)
- [ADR process](decisions/README.md)
- [Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md)
