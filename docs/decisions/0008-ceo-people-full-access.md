# ADR-0008: CEO có toàn quyền trong People/HR Phase 1

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/people-authorization-matrix.md`
- Related open decision: `OD-23`
- Supersedes: `Phần quyền CEO còn mở trong ADR-0005`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project xác nhận trực tiếp CEO có toàn quyền trong ngữ cảnh câu hỏi về module People.`

## Context

- **Đã chốt:** permission core dùng capability/scope, không dùng tên role để bỏ qua kiểm tra server.
- **Đã chốt mới:** CEO có toàn bộ quyền trong module People/HR hiện tại.
- **Chưa quyết định:** quyền CEO trong các module khác ngoài những policy đã được chốt riêng.

## Decision

Tạo bundle `People CEO` gồm toàn bộ capability People hiện có: đọc toàn công ty, projection HR, tạo/sửa Employee, quản lý Department/Team/membership/Leader–Team, promotion toàn công ty và đọc audit. Promotion toàn công ty dùng capability riêng `promote_any_employee`; service không hard-code chuỗi role `CEO`.

“Toàn quyền” chỉ bao phủ hành động mà People Phase 1 đang hỗ trợ. Nó không mở xóa cứng, transition ngoài `Thử việc → Chính thức`, Admin Panel hoặc policy module khác.

## Consequences

- Có persona `ceo.demo` để kiểm thử bundle bằng session backend thật.
- CEO nhìn thấy field HR nhạy cảm, vì vậy endpoint vẫn phải audit và fail-closed.
- CEO có thể duyệt nhân sự ở bất kỳ Team nào hoặc chưa được gán Team.

## Validation

- Test CEO nhận HR projection và company directory.
- Test CEO chuyển nhân sự ngoài Team lãnh đạo lên `Chính thức`.
- Test persona CEO chỉ tồn tại trong Mock Identity development/test.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: trả lời trực tiếp “ceo có toàn quyền” cho câu hỏi quyền CEO trong module People.
