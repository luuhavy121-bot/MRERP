# Phase 1 — People/HR acceptance scenarios

Tài liệu này chuyển gói refinement People/HR thành scenario có thể kiểm thử. People/HR Foundation đã được người sở hữu sản phẩm nghiệm thu `Accepted` ngày 29/08/2026; acceptance không mở rộng sang các nghiệp vụ People ngoài slice.

## 1. Trạng thái

- **Đã chốt:** ownership, UUID ổn định, sáu lớp authorization, fail-closed và test tối thiểu.
- **Đề xuất mục tiêu:** Given/When/Then ở unit/API/integration/E2E phù hợp.
- **Đã chốt cho slice:** actor/scope, projection `basic`/`hr_detail`, promotion `Thử việc → Chính thức` và API People v1.

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

Trạng thái: `Accepted` — có API tests và đã nghiệm thu sản phẩm.

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
- When gửi mã nhân sự hợp lệ và chọn có hoặc không tạo account.
- Then server tạo Employee `Thử việc`; nếu checkbox bật thì account cũng được tạo/liên kết và mật khẩu tạm chỉ trả một lần, nếu tắt thì mapping được phép rỗng; audit không chứa password.

Trạng thái: `Ready` — contract được ADR-0007 chấp nhận.

### PEOPLE-WRITE-001B — Không báo thành công một phần

- Given một bước tạo account hoặc Employee thất bại.
- When orchestration kết thúc request.
- Then UI/API không báo tạo nhân sự thành công, không có Employee mới và hệ thống ghi failure visibility an toàn.

Trạng thái: `Ready` cho mock Identity — account tạo dở được cleanup; production IdP vẫn thuộc OD-19.

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

Trạng thái: `Accepted` — Leader cùng Team, note bắt buộc và đã nghiệm thu sản phẩm.

### PEOPLE-EMP-002 — Transition hoặc actor không hợp lệ

- Given actor thiếu capability hoặc transition không hợp lệ.
- When đổi status.
- Then server từ chối và không thay đổi Employee/history.

### PEOPLE-EMP-002A — Leader ngoài scope

- Given actor là Leader có action capability nhưng target ngoài scope quản lý được duyệt.
- When chuyển target sang `Chính thức`.
- Then server từ chối và không thay đổi status/history.

Trạng thái: `Accepted` — fixture kiểm Leader ngoài Team bị từ chối và đã nghiệm thu sản phẩm.

### PEOPLE-EMP-003 — Không xóa cứng khi nghỉ việc

- Given Employee đã có quan hệ/audit.
- When employment kết thúc.
- Then record được giữ theo retention policy và không bị hard-delete bởi workflow thông thường.

## 6. Organization và Leader–Team

### PEOPLE-ORG-001 — Quản lý đơn vị được phép

- Given actor có capability quản lý organization.
- When tạo/sửa Team hợp lệ.
- Then UUID ổn định và audit được ghi.

Trạng thái: `Ready` — Leader và CEO có capability, cơ cấu phẳng theo ADR-0009.

### PEOPLE-ORG-002 — Client tự gán scope

- Given actor gửi Team hoặc scope tự khai báo để tự mở quyền.
- When thay đổi membership hoặc leadership.
- Then server đánh giá từ permission/configuration hiện hữu và từ chối nếu không được phép.

### PEOPLE-ORG-003 — Quan hệ mồ côi hoặc không hợp lệ

- Given Employee/Team không tồn tại hoặc không còn hiệu lực.
- When tạo membership/leadership.
- Then server từ chối và không tạo quan hệ mồ côi.

### PEOPLE-ORG-004 — Archive đơn vị còn thành viên

- Given Team còn relation hiệu lực.
- When yêu cầu archive Team.
- Then server từ chối cho tới khi Team không còn nhân sự và Leader; archive thành công phải được audit và Team không còn xuất hiện trong danh sách active.

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
