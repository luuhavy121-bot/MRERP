# Roadmap MRERP

Roadmap này là **Đề xuất mục tiêu**. Mỗi phase cần được xác nhận phạm vi, có vertical slice chạy đúng và có ADR cho quyết định kiến trúc liên quan. Không triển khai toàn bộ module chỉ để làm nhiều menu hoạt động.

Đây là source of truth chịu trách nhiệm chính cho thứ tự phase. Bản trạng thái ngắn nằm tại [06 — Kế hoạch triển khai](../06-ke-hoach-trien-khai.md).

## Phase 0 — Khóa context và nền kỹ thuật

- Tạo repository mới và baseline Git.
- Chuyển context thành source of truth và đường đọc `01–06`.
- Tạo cơ chế ADR và open-decision register.
- Chốt conventions, CI, secret handling và Definition of Done.
- Chỉ scaffold React/Vite và Django/DRF sau khi Phase 0 tài liệu được duyệt và có yêu cầu chuyển phase.

**Trạng thái:** hoàn tất. Source of truth, ADR, glossary, test strategy và repository governance baseline đã được duyệt; CI baseline đã chạy thành công trên GitHub. ADR-0003 đến ADR-0009 đã đóng các quyết định chặn People slice mà không chọn Identity Provider production.

## Phase 1 — Vertical slice nền tảng

- Identity integration giả lập có contract rõ; không tự chọn IdP.
- Employee, Team và employment status theo cơ cấu phẳng dưới CEO.
- Capability, data scope và guard fail-closed.
- MRERP shell và Dashboard tối thiểu.
- Một luồng Task end-to-end: UI → API → database → authorization → audit → test.

**Thứ tự đã thực hiện:** People/HR Foundation là slice đầu; sau baseline Leave/Attendance, Task được mở lại cùng Tổng quan và Bảng tin khi organization/Identity foundation đã sẵn sàng.

**Trạng thái hiện tại:** People/HR Foundation được nghiệm thu `Accepted` ngày 29/08/2026. People account/employment lifecycle, Leave/Attendance và Tổng quan–Bảng tin–Công việc đã được hiện thực, đang `In progress / Chờ nghiệm thu`.

## Phase 2 — Nghiệp vụ nội bộ thiết yếu

- Nghỉ phép/chấm công.
- Phê duyệt theo loại.
- Task/List/Kanban cơ bản.
- Dashboard snapshot/fallback.

**Trạng thái hiện tại:** `In progress` cho foundation Leave/Attendance theo ADR-0012. Phạm vi hiện tại chỉ gồm edit đơn pending, Leader duyệt một cấp, holiday calendar và HR adjustment; Approval tổng quát, máy chấm công, Kanban và Dashboard snapshot chưa được mở.

## Phase 3 — Văn hóa và vận hành nhân sự

- Recognition, sao và đổi thưởng.
- Recruitment.
- Documents.
- Personal Settings.

**Trạng thái hiện tại:** `Implementation hoàn tất / Chờ nghiệm thu` theo ADR-0013. Phase 3 được ưu tiên trước phần còn lại của Phase 2. Baseline đã có Personal Settings, Recruitment, Documents, Recognition, Star ledger/balance/leaderboard xuyên UI/API/database; reward catalog và redemption vẫn **Chưa quyết định**.

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

Backlog dùng [Definition of Ready](../testing/definition-of-ready.md) làm cổng đưa story vào triển khai; không dùng phần trăm prototype để chứng minh production đã hoàn thành.

## Nội dung chưa thuộc các phần People hiện tại

- Không chọn Identity Provider production.
- Không mở Payroll hoặc integration CRM/ASSETCONTROL. Recruitment, Documents và Recognition/Stars chỉ mở trong baseline ADR-0013; redemption/catalog vẫn chưa mở.
- Không tích hợp CRM/ASSETCONTROL.
- Không tự chốt policy nghiệp vụ ngoài ADR đã Accepted.

## Tài liệu liên quan

- [Product backlog](backlog.md)
- [Task vertical slice stories](stories/phase-1-task-vertical-slice.md)
- [People/HR Foundation stories](stories/phase-1-people-foundation.md)
- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Open decisions](../decisions/open-decisions.md)
- [ADR process](../decisions/README.md)
