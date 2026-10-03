# Tuyển dụng công khai và đánh giá KPI

Source of truth cho phần mở rộng theo ADR-0017 và ADR-0018. Trạng thái: Implementation hoàn tất / Chờ nghiệm thu sản phẩm. Ưu tiên trước ASSETCONTROL–MKTLogin; tích hợp đó giữ trạng thái thiết kế.

## Tuyển dụng

Leader tạo/sửa bản nháp trong Team, gửi duyệt. HR/CEO cũng dùng draft → pending → approved/rejected; approved tự xuất bản. Nội dung bắt buộc khi gửi: vị trí, số lượng, địa điểm, hình thức làm việc, mô tả, yêu cầu, quyền lợi, hạn nộp và lý do nội bộ. Nội dung đã gửi không sửa trực tiếp. Tin hết hạn không nhận hồ sơ; Leader/HR/CEO đóng tin. Tin legacy không có published_at vẫn nội bộ.

Public application: họ tên, ít nhất email hoặc điện thoại, CV PDF/DOC/DOCX tối đa 10 MB, lời giới thiệu tùy chọn và consent bắt buộc. Không trả Candidate UUID hoặc thông tin trùng hồ sơ. CV lưu private; public route không có endpoint tải. Candidate rejected ẩn danh sau sáu tháng, xóa CV và introduction.

Leader có liên hệ/CV và pipeline trong Team đang lãnh đạo; HR/CEO toàn công ty; Staff không có Candidate API. Convert Employee chỉ HR/CEO. Public DTO không trả lý do nội bộ hoặc requester.

**Đã chốt 03/10/2026 theo [ADR-0022](../decisions/0022-short-recruitment-pipeline.md):** pipeline gọn `Mới → Sàng lọc → Phỏng vấn → Đã tuyển`, có thể `Từ chối` từ các bước đang xử lý. Không có bước Đề nghị mới. Nhu cầu nằm trong tin tuyển, không có quy trình nhu cầu/kế hoạch riêng. `Kế hoạch sử dụng nhân sự` là nội dung nội bộ tùy chọn trong bản nháp: dự kiến người này làm việc gì, phụ trách phần nào và mục tiêu gì; không xuất hiện trên tin công khai. Việc HR/CEO duyệt và xuất bản tin giữ nguyên.

## Đánh giá

Mỗi Employee một phiếu mỗi tháng; probation/official đủ điều kiện, không tự đánh giá. Leader nhập KPI, mô tả, weight, completion và comment. Tổng weight 100, có completion từng KPI và nhận xét tổng mới được chốt. Điểm = tổng(weight × completion)/100, Decimal HALF_UP hai số.

Draft chỉ Leader Team chỉnh; finalized nhân sự nhìn thấy và acknowledge kèm phản hồi tùy chọn. HR/CEO đọc toàn công ty, mở lại bắt buộc lý do. Reopen giữ snapshot cũ, xóa điểm/feedback hiện hành và yêu cầu chốt/xác nhận mới. Snapshot giữ lịch sử phản hồi. Không sửa snapshot. Mọi ghi phiếu dùng version, stale trả 409. Staff không xem draft; HR/CEO không chấm nếu không có capability Leader và scope được cấp riêng.

Team lưu trên phiếu là lịch sử; quyền Leader yêu cầu Employee vẫn ở Team đó. Task theo tháng hạn hoàn thành chỉ tham khảo, giao với ACL Task hiện hành. Không suy rộng quyền xem Task cho HR.

## Ngoài phạm vi

Payroll, tự chấm từ Task, thưởng/thăng chức, đăng Facebook/TopCV, email/SMS, máy chấm công và MKTLogin.

## Luồng Leader chọn nhân sự

Leader thấy danh sách toàn bộ nhân sự đủ điều kiện trong Team phụ trách kể cả khi chưa có phiếu tháng. Có tìm theo tên/mã và lọc Team. Chọn nhân sự mở ngay mẫu KPI; chỉ tạo phiếu ở lần Lưu nháp/Chốt đầu tiên. CEO/HR vẫn chỉ xem và mở lại.

### Bố cục đánh giá đã duyệt

Phương án B dùng bảng nhân sự theo Team với các cột nhân sự, trạng thái, điểm và thao tác; thanh điều khiển có tìm tên/mã, Team, tháng và trạng thái, kèm dòng tổng hợp tiến độ. Trên desktop, chọn một người mở khung đánh giá bên phải và vẫn thấy bảng bên trái. Trên màn hình hẹp, mỗi lần chỉ hiện bảng hoặc khung đánh giá; đóng khung để về bảng.

KPI được nhập theo dòng gồm tên, trọng số, mức hoàn thành và điểm đóng góp; mở chi tiết để sửa mô tả và nhận xét. Tổng trọng số và “Điểm tạm tính” giúp Leader kiểm tra bản nháp; “Điểm đã chốt” lấy từ kết quả server, không thay quy tắc tính điểm hoặc điều kiện chốt. Nhận xét tổng kết, Công việc tham khảo và lịch sử nằm trong khung đánh giá; nút Lưu nháp/Chốt ở cuối khung. Thay đổi chưa lưu có cảnh báo trước khi đóng hoặc chuyển lựa chọn làm mất nội dung.

Bố cục này giữ nguyên scope, quyền xác nhận của nhân sự và mở lại của HR/CEO đã mô tả ở trên. Phê duyệt giao diện đánh giá không bao gồm hợp nhất Ghi nhận vào màn hình này và không thay thế nghiệm thu sản phẩm.

## Nâng cấp demo 06/10/2026

**Đã chốt theo [ADR-0021](../decisions/0021-hr-demo-half-day-and-workflow.md):** KPI do Leader tự đặt, không triển khai bộ mẫu công ty; sao chép tên/mô tả/trọng số tháng trước của cùng nhân sự trong scope, completion và comment được bỏ trống, chỉ lưu khi Leader chọn lưu/chốt. Thêm lịch sử các tháng và thông báo chốt/mở lại/xác nhận.

Tuyển dụng có xem trước nội dung công khai, tìm/lọc vị trí/Team/trạng thái/ứng viên, lịch sử pipeline và lịch phỏng vấn đơn giản. Lịch dùng thời điểm có timezone, UI nhập theo múi giờ thiết bị; tên người phụ trách nhập tự do, không cấp thêm quyền. Người quản lý pipeline sửa lịch/ghi chú khi hồ sơ chưa kết thúc, có version chống ghi đè; audit không lưu nội dung ghi chú. Lịch/ghi chú được xóa khi ẩn danh sáu tháng. Chỉ notification nội bộ, không email/SMS/Calendar connector. Careers vẫn local, chưa mở Internet.
