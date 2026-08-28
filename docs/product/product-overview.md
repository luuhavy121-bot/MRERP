# Tổng quan sản phẩm MRERP

Tài liệu này là source of truth chịu trách nhiệm chính cho mục tiêu, đối tượng sử dụng và product boundary. Bản đọc ngắn nằm tại [01 — Tổng quan sản phẩm](../01-tong-quan-san-pham.md).

## 1. Mục tiêu

**Đã chốt.** MRERP là điểm vào và không gian làm việc chung cho toàn bộ nhân sự MRE. Mục tiêu dài hạn là tập trung nghiệp vụ nội bộ thành một hệ sinh thái thống nhất, thay cho tin nhắn, bảng tính và nhiều tài khoản độc lập.

Sự thống nhất không có nghĩa gom mọi code, process và database vào một ứng dụng. Hệ sinh thái thống nhất nhờ:

- Một danh tính đăng nhập chung.
- Một nguồn chuẩn về nhân sự và cơ cấu tổ chức.
- Giao diện và ngôn ngữ thiết kế nhất quán.
- Authorization được kiểm tra ở server của product sở hữu dữ liệu.
- API, event, snapshot/read model và UUID dùng chung.
- Deep link đưa người dùng đến đúng màn hình mà không phải đăng nhập lại.

## 2. Vấn đề cần giải quyết

**Đã chốt.**

- Nhân sự đang phải tìm công việc, thông báo và quy trình ở nhiều nơi.
- Dữ liệu nhân sự có nguy cơ bị tạo lặp trong nhiều product.
- Task, tuyển dụng, nghỉ phép và phê duyệt có thể bị truyền qua kênh không có trạng thái chuẩn.
- ASSETCONTROL có login và dữ liệu nhân sự riêng nhưng không nên tiếp tục là nguồn chuẩn khi MRERP trở thành cổng chung.
- CRM có dữ liệu lớn và job đồng bộ kênh có thể ảnh hưởng người dùng ERP nếu không cô lập đúng.
- Quyền khác nhau theo action, record, scope và field chứ không chỉ theo menu.

## 3. Kết quả mong muốn

**Đã chốt.**

- Mọi nhân sự MRE có tài khoản và bắt đầu ngày làm việc từ MRERP.
- Dashboard hiển thị thông tin cá nhân hóa, thông báo và công việc phù hợp.
- Người dùng chuyển sang product được cấp quyền mà không nhập lại mật khẩu.
- Employee, Team và employment status có một nguồn chuẩn; MRE hiện không có tầng Phòng ban.
- Product chuyên biệt vẫn cô lập được dữ liệu, tải và quyền nhạy cảm.
- Kiến trúc đủ đơn giản để một developer cùng AI vận hành.
- Cấu hình tổ chức được dữ liệu hóa để tái sử dụng platform cho công ty khác.

## 4. Đối tượng sử dụng

**Đã chốt.** Tất cả nhân sự MRE có tài khoản MRERP. Có tài khoản không tự động cấp quyền vào CRM, ASSETCONTROL, Kanban nâng cao hoặc Admin Panel.

Các persona hiện được mô tả:

- Staff: không gian cá nhân, Task được giao, công/phép và quyền lợi phù hợp.
- Captain: Staff cộng khả năng điều phối nhóm nhỏ theo capability.
- Leader: quản lý team, giao việc, theo dõi và phê duyệt trong scope được giao.
- Manager: quản lý nhiều team/phòng ban theo scope tổ chức.
- CEO: góc nhìn toàn công ty và quyền cao nhất theo policy.
- HR: nghiệp vụ nhân sự, nghỉ phép và tuyển dụng theo capability.
- Sales/Marketing/Ads: CRM theo shop, kênh, team và field policy.
- Kế toán: giá, phí, thanh toán và đối soát; chỉ nhận PII cần thiết.

**Chưa quyết định.** Ranh giới chính xác Captain/Leader/Manager và người được vào Admin Panel.

## 5. Product boundary

### 5.1 MRERP Core

**Đã chốt.**

- Là cổng làm việc chung cho toàn bộ nhân sự.
- Kiến trúc nội bộ: modular monolith.
- Sở hữu Employee, Team, employment status, capability hệ sinh thái, Task, phê duyệt nội bộ, nghỉ phép/chấm công, recognition/rewards, recruitment, documents và preference cá nhân.
- Không sở hữu Customer/Order CRM, credential kênh bán hoặc nội dung Vault.
- Admin Panel nằm trong MRERP để quản lý account/employee/access cấp cao; credential và phiên đăng nhập vẫn thuộc Identity Provider.

### 5.2 MRECRM

**Đã chốt về ranh giới product.**

- Dành cho Sales, Marketing/Ads, Kế toán và người liên quan.
- Sở hữu Customer, Order, Product, Channel, shop/account connector, FFM, đối soát và báo cáo CRM.
- Worker sync/import/export/report không chạy trong request web.
- Mỗi nhóm chỉ nhận field cần cho công việc.

**Đề xuất mục tiêu.** MRECRM là modular monolith deploy độc lập, nằm cùng monorepo mới với MRERP để chia sẻ contract và design system. Quyết định hiện thực cần ADR.

**Chưa quyết định.** Ma trận field-level chi tiết và ngưỡng tách CRM sang VPS riêng.

### 5.3 ASSETCONTROL

**Đã chốt về ranh giới product.**

- Là product/repository/deployment riêng cho Resource, Grant, Vault và audit tài nguyên.
- Hiện chỉ CEO và Leader được cấp quyền truy cập; không tự mở cho toàn bộ nhân sự.
- Sau migration, không còn là nguồn Employee/Team.
- Nhận `employee_uuid` và snapshot nhân sự tối thiểu từ MRERP.
- Tự kiểm tra quyền ở server.
- Không gửi password, cookie, token, OTP, khóa hoặc nội dung Vault sang MRERP.

**Chưa quyết định.** Có mở ASSETCONTROL cho đối tượng khác hay không và theo policy nào. Quan hệ giữa codebase Nhà ZUZU và ASSETCONTROL MRE cũng chưa chốt: dùng lại code, fork, tenant riêng, deployment riêng, multi-tenant hay chỉ tham khảo.

### 5.4 MREKANBAN

**Đã chốt theo hướng chuyển tiếp.**

- Repository/product hiện tại được giữ riêng trong giai đoạn chuyển tiếp.
- MRERP là nguồn chuẩn dài hạn của Task.
- MREKANBAN tham chiếu `task_uuid`, không tạo nguồn Task thứ hai.
- MREKANBAN có thể sở hữu board, column, swimlane, card placement, filter và cấu hình view.

**Chưa quyết định.** MREKANBAN sẽ được retire hay tiếp tục làm client/view chuyên sâu dài hạn. Cần audit repo và workflow hiện tại trước khi quyết định.

### 5.5 Identity

**Đề xuất mục tiêu.** Dùng Identity Provider chuẩn cho credential, login, subject và SSO; các product dùng OIDC/OAuth 2.0.

**Đã chốt về ownership.** MRERP sở hữu hồ sơ nhân sự và trạng thái employment; product đích tự kiểm authorization.

**Chưa quyết định.** Identity Provider cụ thể và hành vi khi IdP suy giảm.

## 6. Product, module, deployable và microservice

- Product là ranh giới ownership nghiệp vụ và dữ liệu.
- Module là ranh giới code/workflow bên trong một product.
- Deployable là đơn vị có thể build và triển khai độc lập.
- Microservice là một kiến trúc phân tán; chạy riêng không tự động biến một product thành microservice.

**Không làm.** Không chia microservice theo từng menu ở giai đoạn đầu.

## 7. Tài liệu liên quan

- [Yêu cầu nghiệp vụ](business-requirements.md)
- [Data ownership](../architecture/data-ownership.md)
- [Open decisions](../decisions/open-decisions.md)
