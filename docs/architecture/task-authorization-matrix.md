# Ma trận phân quyền Task — Phase 1

Tài liệu này chuyên biệt hóa authorization model tại [Identity và phân quyền](identity-and-authorization.md) cho Task vertical slice. Source of truth tổng quát vẫn là tài liệu Identity; quyết định baseline của slice được ghi tại [ADR-0002](../decisions/0002-task-authorization-baseline.md).

## 1. Nguyên tắc

**Đã chốt.** Backend kiểm account/employment, action capability, data scope, object rule và field policy. Cấp bậc chỉ được dùng để cấu hình capability/scope mặc định của MRE; permission core không hard-code tên cấp bậc.

**Đã chốt.** Captain có permission nền giống Staff.

**Đã chốt.** Giai đoạn đầu không có user Manager. Data model vẫn hỗ trợ Manager tương lai với department scope; không tự nâng Leader hiện tại thành Manager.

## 2. Scope mặc định cho Task

| Cấp bậc MRE | Data scope Task đã xác nhận | Ghi chú |
|---|---|---|
| Staff | `self` cho hành động tự giao | Baseline `tasks.read` đầy đủ vẫn cần xác nhận |
| Captain | Giống Staff | Không có quyền tăng thêm chỉ vì là Captain |
| Leader | Team mình phụ trách | Quan hệ quản lý lấy từ server |
| Manager | Phòng ban mình phụ trách | Hỗ trợ tương lai; ban đầu không có user Manager |
| CEO | Toàn công ty | Mỗi action vẫn cần capability; không phải superuser ngầm |

OD-04 vẫn mở cho policy ngoài Task và module khác.

## 3. Capability Task

| Capability | Ý nghĩa | Cấp mặc định trong slice |
|---|---|---|
| `tasks.create` | Tạo Task | Gói capability cơ bản cho mọi employment đang hoạt động |
| `tasks.assign` | Chọn người nhận | Theo scope tại mục 4 |
| `tasks.read` | Đọc Task | **Chưa quyết định đầy đủ** cho Staff/Captain; cần chốt trước khi story P1-TASK-01 Ready |
| `tasks.update_definition` | Sửa tiêu đề, mô tả, deadline, người nhận | Người tạo; phải qua object/field/scope rule |
| `tasks.update_execution` | Sửa trạng thái thực hiện, tiến độ, bình luận, bằng chứng | Người nhận |
| `tasks.manage` | Quản lý Task trong scope | Chỉ có hiệu lực khi được cấp capability và scope |
| `tasks.submit` | Gửi `Chờ xác nhận` | Người nhận hợp lệ |
| `tasks.accept` | Chọn `Đã hoàn thành` hoặc `Yêu cầu làm lại` | Người tạo hoặc người xác nhận trong scope, trừ self-task |
| `tasks.cancel` | Hủy Task | **Chưa quyết định**; không thuộc slice đầu tiên |

## 4. Ma trận hành động và scope

| Hành động | Staff | Captain | Leader | Manager tương lai | CEO |
|---|---|---|---|---|---|
| Tạo Task | Có `tasks.create` | Giống Staff | Có `tasks.create` | Có `tasks.create` | Có `tasks.create` |
| Giao cho bản thân | Có `tasks.assign:self` | Giống Staff | Có | Có | Không dùng self-task cần xác nhận |
| Giao cho người khác | Không | Không | Thành viên team phụ trách | Nhân sự trong phòng ban phụ trách | Nhân sự toàn công ty |
| Sửa phần định nghĩa | Khi là người tạo và object rule cho phép | Giống Staff | Người tạo hoặc `tasks.manage` trong team | Người tạo hoặc `tasks.manage` trong phòng ban | Người tạo hoặc `tasks.manage` company scope |
| Sửa phần thực hiện | Khi là người nhận | Giống Staff | Khi là người nhận; quản lý cần `tasks.manage` | Tương tự trong department scope | Tương tự trong company scope |
| Submit hoàn thành | Khi là người nhận | Giống Staff | Khi là người nhận | Khi là người nhận | Khi là người nhận, trừ self-task bị loại khỏi workflow |
| Accept/rework | Khi là người tạo, không phải self-task | Giống Staff | Người tạo hoặc `tasks.accept` trong team | Tương lai trong department scope | Người tạo hoặc `tasks.accept` company scope |

Mọi ô “Có” vẫn phụ thuộc account/employment hợp lệ và capability tương ứng. Client không được gửi cấp bậc/scope để tự mở quyền.

## 5. Field policy

| Nhóm field | Người tạo | Người nhận | Người có `tasks.manage` trong scope |
|---|---|---|---|
| Tiêu đề, mô tả, deadline, assignee | Được sửa theo object rule | Chỉ đọc | Được sửa theo scope/object rule |
| Trạng thái thực hiện, tiến độ | Chỉ đọc/accept transition | Được cập nhật theo state machine | Được cập nhật nếu policy cho phép |
| Bình luận, bằng chứng | Được thêm bình luận | Được thêm/cập nhật phần của mình | Được xem trong scope; sửa nội dung người khác không thuộc slice |
| Audit fields nội bộ | Không được sửa | Không được sửa | Không được sửa qua Task API |

## 6. State transition đã chốt

```text
Đang thực hiện
    ↓ người nhận có tasks.submit
Chờ xác nhận
    ├─ người xác nhận có tasks.accept → Đã hoàn thành
    └─ người xác nhận có tasks.accept → Yêu cầu làm lại
```

UI có thể dùng status dropdown. Server mới là nơi kiểm tra actor, capability, scope và transition.

## 7. Self-task

**Đã chốt.** Người tạo đồng thời là người nhận không được tự accept:

- Staff/Captain self-task → Leader trực tiếp có `tasks.accept` xác nhận.
- Leader self-task → CEO có `tasks.accept` xác nhận.
- CEO không tạo self-task trong workflow cần xác nhận.

## 8. Chưa quyết định và ngoài slice

- Baseline `tasks.read` chi tiết cho Staff/Captain.
- Xóa/hủy, mở lại sau khi hoàn thành và escalation quá hạn.
- Comment visibility/mention policy chi tiết.
- Delegation khi Leader vắng mặt.
- Manager cross-module policy và danh sách organization chính thức.

## 9. Tài liệu liên quan

- [Task stories](../product/stories/phase-1-task-vertical-slice.md)
- [Task acceptance scenarios](../testing/phase-1-task-acceptance.md)
- [Open decisions](../decisions/open-decisions.md)
