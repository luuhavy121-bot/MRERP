# ADR-0016: Đề xuất tích hợp MKTLogin trên máy công ty

- Status: `Proposed`
- Date: `2026-09-03`
- Deciders: `Người sở hữu sản phẩm MRERP — chờ duyệt phương án`
- Related source of truth: `docs/architecture/ecosystem-integration.md`, `docs/architecture/mktlogin-company-device-proposal.md`
- Related open decision: `OD-27, OD-28; phụ thuộc OD-17, OD-11, OD-21 và các cổng Identity liên quan`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người dùng yêu cầu bản vẽ, kiến trúc và phương án; chưa yêu cầu code hoặc chấp nhận kiến trúc.`

## Context

Người dùng muốn giữ MKTLogin trên máy công ty cho khoảng 50–60 nhân sự, tích hợp tài nguyên ASSETCONTROL và tính trước thu hồi khi nghỉ việc. Cây Resource hiện là quan hệ khai báo thủ công theo mô tả người dùng. Gmail là tài khoản thông thường. Nhà cung cấp trả lời gỡ quyền không đóng profile đang mở và không hỗ trợ API gỡ quyền/buộc đóng từ xa như được hỏi.

**Bổ sung bản 02 và làm rõ mới nhất:** người dùng xác nhận đây là phương án công ty họp bàn, không phải tính năng được MKT xác nhận. Dự kiến mua gói công ty, nhân sự đi từ MRERP sang MKTLogin có sẵn mà không tự nhập credential. Khi nghỉ việc, chỉ cắt quyền sử dụng của nhân viên; tài khoản con, Gmail, profile và tài nguyên công ty giữ nguyên. Cơ chế thực thi ở MKTLogin hoặc máy công ty chưa được chọn/kiểm chứng, theo mục 5.6 tài liệu tích hợp. ADR vẫn Proposed; bằng chứng nhà cung cấp về giới hạn profile đang mở giữ nguyên.

**Đã chốt:** ownership và mục tiêu API linkage theo ADR-0014; workspace riêng theo Team theo ADR-0015. **Chưa quyết định:** implementation, contract, quyền, quy trình bàn giao máy và tiêu chí hoàn tất thu hồi.

## Decision drivers

- Tạo liên kết API thực sự mà giữ cách làm việc trên máy công ty.
- Phù hợp quy mô và khả năng vận hành hiện tại; chưa có số liệu dùng đồng thời.
- Phân biệt khai báo, xác minh profile, quyền tài nguyên và khả năng dùng máy.
- Bảo toàn ownership, cây/Grant hiện có và secret boundary.
- Tính trước thu hồi mà không hứa khả năng nhà cung cấp không có.

## Options considered

| Phương án | Ưu điểm | Giới hạn và kết quả đề xuất |
|---|---|---|
| Điều khiển bắt buộc bằng agent trên mọi máy | Có thể khảo sát đóng profile cục bộ theo lệnh | Cần quản trị thiết bị, chống vô hiệu hóa, xử lý offline/mở lại; chưa chọn làm baseline |
| Remote desktop do công ty quản lý | Kiểm soát môi trường tập trung | Thêm hạ tầng, hiệu năng/bản quyền/vận hành cần kiểm chứng; chưa chọn làm baseline |
| Máy công ty + API đọc liên kết + bàn giao/thu hồi có bằng chứng | Giữ workflow, thêm kết nối có phạm vi hẹp và truy vết rõ | Phụ thuộc kỷ luật bàn giao máy và người xử lý; đề xuất ưu tiên |
| Chỉ nối tên/ID bằng tay | Ít triển khai | Không đáp ứng API linkage ADR-0014; không chọn làm kết quả cuối |

## Decision

**Chưa quyết định khi Status còn là Proposed.** Đề xuất phương án máy công ty + API đọc liên kết + vận hành có bằng chứng. Bản thiết kế chi tiết và sơ đồ nằm tại [đề xuất kiến trúc](../architecture/mktlogin-company-device-proposal.md).

Đề xuất điểm kiểm kê cục bộ chỉ đọc chạy theo yêu cầu, trước tiên trên máy Leader nếu scope API đáp ứng, gửi allow-list metadata tới ASSETCONTROL qua kênh xác thực được duyệt. Không chọn credential protocol hoặc mở cổng local. Chưa cài công cụ, gọi API thật hay code.

Đề xuất bổ sung liên kết Employee–thành viên MKTLogin và contract thực thi thay đổi quyền, tách khỏi công cụ kiểm kê. MRERP là điểm vào và nguồn employment; ASSETCONTROL điều phối cấp phát/audit theo contract; nơi thực thi quyền MKTLogin phải được kiểm chứng. Phiên đăng nhập sẵn hoặc nút mở app chưa chứng minh SSO hay ngăn mở app trực tiếp. Cơ chế này chưa được chọn; bản chỉ đọc không được tuyên bố đáp ứng toàn bộ workflow tài khoản con mới.

Liên kết bổ sung biểu thị quyền sử dụng có hiệu lực, không biến tài khoản công ty thành tài sản cá nhân hoặc xóa tài khoản/profile khi kết thúc Grant. Nếu chỉ khóa MRERP mà giữ nguyên cả quyền MKTLogin và quyền dùng máy thì mục tiêu chưa đạt. Bàn giao máy/thao tác quyền thủ công là phương án vận hành giai đoạn đầu; tự động hóa cần cơ chế thực thi và policy được duyệt riêng.

## Remaining open questions

- OD-17: bản ASSETCONTROL MRE và audit schema/workflow.
- OD-27: Resource–profile, Team–workspace, ID, API scope, lỗi, lifecycle và contract.
- OD-27 bổ sung: Employee–thành viên/phạm vi công ty, gói áp dụng, cơ chế không nhập lại credential, chặn truy cập mới và hiệu lực với app/profile đang chạy; đối chiếu phản hồi nhà cung cấp.
- OD-28: quyền sử dụng máy, actor bàn giao/xác nhận, trường hợp ngoại lệ và tài nguyên dùng chung.
- OD-11/OD-21: danh tính/xác thực và secret rotation. OD-01/OD-03/OD-19 giữ hiệu lực cho Identity/login migration liên quan.

## Consequences

- Bản đầu tập trung liên kết và cấp phát, thu hồi là bước sau.
- Gỡ quyền và chấm dứt phiên có kết quả độc lập; xác nhận thủ công không bị gắn nhãn xác minh API.
- Cây cha/con không tự trở thành cây thu hồi; hành động phải có phạm vi Resource/Grant rõ.
- Thu máy giảm khả năng truy cập phiên trên máy đó; không vô hiệu hóa phiên ở nơi khác hoặc lấy lại dữ liệu đã sao chép.

## Security and authorization impact

ASSETCONTROL tiếp tục chỉ cho CEO/Leader theo policy hiện có; không suy rộng quyền action/scope hoặc mở cho IT/HR/Staff. Endpoint nhạy cảm fail-closed, nguồn kiểm kê phải xác thực và có scope, secret/session không rời ranh giới được duyệt. Không tự ghi API MKTLogin/Google hoặc xây điều khiển máy từ xa.

## Data and contract impact

Employee/Team ở MRERP, Resource/Grant/Vault/audit ở ASSETCONTROL, workspace/profile và phiên bên MKTLogin/dịch vụ. Bổ sung metadata liên kết và bằng chứng sau audit; không tạo nguồn Task hoặc Employee thứ hai. Không di chuyển dữ liệu Nhà ZUZU.

## Rollout and rollback

Duyệt thiết kế → khảo sát API thử chỉ đọc → liên kết/cấp phát → pilot một Team → mở rộng → quy trình thu hồi sau khi policy được duyệt. Tắt công cụ kiểm kê giữ nguyên lịch sử và dữ liệu cấp phát; không tự hoàn nguyên quyền đã thay đổi ngoài hệ thống. Chưa có migration thực thi.

## Validation

Theo tiêu chí nghiệm thu và test strategy hiện có; chi tiết các tình huống đề xuất tại mục 13 của bản thiết kế. Không dùng sơ đồ, UI hay response mẫu để tuyên bố đã tích hợp production.

## Documentation updates

Thêm bản thiết kế, bản vẽ, cập nhật integration/open decisions/backlog/roadmap và đường đọc. Chỉ cập nhật thành yêu cầu đã chốt khi có xác nhận tương ứng; ADR này vẫn Proposed.

## Approval record

- Người chấp nhận: Chưa có.
- Ngày chấp nhận: Chưa có.
- Bằng chứng yêu cầu thiết kế: “/plan chưa code, tôi cần một bản vẽ + kiến trúc + phương án đề xuất cho vấn đề này để hợp lí nhất cho cả hệ sinh thái”.
