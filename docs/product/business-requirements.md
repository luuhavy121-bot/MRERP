# Yêu cầu nghiệp vụ MRERP

Tài liệu này là source of truth chịu trách nhiệm chính cho miền nghiệp vụ và ranh giới module. Bản đọc ngắn nằm tại [02 — Yêu cầu sản phẩm](../02-yeu-cau-san-pham.md).

## 1. Mô hình người dùng

**Đã chốt.** Không gộp mọi thuộc tính người dùng vào một cột `role`. Mô hình phải tách tối thiểu:

1. Cấp bậc: Staff, Captain, Leader, Manager, CEO.
2. Employment status: thử việc, chính thức, tạm khóa, nghỉ việc hoặc trạng thái được duyệt khác.
3. Đơn vị tổ chức: phòng ban, team và quan hệ quản lý.
4. Chức năng nghề nghiệp: HR, Sales, Marketing/Ads, Kế toán và nhóm khác.
5. Capability cụ thể.
6. Data scope: bản thân, team, phòng ban, scope được giao hoặc toàn công ty.

**Đã chốt.** Thử việc là trạng thái làm việc, không phải cấp bậc.

## 2. Module MRERP Core

**Đã chốt về miền nghiệp vụ; workflow/policy chi tiết triển khai theo phase.** Ranh giới module phải dựa trên workflow và dữ liệu, không chỉ theo menu.

1. Dashboard: thông báo, Task, trạng thái đơn, recognition và số liệu cá nhân hóa.
2. People/HR: Employee, Department, Team, hồ sơ, employment status và quan hệ quản lý.
3. Attendance/Leave: đơn nghỉ, số công, lịch và dữ liệu cá nhân được phép.
4. Approvals: workflow theo từng loại yêu cầu; không mặc định một quyền duyệt cho mọi loại.
5. Tasks: giao/nhận việc, List, Calendar và view cơ bản.
6. Recognition/Rewards: thành tích, sao, bảng xếp hạng và đổi quyền lợi theo policy.
7. Recruitment: yêu cầu tuyển, JD/link nội bộ, ứng viên và pipeline.
8. Documents: thư viện, phân loại, upload, import/export và quyền xem.
9. Personal Payroll: chỉ đúng chủ thể/người có capability; policy nghiệp vụ chưa chốt.
10. Reporting: đọc read model được phép, không join trực tiếp DB product khác.
11. Admin Panel: account, cơ cấu tổ chức, capability, scope, feature flag, audit và integration health.
12. Personal Settings: hồ sơ hiển thị, notification, security và preference.

People/HR Foundation Phase 1 được refinement tại [People stories](stories/phase-1-people-foundation.md). Field, workflow và quyền chi tiết vẫn giữ đúng trạng thái trong [People data contract](../architecture/people-data-contract.md) và [People authorization matrix](../architecture/people-authorization-matrix.md).

**Đã chốt cho People slice đầu tiên:**

- Form thêm nhân sự yêu cầu mã nhân sự và cho HR chọn có tạo tài khoản đăng nhập hay không. Tài khoản/mật khẩu chỉ bắt buộc khi checkbox tạo tài khoản được bật.
- HR được thêm Employee với trạng thái ban đầu là `Thử việc`; server không cho HR dùng luồng này để tạo thẳng trạng thái `Chính thức`.
- Khi có chọn tạo tài khoản, account và Employee phải được tạo/liên kết trong cùng một thao tác nghiệp vụ; nếu một bước lỗi thì không tạo Employee. Khi không chọn, chỉ Employee được tạo và account có thể cấp sau.
- Mã nhân sự được nhập tự do, không rỗng và không trùng không phân biệt hoa/thường.
- Leader quyết định chuyển một Employee từ `Thử việc` sang `Chính thức`.

**Đã chốt về ranh giới:** mật khẩu là credential do Identity Provider sở hữu; MRERP không được lưu mật khẩu trong Employee, database, audit hoặc log.

**Chưa quyết định:** workflow cấp account production về sau cho Employee chưa có account.

**Đề xuất mục tiêu.** Recruitment có thể nằm dưới navigation Nhân sự nhưng nên là code module riêng.

## 3. Dashboard và khả năng chịu lỗi

**Đã chốt.** Dashboard không gọi trực tiếp CRM hoặc ASSETCONTROL trong request tải trang. Dashboard đọc snapshot/read model cục bộ.

Khi source product lỗi:

- Dashboard vẫn tải.
- Hiển thị dữ liệu gần nhất và thời điểm cập nhật.
- Hiển thị trạng thái dữ liệu cũ hoặc chưa đồng bộ.
- HR, Task và nghỉ phép không bị treo.

**Chưa quyết định.** Ngưỡng stale, timeout, retry và SLA.

## 4. CRM và dữ liệu theo field

**Đã chốt về nguyên tắc.**

- Kế toán nhận giá, phí, thanh toán, đối soát và trường đơn hàng cần thiết.
- Marketing nhận thông tin khách hàng/dữ liệu chiến dịch cần thiết.
- Dùng chung một bảng UI không có nghĩa nhận cùng payload.
- Server phải áp dụng field policy và data minimization.

**Chưa quyết định.** Ma trận field-level cụ thể cho Sales, Marketing/Ads, Kế toán và nhóm liên quan.

## 5. Task và Kanban

**Đã chốt.** MRERP sở hữu Task nghiệp vụ dài hạn: UUID, người giao, người nhận, trạng thái, deadline và liên kết đối tượng.

MREKANBAN hiện tại chỉ tham chiếu Task và có thể sở hữu bố cục/view chuyên sâu. Không được tạo nguồn Task cạnh tranh.

**Đã chốt trong phạm vi Task Phase 1.** Capability, scope, trách nhiệm theo field, luồng gửi xác nhận và quy tắc self-task được ghi tại [ADR-0002](../decisions/0002-task-authorization-baseline.md) và [ma trận phân quyền Task](../architecture/task-authorization-matrix.md).

**Chưa quyết định.** Quyền đọc Task nền của Staff/Captain, hủy/xóa Task và các workflow nâng cao chưa thuộc vertical slice đầu tiên.

**Chưa quyết định.** Retire MREKANBAN hay giữ làm client/view chuyên sâu dài hạn.

## 6. Recognition và Rewards

**Đã chốt về ownership.** MRERP Rewards sở hữu recognition, sao và đổi thưởng. CRM chỉ phát sự kiện thành tích; không tự cộng sao.

**Chưa quyết định.** Công thức cộng sao, reward policy, người quản trị Rewards và catalog chính thức.

## 7. Yêu cầu authorization cho nghiệp vụ

**Đã chốt.** Mọi endpoint nhạy cảm phải kiểm tra account/employment, product capability, action capability, data scope, object rule và field policy tại server.

Không tin `role`, `team_id`, `owner_id`, `price_access` hoặc capability do client gửi.

## 8. Definition of Done

Điều kiện đạt/không đạt không được duy trì lặp lại trong tài liệu nghiệp vụ này. Source of truth chịu trách nhiệm chính là [04 — Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md); chiến lược test chi tiết nằm tại [Test strategy](../testing/test-strategy.md).

## 9. Policy nghiệp vụ chưa chốt

- Công thức lương.
- Chính sách chấm công và phép.
- Quy trình/phạm vi phê duyệt chi tiết.
- Chính sách đổi thưởng.
- Field matrix CRM.
- Ranh giới Captain/Leader/Manager ngoài policy Task Phase 1.
- Danh sách phòng ban, team, cấp bậc và capability chính thức.

## 10. Tài liệu liên quan

- [Tổng quan sản phẩm](product-overview.md)
- [Identity và phân quyền](../architecture/identity-and-authorization.md)
- [Product backlog](backlog.md)
- [Task stories Phase 1](stories/phase-1-task-vertical-slice.md)
- [People stories Phase 1](stories/phase-1-people-foundation.md)
- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Open decisions](../decisions/open-decisions.md)
