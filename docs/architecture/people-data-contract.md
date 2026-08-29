# People/HR — field, data model và API contract dự thảo

Tài liệu này là contract nội bộ của slice People/HR Phase 1. [Data ownership](data-ownership.md) vẫn là source of truth về quyền sở hữu dữ liệu. Các phần được ADR-0003 đến ADR-0008 chấp nhận có nhãn **Đã chốt**; phần production Identity và policy ngoài slice vẫn giữ nguyên trạng thái mở.

## 1. Ranh giới dữ liệu

**Đã chốt.** MRERP sở hữu Employee, Team, employment status và organization mapping. Cơ cấu MRE hiện là `CEO → Team → Employee`, không có tầng Department. Identity Provider production sở hữu credential, login, subject và phiên. Adapter mock development/test dùng Django auth để mô phỏng boundary này trong cùng deployable; password chỉ được hash bởi auth subsystem, không là field Employee và không xuất hiện trong audit. Mật khẩu tạm chỉ được trả một lần ngay sau provision/reset.

## 2. Field catalog

### 2.1 Field hệ thống

| Field dự thảo | Mục đích | Trạng thái |
|---|---|---|
| `employee_uuid` | Định danh ổn định | **Đã chốt**; hiện thực bằng UUID server-generated |
| `created_at`, `updated_at` | Audit kỹ thuật | **Đã chốt cho slice** |
| `version` | Chống ghi đè cạnh tranh/optimistic concurrency | **Đã chốt cho slice** |
| `identity_subject` | Mapping subject IdP production | **Chưa quyết định**; mock hiện liên kết tới auth user nội bộ |

### 2.2 Projection `basic` và `hr_detail`

**Đã chốt cho slice:**

- `display_name`;
- `employee_code`;
- `job_title`;
- `team_uuid` và tên hiển thị.

Staff nhận `basic` trong cùng Team; Leader nhận `basic` toàn công ty. Projection `hr_detail` dành cho HR và CEO, bổ sung username/account mapping, CCCD, ngày sinh, địa chỉ và employment status. Leader nhận employment status của target trong command promotion nhưng field nhạy cảm không xuất hiện trong directory payload.

### 2.3 Input của form thêm nhân sự

**Đã chốt về yêu cầu nghiệp vụ:** form luôn nhận mã nhân sự và có checkbox chọn tạo tài khoản. Username chỉ bắt buộc khi checkbox bật; server sinh mật khẩu tạm và trả đúng một lần. HR chỉ được tạo với trạng thái `Thử việc`.

**Đã chốt về outcome:** nếu checkbox bật, một lần bấm Lưu phải tạo/liên kết được cả account Identity lẫn Employee trước khi trả thành công. Nếu checkbox tắt, chỉ tạo Employee và để account mapping rỗng.

**Đã chốt về failure outcome cho mock:** nếu một bước thất bại thì không tạo Employee và API không trả kết quả thành công; account mock vừa tạo phải bị xóa. Compensation với IdP production vẫn cần ADR khi chọn provider.

| Input | Owner/nơi lưu | Trạng thái |
|---|---|---|
| Mã nhân sự | MRERP `Employee` | Bắt buộc, nhập tự do tối đa 64 ký tự, duy nhất không phân biệt hoa/thường |
| Tạo tài khoản | Command input | Boolean; mặc định bật trong quick-create |
| Tài khoản | Identity Provider; MRERP chỉ giữ mapping subject sau provisioning | Ownership **Đã chốt**; mock username là duy nhất; production format/recovery **Chưa quyết định** |
| Mật khẩu khởi tạo | Identity Provider/auth subsystem | Ownership **Đã chốt**; không lưu trong Employee/log/audit/response; không bắt buộc đổi lần đầu trong mock slice |
| Trạng thái công việc | MRERP `Employee`/history | Initial value `Thử việc` **Đã chốt** cho HR create flow |

Form UI không làm thay đổi ownership: password không trở thành field của `Employee`; UI không nhận mật khẩu do HR tự đặt cho account mới.

### 2.4 Field bị loại khỏi slice

**Không làm trong slice đầu:** giới tính, số điện thoại cá nhân, thuế, ngân hàng, lương/phụ cấp, dữ liệu chấm công/nghỉ phép, hồ sơ tuyển dụng và file pháp lý. Ngày sinh, địa chỉ và CCCD đã được người sở hữu sản phẩm đưa vào projection `hr_detail`; HR và CEO được nhận/sửa trong slice.

Loại khỏi slice không có nghĩa các field này được chấp nhận cho phase sau; privacy, retention và quyền xem vẫn **Chưa quyết định**.

## 3. Data model dự thảo

| Entity | Trách nhiệm | Quan hệ chính |
|---|---|---|
| `Employee` | Hồ sơ công việc và trạng thái hiện tại | Tham chiếu tối đa một Team |
| `Team` | Đơn vị làm việc trực tiếp dưới CEO | Có nhiều Employee và nhiều Leader; dùng UUID |
| `TeamLeadership` | Quan hệ Leader–Team | Unique theo cặp Team–Leader; một Team có nhiều Leader |
| `EmploymentTransition` | Lịch sử chuyển trạng thái | Employee, from/to, effective time, note và actor |
| `AuditEvent` | Bằng chứng hành động nhạy cảm | Actor, action, target, timestamp, correlation ID |

**Chưa quyết định:**

- Nếu tương lai MRE phát sinh tầng tổ chức khác Team thì phải mở decision/ADR mới; không tái kích hoạt Department âm thầm.
- Retention/anonymization sau khi employment kết thúc.

**Đã chốt:** một Employee thuộc tối đa một Team tại một thời điểm; một Team có thể có nhiều Leader. ADR-0010 mở rộng trạng thái bằng `Tạm nghỉ` và `Nghỉ việc`; promotion `Thử việc → Chính thức` vẫn do Leader cùng Team thực hiện, còn HR/CEO quản lý pause/terminate/reactivate.

## 4. Invariant dự thảo

- UUID do server tạo và không đổi khi tên/email thay đổi.
- Team được archive thay vì xóa cứng khi đã được tham chiếu.
- Employee nghỉ việc không bị xóa cứng.
- Membership/leadership không trỏ tới entity không tồn tại hoặc đã vô hiệu theo rule được duyệt.
- Client không được đặt audit actor, created timestamp, capability hoặc scope.
- Thay đổi organization không tự cấp capability nếu chưa qua policy/configuration được duyệt.

Các invariant trên là **Đề xuất mục tiêu** trừ ràng buộc UUID ổn định, không tin client và không hard-code cơ cấu đã **Đã chốt** ở source of truth.

## 5. API contract Phase 1

Prefix đã dùng: `/api/v1`. OpenAPI version-control tại `apps/mrerp/backend/openapi.yaml` là contract máy đọc của implementation.

| Method/path dự thảo | Outcome | Trạng thái |
|---|---|---|
| `GET /people/employees/me/` | Hồ sơ actor theo projection | **Đã chốt/đã hiện thực** |
| `GET /people/employees/` | Danh sách theo capability/scope/projection | **Đã chốt/đã hiện thực** |
| `GET /people/employees/{uuid}/` | Hồ sơ theo scope | **Đã chốt/đã hiện thực** |
| `POST /people/employees/` | HR tạo Employee `Thử việc`, tùy chọn tạo account mock cùng thao tác | **Đã chốt/đã hiện thực** |
| `PATCH /people/employees/{uuid}/` | HR sửa allow-list, bắt buộc `expected_version` | **Đã chốt/đã hiện thực** |
| `POST /people/employees/{uuid}/promote/` | Leader chuyển `Thử việc → Chính thức` trong Team lãnh đạo | **Đã chốt/đã hiện thực** |
| `PUT /people/employees/{uuid}/membership/` | Leader gán tối đa một Team | **Đã chốt/đã hiện thực** |
| `GET/POST/PATCH /people/teams/` | Đọc/quản lý Team theo quyền | **Đã chốt/đã hiện thực** |
| `POST /people/teams/{uuid}/archive/` | Archive Team sau khi đã chuyển hết nhân sự và gỡ Leader | **Đã chốt/đã hiện thực** |
| `GET/POST /people/teams/{uuid}/leaders/` | Đọc/thêm Leader–Team | **Đã chốt/đã hiện thực** |
| `DELETE /people/teams/{uuid}/leaders/{employee_uuid}/` | Gỡ Leader–Team | **Đã chốt/đã hiện thực** |
| `PATCH /people/employees/me/` | Self-edit tên hiển thị, ngày sinh, địa chỉ | **Đã chốt qua ADR-0010** |
| `POST /people/employees/me/change-password/` | Actor đổi mật khẩu của chính mình qua Identity adapter | **Đã chốt cho mock; production IdP Chưa quyết định** |
| `POST /people/employees/{uuid}/account/{command}/` | Provision, lock, unlock hoặc reset password theo quyền | **Đã chốt cho mock; production IdP Chưa quyết định** |
| `POST /people/employees/{uuid}/employment/` | Pause, terminate hoặc reactivate có audit/history | **Đã chốt qua ADR-0010** |
| `GET /people/employees/{uuid}/history/` | Membership/employment history được phép | **Đã chốt qua ADR-0010** |
| `POST/GET /people/employees/import-csv|export-csv/` | CSV không password | **Đã chốt qua ADR-0010** |
| `GET/PUT /people/access/` | CEO xem/gán access bundle allow-list | **Đã chốt qua ADR-0010** |
| `GET /people/audit/` | CEO/HR đọc projection audit được phép | **Đã chốt qua ADR-0010** |

Contract chung **Đã chốt và đã hiện thực cho slice**:

- JSON UTF-8; UUID trong path/body khi tham chiếu entity.
- Page-number pagination, mặc định 20 bản ghi/trang.
- Error envelope có `code`, `detail`, `correlation_id`; validation có thể bổ sung `errors`, và response mang `X-Correlation-ID`. Server tự tạo correlation ID và không lộ lý do authorization nhạy cảm.
- `PATCH` chỉ nhận allow-list field; server từ chối hoặc bỏ field hệ thống theo contract đã duyệt.
- Response projection được quyết định ở server; client không thể yêu cầu field nhạy cảm tùy ý.
- OpenAPI là contract được version-control nếu ADR stack được chấp nhận.

## 6. Migration và rollback approach

**Đề xuất mục tiêu cho lần migration đầu:**

1. Chỉ tạo schema rỗng và fixture test giả; không import dữ liệu MRE production.
2. Migration additive, có reverse migration khi framework và dữ liệu cho phép.
3. Seed/config cơ cấu thử nghiệm phải được đánh dấu test-only, deterministic và không chứa PII thật.
4. Trước migration có dữ liệu, backup/restore evidence được yêu cầu theo mức rủi ro.
5. Thay đổi enum/status dùng expand–migrate–contract khi đã có dữ liệu; không sửa/xóa code đang được tham chiếu trong một bước.
6. Rollback application không được giả định rollback dữ liệu an toàn; mỗi migration phải ghi rõ trigger, dữ liệu bị ảnh hưởng và cách phục hồi.

**Đã chốt cho slice:** Django migration; migration đầu đã được kiểm tra forward → reverse → forward trên database tạm. **Chưa quyết định:** policy import dữ liệu hiện hữu, retention và data cleanup.

Account provisioning không phải database transaction xuyên MRERP–IdP. ADR-0007 giữ lại mock compensation/orphan-account handling của ADR-0006 khi checkbox tạo account bật; behavior với IdP production vẫn phải được thiết kế lại khi OD-19 được giải quyết.

## 7. Tài liệu liên quan

- [People stories](../product/stories/phase-1-people-foundation.md)
- [People authorization matrix](people-authorization-matrix.md)
- [Data ownership](data-ownership.md)
- [Identity và phân quyền](identity-and-authorization.md)
