# Phase 1 — People/HR acceptance scenarios

Tài liệu này chuyển gói refinement People/HR thành scenario có thể kiểm thử. Scenario có nhãn `Blocked` không được tự động hóa thành policy tùy ý trước khi quyết định tương ứng được chấp nhận.

## 1. Trạng thái

- **Đã chốt:** ownership, UUID ổn định, sáu lớp authorization, fail-closed và test tối thiểu.
- **Đề xuất mục tiêu:** Given/When/Then ở unit/API/integration/E2E phù hợp.
- **Chưa quyết định:** actor/scope, field projection, employment workflow và API payload cuối cùng.

## 2. Identity và account gate

### PEOPLE-AUTH-001 — Actor hợp lệ

- Given identity context ánh xạ được tới Employee có account/employment hợp lệ.
- When gọi action có capability, scope và field policy phù hợp.
- Then request đi tiếp tới validation nghiệp vụ.

### PEOPLE-AUTH-002 — Subject không mapping

- Given subject không ánh xạ được tới Employee.
- When gọi endpoint People được bảo vệ.
- Then server từ chối fail-closed và không tự tạo Employee.

### PEOPLE-AUTH-003 — Account khóa hoặc employment kết thúc

- Given actor còn claim/capability cũ nhưng account khóa hoặc employment đã kết thúc.
- When gọi endpoint People.
- Then server từ chối; cache/claim cũ không mở quyền.

## 3. Read và field policy

### PEOPLE-READ-001 — Đọc trong scope

- Given actor có capability và scope đã được duyệt.
- When đọc list/detail Employee trong scope.
- Then chỉ record và projection được phép xuất hiện.

Trạng thái: `Blocked` — chờ read matrix và field projection.

### PEOPLE-READ-002 — Đọc ngoài scope

- Given actor có action capability nhưng target ngoài scope.
- When đọc detail hoặc search/filter target.
- Then server từ chối/không trả record theo contract và không rò rỉ qua count.

### PEOPLE-READ-003 — Field nhạy cảm không xuất hiện

- Given actor gọi list/detail trong slice đầu.
- When server serialize response.
- Then field bị loại khỏi slice không xuất hiện, kể cả giá trị `null` hoặc metadata suy ra được.

### PEOPLE-READ-004 — Client yêu cầu projection trái phép

- Given actor thêm query/header yêu cầu field ngoài quyền.
- When gọi list/detail.
- Then server bỏ qua hoặc từ chối theo contract; không mở rộng payload.

## 4. Employee write

### PEOPLE-WRITE-001 — Tạo Employee được phép

- Given actor là HR có capability được duyệt.
- When gửi mã nhân sự, account, password khởi tạo và initial status `Thử việc` hợp lệ.
- Then Identity/Employee orchestration tuân ADR-0006, server chỉ trả thành công khi account và Employee đã được tạo/liên kết, đồng thời audit không chứa password.

Trạng thái: `Blocked` — actor/initial status đã chốt; chờ provisioning và contract.

### PEOPLE-WRITE-001B — Không báo thành công một phần

- Given một bước tạo account hoặc Employee thất bại.
- When orchestration kết thúc request.
- Then UI/API không báo tạo nhân sự thành công, không có Employee mới và hệ thống ghi failure visibility an toàn.

Trạng thái: `Blocked` — xử lý account đã tạo dở chưa quyết định.

### PEOPLE-WRITE-001A — HR cố tạo thẳng Chính thức

- Given actor là HR có capability tạo Employee.
- When sửa payload initial status thành `Chính thức`.
- Then server từ chối; frontend dropdown/hidden option không phải hàng rào duy nhất.

### PEOPLE-WRITE-002 — Thiếu capability

- Given actor đăng nhập hợp lệ nhưng thiếu capability write.
- When tạo/sửa Employee.
- Then server từ chối dù frontend có hiển thị nút hoặc client giả role.

### PEOPLE-WRITE-003 — Sửa field hệ thống

- Given payload chứa UUID, audit actor, timestamp, capability hoặc scope do client tự đặt.
- When tạo/sửa Employee.
- Then server từ chối hoặc loại field theo contract; không ghi giá trị client.

### PEOPLE-WRITE-004 — Concurrent update

- Given hai actor sửa cùng version Employee.
- When request cũ được gửi sau request đã commit.
- Then server phát hiện conflict theo cơ chế được duyệt, không âm thầm ghi đè.

## 5. Employment lifecycle

### PEOPLE-EMP-001 — Transition hợp lệ

- Given actor là Leader có capability và target ở trong scope được duyệt.
- When chuyển `Thử việc → Chính thức`.
- Then current status và history/audit nhất quán.

Trạng thái: `Blocked` — actor/transition đã chốt; chờ Leader scope và contract.

### PEOPLE-EMP-002 — Transition hoặc actor không hợp lệ

- Given actor thiếu capability hoặc transition không hợp lệ.
- When đổi status.
- Then server từ chối và không thay đổi Employee/history.

### PEOPLE-EMP-002A — Leader ngoài scope

- Given actor là Leader có action capability nhưng target ngoài scope quản lý được duyệt.
- When chuyển target sang `Chính thức`.
- Then server từ chối và không thay đổi status/history.

Trạng thái: `Blocked` — cần chốt Leader scope trước khi xác định fixture expected.

### PEOPLE-EMP-003 — Không xóa cứng khi nghỉ việc

- Given Employee đã có quan hệ/audit.
- When employment kết thúc.
- Then record được giữ theo retention policy và không bị hard-delete bởi workflow thông thường.

## 6. Organization và Leader–Team

### PEOPLE-ORG-001 — Quản lý đơn vị được phép

- Given actor có capability quản lý organization.
- When tạo/sửa Department hoặc Team hợp lệ.
- Then UUID ổn định và audit được ghi.

Trạng thái: `Blocked` — chờ actor/structure policy.

### PEOPLE-ORG-002 — Client tự gán scope

- Given actor gửi team/department của mình để tự mở scope.
- When thay đổi membership hoặc leadership.
- Then server đánh giá từ permission/configuration hiện hữu và từ chối nếu không được phép.

### PEOPLE-ORG-003 — Quan hệ mồ côi hoặc không hợp lệ

- Given Employee/Team/Department không tồn tại hoặc không còn hiệu lực.
- When tạo membership/leadership.
- Then server từ chối và không tạo quan hệ mồ côi.

### PEOPLE-ORG-004 — Archive đơn vị còn thành viên

- Given Team/Department còn relation hiệu lực.
- When yêu cầu archive.
- Then server từ chối hoặc yêu cầu migration plan theo contract được duyệt.

## 7. Migration, audit và E2E

- Migration apply trên database rỗng và reverse được khi migration tuyên bố reversible.
- Fixture chỉ dùng danh tính/tổ chức giả, không chứa PII production.
- Audit không chứa token, password hoặc field nhạy cảm ngoài nhu cầu điều tra được duyệt.
- E2E tối thiểu chứng minh UI list/detail nhận payload đã redaction từ backend; không coi việc ẩn DOM là authorization.
- Contract test xác minh error envelope, pagination và concurrency behavior sau khi contract được chấp nhận.

## 8. Tài liệu liên quan

- [People stories](../product/stories/phase-1-people-foundation.md)
- [People authorization matrix](../architecture/people-authorization-matrix.md)
- [People data contract](../architecture/people-data-contract.md)
- [People readiness register](phase-1-people-readiness.md)
