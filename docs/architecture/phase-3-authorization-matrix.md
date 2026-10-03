# Ma trận authorization Phase 3

**Cập nhật được duyệt 01/10/2026:** ưu tiên [Tuyển dụng công khai và đánh giá KPI](hr-expansion-contract.md) trước MKTLogin theo ADR-0017/0018. Quyền Leader với CV/pipeline và quy trình draft → gửi duyệt thay thế baseline tuyển dụng cũ ở phần bên dưới. Các phần khác giữ trạng thái riêng.

Mọi hàng bên dưới vẫn phải qua account/employment gate. Capability không thay thế scope, object rule hoặc field policy.

| Hành động | Staff | Leader | HR | CEO |
|---|---|---|---|---|
| Sửa preference của mình | Own | Own | Own | Own |
| Tạo Hiring Request | Không | Team lãnh đạo | Company | Company |
| Duyệt Hiring Request | Không | Không | Company | Company |
| Xem Candidate/Application | Không | Team lãnh đạo, full | Company, full | Company, full |
| Quản lý pipeline | Không | Team lãnh đạo | Company | Company |
| Convert Employee | Không | Không | Company | Company |
| Upload Document | Không | Team lãnh đạo | Company | Company |
| Đọc Document | Theo audience | Theo audience | Theo audience + HR confidential | Company |
| Gửi Recognition | Không | Team lãnh đạo | Company | Company |
| Cấp sao | Không | Team lãnh đạo, số dương trong hạn mức tháng | Company | Company |
| Điều chỉnh giảm sao | Không | Không | Company | Company |
| Quản lý quà/hạn mức Team | Không | Không | Company | Company |
| Xem quà hoạt động/gửi đổi quà | Own | Own | Own | Own |
| Xem yêu cầu đổi quà | Own | Own | Company | Company |
| Duyệt/từ chối/xác nhận trao | Không | Không | Company, không own | Company, không own |
| Hủy yêu cầu trước khi trao | Own | Own | Company | Company |
| Xem leaderboard | Company | Company | Company | Company |
| Xem Star ledger | Own | Own | Own | Own |

Field policy Candidate:

- Leader có capability manage_candidates nhận liên hệ và CV trong Team lãnh đạo theo ADR-0017; capability không mở company scope.
- HR/CEO nhận projection full theo capability.
- Staff không có Candidate endpoint.

Object rules quan trọng:

- Không tự Recognition hoặc tự cấp sao.
- Chỉ application `hired` chưa convert mới chuyển thành Employee.
- Document archived không nhận version mới; download vẫn phải qua audience hiện tại và trạng thái chưa xóa.
- Hiring Request đã duyệt/từ chối không được duyệt lại.

**Bổ sung ADR-0020:** quản lý catalog, hạn mức và xử lý yêu cầu dùng capability `rewards_domain.grant_stars_company` hiện hành trong bundle HR/CEO; quyền xem/gửi own dùng `rewards_domain.view_rewards`. Không suy quyền từ tên vai trò ở frontend. Hủy/từ chối cần lý do; fulfilled/rejected/cancelled không mở lại. Số dư khả dụng và tồn không âm; Leader chưa có hạn mức tháng bị từ chối cấp sao. Ghi nhận theo Employee chỉ đọc own hoặc scope được ghi nhận; giữ field policy ledger own.
