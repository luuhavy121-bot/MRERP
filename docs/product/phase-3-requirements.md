# Yêu cầu Phase 3 — Văn hóa và vận hành nhân sự

**Cập nhật được duyệt 01/10/2026:** ưu tiên [Tuyển dụng công khai và đánh giá KPI](hr-expansion-requirements.md) trước MKTLogin theo ADR-0017/0018. Quyền Leader với CV/pipeline và quy trình draft → gửi duyệt thay thế baseline tuyển dụng cũ ở phần bên dưới. Các phần khác giữ trạng thái riêng.

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

Baseline này được mở rộng bởi ADR-0017 ngày 01/10/2026. Quy tắc hiện hành tại [Yêu cầu HR mở rộng](hr-expansion-requirements.md): bản nháp → gửi → HR/CEO duyệt → công khai; Leader được quản lý liên hệ/CV/pipeline trong Team, HR/CEO company scope và độc quyền convert Employee thử việc. Retention từ chối sáu tháng giữ nguyên. Việc xuất bản tin công khai không tự công khai các opening legacy.

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

### Mở rộng Sao & Đổi thưởng ngày 02/10/2026

**Đã chốt qua [ADR-0020](../decisions/0020-stars-redemption-and-recognition.md); `Implementation hoàn tất / Chờ nghiệm thu sản phẩm`, riêng với baseline.**

- Ghi nhận đóng góp chuyển vào pane nhân sự trong Đánh giá nhân sự, lọc theo Employee/tháng; không tự đổi điểm KPI hoặc cộng sao. Navigation cũ đổi thành **Sao & Đổi thưởng**.
- HR/CEO quản lý quà (tên, mô tả, nhóm, chi phí sao, tồn khả dụng, hoạt động), duyệt yêu cầu và xác nhận đã trao. Không tự duyệt/từ chối/trao yêu cầu của mình.
- HR/CEO đặt hạn mức cấp sao cho mỗi Team/tháng. Leader chỉ cấp sao dương trong Team, dùng chung hạn mức của Team; chưa có hạn mức hoặc hết hạn mức thì server từ chối. Không hạ hạn mức dưới số đã dùng. HR/CEO cấp và điều chỉnh toàn công ty; điều chỉnh giảm không làm âm số dư khả dụng.
- Nhân sự đổi quà đang hoạt động khi đủ sao và còn tồn. Khi gửi, giữ sao bằng bút toán âm và giữ một quà; snapshot tên/chi phí không đổi khi catalog sửa sau đó.
- Yêu cầu đi từ Chờ duyệt → Đã duyệt → Đã trao; Chờ duyệt có thể bị từ chối. Người yêu cầu hoặc HR/CEO hủy trước khi trao, kể cả đã duyệt. Hủy/từ chối cần lý do, hoàn sao và tồn đúng một lần; đã trao không hủy trong phạm vi này.
- Số dư khả dụng đã trừ phần giữ; sao đang giữ hiển thị riêng. Leaderboard tính cấp/điều chỉnh, bỏ qua giữ/hoàn đổi thưởng. Chỉ chủ sở hữu đọc ledger cá nhân; HR/CEO xem yêu cầu company phục vụ xử lý.
- Mười hai gợi ý quà chỉ giúp điền form; không tự tạo quà hoạt động/tồn hoặc giá tiền. Catalog trống yêu cầu HR/CEO cấu hình.

## 6. Ngoài phạm vi

**Chưa quyết định và không hiện thực:** ngân sách tiền mặt tổng của CEO, quy đổi sao/tiền, email/SMS/push, object storage product cụ thể. Catalog và redemption đã được mở qua ADR-0020.

**Không làm:** CRM achievement ingestion, ASSETCONTROL integration, Payroll, máy chấm công hoặc workflow Approval tổng quát trong Phase 3.
