# Definition of Ready

Tài liệu này quy định khi nào một story đủ rõ để bắt đầu production implementation. Nó không thay thế [Definition of Done](../04-tieu-chi-nghiem-thu.md).

## 1. Trạng thái

**Đề xuất mục tiêu.** Checklist này được áp dụng cho story Phase 1 trước khi scaffold/implement. Người sở hữu sản phẩm cần duyệt Definition of Ready cùng gói Phase 1.

## 2. Story đạt Ready khi

- Outcome và actor được mô tả rõ.
- Data owner và module owner đã xác định.
- Acceptance criteria có thể kiểm thử.
- Capability, data scope, object rule và field policy liên quan đã rõ.
- Các trường hợp allowed, thiếu capability, ngoài scope và account/employment không hợp lệ đã được nêu.
- API/data contract tối thiểu đã được duyệt hoặc có ADR/contract draft được chấp nhận cho slice.
- Audit requirement đã xác định.
- Dependency và blocker được ghi rõ.
- Open decision ảnh hưởng trực tiếp đã được giải quyết hoặc phần phụ thuộc bị loại khỏi scope.
- Có test data/fixture an toàn, không chứa dữ liệu production.
- Có cách demo outcome xuyên UI → API → DB → authorization → audit → test.
- Không dùng prototype để chứng minh backend hoặc security đã tồn tại.

## 3. Story không đạt Ready khi

- Chỉ có mockup hoặc tên menu.
- Chưa biết ai được phép thao tác hoặc được xem record nào.
- Cần tự đoán policy nghiệp vụ.
- Chưa biết product nào sở hữu dữ liệu.
- Acceptance criteria chỉ ghi “hoạt động đúng”.
- Có open decision chặn trực tiếp nhưng không được ghi nhận.
- Phụ thuộc Identity, integration hoặc deployment contract chưa được quyết định.

## 4. Ready không có nghĩa Done

`Ready` chỉ cho phép bắt đầu implementation. Story chỉ `Accepted` khi đáp ứng [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md), test strategy, authorization matrix và bằng chứng vận hành phù hợp.

## 5. Tài liệu liên quan

- [Product backlog](../product/backlog.md)
- [Task stories Phase 1](../product/stories/phase-1-task-vertical-slice.md)
- [People readiness register](phase-1-people-readiness.md)
- [Test strategy](test-strategy.md)
