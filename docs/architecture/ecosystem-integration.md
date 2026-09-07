# Tích hợp hệ sinh thái

Tài liệu này là source of truth chịu trách nhiệm chính cho cách các product giao tiếp và hành vi khi integration lỗi. Bản đọc ngắn nằm tại [03 — Thiết kế kỹ thuật](../03-thiet-ke-ky-thuat.md).

## 1. Nguyên tắc

**Đã chốt.** Một hệ sinh thái tích hợp cần SSO, authorization server-side, contract dữ liệu và shared identifier. Deep link đơn thuần không phải tích hợp đầy đủ.

Không product nào đọc database của product khác. Product nguồn chỉ chia sẻ dữ liệu tối thiểu theo quyền.

## 2. Chọn cơ chế giao tiếp

Đây là **Đề xuất mục tiêu cần được cụ thể hóa bằng contract/ADR**:

| Cơ chế | Khi dùng | Ví dụ |
|---|---|---|
| Deep link | Điều hướng đến đúng màn hình | MRERP mở đúng resource trong ASSETCONTROL |
| REST/OpenAPI | Cần phản hồi ngay hoặc command rõ | CRM tạo Task liên quan Order qua MRERP API |
| Event/queue | Thông báo thay đổi không cần phản hồi đồng bộ | CRM phát sự kiện đạt doanh số |
| Snapshot/read model | Dashboard/report cần tồn tại khi source lỗi | MRERP giữ aggregate CRM gần nhất |
| Đồng bộ định kỳ | Chấp nhận độ trễ vài phút | Cập nhật snapshot nhân sự ở product đích |

## 3. Dashboard integration

**Đã chốt.**

```text
CRM / ASSETCONTROL
        │
        │ event hoặc đồng bộ định kỳ
        ▼
MRERP snapshot/read model
        │
        ▼
Dashboard
```

Dashboard không gọi trực tiếp source product trong request tải trang. Khi source lỗi, Dashboard dùng snapshot gần nhất và báo stale state.

**Chưa quyết định.** Stale threshold, timeout, retry và SLA.

## 4. ASSETCONTROL integration

**Đã chốt về yêu cầu:**

- Nhận `employee_uuid` và snapshot tối thiểu từ MRERP.
- Tự kiểm authorization ở server.
- Không gửi Vault content/secret sang MRERP.
- Migration login phải dual-run, có UUID mapping, rollback và emergency access.

**Đề xuất mục tiêu.** SSO qua OIDC flow riêng cho ASSETCONTROL.

**Chưa quyết định.** Break-glass, thời gian giữ login cũ và quan hệ deployment/tenant ZUZU–MRE.

## 5. MKTLogin integration

**Đã chốt qua ADR-0014:**

- Công ty dùng MKTLogin; MKT City không thuộc phạm vi hiện tại.
- MKTLogin tiếp tục là hệ thống bên ngoài vận hành tài nguyên thực tế; không clone đầy đủ vào MRERP hoặc ASSETCONTROL.
- ASSETCONTROL sở hữu catalog Resource, Grant, Vault và audit. Đích cuối là Resource ASSETCONTROL liên kết bằng định danh ổn định với resource tương ứng trong MKTLogin qua API.
- MRERP chỉ cung cấp Employee/Team/capability theo contract và không nhận cookie, session, password hoặc API credential MKTLogin.
- Một deep link hoặc tên nhập tay giống nhau không đủ được coi là resource linkage đã hoàn tất.

**Chưa quyết định theo OD-27:**

- Resource MKTLogin nào cần mapping và identifier nào ổn định.
- API authentication, secret storage/rotation và trust boundary.
- Đồng bộ một chiều, hai chiều hay command theo use case; tần suất và reconciliation.
- Ai được link, unlink, sync, cấp hoặc thu hồi; object/field rule và audit chi tiết.
- Rate limit, timeout, retry, idempotency, degraded mode và rollback.
- MKTLogin có hỗ trợ SSO cho người dùng hay không; việc có API không tự động đồng nghĩa có SSO.

### 5.1 Thông tin API cần người sở hữu sản phẩm cung cấp

**Đã chốt về yêu cầu chuẩn bị:** người sở hữu sản phẩm yêu cầu cập nhật mục tiêu MKTLogin và yêu cầu cung cấp thông tin API để chuẩn bị triển khai. Mục tiêu đã có trong ADR-0014; yêu cầu này không tự phê duyệt contract hoặc thao tác ghi qua API thật.

**Hiện trạng ngày 03/09/2026:** đã nhận bản OpenAPI và ảnh mục **Tài Liệu API** trong ứng dụng MKTLogin từ người sở hữu sản phẩm. Kết quả đọc tài liệu nằm ở mục 5.3; chưa gọi API thật hoặc kiểm chứng phạm vi quyền thực tế. Việc có endpoint trong tài liệu không chứng minh gói/tài khoản của mọi nhân viên đều sử dụng được.

Thông tin đã nhận và còn cần bổ sung:

1. **Đã nhận:** bản OpenAPI 3.0.0, phiên bản tài liệu 1.0.0, lấy từ mục Tài Liệu API trong MKTLogin theo xác nhận và ảnh người dùng cung cấp.
2. **Quan sát từ ảnh:** ứng dụng hiển thị phiên bản 2.1.3; workspace đang xem hiển thị gói Free. Chưa xác nhận mọi máy/workspace công ty dùng cùng phiên bản/gói hoặc các API đã được kích hoạt đầy đủ.
3. **Người dùng đã xác nhận:** mỗi máy cài ứng dụng MKTLogin riêng và có phân quyền theo Team. **Đã chốt bổ sung qua [ADR-0015](../decisions/0015-mktlogin-workspace-per-team.md):** các Team sẽ có workspace riêng. Chưa xác nhận workspace thực tế, quy tắc số lượng workspace mỗi Team hoặc phạm vi quyền API. Tài liệu công bố server `http://localhost:4980`; cách hệ thống tích hợp kết nối tới các máy vẫn chưa kiểm chứng. Máy cài ứng dụng và workspace là hai khái niệm khác nhau; chưa tự chọn cách mở cổng hoặc công khai API máy cá nhân.
4. Loại tài nguyên muốn liên kết đầu tiên và một ví dụ đã ẩn dữ liệu nhạy cảm; ví dụ browser profile là môi trường trình duyệt riêng nhớ trạng thái đăng nhập, chưa mặc định đây là loại tài nguyên được chọn.
5. Có môi trường thử hoặc tài nguyên thử riêng hay không. Chỉ cần thông tin về cách cấp quyền thử ở bước này, không gửi API key, mật khẩu, cookie, token hoặc nội dung Vault vào chat/tài liệu/Git.

### 5.2 Nhóm API cần kiểm kê để triển khai

**Đề xuất mục tiêu.** Bắt đầu bằng đọc và xác minh liên kết cho một loại Resource sau khi phạm vi, contract và quyền được duyệt. Tên đường dẫn, HTTP method và field thực tế chỉ được ghi sau khi đối chiếu tài liệu chính thức; không tự đặt endpoint của MKTLogin.

| Nhóm khả năng cần tài liệu | Mục đích | Phạm vi kiểm kê |
|---|---|---|
| Xác thực kết nối, quyền API và thông tin phiên bản | Biết hệ thống được phép gọi gì, cách cấp/thay/thu hồi credential và gói nào hỗ trợ | Cần cho kết nối đầu tiên; chưa chọn cơ chế xác thực |
| Đọc danh sách tài nguyên, phân trang và bộ lọc nếu có | Tìm đối tượng thật để liên kết với Resource ASSETCONTROL | Đề xuất cho bản tích hợp đầu tiên |
| Đọc chi tiết theo định danh ổn định hoặc khả năng truy vấn tương đương | Kiểm tra đúng đối tượng, metadata được phép và trường hợp không còn tồn tại/không đủ quyền | Cần chứng minh mục tiêu liên kết; không dựa vào tên hiển thị |
| Mã lỗi, giới hạn số lần gọi và quy tắc tương thích phiên bản | Thiết kế timeout/retry, xử lý API gián đoạn và dữ liệu cũ | Cần trong tài liệu kết nối; có thể không phải API riêng |
| Đọc thay đổi, thời điểm cập nhật hoặc thông báo thay đổi từ MKTLogin nếu có | Phát hiện dữ liệu lệch mà không luôn đọc lại toàn bộ | Chưa chọn cơ chế hoặc tần suất đồng bộ |
| Đọc tài khoản thành viên, phạm vi công ty/workspace và quyền thực tế nếu có | Liên kết Employee với thành viên MKTLogin; so sánh Grant với quyền thực tế | Cần kiểm kê cho workflow tài khoản con mới ở mục 5.6; chưa có endpoint tương ứng trong OpenAPI đã nhận |
| Cấp, bàn giao, thu hồi quyền và kiểm tra kết quả nếu có | Thực hiện nghiệp vụ chuyển Team/nghỉ việc có kiểm chứng | Phạm vi tương lai chưa được duyệt; không suy ra thành công từ việc khóa account MRERP |
| Mở đúng môi trường, đăng nhập chung hoặc quản lý phiên nếu có | Đánh giá trải nghiệm chuyển sang MKTLogin và giới hạn thu hồi phiên | Không bắt buộc cho khảo sát đọc profile; phải làm rõ để đáp ứng đầy đủ workflow mới ở mục 5.6 |

API chia sẻ Employee/Team/employment/capability từ MRERP và API Resource/Grant của ASSETCONTROL cũng cần contract được duyệt khi triển khai luồng liên quan. Đây là contract nội bộ phải thiết kế/kiểm tra tại product sở hữu dữ liệu, không phải API yêu cầu nhà cung cấp MKTLogin cung cấp. ASSETCONTROL dành cho MRE còn phụ thuộc OD-17 về codebase/deployment; không lấy dữ liệu hoặc secret Nhà ZUZU để làm mẫu.

Kết quả kiểm kê phải ghi nguồn tài liệu, phiên bản/gói, khả năng được hỗ trợ hoặc chưa rõ, định danh/field được phép và các khoảng trống cần nhà cung cấp trả lời. Sau đó cập nhật contract/ADR cho phần được duyệt theo OD-27; không tự chuyển backlog sang `Ready`. Tiêu chí đạt/không đạt tiếp tục theo [tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md) và [test strategy](../testing/test-strategy.md).

### 5.3 Kết quả đọc tài liệu MKTLogin được cung cấp

**Bằng chứng tài liệu, chưa phải kết quả chạy thực tế:** bản JSON đọc được và mô tả 12 thao tác. Ảnh cho thấy tài liệu được phục vụ tại `http://localhost:4980/v3/api-docs` trong MKTLogin 2.1.3; phiên bản tài liệu 1.0.0 khác với phiên bản ứng dụng.

| Nhóm | Thao tác được mô tả |
|---|---|
| Workspace | `GET /api/v1/workspaces` |
| Profile | `GET /api/v1/profiles`; `GET`, `PUT`, `DELETE /api/v1/profiles/{id}` |
| Mở/đóng Profile | `GET /api/v1/profiles/{id}/open`; `GET /api/v1/profiles/{id}/close` |
| Task MKTLogin | `GET /api/v1/tasks`; `GET /api/v1/tasks/{taskId}/start`; `GET /api/v1/tasks/{taskId}/stop`; `POST /api/v1/tasks/status` |
| Workflow | `POST /api/v1/workflows/run` |

Ba API đọc workspace, danh sách profile và chi tiết profile là cơ sở cho **đề xuất** liên kết Profile đầu tiên; người dùng chưa chốt loại Resource. Task trong tài liệu này thuộc MKTLogin, không tự ánh xạ thành Task nghiệp vụ MRERP. Các lệnh mở/đóng profile và bắt đầu/dừng Task có tác động dù dùng `GET`; không được gọi trong đợt kiểm tra chỉ đọc.

Các khoảng trống cần xử lý trong OD-27:

- `localhost` trỏ về máy gọi API. ASSETCONTROL trên máy chủ không thể dùng nguyên địa chỉ đó để truy cập ứng dụng trên máy nhân viên. Cách kết nối, nhận diện máy, dữ liệu trùng giữa các máy và hành vi khi máy/ứng dụng tắt còn **Chưa quyết định**; chưa chọn agent cục bộ, gateway hoặc mở cổng từ xa.
- API danh sách/chi tiết Profile có `workspace_id`; nếu bỏ trống, tài liệu nói dùng workspace đang chọn trong ứng dụng. Cần kiểm chứng ID ổn định/duy nhất trong phạm vi nào, đồng thời thiết kế contract không liên kết nhầm khi người dùng đổi workspace. API đóng Profile không khai báo workspace; cách phân biệt đối tượng chưa rõ.
- Các operation ghi `security: []`, không có `securitySchemes`. Chỉ kết luận tài liệu chưa mô tả yêu cầu xác thực; chưa kết luận API thực tế không cần đăng nhập hoặc tự áp dụng đúng quyền Team. Cần kiểm tra phạm vi theo tài khoản/workspace và hành vi khi yêu cầu tài nguyên ngoài quyền.
- Chỉ có response 200; schema trả về sơ lược, ví dụ danh sách rỗng, thiếu quy tắc lỗi/phân trang đầy đủ/giới hạn gọi. Ví dụ chi tiết Profile chứa field mật khẩu proxy; lệnh mở trả thông tin điều khiển trình duyệt. Phải xác định allow-list metadata, không đưa secret hoặc thông tin điều khiển phiên vào MRERP, log hoặc audit.
- Một số response thiếu `description`, path parameter `taskId` bị ghi không bắt buộc, ví dụ chi tiết/mở Profile là chuỗi chứa JSON lỗi cú pháp. Cần đối chiếu response thực tế đã lọc dữ liệu nhạy cảm trước khi dùng tài liệu để sinh client/contract test.
- Chưa thấy API quản lý thành viên, đọc/cấp/bàn giao/thu hồi quyền, SSO hoặc thông báo thay đổi trong bản được cung cấp. Người dùng xác nhận có phân quyền theo Team không đồng nghĩa các thao tác quản lý quyền đó đã có API. Đóng Profile không chứng minh đã thu hồi quyền sử dụng.

### 5.4 Giới hạn thu hồi được nhà cung cấp trả lời

**Bằng chứng do người dùng chuyển tiếp ngày 03/09/2026, chưa kiểm thử độc lập:** khi hỏi về hiệu lực gỡ quyền với hồ sơ đang mở, nhà cung cấp trả lời: “dạ không bị đóng ạ, thành viên vẫn đang mở hồ sơ đó thì vẫn dùng bình thường ạ”.

Kết luận trong phạm vi phản hồi: thao tác gỡ quyền được hỏi không đóng hồ sơ đang mở và không chấm dứt khả năng sử dụng phiên đó. Không dùng việc gỡ quyền MKTLogin làm bằng chứng nhân viên đã mất toàn bộ quyền truy cập tài nguyên. Điều này không phủ nhận giá trị liên kết profile hoặc quản lý cấp phát theo ADR-0014.

**Phản hồi bổ sung do người dùng chuyển tiếp:** khi được hỏi “Có API gỡ quyền và buộc đóng profile trên máy thành viên không?”, nhà cung cấp trả lời không thực hiện được vì khác máy. Không thiết kế dựa trên khả năng gỡ quyền/buộc đóng từ xa qua API được hỏi. Đây là phản hồi nhà cung cấp, chưa phải kiểm thử API độc lập; cũng không chứng minh mọi thao tác quyền khác đều không có API.

**Chưa kiểm chứng:** khả năng mở lại sau khi đóng, hành vi offline/dữ liệu đã tải về, định danh/phạm vi quyền và đồng bộ giữa các máy. Lệnh đóng cục bộ trong tài liệu không trở thành lệnh đóng trên máy thành viên từ máy chủ.

**Đề xuất mục tiêu, chưa phải policy được duyệt:** contract thu hồi cần phân biệt kết quả gỡ quyền với kết quả chấm dứt phiên; nếu không có bằng chứng phiên đã bị vô hiệu hóa thì trạng thái phải thể hiện chưa xác minh, không báo hoàn tất thu hồi toàn bộ. Phương thức xử lý phiên tại dịch vụ đích hoặc trên thiết bị thuộc OD-27/OD-28 và cần đánh giá trước khi hiện thực. Theo yêu cầu người dùng, hiện chỉ tính trước bước cuối, chưa triển khai thu hồi thật.

### 5.5 Thiết kế theo phương án máy công ty

**Căn cứ mới từ người dùng:** giữ MKTLogin trên máy công ty cho khoảng 50–60 nhân sự; Gmail là tài khoản thông thường. Cây cha/con ASSETCONTROL hiện do người quản lý khai báo, chưa phải quan hệ được kiểm chứng tại dịch vụ nguồn. Đây là mô tả người dùng, chưa phải kết quả audit ASSETCONTROL hoặc kiểm kê thiết bị.

[Bản vẽ và kiến trúc đề xuất](mktlogin-company-device-proposal.md) cùng [ADR-0016](../decisions/0016-mktlogin-company-device-integration-proposal.md) giữ trạng thái **Proposed**: kết nối chỉ đọc để xác minh workspace/profile, liên kết Resource/Grant và ghi nhận bằng chứng; về sau phối hợp gỡ quyền, bàn giao máy và rà soát quyền/phiên tại dịch vụ ngoài. Điểm kiểm kê cục bộ trên máy có scope phù hợp là đề xuất, chưa chọn cơ chế xác thực hoặc cài đặt.

Không biến cây khai báo thành cây thu hồi tự động. Việc công ty sở hữu máy không chứng minh đã cắt quyền sử dụng máy, phiên ở thiết bị khác hoặc dữ liệu đã được sao chép. OD-28 bổ sung policy bàn giao và bằng chứng cần duyệt. Không code trong lượt yêu cầu thiết kế; mục tiêu ADR-0014/0015 giữ nguyên, implementation Phase 4 vẫn Refining.

### 5.6 Bổ sung từ người dùng: gói công ty và tài khoản thành viên

**Làm rõ mới nhất từ người dùng ngày 03/09/2026:** workflow này là phương án công ty họp bàn và nghĩ ra, **không phải tính năng hoặc cơ chế MKT đã xác nhận**. Công ty dự kiến mua một gói MKTLogin, nhân sự dùng tài khoản con trong tài khoản tổng. Mục tiêu là nhân sự vào MRERP, nhận thông tin rồi dùng MKTLogin có sẵn trên máy mà không tự nhập tài khoản/mật khẩu. Khi nhân viên nghỉ việc, chỉ chấm dứt quyền sử dụng của nhân viên đó; tài khoản MKTLogin, Gmail, profile và tài nguyên công ty giữ nguyên.

**Đã rõ về ý định nghiệp vụ; phương án kỹ thuật vẫn Proposed/Chưa quyết định.** Chưa có tài liệu cơ chế hoặc kiểm thử tích hợp cho phần MRERP tác động tới MKTLogin; chưa biết tên gói, cách chuẩn bị phiên trên máy, API quản lý thành viên/thu hồi phiên hoặc hỗ trợ SSO. OpenAPI đã nhận chỉ mô tả các thao tác ở mục 5.3, chưa có contract tài khoản/thành viên/SSO này. Việc chỉ cài app hoặc đăng nhập sẵn chưa tạo quan hệ phụ thuộc giữa phiên MKTLogin và account MRERP.

Phản hồi nhà cung cấp ở mục 5.4 vẫn là bằng chứng hiện có: gỡ quyền không đóng profile đang mở và API gỡ quyền/buộc đóng từ xa được hỏi không thực hiện được. Mục tiêu nội bộ không thay thế bằng chứng này. Từ chối đăng nhập mới, chặn app đã đăng nhập và xử lý profile đang chạy cần được kiểm tra riêng; chưa cam kết khóa MRERP tự đạt cả ba.

**Tác động thiết kế trong ADR-0016 Proposed:** bổ sung việc cấp quyền sử dụng cho `Employee UUID ↔ định danh tài khoản/thành viên MKTLogin trong phạm vi công ty`, bên cạnh Team–workspace và Resource–profile. Đây là liên kết có hiệu lực và lịch sử; chấm dứt cấp phát không xóa tài khoản/profile. Tài khoản MKTLogin là danh tính dùng ứng dụng; Gmail Resource là tài khoản được sử dụng bên trong profile, không phải khóa để định danh nhân sự. Không mặc định tài khoản con thuộc sở hữu cá nhân hoặc phải bị xóa khi người dùng nghỉ.

- MRERP là điểm vào và nguồn trạng thái làm việc. Chặn quyền nhạy cảm tại server MRERP không tự thay đổi phiên bên MKTLogin.
- ASSETCONTROL tiếp tục sở hữu cấp phát/liên kết/audit; đề xuất phối hợp yêu cầu thay đổi quyền tới MKTLogin qua contract được hỗ trợ. Cơ chế xác thực, nơi thực thi và quyền quản trị còn phải duyệt, không chọn giao thức trước tài liệu.
- Phải có nơi thực thi từ chối truy cập: quyền thực tế MKTLogin được hỗ trợ, hoặc quyền sử dụng máy/phiên làm việc do công ty kiểm soát theo policy được duyệt. Ẩn nút/mở app từ MRERP không đủ; cần thử mở trực tiếp app khi không đi qua MRERP. Nếu chỉ khóa MRERP và giữ nguyên cả quyền MKTLogin lẫn quyền dùng máy, mục tiêu chặn MKTLogin chưa được đáp ứng.
- Sẵn ứng dụng, sẵn phiên đăng nhập và SSO là ba trạng thái khác nhau. Nếu chỉ là đăng nhập sẵn thì chưa chứng minh phiên đó phụ thuộc quyền MRERP; không chia sẻ tài khoản tổng cho nhân viên hoặc đưa mật khẩu vào URL/MRERP.
- Tách kết quả chặn đăng nhập/mở mới, quyền mở profile trong app đã đăng nhập, và profile đang chạy; độ trễ, offline, app tắt và lỗi kết nối phải có hành vi đã kiểm chứng.

**Công việc khảo sát tiếp theo:** hỏi nhà cung cấp khả năng hỗ trợ đăng nhập và thu hồi quyền sử dụng mà giữ tài khoản/profile; xác minh gói/phiên bản và hiệu lực với phiên đang mở. Đây là thông tin cần đi tìm, không phải tài liệu người dùng đã có hoặc MKT đã cam kết. Đồng thời kiểm kê cách công ty kiểm soát quyền dùng máy nếu chọn cách thực thi ở thiết bị. Không yêu cầu credential. OD-27 giữ contract, OD-28 giữ policy bàn giao máy và xử lý tồn dư; chưa chọn quản trị thiết bị, agent hoặc SSO.

## 6. MREKANBAN integration

**Đã chốt.** MRERP là Task source dài hạn; MREKANBAN tham chiếu `task_uuid` và không tạo Task source cạnh tranh.

**Chưa quyết định.** Giữ MREKANBAN làm client/view chuyên sâu hay retire sau migration.

## 7. CRM integration

**Đã chốt về ownership:** CRM sở hữu Customer/Order/Product/Channel/FFM; MRERP sở hữu Task và Rewards.

- CRM có thể tạo Task qua MRERP contract.
- CRM phát event achievement; MRERP Rewards quyết định sao.
- CRM đồng bộ aggregate vào MRERP read model cho Dashboard/report.
- Worker adapter/import/report không giữ web request.

Contract endpoint/event cụ thể là **Đề xuất mục tiêu cần ADR/versioning**.

## 8. Contract rules

**Đã chốt về nguyên tắc:**

- Dùng UUID ổn định.
- Contract có version và compatibility rule.
- Snapshot không trở thành source of truth.
- Field/data được tối thiểu hóa theo authorization.
- Integration failure không làm hỏng product khác.

## 9. Service security

**Chưa quyết định.** Service account, token format, rotation và trust boundary cụ thể. Không dùng shared static production token.

## 10. Failure contract tối thiểu

**Đã chốt về nguyên tắc:** integration failure không được làm hỏng product khác.

| Tình huống | Hành vi bắt buộc | Chi tiết chưa chốt |
|---|---|---|
| CRM/ASSETCONTROL không phản hồi khi Dashboard tải | Đọc snapshot gần nhất; không gọi source trong request | Timeout, stale threshold, SLA |
| Event xử lý lỗi | Không mất lỗi âm thầm; phải có failure visibility | Queue/tool, retry count, dead-letter policy |
| Snapshot chưa từng đồng bộ | Hiển thị trạng thái chưa có dữ liệu, không giả số liệu | Copy/UI wording cuối cùng |
| Contract không tương thích | Từ chối fail-closed hoặc giữ version tương thích | Compatibility window và deprecation policy |
| MKTLogin API không phản hồi | ASSETCONTROL không giả trạng thái đã đồng bộ; giữ trạng thái gần nhất kèm thời điểm và cảnh báo | Timeout, retry, reconciliation và SLA theo OD-27 |

## 11. Tài liệu liên quan

- [Data ownership](data-ownership.md)
- [Identity và phân quyền](identity-and-authorization.md)
- [Deployment](../operations/deployment.md)
- [Open decisions](../decisions/open-decisions.md)
