# ADR-0015: Workspace MKTLogin riêng theo Team

- Status: `Accepted`
- Date: `2026-09-03`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/architecture/ecosystem-integration.md`, `docs/product/business-requirements.md`
- Related open decision: `OD-27 (không đóng)`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người dùng xác nhận trực tiếp các Team sẽ có workspace riêng; chỉ chấp nhận yêu cầu tổ chức này.`

## Context

**Đã chốt:** mỗi máy cài MKTLogin riêng; công ty có phân quyền theo Team. Tài liệu API trong ứng dụng có khái niệm workspace nhưng chưa đủ chứng minh cơ chế phân quyền API hoặc đồng bộ giữa các máy.

**Chưa quyết định trước xác nhận:** các Team dùng chung workspace hay có workspace riêng.

## Decision drivers

- Phản ánh đúng yêu cầu tổ chức tài nguyên theo Team.
- Phân biệt Team nghiệp vụ trong MRERP với workspace bên MKTLogin và máy cài ứng dụng.
- Không suy ra quyền API từ tổ chức giao diện.

## Options considered

- Workspace riêng theo Team: được người dùng xác nhận là yêu cầu mục tiêu.
- Các Team dùng chung workspace rồi chia quyền hồ sơ: không chọn cho mô hình được xác nhận này.

## Decision

**Đã chốt:** các Team sẽ có workspace MKTLogin riêng. Đây là yêu cầu mục tiêu, chưa phải bằng chứng mọi workspace thực tế đã được tạo.

Không suy rộng thành mỗi Team chỉ được có đúng một workspace, mỗi workspace gắn với một máy hoặc hệ thống tự động tạo workspace. Không thay đổi quyền truy cập ASSETCONTROL hiện chỉ dành cho CEO và Leader.

## Remaining open questions

OD-27 vẫn mở cho định danh và quy tắc liên kết cụ thể, quyền tài khoản/API, hành vi chia sẻ hồ sơ giữa các máy, kết nối API cục bộ, đồng bộ, thu hồi, audit và xử lý lỗi. Chưa chọn loại Resource đầu tiên hoặc kiến trúc agent/gateway.

## Consequences

- Contract cần giữ ngữ cảnh workspace để kiểm chứng đúng Resource của Team.
- Cần kiểm kê workspace thực tế; không tạo liên kết bằng tên Team/workspace hoặc dựa vào workspace đang chọn trong ứng dụng.
- Tách workspace không tự chứng minh API ngăn truy cập ngoài Team; phải kiểm thử tại server.

## Security and authorization impact

Không chốt ma trận quyền hoặc tự cấp quyền MKTLogin từ quyền MRERP. Phải kiểm chứng quyền của API theo tài khoản/workspace; việc có workspace riêng không thay thế authorization.

## Data and contract impact

MRERP tiếp tục sở hữu Team; MKTLogin sở hữu workspace và môi trường vận hành; ASSETCONTROL sở hữu Resource/Grant và liên kết tài nguyên. Vị trí lưu quan hệ Team–workspace, khóa liên kết và cardinality chi tiết còn thuộc contract OD-27.

## Rollout and rollback

Lượt này chỉ ghi nhận yêu cầu; chưa tạo workspace, sửa quyền hoặc migration. Kế hoạch triển khai/rollback thực tế phải theo contract được duyệt.

## Validation

Khi triển khai, phải kiểm chứng Resource được liên kết trong đúng workspace, quyền ngoài phạm vi bị từ chối và đổi workspace đang chọn không làm liên kết nhầm. Điều kiện đạt theo tài liệu nghiệm thu và test strategy hiện có; chưa có bằng chứng chạy API thật.

## Documentation updates

Cập nhật yêu cầu nghiệp vụ, tài liệu tích hợp, open decisions, kế hoạch và backlog; không đóng OD-27.

## Approval record

- Người chấp nhận: Người sở hữu sản phẩm trong task hiện tại.
- Ngày chấp nhận: 03/09/2026.
- Bằng chứng/xác nhận: “các team sẽ có workspace riêng”.
