# Phase 1 — People/HR Foundation stories

Tài liệu này chi tiết hóa EPIC-02 trong [Product backlog](../backlog.md). Đây là gói refinement; không phải yêu cầu scaffold hoặc hiện thực production.

## 1. Outcome và phạm vi nhỏ nhất

**Đề xuất mục tiêu.** Slice đầu tiên chứng minh một luồng People/HR chạy xuyên:

```text
Identity context giả lập
    → account/employment gate
    → UI danh sách và hồ sơ nhân sự cơ bản
    → API kiểm capability/scope/field policy
    → PostgreSQL lưu Employee/Department/Team/quan hệ quản lý
    → audit hành động ghi
    → automated tests allowed và denied
```

**Đã chốt.** MRERP People/HR sở hữu Employee, Department, Team, employment status và organization mapping. Identity Provider vẫn sở hữu credential, login, subject và phiên.

## 2. Ngoài phạm vi slice đầu tiên

**Không làm trong slice đầu:**

- Payroll hoặc bất kỳ field/công thức lương nào.
- Attendance/Leave, Recruitment, Rewards và Documents.
- CRM, ASSETCONTROL hoặc MREKANBAN integration/snapshot.
- Provisioning/deprovisioning credential ở Identity Provider.
- Chọn Identity Provider thật.
- Import dữ liệu production hoặc tự tạo cơ cấu MRE chính thức.
- Hồ sơ pháp lý, ngân hàng, thuế, địa chỉ nhà và dữ liệu nhạy cảm khác.
- Upload avatar/file, bulk import/export và xóa cứng Employee.

## 3. Story nền tảng

### P1-PLAT-01 — Identity context giả lập

**Là một** backend MRERP, **tôi muốn** nhận identity context giả lập theo contract được duyệt **để** kiểm account, employment, capability và scope mà chưa chọn IdP thật.

Trạng thái: `Ready` — ADR-0004 đã được chấp nhận.

### P1-PPL-01 — Đọc hồ sơ của chính mình

**Là một** nhân sự đang hoạt động, **tôi muốn** xem hồ sơ cơ bản của mình **để** xác nhận thông tin tổ chức đang được MRERP lưu.

Acceptance criteria dự thảo:

- Actor được suy ra từ identity context, không nhận `employee_uuid` của actor từ client.
- Account khóa hoặc employment không hợp lệ bị từ chối fail-closed.
- Payload chỉ chứa field được phép; field nhạy cảm không xuất hiện.
- UI có loading, empty, forbidden và error state.

Trạng thái: `Ready`.

### P1-PPL-02 — Xem danh sách nhân sự cơ bản

**Là một** nhân sự có capability đọc danh bạ, **tôi muốn** tìm và phân trang danh sách Employee trong scope **để** biết đúng người, team và vị trí công việc.

Acceptance criteria dự thảo:

- Server-side pagination, search và filter chỉ dùng field được duyệt.
- Record ngoài scope không xuất hiện và không rò rỉ qua count/filter.
- Response dùng UUID ổn định, không dùng email/mã nhân viên làm khóa liên kết.
- API không trả field ngoài projection `basic` đã duyệt.

Trạng thái: `Ready` — Staff cùng Team; Leader toàn công ty; projection cơ bản.

### P1-PPL-03 — Xem hồ sơ nhân sự cơ bản

**Là một** người có capability phù hợp, **tôi muốn** mở hồ sơ Employee trong scope **để** xem thông tin công việc và quan hệ tổ chức.

Acceptance criteria dự thảo:

- Endpoint kiểm action capability, data scope, object rule và field policy.
- UUID không tồn tại và UUID ngoài scope không làm rò rỉ dữ liệu trái phép.
- Department, Team và Leader được đọc từ dữ liệu server.

Trạng thái: `Ready`.

### P1-PPL-04 — Tạo Employee

**Là một** HR có capability phù hợp, **tôi muốn** thêm nhân sự ở trạng thái `Thử việc` và chọn có tạo tài khoản hay không **để** MRERP có thể tạo hồ sơ trước hoặc đồng thời chuẩn bị quyền đăng nhập.

Acceptance criteria dự thảo:

- Chỉ HR có capability được duyệt mới tạo được qua luồng này.
- Server chỉ chấp nhận trạng thái ban đầu `Thử việc`; HR không thể sửa payload để tạo thẳng `Chính thức`.
- Mã nhân sự nhập tự do, không rỗng và không trùng không phân biệt hoa/thường; tài khoản/mật khẩu thuộc luồng Identity provisioning.
- Employee nhận UUID do server tạo; `identity_subject` có thể để trống trước khi mapping.
- Dữ liệu đầu vào được validate; password không được lưu trong Employee, audit hoặc log.
- Khi checkbox bật, UI chỉ báo thành công khi account và Employee đã được tạo/liên kết. Khi tắt, username/password không bắt buộc và Employee có account mapping rỗng.
- Nếu một bước thất bại, request thất bại và không tạo Employee.
- Tạo account tại IdP và Employee phải có failure/compensation behavior được ADR chấp nhận.

Trạng thái: `Ready` — ADR-0004 và ADR-0007 đã được chấp nhận.

### P1-PPL-05 — Cập nhật hồ sơ và employment status

**Là một** Leader có capability phù hợp, **tôi muốn** chuyển nhân sự từ `Thử việc` sang `Chính thức` **để** ghi nhận quyết định tiếp nhận chính thức.

Acceptance criteria dự thảo:

- Field-level authorization được kiểm ở server.
- Leader được phép thực hiện transition `Thử việc → Chính thức`; transition khác không được suy ra.
- Server ghi actor, effective time và before/after status; reason/ghi chú có bắt buộc hay không vẫn chưa quyết định.
- Leader ngoài scope không được phép xác nhận; scope Leader vẫn cần người dùng chốt.
- Không xóa cứng Employee khi nghỉ việc.
- Mọi thay đổi quan trọng có before/after audit được tối thiểu hóa.

Trạng thái: `Ready` — Leader cùng Team, hiệu lực ngay và note bắt buộc.

### P1-PPL-06 — Quản lý Department và Team

**Là một** người quản trị organization được ủy quyền, **tôi muốn** tạo/sửa Department và Team **để** Employee được gắn vào cơ cấu có UUID ổn định.

Acceptance criteria dự thảo:

- Tên đơn vị không phải khóa liên kết duy nhất.
- Không hard-code tên phòng ban/team trong permission core.
- Không cho archive đơn vị khi còn quan hệ hiệu lực nếu chưa có phương án chuyển.
- Mọi thay đổi có audit.

Trạng thái: `Ready` — Leader quản lý organization; fixture chỉ dùng dữ liệu giả.

### P1-PPL-07 — Gán Employee vào Team và gán Leader

**Là một** người quản trị organization được ủy quyền, **tôi muốn** quản lý membership và quan hệ Leader–Team theo thời gian **để** authorization có scope đáng tin cậy.

Acceptance criteria dự thảo:

- Membership và leadership có UUID/effective period hoặc cơ chế lịch sử tương đương được duyệt.
- Không tin team/Leader do client gửi để mở quyền cho chính actor.
- Không cho quan hệ mồ côi hoặc vòng tham chiếu không hợp lệ theo data contract.
- Thay đổi scope có audit và test cache invalidation/fail-closed phù hợp.

Trạng thái: `Ready` — một Team/Employee và nhiều Leader/Team.

### P1-PPL-08 — Audit và bằng chứng authorization

**Là một** người vận hành được ủy quyền, **tôi muốn** có audit cho thay đổi People/organization **để** điều tra nguồn gốc thay đổi mà không lộ dữ liệu nhạy cảm.

Acceptance criteria dự thảo:

- Create/update/status/membership/leadership đều ghi actor, action, target, timestamp và thay đổi tối thiểu cần thiết.
- Denied event quan trọng có correlation identifier; không ghi token hoặc payload nhạy cảm.
- Automated tests bao phủ allowed, thiếu capability, ngoài scope, field absence và account/employment không hợp lệ.

Trạng thái: `Ready`.

## 4. Definition of Ready của slice

Mỗi story đạt [Definition of Ready chung](../../testing/definition-of-ready.md) theo đánh giá tại [People readiness register](../../testing/phase-1-people-readiness.md). Việc chuyển `Ready` dựa trên ADR/contract được duyệt, không dựa vào UI prototype.

## 5. Tài liệu liên quan

- [People data và API contract dự thảo](../../architecture/people-data-contract.md)
- [Ma trận phân quyền People](../../architecture/people-authorization-matrix.md)
- [Acceptance scenarios](../../testing/phase-1-people-acceptance.md)
- [Open decisions](../../decisions/open-decisions.md)
