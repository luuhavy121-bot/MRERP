# Ma trận phân quyền Task

Tài liệu này chuyên biệt hóa authorization Task theo ADR-0002 và ADR-0011. Backend luôn kiểm account/employment, capability, data scope, object rule và field policy; frontend không phải hàng rào bảo mật.

## Read scope đã chốt

| Actor | Task được đọc |
|---|---|
| Staff/Captain | Task mình tạo hoặc được giao |
| HR | Task mình tạo hoặc được giao; HR role không tự mở company Task |
| Leader | Task cá nhân và Task thuộc Team đang lãnh đạo |
| Manager | **Chưa quyết định**; giai đoạn đầu không có user Manager |
| CEO | Task toàn công ty khi có capability đọc |

## Hành động

| Hành động | Staff/Captain/HR | Leader | CEO |
|---|---|---|---|
| Tạo/giao | Chỉ tự giao | Bản thân hoặc thành viên Team lãnh đạo | Nhân sự trong công ty; không self-task |
| Sửa definition | Khi là creator | Creator hoặc Task trong Team lãnh đạo | Company scope |
| Sửa progress | Chỉ khi là assignee | Chỉ khi là assignee | Chỉ khi là assignee; CEO self-task bị chặn |
| Submit | Assignee | Assignee | Assignee hợp lệ |
| Accept/rework | Không có capability mặc định | Task trong Team, không tự accept | Company scope, không tự accept |
| Brief attachment | Creator | Creator/manager Team | Company scope |
| Evidence attachment | Assignee | Khi là assignee | Khi là assignee |
| Goal | Đọc company + Team hiện tại | Quản lý Goal Team lãnh đạo | Quản lý Goal company và mọi Team |
| Recurrence | Không mở UI quản lý mặc định | Quản lý series mình tạo trong Team | Quản lý company scope |

Captain giữ permission nền như Staff. HR không nhận quyền Task cao hơn chỉ vì quản lý People.

## Object và field rule

- State machine: `Đang thực hiện/Yêu cầu làm lại → Chờ xác nhận → Đã hoàn thành hoặc Yêu cầu làm lại`.
- Task hoàn thành không sửa definition/progress trong phạm vi hiện tại.
- Rework cần ghi chú. Assignee không tự accept Task của mình.
- Goal Team chỉ liên kết Task cùng Team; deadline Task phải nằm trong timebox Goal.
- Recurrence gắn Goal phải dừng trong timebox; occurrence unique theo series + scheduled time.
- Client không gửi role/capability/scope để tự mở quyền.

## Không làm và chưa quyết định

- **Không làm trong phạm vi hiện tại:** cancel/delete/reopen Task, dependency, checklist, delegation và Task comments.
- **Chưa quyết định:** scope Manager và policy Task ngoài phạm vi ADR-0002/0011.

## Tài liệu liên quan

- [Contract](dashboard-feed-task-contract.md)
- [Task stories](../product/stories/phase-1-task-vertical-slice.md)
- [Acceptance](../testing/dashboard-feed-task-acceptance.md)
