# ADR-0009: Cơ cấu MRE phẳng theo Team

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/people-data-contract.md`
- Related open decision: `OD-16`
- Supersedes: `Phần Department trong ADR-0005 và refinement People ban đầu`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project xác nhận công ty hiện chỉ có CEO và các Team, không có Phòng ban.`

## Context

- **Đã chốt mới:** cấu hình tổ chức MRE là `CEO → Team → Employee`.
- **Không làm:** không ép Team thuộc Department và không dùng Department làm authorization scope.
- **Chưa quyết định:** nếu tương lai công ty phát sinh một tầng tổ chức mới thì model/policy nào sẽ được dùng.

## Decision

Team nằm trực tiếp dưới CEO và không bắt buộc Department. UI Team dùng split view: danh sách Team bên trái; Team được chọn, Leader và nhân sự bên phải. Sơ đồ tổ chức cũng hiển thị `CEO → Team → Employee`.

Endpoint Department không còn được expose trong contract People MRE. Bảng/foreign key Department cũ chỉ được giữ nullable để migration không phá dữ liệu; nó không phải source authorization và không xuất hiện trong UI. Không xóa dữ liệu cũ tự động.

## Consequences

- Tạo Team chỉ cần mã và tên.
- Employee thuộc tối đa một Team; Team có thể có nhiều Leader.
- Quyền Leader tiếp tục lấy từ quan hệ Leader–Team; CEO dùng company scope.
- Scope Manager tương lai chưa quyết định; không còn mặc định theo Department.

## Validation

- Test tạo Team không có Department.
- Test endpoint Department không còn trong router.
- Frontend lint/build và split-view Team.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: yêu cầu trực tiếp “dưới CEO là các team, không có các phòng ban”.
