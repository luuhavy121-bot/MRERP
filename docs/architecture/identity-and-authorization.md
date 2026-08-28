# Identity và phân quyền

Tài liệu này là source of truth chịu trách nhiệm chính cho Identity ownership, SSO target và authorization model. Bản đọc ngắn nằm tại [03 — Thiết kế kỹ thuật](../03-thiet-ke-ky-thuat.md).

## 1. Ownership

**Đã chốt.**

- Identity Provider sở hữu credential, login flow, subject và phiên SSO.
- MRERP sở hữu Employee profile, organization mapping, employment status và capability cấp hệ sinh thái.
- Product đích sở hữu authorization nghiệp vụ chi tiết đối với dữ liệu của mình.

**Chưa quyết định.** Identity Provider cụ thể và mô hình vận hành/backup.

## 2. Luồng SSO mục tiêu

**Đề xuất mục tiêu cần ADR.**

1. Người dùng mở MRERP.
2. MRERP chuyển tới IdP bằng OIDC Authorization Code flow.
3. Sau xác thực, server tạo phiên bằng cookie `HttpOnly`, `Secure` và `SameSite` phù hợp.
4. MRERP ánh xạ IdP subject với `employee_uuid` và kiểm tra employment status.
5. Khi mở CRM/ASSETCONTROL/MREKANBAN, product đích chạy OIDC flow riêng; phiên IdP giúp không phải nhập lại mật khẩu.
6. Product đích tự kiểm product capability, action, scope, object rule và field policy.

**Không làm.** Không truyền token qua URL, không chia sẻ cookie tùy tiện và không lưu access token dài hạn trong `localStorage`.

## 3. Sáu lớp authorization

**Đã chốt.**

1. Account/employment gate: account và employment còn hiệu lực.
2. Product capability: có quyền vào product hay không.
3. Action capability: xem, tạo, sửa, duyệt, export hoặc quản trị.
4. Data scope: bản thân, team, phòng ban, scope được giao hoặc toàn công ty.
5. Object rule: state/ownership của record có cho phép hành động không.
6. Field policy: query/serializer chỉ trả field được phép.

Frontend có thể ẩn menu/nút để giảm nhầm lẫn nhưng không phải hàng rào bảo mật. Endpoint nhạy cảm phải fail-closed ở server.

## 4. Nguồn dữ liệu tin cậy

**Đã chốt.** Không tin `role`, `team_id`, `owner_id`, `price_access` hoặc capability do client gửi. Server lấy identity, organization, capability và scope từ session/claim đã xác thực cùng dữ liệu server.

## 5. Test authorization tối thiểu

**Đã chốt.** Mỗi endpoint nhạy cảm phải có:

- Allowed.
- Denied do thiếu capability.
- Denied do ngoài scope.
- Field redaction/absence.
- Denied khi account khóa hoặc employment kết thúc.

Thêm test object state/ownership khi endpoint có object rule.

## 6. Field-level authorization CRM

**Đã chốt về nguyên tắc.** Kế toán, Marketing/Ads và Sales không mặc nhiên nhận cùng payload. Field policy phải được thực thi ở server CRM.

**Chưa quyết định.** Ma trận field cụ thể theo chức năng, channel, shop, team và scope.

## 7. Phạm vi truy cập ASSETCONTROL

**Đã chốt.** Hiện chỉ CEO và Leader được cấp quyền truy cập ASSETCONTROL. Product vẫn phải kiểm tra authorization tại server; tên cấp bậc không phải lý do để bỏ qua account/employment, action, scope, object hoặc field check.

**Chưa quyết định.** Có mở cho đối tượng khác hay không và theo capability/policy nào (OD-18).

## 8. IdP outage và break-glass

**Đã chốt về giới hạn:**

- Không tự phát minh backdoor.
- ASSETCONTROL migration phải có dual-run, UUID mapping, rollback và emergency access trước khi tắt login cũ.
- Không dùng shared static token trong production.

**Chưa quyết định:**

- Phiên hiện hữu sống thế nào khi IdP lỗi.
- Grace period/fail-closed rule cho từng product.
- Break-glass ASSETCONTROL.
- Thời gian giữ login cũ.
- IdP recovery/backup model.

## 9. Admin Panel và Identity Provider

**Đã chốt về ownership.** Admin Panel nằm trong MRERP để quản lý account/employee/access cấp cao; IdP vẫn sở hữu credential, login và phiên.

**Chưa quyết định.** Provisioning/deprovisioning flow, thao tác nào Admin Panel được phép gửi sang IdP, cơ chế phê duyệt và audit cụ thể (OD-19).

## 10. Service-to-service authentication

**Chưa quyết định.** Cần chọn service account/token rotation hoặc cơ chế tương đương. Token tĩnh dùng chung chỉ được phép trong demo cục bộ, không phải production.

## 11. Chuyên biệt hóa cho Task Phase 1

**Đã chốt trong phạm vi Task Phase 1.** [ADR-0002](../decisions/0002-task-authorization-baseline.md) và [ma trận phân quyền Task](task-authorization-matrix.md) áp dụng sáu lớp kiểm tra trên vào capability, scope, field responsibility và state transition của Task.

Các điểm đã chốt gồm Captain có permission nền như Staff; Leader quản lý trong team; Manager tương lai quản lý trong phòng ban nhưng ban đầu không có user Manager; CEO có scope toàn công ty nhưng không bỏ qua capability. Người tạo quản lý trường định nghĩa, người nhận quản lý trường thực thi và hoàn thành cần bước xác nhận riêng.

**Chưa quyết định.** Quyền đọc Task nền của Staff/Captain, hủy/xóa Task và ranh giới cấp bậc ngoài module Task. Không suy rộng ma trận Task sang product/module khác.

## 12. Chuyên biệt hóa cho People/HR Phase 1

**Đề xuất mục tiêu.** [Ma trận phân quyền People](people-authorization-matrix.md) định nghĩa capability, scope, object và field dimensions cho slice. Không capability nào được gán mặc định cho persona cho tới khi ADR-0005 được chấp nhận.

**Chưa quyết định.** Write authority, directory read scope, field projection, employment workflow và mock Identity trust boundary.

## 13. Persona switcher development/test

**Đã chốt trong phạm vi Mock Identity Phase 1.** Theo [ADR-0004](../decisions/0004-mock-identity-context.md), development/test có thể đổi giữa các persona fixture bằng endpoint phía server. Endpoint chỉ chấp nhận allow-list được cấu hình trong backend, tạo một session mới cho account demo hợp lệ và trả normalized actor context. Client không được gửi role, capability hoặc scope để tự nâng quyền.

**Không làm.** Không bật endpoint hoặc hiển thị bộ chọn này trong production; không coi persona demo là quyết định về cơ cấu tổ chức thật; không tự bổ sung Captain/Manager khi capability và dữ liệu mẫu chưa được duyệt.

## 14. Tài liệu liên quan

- [Data ownership](data-ownership.md)
- [Tích hợp hệ sinh thái](ecosystem-integration.md)
- [Ma trận phân quyền Task](task-authorization-matrix.md)
- [Ma trận phân quyền People](people-authorization-matrix.md)
- [Test strategy](../testing/test-strategy.md)
- [Open decisions](../decisions/open-decisions.md)
