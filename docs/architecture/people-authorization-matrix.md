# Ma trận phân quyền People/HR — Phase 1

Tài liệu này chuyên biệt hóa [Identity và phân quyền](identity-and-authorization.md) cho People/HR Foundation. Actor/scope/field policy trong slice đã được chấp nhận qua ADR-0005; quyền CEO/Admin và policy ngoài slice vẫn chưa được suy ra.

## 1. Nguyên tắc bắt buộc

**Đã chốt.** Mỗi endpoint nhạy cảm kiểm account/employment, product capability, action capability, data scope, object rule và field policy tại server. Không tin role, `employee_uuid`, department/team hoặc capability do client gửi.

**Đã chốt.** MRERP sở hữu organization mapping và capability cấp hệ sinh thái. Tên cấp bậc/phòng ban/team là company configuration, không được hard-code vào permission core.

**Đã chốt cho slice.** HR tạo Employee ở trạng thái `Thử việc` và xem/sửa hồ sơ chi tiết. Staff đọc nhân sự cùng Team. Leader đọc mọi Team, quản lý organization và chỉ chuyển `Thử việc → Chính thức` trong Team mình lãnh đạo.

**Chưa quyết định ngoài slice.** Người được vào Admin Panel, quyền Captain/Manager tương lai và các employment transition khác.

## 2. Capability catalog của slice

| Capability | Action | Trạng thái |
|---|---|---|
| `people_domain.view_employee` | Đọc Employee trong scope | **Đã chốt cho slice** |
| `people_domain.view_company_directory` | Mở rộng read scope ra toàn công ty | **Đã chốt cho Leader** |
| `people_domain.view_hr_detail` | Nhận projection HR | **Đã chốt cho HR** |
| `people_domain.add_employee` | Tạo Employee `Thử việc` | **Đã chốt cho HR** |
| `people_domain.change_employee` | Sửa allow-list hồ sơ HR | **Đã chốt cho HR** |
| `people_domain.promote_employee` | Chuyển `Thử việc → Chính thức` | **Đã chốt cho Leader cùng Team** |
| `people_domain.manage_organization` | Tạo/sửa Department/Team | **Đã chốt cho Leader** |
| `people_domain.manage_membership` | Quản lý Employee–Team và Leader–Team | **Đã chốt cho Leader** |
| `people_domain.view_people_audit` | Đọc audit People | Capability có sẵn; actor/UI **Chưa quyết định** |

Projection nhạy cảm dùng capability riêng `view_hr_detail`; Staff/Leader không nhận CCCD, ngày sinh hoặc địa chỉ.

## 3. Data scope dự thảo

| Scope | Ý nghĩa |
|---|---|
| `self` | Employee được ánh xạ với actor |
| `managed_team` | Team mà actor có quan hệ quản lý hiệu lực |
| `managed_department` | Department actor được giao quản lý |
| `assigned` | Scope được cấp rõ bằng configuration |
| `company` | Toàn công ty, vẫn cần action capability |

**Đã chốt trong slice:** Staff dùng `managed_team` theo membership hiện tại để đọc; Leader có `company` scope cho đọc directory và `managed_team` cho promotion; HR có `company` scope cho create/read/update Employee. Captain/Manager chưa có user và chưa có bundle.

## 4. Action matrix

| Hành động | Capability | Scope/object/field rule | Trạng thái |
|---|---|---|---|
| Xem hồ sơ của mình | `people.employee.read_self` | `self`, projection cơ bản | **Đã chốt** |
| Staff xem danh bạ | `people.employee.read_basic` | Team hiện tại, projection cơ bản | **Đã chốt** |
| Leader xem danh bạ | `people.employee.read_basic` | Company scope, projection cơ bản | **Đã chốt** |
| HR xem hồ sơ chi tiết | `people.employee.read_detail` | Company scope, projection HR | **Đã chốt** |
| HR tạo Employee `Thử việc` | `people_domain.add_employee` | Chỉ initial `Thử việc`; input/field allow-list | **Đã chốt** |
| HR sửa hồ sơ chi tiết | `people_domain.change_employee` | Company scope, allow-list HR | **Đã chốt** |
| Leader chuyển `Thử việc → Chính thức` | `people_domain.promote_employee` | Team mình lãnh đạo, hiệu lực ngay, note bắt buộc | **Đã chốt** |
| Leader quản lý Department/Team | `people_domain.manage_organization` | Company scope, object rule/audit | **Đã chốt** |
| Leader gán membership/Leader–Team | `people_domain.manage_membership` | Một Employee tối đa một Team; Team nhiều Leader | **Đã chốt** |
| Đọc audit | `people_domain.view_people_audit` | Scope và redaction riêng | **Chưa quyết định actor** |

## 5. Field policy dự thảo

| Nhóm field | Projection | Quy tắc |
|---|---|---|
| Field hệ thống | `system` | Chỉ server ghi; response tối thiểu theo use case |
| Hồ sơ công việc cơ bản | `basic` | UUID, mã nhân sự, tên hiển thị, vị trí, phòng ban, Team; Staff cùng Team và Leader company scope |
| Hồ sơ HR | `hr_detail` | `basic` cộng account, CCCD, ngày sinh, địa chỉ và employment status; chỉ HR |
| Organization relation | `organization` | Đọc/ghi theo capability và scope |
| Employment lifecycle | `employment` | Hạn chế hơn `basic`; transition riêng |
| Audit | `audit` | Không nằm trong Employee payload thông thường |
| Field HR nhạy cảm | `hr_detail` | CCCD, ngày sinh, địa chỉ; chỉ HR, không trả Staff/Leader |

Server phải tạo projection rõ; không serialize toàn bộ model rồi dựa vào frontend để ẩn field.

## 6. Object rule dự thảo

- Không tự sửa field hệ thống hoặc tự gán capability/scope.
- Không dùng endpoint Employee để tạo credential IdP.
- Không xóa cứng Employee đã được tham chiếu.
- Không archive Department/Team còn quan hệ hiệu lực khi chưa xử lý thành viên.
- Không cho actor sửa organization mapping của chính mình nếu policy chưa có phê duyệt/segregation phù hợp.
- Employment không hợp lệ làm fail account/employment gate cho nghiệp vụ được bảo vệ.

Các rule của slice được ADR-0005 chấp nhận; rule ngoài slice không được suy diễn.

## 7. Ngoài phạm vi/chưa quyết định

- Transition khác ngoài `Thử việc → Chính thức` và quy tắc thu hồi quyết định.
- Self-service edit.
- Ai được xem audit People.

## 8. Tài liệu liên quan

- [People stories](../product/stories/phase-1-people-foundation.md)
- [People data contract](people-data-contract.md)
- [People acceptance scenarios](../testing/phase-1-people-acceptance.md)
- [ADR-0005](../decisions/0005-people-authorization-and-field-policy.md)
