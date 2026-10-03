# ADR-0021: Hoàn thiện ba luồng HR cho demo 06/10/2026

- Status: `Accepted`
- Date: `2026-10-03`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/product/hr-expansion-requirements.md`, `docs/product/leave-attendance-requirements.md`
- Related open decision: `OD-13 (giải quyết nửa ngày và lịch làm thứ Bảy; các phần còn lại vẫn mở)`
- Supersedes: `ADR-0012 chỉ ở giới hạn nguyên ngày và công chuẩn thứ Hai–thứ Sáu`
- Superseded by: `Không có`
- Status rationale: `Người dùng chốt demo local, nghỉ nửa ngày, KPI do Leader đặt và yêu cầu triển khai; sau đó xác nhận thứ Bảy làm cả ngày.`

## Context

Ba module đã có nền và kiểm thử. Mốc 06/10 là demo local, không phải mở production hoặc public careers trên Internet. User xác nhận KPI do Leader đặt; không triển khai bộ mẫu KPI công ty.

## Decision

**Đã chốt:**

- Leave lưu buổi bắt đầu/kết thúc `am/pm`, tính khoảng nghỉ liên tục theo buổi. Cùng ngày/cùng buổi là 0,5 ngày; sáng đến chiều là nguyên ngày. Chặn overlap cùng buổi của đơn pending/approved; hai buổi riêng có thể dùng hai đơn.
- Công dự kiến dùng thứ Hai–thứ Bảy cả ngày, trừ PublicHoliday đang hoạt động; Chủ nhật không tính công. Chính sách tính mới áp dụng khi truy vấn công dự kiến, kể cả tháng cũ; không sửa dữ liệu AttendanceRecord nhập Excel. Legacy LeaveRequest mặc định am→pm nên giữ nghỉ nguyên ngày.
- Leader duyệt một cấp, không tự duyệt; từ chối bắt buộc lý do. Quyền chỉ trong Team đang phụ trách và Employee còn ở Team gắn với đơn. Lịch nghỉ chỉ trả đơn approved theo quyền own/Team, không trả reason/review_note.
- Leader tự đặt KPI; sao chép tháng trước chỉ tên/mô tả/trọng số của cùng Employee đang trong scope. Không sao chép completion/comment/score; không tự tạo phiếu hoặc lưu khi chỉ sao chép. Lịch sử vẫn dùng ACL hiện hành; nhân sự không thấy draft.
- Thông báo nội bộ khi chốt/mở lại/xác nhận KPI, yêu cầu tuyển gửi duyệt, hồ sơ mới và đơn nghỉ mới. Không đưa lý do nghỉ, CV hoặc ghi chú ứng viên vào notification/audit.
- Application bổ sung interview_at, interviewer_name nhập tên tự do và recruiter_note tối đa 2.000 ký tự. Người quản lý pipeline hiện có được sửa trong Team scope, yêu cầu version và trả 409 khi stale. Hồ sơ hired/rejected/anonymized không sửa; không tự chuyển stage khi đặt lịch. Tên người phụ trách là thông tin lịch, không cấp quyền cho người đó.
- Notes/lịch chỉ có trong projection quản lý Candidate; không đưa vào public DTO. Quy trình ẩn danh sáu tháng xóa thêm lịch/ghi chú và ghi chú transition; audit giữ metadata thao tác, không lưu nội dung nhạy cảm.
- Recruitment thêm xem trước nội dung public, tìm/lọc và lịch sử pipeline; không tự xuất bản khi xem trước.

## Consequences

Migration bổ sung field có default, không xóa dữ liệu cũ; backup database/media trước migrate. Rollback app giữ schema bổ sung, không reverse migration sau khi đã có đơn nửa ngày/lịch mới. App cũ không hiểu nửa ngày nên không dùng để xử lý những đơn đó; khi cần phục hồi phải chọn backup cùng mốc và đối chiếu thao tác phát sinh.

Đây là gói demo, không nghiệm thu sản phẩm chỉ vì build/test đạt. Payroll, máy chấm công, hạn mức/loại phép, hủy đơn, duyệt thay, khóa kỳ, sửa công thực tế, email/SMS, Calendar connector, IdP và deployment production vẫn ngoài phạm vi. Tiêu chí đạt/không đạt giữ tại docs/04 và acceptance theo module.
