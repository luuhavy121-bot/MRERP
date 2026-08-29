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

- Đơn nghỉ dùng ngày bắt đầu, ngày kết thúc và lý do; chỉ hỗ trợ nguyên ngày.
- Một nhân sự không thể có hai đơn `Chờ duyệt` hoặc `Đã duyệt` trùng ngày.
- Chỉ Leader được cấu hình là Leader của Team hiện tại của người gửi mới được review; Leader không tự duyệt đơn của mình.
- Đơn chỉ chuyển `Chờ duyệt → Đã duyệt` hoặc `Chờ duyệt → Từ chối`; requester chỉ sửa khi đang `Chờ duyệt`; chưa có hủy hoặc mở lại.
- `Công chuẩn` bằng ngày thứ Hai–thứ Sáu trừ ngày lễ Việt Nam đang hoạt động. `Công dự kiến` bằng công chuẩn trừ ngày nghỉ đã duyệt và cộng adjustment HR.
- Adjustment là số ngày nguyên theo nhân sự/tháng, có thể âm hoặc dương, bắt buộc lý do và audit.
- Kết quả này là dữ liệu Attendance tạm thời, không phải bảng lương và không tạo khoản tiền.

## 3. Chưa quyết định

- Loại phép, hạn mức phép, nghỉ có lương/không lương và nửa ngày/theo giờ.
- Hủy đơn, duyệt thay, đính kèm và lịch làm việc theo ca.
- Chấm công thực tế/máy chấm công, khóa kỳ công và quy trình điều chỉnh hồi tố chi tiết.
- Công thức lương, mức lương, quyền xem lương và kỳ lương.

Các mục trên không xuất hiện trong API hoặc UI của lần triển khai này.

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
