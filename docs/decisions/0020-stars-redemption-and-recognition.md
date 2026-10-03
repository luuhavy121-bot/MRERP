# ADR-0020: Sao, đổi thưởng và ghi nhận trong đánh giá nhân sự

- Status: `Accepted`
- Date: `2026-10-02`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/product/phase-3-requirements.md`
- Related open decisions: `OD-05, OD-13 (giải quyết một phần)`
- Supersedes: `Phần catalog/redemption chưa chốt của ADR-0013`
- Superseded by: `Không có`

## Context

Người sở hữu sản phẩm duyệt chuyển ghi nhận đóng góp vào bề mặt đánh giá nhân sự, đổi mục điều hướng thành Sao & Đổi thưởng và triển khai catalog/đổi thưởng. Phần ngân sách tiền mặt tổng của CEO được hoãn. MRERP `rewards_domain` tiếp tục sở hữu Recognition, sao và đổi thưởng; Performance chỉ hiển thị ghi nhận theo nhân sự/tháng.

## Decision

**Đã chốt:**

- Ghi nhận đóng góp nằm trong pane nhân sự của Đánh giá nhân sự; không tự cộng sao hoặc sửa điểm KPI.
- Sao & Đổi thưởng gồm số dư khả dụng, sao đang giữ, lịch sử, bảng xếp hạng, danh mục quà và yêu cầu đổi thưởng.
- HR/CEO quản lý danh mục, số sao cần đổi, tồn khả dụng, trạng thái hoạt động và duyệt/trao quà. Dùng capability `grant_stars_company` hiện hành; account/employment gate vẫn bắt buộc. Không tự duyệt, từ chối hoặc xác nhận trao yêu cầu của mình.
- HR/CEO cấu hình hạn mức sao từng Team/tháng. Leader chỉ cấp số dương cho người khác trong Team lãnh đạo và trong hạn mức tháng hiện tại; chưa cấu hình thì không được cấp. Không hạ hạn mức dưới số đã dùng. HR/CEO cấp/điều chỉnh toàn công ty; chỉ nhóm có capability company được điều chỉnh giảm, không làm âm số dư khả dụng.
- Yêu cầu đổi giữ sao và một đơn vị tồn ngay khi gửi: ledger `hold` âm; lưu snapshot tên quà và chi phí sao. Giá thay đổi so với xác nhận của người dùng thì yêu cầu bị từ chối để tải lại.
- Luồng `pending → approved → fulfilled`; `pending → rejected`; người yêu cầu hoặc HR/CEO được hủy `pending/approved → cancelled` trước khi trao. Từ chối/hủy bắt buộc lý do, hoàn sao bằng ledger `refund` dương và hoàn tồn đúng một lần. Duyệt/trao không trừ sao lần nữa.
- Ledger append-only; giao dịch và chuyển trạng thái có audit, chống xử lý lặp và kiểm soát cập nhật đồng thời. Bảng xếp hạng chỉ tính cấp/điều chỉnh, không tính giữ/hoàn khi đổi thưởng.
- Mười hai gợi ý quà là mẫu điền form, không phải tồn kho được kích hoạt hoặc giá trị tiền mặt đã duyệt. HR/CEO phải cấu hình và lưu quà thật trước khi nhân sự đổi.

## Deliberately unresolved

**Hoãn, chưa triển khai:** ngân sách tiền mặt tổng của CEO, tỷ lệ sao/tiền, giá tiền và kế toán/payroll. OD-05 vẫn mở cho Admin Panel ngoài phạm vi đã duyệt; OD-13 vẫn mở cho các policy còn lại.

## Consequences and validation

Thêm dữ liệu catalog, yêu cầu đổi và hạn mức trong MRERP, không tạo service/product mới. Migration bổ sung phải giữ Recognition/ledger cũ; không seed giá tiền hoặc quà khả dụng. Kiểm thử authorization, số dư/tồn/hạn mức, retry, đồng thời, snapshot và chuyển trạng thái; nghiệm thu theo [Phase 3](../testing/phase-3-acceptance.md). ADR Accepted không phải nghiệm thu implementation.

## Approval record

- Người chấp nhận: Người sở hữu sản phẩm MRERP.
- Ngày: 2026-10-02.
- Bằng chứng trong task: `duyệt tất cả còn ý số 3 chưa cần quan tâm, triển khai đi`; ý số 3 là ngân sách tiền mặt tổng của CEO. Phạm vi đã duyệt được ghi tại Decision; không suy ra phê duyệt phần đã hoãn.
