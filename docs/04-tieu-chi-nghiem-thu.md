# 04 — Tiêu chí nghiệm thu

Tài liệu này là cổng đạt/không đạt cấp sản phẩm và phase. Test case, test pyramid và bằng chứng kỹ thuật được quản lý tại [Test strategy](testing/test-strategy.md).

## Điều kiện đạt chung

Một thay đổi chỉ **Đạt** khi:

- Đáp ứng đúng yêu cầu đã được xác nhận.
- Không tự hiện thực mục **Chưa quyết định**.
- Server kiểm tra authorization, không chỉ ẩn UI.
- Endpoint nhạy cảm có test allowed, thiếu capability, ngoài scope, field redaction và account/employment không hợp lệ.
- Data ownership và contract không bị phá vỡ.
- Migration bảo toàn dữ liệu và có rollback khi thực tế cho phép.
- Không có secret hoặc dữ liệu production trong diff/fixture.
- Contract, tài liệu và ADR liên quan được cập nhật.
- Hành động nhạy cảm có audit.
- Integration lỗi không làm hỏng product khác.
- Có hướng dẫn kiểm tra và vận hành phù hợp với thay đổi.

## Điều kiện không đạt

Một thay đổi **Không đạt** nếu có bất kỳ lỗi nghiêm trọng nào sau đây:

- Chỉ ẩn nút frontend để bảo vệ dữ liệu.
- Product đọc hoặc sửa trực tiếp database của product khác.
- Direct link được coi là tích hợp đầy đủ.
- Resource ASSETCONTROL chỉ có tên/link thủ công nhưng được tuyên bố đã liên kết MKTLogin mà chưa kiểm chứng qua contract/API.
- Dashboard gọi CRM đồng bộ trong request tải trang.
- Tạo nhiều nguồn chuẩn Employee hoặc Task cạnh tranh.
- Hard-code phòng ban/cấp bậc MRE vào lõi permission.
- Truyền access token qua URL hoặc lưu token dài hạn thiếu đánh giá bảo mật.
- Dùng prototype làm bằng chứng đã có backend/auth production.
- Tự lựa chọn Identity Provider hoặc policy chưa chốt.
- Đưa secret/Vault hoặc dữ liệu Nhà ZUZU vào MRERP.

## Cổng Phase 0

Phase 0 **Đạt** khi:

- Có đường đọc chính và tài liệu chuyên sâu nhất quán.
- Có bản đồ tài liệu chịu trách nhiệm chính và glossary thống nhất thuật ngữ.
- Có danh sách open decisions.
- Có ADR template và quy trình chấp nhận ADR.
- Có governance baseline, CI kiểm tra repository và quy tắc config/secret đã được chấp nhận.
- Chưa scaffold/cài dependency ngoài phạm vi được yêu cầu.
- Người sở hữu sản phẩm duyệt source of truth hoặc chỉ rõ phần cần sửa.
- Checker Phase 0 và `git diff --check` chạy thành công.

Phase 0 **Không đạt** nếu tài liệu âm thầm biến đề xuất/open decision thành quyết định hoặc có hai nguồn sự thật mâu thuẫn.

## Cổng đầu vào story Phase 1

**Đề xuất mục tiêu.** Trước khi một story được đưa từ `Refining` sang `Ready`, story phải đạt [Definition of Ready](testing/definition-of-ready.md): có outcome, actor, data owner, acceptance criteria, capability/scope/object/field rule, contract, audit, dependency và test tối thiểu. Cổng này không thay thế Definition of Done.

Riêng Task vertical slice, điều kiện quyền phải đối chiếu với [ma trận phân quyền Task](architecture/task-authorization-matrix.md) và [acceptance scenarios Phase 1](testing/phase-1-task-acceptance.md). Mục còn **Chưa quyết định** không được giả lập thành policy production chỉ để đưa story sang `Ready`.

Gói Tổng quan–Bảng tin–Công việc phải đồng thời đạt [acceptance ba module](testing/dashboard-feed-task-acceptance.md), gồm audience/share không rò dữ liệu, file protected download, recurrence idempotent/backfill và Dashboard general/private đúng recipient.

Phase 3 phải đạt [acceptance Phase 3](testing/phase-3-acceptance.md): Recruitment không lộ PII/vượt Team, Documents không lộ file ngoài audience, Recognition không tự cộng sao, Star ledger append-only và notification bắt buộc không bị preference xã hội tắt. Trạng thái implementation hoặc test xanh không tự thay thế nghiệm thu của người sở hữu sản phẩm.

Riêng People/HR Foundation, trạng thái từng story nằm tại [People readiness register](testing/phase-1-people-readiness.md) và phải đối chiếu [People acceptance scenarios](testing/phase-1-people-acceptance.md). Gói refinement hoàn tất không đồng nghĩa story đã `Ready`.

## Bằng chứng nghiệm thu

Mỗi phase sau phải cung cấp bằng chứng phù hợp: test result, contract diff, migration/rollback evidence, authorization matrix, audit evidence và hướng dẫn vận hành. Không nghiệm thu chỉ dựa trên việc giao diện bấm được.

## Đọc sâu hơn

- [Test strategy](testing/test-strategy.md)
- [Yêu cầu nghiệp vụ](product/business-requirements.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [ADR process](decisions/README.md)

Tiếp theo: [05 — Hướng dẫn và vận hành](05-huong-dan-va-van-hanh.md).
