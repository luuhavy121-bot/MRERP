# 01 — Tổng quan sản phẩm

Tài liệu này là điểm bắt đầu dành cho người sở hữu sản phẩm. Nội dung chi tiết và trạng thái đầy đủ được quản lý tại [Tổng quan sản phẩm chuyên sâu](product/product-overview.md).

## MRERP là gì?

**Đã chốt.** MRERP là điểm vào và không gian làm việc chung cho toàn bộ nhân sự MRE. Mục tiêu là thay những luồng rời rạc bằng một hệ sinh thái có danh tính chung, nguồn nhân sự chuẩn, giao diện nhất quán và các product liên kết bằng contract rõ ràng.

Một hệ sinh thái thống nhất không có nghĩa gom mọi code và database vào một ứng dụng.

## Dành cho ai?

**Đã chốt.** Tất cả nhân sự MRE có tài khoản MRERP. Sau đăng nhập, mỗi người chỉ nhìn thấy công việc, thông báo, dữ liệu và module phù hợp với quyền của mình.

Có tài khoản MRERP không tự động cấp quyền vào CRM, ASSETCONTROL, Kanban nâng cao hoặc Admin Panel.

**Đã chốt trong phạm vi hiện tại.** Sau đăng nhập, người dùng bắt đầu ở Tổng quan, có Bảng tin theo audience và Công việc/Goal theo đúng capability/scope. Implementation của ba phần này đang `In progress / Chờ nghiệm thu`.

## Các product trong hệ sinh thái

| Thành phần | Vai trò ngắn gọn | Trạng thái |
|---|---|---|
| MRERP Core | Cổng chung; sở hữu nhân sự, cơ cấu tổ chức, Task và nghiệp vụ nội bộ | **Đã chốt** |
| MRECRM | Vận hành Customer, Order, Product, Channel, đối soát và báo cáo CRM | Ranh giới **Đã chốt**; kiến trúc mục tiêu cần ADR |
| ASSETCONTROL | Quản lý Resource, Grant, Vault và audit tài nguyên; repo/deployment riêng | Ranh giới **Đã chốt** |
| MREKANBAN | Dùng Task MRERP cho board/view chuyên sâu trong giai đoạn chuyển tiếp | Hướng chuyển tiếp **Đã chốt**; tương lai **Chưa quyết định** |
| Identity | Credential, đăng nhập và SSO dùng chung | Ownership **Đã chốt**; provider **Chưa quyết định** |

## Phạm vi ASSETCONTROL

**Đã chốt.** Hiện chỉ CEO và Leader được cấp quyền truy cập ASSETCONTROL.

**Chưa quyết định.** Có mở cho đối tượng khác hay không và theo capability/policy nào.

## Năm nguyên tắc cần nhớ

1. MRERP là nguồn chuẩn của Employee, Team và Task.
2. Product sở hữu dữ liệu phải tự kiểm tra quyền ở server.
3. Product không đọc database trực tiếp của nhau.
4. Dashboard không phụ thuộc trực tiếp vào CRM khi tải trang.
5. Prototype chỉ minh họa UI, không phải production architecture.

## Đọc sâu hơn

- [Tổng quan sản phẩm và product boundary](product/product-overview.md)
- [Data ownership](architecture/data-ownership.md)
- [Yêu cầu Tổng quan, Bảng tin và Công việc](product/dashboard-feed-task-requirements.md)
- [Thuật ngữ](glossary.md)
- [Open decisions](decisions/open-decisions.md)

Tiếp theo: [02 — Yêu cầu sản phẩm](02-yeu-cau-san-pham.md).
