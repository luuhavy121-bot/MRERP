# Phase 1 — Task acceptance scenarios

Tài liệu này chuyển [ma trận quyền Task](../architecture/task-authorization-matrix.md) thành các scenario có thể kiểm thử. Endpoint URL và schema cụ thể chỉ được bổ sung sau khi API contract được duyệt.

## 1. Trạng thái

- **Đã chốt:** hành vi quyền lấy từ ADR-0002 và ma trận Task.
- **Đề xuất mục tiêu:** biểu diễn scenario theo Given/When/Then và tự động hóa ở API/integration test.
- **Chưa quyết định:** endpoint, payload schema, cancellation và baseline `tasks.read` đầy đủ.

## 2. Account và employment gate

### TASK-AUTH-001 — Account hợp lệ

- Given actor có account và employment hợp lệ.
- When gọi một action có capability và scope phù hợp.
- Then request được đi tiếp tới business/object validation.

### TASK-AUTH-002 — Account khóa

- Given actor có capability nhưng account bị khóa.
- When gọi Task action.
- Then server từ chối fail-closed.

### TASK-AUTH-003 — Employment kết thúc

- Given capability cũ vẫn còn nhưng employment đã kết thúc.
- When gọi Task action.
- Then server từ chối và không tin capability cache cũ.

## 3. Tạo và giao Task

### TASK-CREATE-001 — Tạo được phép

- Given nhân sự đang hoạt động có `tasks.create`.
- When tạo Task với dữ liệu hợp lệ.
- Then Task có UUID, creator từ server context và audit create.

### TASK-CREATE-002 — Thiếu capability

- Given actor không có `tasks.create`.
- When tạo Task.
- Then server từ chối; việc frontend ẩn nút không ảnh hưởng kết quả.

### TASK-ASSIGN-001 — Staff tự giao

- Given Staff có `tasks.assign:self`.
- When assignee là chính actor.
- Then được phép.

### TASK-ASSIGN-002 — Staff giao cho đồng đội

- Given Staff/Captain cố chọn người khác.
- When tạo hoặc đổi assignee.
- Then server từ chối ngoài scope.

### TASK-ASSIGN-003 — Leader giao trong team

- Given Leader quản lý team A và có `tasks.assign`.
- When giao cho thành viên team A.
- Then được phép.

### TASK-ASSIGN-004 — Leader giao team khác

- Given Leader chỉ quản lý team A.
- When giao cho thành viên team B.
- Then server từ chối ngoài scope dù client gửi `team_uuid=A` giả.

### TASK-ASSIGN-005 — CEO thiếu action capability

- Given CEO có company scope nhưng không có `tasks.assign`.
- When giao Task cho người khác.
- Then server từ chối do thiếu capability.

## 4. Field và object rule

### TASK-FIELD-001 — Người tạo sửa definition

- Given actor là creator và Task ở state cho phép.
- When sửa title/description/deadline/assignee trong scope.
- Then được phép và ghi audit phần thay đổi cần thiết.

### TASK-FIELD-002 — Người nhận sửa definition

- Given actor chỉ là assignee.
- When sửa title/deadline/assignee.
- Then server từ chối field-level update.

### TASK-FIELD-003 — Người nhận cập nhật execution

- Given actor là assignee.
- When cập nhật progress, trạng thái thực hiện, comment hoặc evidence của mình.
- Then được phép theo object state.

### TASK-FIELD-004 — Client sửa audit field

- Given bất kỳ actor nghiệp vụ nào.
- When payload chứa creator UUID, audit actor hoặc timestamp do client tự đặt.
- Then server bỏ qua hoặc từ chối theo contract; không ghi giá trị client vào field hệ thống.

## 5. Submit và accept

### TASK-STATE-001 — Người nhận submit

- Given actor là assignee và Task đang thực hiện.
- When chọn `Chờ xác nhận`.
- Then transition hợp lệ và có audit.

### TASK-STATE-002 — Người nhận tự đóng Task do người khác tạo

- Given actor là assignee nhưng không phải creator/người accept.
- When chọn `Đã hoàn thành`.
- Then server từ chối object transition.

### TASK-STATE-003 — Người tạo accept

- Given Task không phải self-task và actor là creator có quyền phù hợp.
- When chọn `Đã hoàn thành` hoặc `Yêu cầu làm lại`.
- Then transition hợp lệ và có audit.

### TASK-STATE-004 — Staff/Captain self-task

- Given creator đồng thời là assignee ở cấp Staff/Captain.
- When actor tự chọn `Đã hoàn thành`.
- Then server từ chối; Leader trực tiếp có `tasks.accept` mới được xác nhận.

### TASK-STATE-005 — Leader self-task

- Given creator đồng thời là assignee ở cấp Leader.
- When Leader tự accept.
- Then server từ chối; CEO có `tasks.accept` mới được xác nhận.

### TASK-STATE-006 — CEO self-task

- Given actor là CEO.
- When cố tạo self-task trong workflow cần xác nhận.
- Then server từ chối theo rule của slice.

## 6. Bằng chứng tối thiểu

- Unit test policy cho capability, scope và state transition.
- API test cho allowed/denied/field policy/employment gate.
- Integration test chứng minh audit và Task cùng transaction hoặc có failure behavior rõ.
- Contract evidence cho actor UUID do server xác định.
- Không dùng dữ liệu production trong fixture.

## 7. Tài liệu liên quan

- [Test strategy](test-strategy.md)
- [Definition of Ready](definition-of-ready.md)
- [Task stories](../product/stories/phase-1-task-vertical-slice.md)
