# Bộ source of truth MRERP

Thư mục này chuyển context bàn giao MRERP thành các tài liệu có phạm vi rõ ràng. Mỗi khẳng định quan trọng phải giữ một trong ba nhãn: **Đã chốt**, **Đề xuất mục tiêu** hoặc **Chưa quyết định**.

## Đường đọc chính

Người sở hữu sản phẩm đọc tuần tự sáu tài liệu sau trước khi đi vào chi tiết:

1. [01 — Tổng quan sản phẩm](01-tong-quan-san-pham.md).
2. [02 — Yêu cầu sản phẩm](02-yeu-cau-san-pham.md).
3. [03 — Thiết kế kỹ thuật](03-thiet-ke-ky-thuat.md).
4. [04 — Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md).
5. [05 — Hướng dẫn và vận hành](05-huong-dan-va-van-hanh.md).
6. [06 — Kế hoạch triển khai](06-ke-hoach-trien-khai.md).

Các file `01–06` là bản dẫn đường ngắn gọn. Chúng không sao chép đầy đủ policy/contract; mỗi chủ đề dẫn tới một source of truth chuyên sâu chịu trách nhiệm chính.

## Vai trò của từng loại tài liệu

- `01–06`: đường đọc tuần tự, tóm tắt và điều hướng; không sở hữu contract/policy chi tiết trừ khi bảng dưới ghi rõ.
- `product/`, `architecture/`, `operations/`, `testing/`: source of truth chuyên sâu theo miền.
- `decisions/open-decisions.md`: danh mục duy nhất của các câu hỏi chưa chốt.
- ADR: hồ sơ một quyết định; khi được chấp nhận phải cập nhật source of truth chuyên sâu.
- [glossary.md](glossary.md): định nghĩa thuật ngữ, không tạo quyết định sản phẩm mới.

## Source of truth theo miền

| Miền | Source of truth |
|---|---|
| Mục tiêu, product boundary và đối tượng sử dụng | [product/product-overview.md](product/product-overview.md) |
| Yêu cầu nghiệp vụ và ranh giới module | [product/business-requirements.md](product/business-requirements.md), [Leave/Attendance hiện tại](product/leave-attendance-requirements.md), [Tổng quan–Bảng tin–Công việc](product/dashboard-feed-task-requirements.md), [Phase 3](product/phase-3-requirements.md) |
| Epic, backlog status và story chi tiết | [product/backlog.md](product/backlog.md), [People stories](product/stories/phase-1-people-foundation.md) và [Task stories](product/stories/phase-1-task-vertical-slice.md) |
| Kiến trúc, stack và cấu trúc monorepo | [architecture/technical-architecture.md](architecture/technical-architecture.md) |
| Nguồn dữ liệu chuẩn và quy tắc đồng bộ | [architecture/data-ownership.md](architecture/data-ownership.md) |
| Identity, SSO và authorization | [architecture/identity-and-authorization.md](architecture/identity-and-authorization.md) |
| Ma trận authorization chuyên biệt của Task Phase 1 | [architecture/task-authorization-matrix.md](architecture/task-authorization-matrix.md) |
| Data/API/worker/file contract Dashboard, Feed và Task | [architecture/dashboard-feed-task-contract.md](architecture/dashboard-feed-task-contract.md) |
| Field, data model và API contract People Phase 1 | [architecture/people-data-contract.md](architecture/people-data-contract.md) |
| Ma trận authorization chuyên biệt của People Phase 1 | [architecture/people-authorization-matrix.md](architecture/people-authorization-matrix.md) |
| Data/API/authorization contract Leave/Attendance hiện tại | [architecture/leave-attendance-contract.md](architecture/leave-attendance-contract.md) |
| Data/API/worker/file contract Phase 3 | [architecture/phase-3-contract.md](architecture/phase-3-contract.md) |
| Ma trận authorization Recruitment, Documents và Rewards | [architecture/phase-3-authorization-matrix.md](architecture/phase-3-authorization-matrix.md) |
| API, event, snapshot và tích hợp product | [architecture/ecosystem-integration.md](architecture/ecosystem-integration.md) |
| VPS, database, worker, backup và quan sát | [operations/deployment.md](operations/deployment.md) |
| Cấu hình và secret ở mức repository | [operations/configuration-and-secrets.md](operations/configuration-and-secrets.md) |
| Điều kiện đạt/không đạt cấp sản phẩm và phase | [04-tieu-chi-nghiem-thu.md](04-tieu-chi-nghiem-thu.md) |
| Chiến lược kiểm thử kỹ thuật | [testing/test-strategy.md](testing/test-strategy.md) |
| Cổng đầu vào story | [testing/definition-of-ready.md](testing/definition-of-ready.md) |
| Acceptance scenarios của Task Phase 1 | [testing/phase-1-task-acceptance.md](testing/phase-1-task-acceptance.md) |
| Acceptance tích hợp Dashboard, Feed và Task | [testing/dashboard-feed-task-acceptance.md](testing/dashboard-feed-task-acceptance.md) |
| Acceptance scenarios và readiness của People Phase 1 | [testing/phase-1-people-acceptance.md](testing/phase-1-people-acceptance.md), [testing/phase-1-people-readiness.md](testing/phase-1-people-readiness.md) và [People account/lifecycle](testing/people-account-lifecycle-acceptance.md) |
| Acceptance scenarios Leave/Attendance hiện tại | [testing/leave-attendance-acceptance.md](testing/leave-attendance-acceptance.md) |
| Acceptance scenarios Phase 3 | [testing/phase-3-acceptance.md](testing/phase-3-acceptance.md) |
| Phase và thứ tự triển khai | [product/roadmap.md](product/roadmap.md) |
| Danh sách quyết định chưa chốt | [decisions/open-decisions.md](decisions/open-decisions.md) |
| Quyết định kiến trúc đã được xem xét | [decisions/](decisions/README.md) |

Mỗi chủ đề chỉ có một tài liệu chịu trách nhiệm chính trong bảng này. Tài liệu khác chỉ tóm tắt và phải dẫn link về nguồn chính thay vì sao chép chi tiết dài.

## Ý nghĩa trạng thái

- **Đã chốt**: yêu cầu hoặc ràng buộc đã xác nhận.
- **Đề xuất mục tiêu**: hướng thiết kế để bắt đầu; cần ADR trước khi hiện thực các lựa chọn kiến trúc quan trọng.
- **Chưa quyết định**: AI và developer không được tự lựa chọn.

## Quan hệ với tài liệu bàn giao

Bộ tài liệu này là bản phân rã có cấu trúc từ `CONTEXT.md` trong gói bàn giao ngày 27/08/2026. Prototype bàn giao chỉ là nguồn tham khảo UI; prototype Claude chỉ là nguồn tham khảo về ý tưởng fail-closed, configuration, contract và fallback. [Visual prototype mới trong repository](../prototype/README.md) là bề mặt để duyệt trải nghiệm và phát triển frontend-first theo từng vertical slice. Không prototype nào là source of truth production.

## Cập nhật tài liệu

Khi một mục **Chưa quyết định** được người dùng chốt:

1. Tạo ADR từ template.
2. Ghi trạng thái ADR là `Proposed` trong thời gian xem xét.
3. Chỉ chuyển thành `Accepted` khi có xác nhận của người có thẩm quyền.
4. Cập nhật source of truth liên quan và mục open decision.
5. Không để ADR và source of truth mâu thuẫn âm thầm.

## Kiểm tra chất lượng tài liệu

Trước khi commit thay đổi tài liệu:

- Đọc theo đường `01–06` để phát hiện câu chuyện bị đứt đoạn.
- Kiểm tra toàn bộ relative link.
- Kiểm tra mọi quyết định quan trọng có nhãn trạng thái.
- Kiểm tra open decision mới đã vào đúng danh mục.
- Kiểm tra không có hai tài liệu cùng tự nhận sở hữu một policy/contract.
- Kiểm tra prototype không bị dùng làm bằng chứng production.
- Chạy `python scripts/check_docs.py` và `git diff --check`.
