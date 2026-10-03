# ADR-0019: Nhập bảng chấm công Excel do HR xuất

- Status: `Accepted`
- Date: `2026-10-01`
- Deciders: Người sở hữu sản phẩm MRERP
- Related open decision: OD-13 (giải quyết phần nhập kết quả, không chốt công thức công/lương)
- Approval record: Người dùng cung cấp mẫu Excel, xác nhận đây là bảng HR xuất và đồng ý nhập nguyên kết quả; HR nhập, Leader xem Team, nhân sự xem bản thân.

## Decision

MRERP sở hữu bản ghi nhập trong `leave_domain`. Tách kết quả Excel khỏi projection công dự kiến theo ADR-0012. Không tính lại công, trừ phép, làm tròn giờ hoặc suy ra ca. Không kết nối thiết bị.

HR tải `.xlsx` theo mẫu Chi Tiet → xem trước → ghép mã chấm công với Employee → xác nhận. Giữ mã dạng chuỗi có số 0 đầu. Mapping được nhớ sau khi nhập thành công; không ghép tên tự động. Bản đầu không đổi mapping đã lưu; sửa mapping là phạm vi cần refinement để tránh gán lại lịch sử cho sai người.

Mỗi Employee/ngày chỉ có một kết quả hiện hành. Khi ngày đã tồn tại, HR phải chọn rõ thay thế; ghi nhật ký và giữ snapshot nguồn ở các đợt nhập cũ. Khóa transaction và kiểm tra dữ liệu thay đổi kể từ xem trước; gặp xung đột yêu cầu xem trước lại. Không xóa ngày vắng khỏi file mới. Toàn bộ đợt nhập thành công hoặc không ghi gì.

Không lưu file Excel gốc hoặc đưa file người dùng vào Git. Lưu tên file, SHA-256, snapshot đã phân tích, actor và thời gian để truy vết. Chỉ HR có capability nhập/xem snapshot và lịch sử; CEO giữ quyền xem bảng toàn công ty hiện có. Leader đọc Team hiện tại mình lãnh đạo, nhân sự đọc bản thân. Server kiểm account/employment và capability mọi lần gọi.

## Trade-offs và giới hạn

Hỗ trợ một định dạng cụ thể thay vì bộ ánh xạ cột tùy ý. Kết quả nguồn có thể chưa được HR chốt; UI ghi rõ “Theo file HR”, không tuyên bố công đã duyệt. Không có sửa từng ô, khóa kỳ, payroll, export hoặc tự chấm từ giờ vào/ra. Retention/xóa lịch sử và quy trình sửa mapping giữ trạng thái Chưa quyết định ở OD-13.

## Migration và kiểm chứng

Migration chỉ thêm bảng/permission, không nạp mẫu thật hoặc sửa công dự kiến cũ. Rollback ứng dụng giữ schema/dữ liệu; không reverse migration khi đã nhập dữ liệu cần giữ. Test parser, quyền/scope, dữ liệu thiếu/sai, số 0 đầu, trùng lặp, transaction, nhập lại và conflict. Kiểm chứng luồng HR → Leader → Staff bằng fixture tổng hợp.
