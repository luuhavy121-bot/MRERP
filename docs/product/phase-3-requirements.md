# Yêu cầu Phase 3 — Văn hóa và vận hành nhân sự

Tài liệu này là source of truth nghiệp vụ cho Personal Settings, Recruitment, Documents, Recognition và Stars trong Phase 3. Quyết định cục bộ được chấp nhận tại [ADR-0013](../decisions/0013-phase-3-culture-operations-baseline.md).

## 1. Trạng thái

**Đã chốt:** ưu tiên Phase 3 trước phần còn lại của Phase 2. Phase 2 không được tự đánh dấu hoàn tất.

**Trạng thái implementation ngày 29/08/2026:** `Implementation hoàn tất / Chờ nghiệm thu`. Không đồng nghĩa `Accepted` hoặc 100%.

## 2. Personal Settings

- Người dùng quản lý notification preference của chính mình.
- Chỉ notification xã hội như Feed/Recognition được phép tắt.
- Notification account, security, Task, Leave và Recruitment liên quan luôn bắt buộc.
- Chỉ có notification trong app ở Phase 3.
- Profile, account, password và theme tiếp tục dùng bề mặt hiện có; không tạo nguồn dữ liệu cạnh tranh.

## 3. Recruitment

- Leader tạo yêu cầu tuyển cho Team đang lãnh đạo; HR/CEO tạo cho mọi Team.
- Yêu cầu Leader tạo cần HR duyệt một cấp. HR/CEO tạo thì approved ngay.
- HR/CEO xem toàn bộ candidate/application; Leader chỉ xem application của Team mình.
- HR/CEO quản lý Candidate và pipeline. Leader có read-only scoped view trong baseline.
- Pipeline: `new`, `screening`, `interview`, `offer`, `hired`, `rejected`.
- Chỉ HR/CEO convert application `hired` thành Employee `Thử việc`; việc tạo account là tùy chọn.
- Candidate bị từ chối được ẩn danh sau sáu tháng. Candidate đã chuyển thành Employee giữ liên kết tối thiểu phục vụ audit nhưng không tạo nguồn hồ sơ nhân sự cạnh tranh.

## 4. Documents

- Uploader: Leader, HR, CEO.
- Audience: Employee cụ thể, một hoặc nhiều Team, company, hoặc HR confidential.
- Leader chỉ phát hành trong Team lãnh đạo/Employee thuộc Team đó. HR/CEO có company scope; HR confidential chỉ HR/CEO đọc.
- Một document có nhiều version; mỗi version tối đa 10 file, 25 MB/file.
- Download luôn qua endpoint xác thực và kiểm ACL.
- Soft-delete/archived file giữ 30 ngày rồi worker purge.
- Local-media persistent volume là baseline. Object storage production dài hạn **Chưa quyết định**.

## 5. Recognition và Stars

- Leader, HR và CEO được gửi Recognition; không tự gửi cho mình.
- Leader chỉ gửi/cấp sao trong Team lãnh đạo; HR/CEO có company scope.
- Recognition không tự cộng sao.
- Star balance được tính từ append-only ledger. Sao không hết hạn trong baseline.
- Điều chỉnh sai lệch tạo ledger entry mới; không sửa/xóa lịch sử.
- Mọi nhân sự đang hoạt động xem leaderboard tháng/quý/năm; chỉ xem ledger chi tiết của chính mình.

## 6. Ngoài phạm vi

**Chưa quyết định và không hiện thực:** reward catalog management, redemption request, approval, hold/refund policy, email/SMS/push, object storage product cụ thể.

**Không làm:** CRM achievement ingestion, ASSETCONTROL integration, Payroll, máy chấm công hoặc workflow Approval tổng quát trong Phase 3.
