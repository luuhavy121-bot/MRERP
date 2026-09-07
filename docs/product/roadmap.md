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
- Liên kết resource ASSETCONTROL với resource thật trong MKTLogin qua API; không clone MKTLogin và không đưa MKT City vào scope.
- MREKANBAN dùng Task contract hoặc migration được duyệt.

**Trạng thái hiện tại:** `Refining`. Mục tiêu MKTLogin đã được chốt qua ADR-0014; contract API, mapping, quyền thao tác, security và failure handling vẫn bị chặn bởi OD-27. Chưa được coi là đã tích hợp chỉ vì có deep link hoặc bản ghi trùng tên.

**Chuẩn bị tiếp theo:** tài liệu API trong ứng dụng đã được cung cấp; yêu cầu workspace riêng theo Team đã chốt qua ADR-0015. Hoàn thiện [thông tin API cần kiểm kê](../architecture/ecosystem-integration.md#51-thông-tin-api-cần-người-sở-hữu-sản-phẩm-cung-cấp) về workspace thực tế, định danh/liên kết, quyền API và kết nối các máy cài MKTLogin riêng, sau đó đối chiếu khả năng thực tế và trình duyệt phạm vi đọc/xác minh liên kết đầu tiên. Cấp phát, bàn giao và thu hồi tự động vẫn chưa được chốt.

**Bản thiết kế đang duyệt:** [máy công ty + API chỉ đọc + cấp phát có bằng chứng](../architecture/mktlogin-company-device-proposal.md), theo ADR-0016 **Proposed**. Đề xuất thử một Team/Gmail Resource/profile trước; quy trình thu hồi ở bước sau phối hợp bàn giao máy và rà soát quyền tại dịch vụ, theo OD-28. Chưa code, chưa chọn agent điều khiển toàn bộ máy hoặc remote desktop; Phase 4 không chuyển Ready/Accepted chỉ vì đã có bản vẽ.

**Cập nhật bản 02:** workflow MRERP → MKTLogin và chặn quyền dùng khi nghỉ việc là phương án họp nội bộ; không phải khả năng nhà cung cấp đã xác nhận. Tài khoản/profile/tài nguyên công ty giữ nguyên. Cần khảo sát nơi thực thi quyền tại MKTLogin hoặc máy công ty, theo OD-27/OD-28. Khảo sát metadata và thực thi quyền là hai phần cần nghiệm thu riêng; không cam kết tự động chặn khi chỉ khóa MRERP.

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
- Không mở Payroll hoặc CRM trong các phần People hiện tại. Recruitment, Documents và Recognition/Stars chỉ mở trong baseline ADR-0013; redemption/catalog vẫn chưa mở.
- MKTLogin–ASSETCONTROL là workstream Phase 4 riêng; không trộn code integration vào module People/HR.
- Không tự chốt policy nghiệp vụ ngoài ADR đã Accepted.

## Tài liệu liên quan

- [Product backlog](backlog.md)
- [Task vertical slice stories](stories/phase-1-task-vertical-slice.md)
- [People/HR Foundation stories](stories/phase-1-people-foundation.md)
- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Open decisions](../decisions/open-decisions.md)
- [ADR process](../decisions/README.md)
