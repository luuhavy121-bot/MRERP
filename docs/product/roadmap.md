# Roadmap MRERP

Roadmap này là **Đề xuất mục tiêu**. Mỗi phase cần được xác nhận phạm vi, có vertical slice chạy đúng và có ADR cho quyết định kiến trúc liên quan. Không triển khai toàn bộ module chỉ để làm nhiều menu hoạt động.

Đây là source of truth chịu trách nhiệm chính cho thứ tự phase. Bản trạng thái ngắn nằm tại [06 — Kế hoạch triển khai](../06-ke-hoach-trien-khai.md).

## Phase 0 — Khóa context và nền kỹ thuật

- Tạo repository mới và baseline Git.
- Chuyển context thành source of truth và đường đọc `01–06`.
- Tạo cơ chế ADR và open-decision register.
- Chốt conventions, CI, secret handling và Definition of Done.
- Chỉ scaffold React/Vite và Django/DRF sau khi Phase 0 tài liệu được duyệt và có yêu cầu chuyển phase.

**Trạng thái hiện tại:** nền tài liệu, ADR, glossary và test strategy đã có; Phase 0 chưa đóng vì còn cần duyệt source of truth và hoàn tất conventions/CI/secret handling cho Phase 1.

## Phase 1 — Vertical slice nền tảng

- Identity integration giả lập có contract rõ; không tự chọn IdP.
- Employee, Department, Team và employment status.
- Capability, data scope và guard fail-closed.
- MRERP shell và Dashboard tối thiểu.
- Một luồng Task end-to-end: UI → API → database → authorization → audit → test.

## Phase 2 — Nghiệp vụ nội bộ thiết yếu

- Nghỉ phép/chấm công.
- Phê duyệt theo loại.
- Task/List/Kanban cơ bản.
- Dashboard snapshot/fallback.

## Phase 3 — Văn hóa và vận hành nhân sự

- Recognition, sao và đổi thưởng.
- Recruitment.
- Documents.
- Personal Settings.

## Phase 4 — Tích hợp product hiện hữu

- Audit tài khoản và Task hiện tại.
- Map UUID.
- ASSETCONTROL OIDC dual-run và rollback.
- MREKANBAN dùng Task contract hoặc migration được duyệt.

## Phase 5 — MRECRM

- Customer, Product và Order tối thiểu.
- Field-level permission.
- Adapter từng kênh và worker riêng.
- Reporting read model sang MRERP.
- Load test trước khi quyết định tách VPS.

## Cổng chuyển phase

Trước khi bắt đầu code Phase 1 cần tối thiểu:

- Source of truth Phase 0 được duyệt.
- Có quyết định về phạm vi vertical slice.
- Contract Identity giả lập được chấp nhận mà không lựa chọn IdP thật.
- Permission semantics tối thiểu cho slice được chốt.
- Data ownership không còn mơ hồ trong slice.
- Definition of Done và chiến lược test được xác nhận.

## Nội dung không thuộc Phase 0 hiện tại

- Không scaffold frontend/backend.
- Không tạo database migration.
- Không cài dependency.
- Không chọn Identity Provider.
- Không chốt policy nghiệp vụ thay người dùng.

## Tài liệu liên quan

- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Open decisions](../decisions/open-decisions.md)
- [ADR process](../decisions/README.md)
