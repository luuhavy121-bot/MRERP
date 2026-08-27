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

Chưa có:

- Frontend/backend scaffold.
- Database migration.
- Dependency ứng dụng.
- Identity Provider được chọn.
- Tính năng nghiệp vụ.
- Conventions/CI/secret-handling hoàn chỉnh cho Phase 1.

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
2. Hoàn tất baseline Git và kiểm tra chất lượng tài liệu.
3. Chốt conventions, CI tối thiểu và secret-handling rule cho Phase 1.
4. Ưu tiên các open decision chặn Phase 1: role boundary, Admin access, cơ cấu/capability chính thức và Identity contract giả lập.
5. Tạo ADR cho những lựa chọn cần hiện thực.
6. Chỉ sau khi có yêu cầu chuyển Phase 1 mới scaffold stack được duyệt.

## Đọc sâu hơn

- [Roadmap chi tiết](product/roadmap.md)
- [Open decisions](decisions/open-decisions.md)
- [ADR process](decisions/README.md)
- [Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md)
