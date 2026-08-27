# Data ownership

Tài liệu này là source of truth duy nhất cho product sở hữu từng miền dữ liệu và quy tắc sao chép dữ liệu. Bản tóm tắt kiến trúc nằm tại [03 — Thiết kế kỹ thuật](../03-thiet-ke-ky-thuat.md).

## 1. Bảng nguồn dữ liệu chuẩn

| Miền dữ liệu | Product nguồn chuẩn | Dữ liệu product khác được nhận | Trạng thái |
|---|---|---|---|
| Credential, login, subject, phiên SSO | Identity Provider | Subject/claim tối thiểu theo OIDC | Ownership **Đã chốt**; provider **Chưa quyết định** |
| Employee, Department, Team, employment status | MRERP | UUID và snapshot tối thiểu theo quyền | **Đã chốt** |
| Capability cấp hệ sinh thái | MRERP/Admin | Claim/snapshot; product đích vẫn tự kiểm tra | **Đã chốt** |
| Task nghiệp vụ | MRERP Task | Kanban/CRM tham chiếu hoặc tạo qua API | **Đã chốt** |
| Board, column, swimlane, card placement | MREKANBAN trong giai đoạn chuyển tiếp | MRERP nhận deep link/metadata cần thiết | **Đã chốt theo hướng chuyển tiếp** |
| Recognition, stars, redemption | MRERP Rewards | CRM phát sự kiện thành tích | **Đã chốt** |
| Customer, Order, Product, Channel, FFM | MRECRM | MRERP nhận aggregate được phép | **Đã chốt** |
| Resource, Grant, Vault, asset audit | ASSETCONTROL | MRERP chỉ nhận metadata/notification không chứa secret | **Đã chốt** |
| Tài liệu nội bộ | MRERP Documents + storage được chọn | Product khác nhận link/quyền phù hợp | Ownership **Đã chốt**; storage **Chưa quyết định** |

## 2. Quy tắc bắt buộc

**Đã chốt.**

- Không product nào đọc hoặc sửa trực tiếp database của product khác.
- Không dùng tên, email hoặc mã nhân viên dễ đổi làm khóa liên kết duy nhất.
- Dùng UUID ổn định và mapping migration có audit.
- Bản sao ở product khác chỉ là snapshot/read model, không thành nguồn chuẩn.
- Contract phải có version và compatibility rule.
- Product chỉ nhận dữ liệu tối thiểu cần thiết theo authorization.

Quyền ghi dữ liệu thuộc product nguồn chuẩn. API/event consumer không được dùng snapshot để cập nhật ngược nguồn hoặc tự hợp nhất hai nguồn chuẩn nếu chưa có command contract được chấp nhận.

## 3. Employee propagation

**Đã chốt.** MRERP phát `employee_uuid` và snapshot tối thiểu cho CRM/ASSETCONTROL/MREKANBAN theo contract. Product đích không được tự tạo bản ghi Employee cạnh tranh để tránh gọi API.

Snapshot có thể chứa những thuộc tính cần cho display/authorization, nhưng field cụ thể phải được xác định theo use case và quyền.

## 4. Task ownership

**Đã chốt.** MRERP Task sở hữu:

- `task_uuid`;
- người giao và người nhận;
- trạng thái nghiệp vụ;
- deadline;
- liên kết đối tượng nghiệp vụ.

MREKANBAN có thể sở hữu cấu hình view nhưng không được sửa Task như một nguồn độc lập ngoài contract MRERP.

**Chưa quyết định.** MREKANBAN retire hay tiếp tục dài hạn và cách migrate layout/workflow cũ.

## 5. Secret boundary

**Đã chốt.** Password, cookie, token, OTP, key và nội dung Vault không được gửi từ ASSETCONTROL sang MRERP. MRERP chỉ có thể nhận metadata/notification không chứa secret theo quyền.

Không chuyển dữ liệu hoặc secret Nhà ZUZU sang MRE chỉ vì dùng chung codebase.

## 6. Database topology

**Chưa quyết định.** MRERP và CRM dùng database riêng hay schema riêng khi cùng PostgreSQL instance.

**Đã chốt bất kể topology:** logical ownership, credential riêng/tối thiểu và không cross-read/cross-write.

## 7. Tài liệu liên quan

- [Tổng quan product](../product/product-overview.md)
- [Identity và phân quyền](identity-and-authorization.md)
- [Tích hợp hệ sinh thái](ecosystem-integration.md)
- [Open decisions](../decisions/open-decisions.md)
