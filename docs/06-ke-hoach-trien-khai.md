# 06 — Kế hoạch triển khai

**Cập nhật được duyệt 01/10/2026:** ưu tiên [Tuyển dụng công khai và đánh giá KPI](product/hr-expansion-requirements.md) trước MKTLogin theo ADR-0017/0018. Quyền Leader với CV/pipeline và quy trình draft → gửi duyệt thay thế baseline tuyển dụng cũ ở phần bên dưới. Các phần khác giữ trạng thái riêng.

Roadmap chi tiết được quản lý tại [Roadmap chuyên sâu](product/roadmap.md). Tài liệu này cho biết đang ở đâu, cổng chuyển phase và bước tiếp theo.

## Trạng thái hiện tại

**Hiện tại: Phase 3 đã được hiện thực và đang chờ nghiệm thu; ưu tiên triển khai hiện tại là Tuyển dụng công khai và đánh giá KPI theo ADR-0017/0018; MKTLogin–ASSETCONTROL giữ trạng thái thiết kế. People/HR Foundation đã được nghiệm thu; các gói Phase 1–2 khác vẫn giữ trạng thái riêng.**

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
5. Phase 4: tích hợp ASSETCONTROL, liên kết resource ASSETCONTROL với MKTLogin qua API và xử lý MREKANBAN hiện hữu.
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

## Bước tiếp theo

Nghiệm thu [HR mở rộng](testing/hr-expansion-acceptance.md) trước khi trở lại workstream tích hợp bên dưới.

1. Duyệt [bản vẽ và kiến trúc MKTLogin trên máy công ty, bản 02](architecture/mktlogin-company-device-proposal.md), ADR-0016 **Proposed**. Workflow MRERP → MKTLogin và mất quyền dùng khi nghỉ việc là phương án nội bộ, chưa được MKT xác nhận; tài khoản/profile/tài nguyên công ty giữ nguyên. Khảo sát nơi thực thi chặn tại MKTLogin hoặc máy công ty; API đọc/khóa MRERP chưa đủ. Vẫn chỉ thiết kế, chưa code; các Team có workspace riêng theo ADR-0015.
2. Xác định ASSETCONTROL MRE và refinement contract (OD-17/OD-27): thử một Team/Gmail Resource/profile, kiểm chứng ID, scope API, điểm đọc cục bộ, dữ liệu tối thiểu, lỗi và audit theo [danh sách kiểm kê](architecture/ecosystem-integration.md#51-thông-tin-api-cần-người-sở-hữu-sản-phẩm-cung-cấp). Chốt xác thực của slice trước production; bổ sung policy bàn giao máy/thu hồi ở OD-28. Không ghi credential vào tài liệu hoặc Git.
3. Nghiệm thu Phase 3 baseline đã triển khai độc lập: Settings → Recruitment → Documents → Recognition/Stars.
4. Giữ MKT City, ngân sách tiền mặt Rewards, Payroll, máy chấm công và nghiệp vụ CRM ngoài phạm vi hiện tại.

## Đọc sâu hơn

- [Roadmap chi tiết](product/roadmap.md)
- [Open decisions](decisions/open-decisions.md)
- [ADR process](decisions/README.md)
- [Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md)

## Bổ sung chấm công bằng file

**Đã chốt 01/10/2026:** triển khai [nhập bảng công HR](product/leave-attendance-requirements.md#6-nhập-bảng-công-hr-từ-excel), chưa kết nối máy. Trạng thái triển khai và bằng chứng nằm trong [nghiệm thu Leave/Attendance](testing/leave-attendance-acceptance.md).

**Đã chốt 02/10/2026:** mở rộng [Sao & Đổi thưởng](product/phase-3-requirements.md) theo ADR-0020; `Implementation hoàn tất / Chờ nghiệm thu sản phẩm`. Ngân sách tiền mặt CEO hoãn; các phase khác giữ trạng thái riêng.

## Gói demo 06/10/2026

[ADR-0021](decisions/0021-hr-demo-half-day-and-workflow.md) chốt KPI do Leader đặt, sao chép cấu trúc/lịch sử/thông báo; tuyển dụng xem trước/lọc/lịch phỏng vấn; nghỉ nửa ngày và thứ Bảy cả ngày. Hoàn thiện và kiểm tra local trước demo; không nâng trạng thái nghiệm thu hoặc tự triển khai VPS.
