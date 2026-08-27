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
- Chưa scaffold/cài dependency ngoài phạm vi được yêu cầu.
- Người sở hữu sản phẩm duyệt source of truth hoặc chỉ rõ phần cần sửa.
- Conventions, CI tối thiểu và secret-handling rule cần cho phase kế tiếp đã được xác nhận hoặc được ghi rõ là công việc Phase 0 còn lại.

Phase 0 **Không đạt** nếu tài liệu âm thầm biến đề xuất/open decision thành quyết định hoặc có hai nguồn sự thật mâu thuẫn.

## Bằng chứng nghiệm thu

Mỗi phase sau phải cung cấp bằng chứng phù hợp: test result, contract diff, migration/rollback evidence, authorization matrix, audit evidence và hướng dẫn vận hành. Không nghiệm thu chỉ dựa trên việc giao diện bấm được.

## Đọc sâu hơn

- [Test strategy](testing/test-strategy.md)
- [Yêu cầu nghiệp vụ](product/business-requirements.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [ADR process](decisions/README.md)

Tiếp theo: [05 — Hướng dẫn và vận hành](05-huong-dan-va-van-hanh.md).
