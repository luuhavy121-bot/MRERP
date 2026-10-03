# Yêu cầu Leave và bảng công hiện tại

Tài liệu này chịu trách nhiệm chính cho phạm vi nghiệp vụ Leave/Attendance đang triển khai. Công thức lương vẫn thuộc [OD-13](../decisions/open-decisions.md) và không được suy ra từ tài liệu này.

## 1. Phạm vi đã chốt

**Đã chốt ngày 29/08/2026 theo xác nhận trực tiếp của người sở hữu sản phẩm và [ADR-0012](../decisions/0012-phase-2-leave-attendance-foundation.md):**

- Nhân sự có thể tạo một đơn xin nghỉ trên MRERP.
- Đơn trở thành ticket để Leader phụ trách Team duyệt hoặc từ chối.
- HR có thể xem và điều chỉnh bảng công của các nhân sự, nhưng không duyệt thay Leader.
- Quy trình duyệt chỉ có một cấp.
- Nhân sự có thể sửa đơn; foundation giới hạn edit khi đơn còn `Chờ duyệt`.
- Công chuẩn loại các ngày lễ Việt Nam được cấu hình theo năm.
- Máy chấm công đã có sẵn của công ty sẽ được tích hợp sau.

## 2. Baseline tạm thời của lần triển khai

**Đề xuất mục tiêu được dùng để giới hạn delivery hiện tại:**

- Đơn nghỉ dùng ngày bắt đầu/kết thúc, buổi sáng/chiều và lý do theo ADR-0021. Cùng ngày/cùng buổi = 0,5 ngày; mặc định sáng→chiều giữ đơn cũ nguyên ngày.
- Một nhân sự không thể có hai đơn `Chờ duyệt` hoặc `Đã duyệt` trùng buổi; hai buổi khác nhau không trùng nhau.
- Chỉ Leader được cấu hình là Leader của Team hiện tại của người gửi mới được review; Leader không tự duyệt đơn của mình.
- Đơn chỉ chuyển `Chờ duyệt → Đã duyệt` hoặc `Chờ duyệt → Từ chối`; requester chỉ sửa khi đang `Chờ duyệt`; chưa có hủy hoặc mở lại.
- `Công chuẩn` bằng ngày thứ Hai–thứ Bảy (cả ngày) trừ ngày lễ Việt Nam đang hoạt động. `Công dự kiến` bằng công chuẩn trừ ngày nghỉ đã duyệt và cộng adjustment HR.
- Adjustment là số ngày nguyên theo nhân sự/tháng, có thể âm hoặc dương, bắt buộc lý do và audit.
- Kết quả này là dữ liệu Attendance tạm thời, không phải bảng lương và không tạo khoản tiền.

## 3. Chưa quyết định

- Loại phép, hạn mức phép, nghỉ có lương/không lương và theo giờ. Nửa ngày đã chốt theo ADR-0021.
- Hủy đơn, duyệt thay, đính kèm và lịch làm việc theo ca.
- Kết nối máy chấm công, khóa kỳ công và quy trình điều chỉnh hồi tố chi tiết. Nhập kết quả Excel được chốt riêng tại mục 6.
- Công thức lương, mức lương, quyền xem lương và kỳ lương.

Các mục trên không xuất hiện trong API hoặc UI của lần triển khai này.

## 6. Nhập bảng công HR từ Excel

**Đã chốt ngày 01/10/2026** theo [ADR-0019](../decisions/0019-attendance-excel-import.md): HR nhập kết quả từ file `.xlsx`, Leader xem Team hiện tại, nhân sự xem bản thân; CEO giữ quyền xem toàn công ty. File nguồn là bản xuất từ HR, không mặc định là bảng đã được chốt.

- Nhận mẫu sheet `Chi Tiet`, từng khối mã/tên nhân viên với ngày, ba cặp Vào/Ra, Trễ/Sớm, Công/T.Giờ/T.Ca1–3. Mỗi file một tháng, tối đa 10 MB/20.000 dòng/500 nhân sự; không nhận công thức.
- Xem trước dữ liệu và lỗi; ghép mã chấm công với Employee. Không tự tạo Employee hoặc ghép theo tên. Lần sau nhớ mapping đã nhập, giữ số 0 đầu mã.
- Chỉ xác nhận được khi mọi mã đã ghép duy nhất và không có lỗi. Import atomic, retry không cộng trùng; thay thế ngày cũ cần chọn rõ. Dữ liệu đổi sau preview trả conflict để tải lại.
- Giữ nguyên kết quả nguồn, phân biệt ô trống và số 0; không tính lại ca, tự trừ phép hay cộng adjustment từ công dự kiến. Tổng tháng cộng giá trị ngày đã nhập; có chỉ báo khi thiếu Công/T.Giờ. Không suy ra ngày chưa nhập là nghỉ.
- Bảng theo nhân sự/ngày có tìm kiếm, lọc Team, chi tiết ngày và lịch sử đợt nhập HR. Snapshot nguồn đã phân tích giữ trong database; không lưu Excel gốc, không đưa dữ liệu thật vào fixture/Git.
- Không bao gồm sửa ô trực tiếp, khóa kỳ, kết nối thiết bị, export hoặc tính lương. Retention/xóa lịch sử và sửa mapping thuộc OD-13 chưa chốt.

## 4. Điều kiện đạt

- Nhân sự chỉ xem và gửi đơn của chính mình, trừ người có capability review Team.
- Leader chỉ xem/review ticket của thành viên trong Team mình lãnh đạo.
- HR xem bảng công toàn công ty nhưng không được suy ra quyền duyệt đơn.
- Server kiểm account/employment, capability, scope và object state.
- Tạo và review đơn có audit; endpoint nhạy cảm có automated tests.
- Bảng công không trả CCCD, địa chỉ, credential hoặc field hồ sơ nhạy cảm.

## 5. Tài liệu liên quan

- [Contract Leave/Attendance](../architecture/leave-attendance-contract.md)
- [Acceptance scenarios](../testing/leave-attendance-acceptance.md)
- [Identity và phân quyền](../architecture/identity-and-authorization.md)

## Bổ sung demo 06/10

**Đã chốt 03/10/2026:** [ADR-0021](../decisions/0021-hr-demo-half-day-and-workflow.md) bổ sung nửa ngày, thứ Bảy cả ngày, từ chối bắt buộc lý do, thông báo đơn mới và lịch nghỉ approved own/Team không có lý do nghỉ. Công dự kiến truy vấn lại theo lịch mới cả với tháng cũ, không sửa kết quả công thực tế đã nhập. Quyền duyệt vẫn một cấp Leader; HR không được duyệt thay. Implementation chờ nghiệm thu sản phẩm; mốc 06/10 là demo local.
