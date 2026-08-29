# Ma trận authorization Phase 3

Mọi hàng bên dưới vẫn phải qua account/employment gate. Capability không thay thế scope, object rule hoặc field policy.

| Hành động | Staff | Leader | HR | CEO |
|---|---|---|---|---|
| Sửa preference của mình | Own | Own | Own | Own |
| Tạo Hiring Request | Không | Team lãnh đạo | Company | Company |
| Duyệt Hiring Request | Không | Không | Company | Company |
| Xem Candidate/Application | Không | Team lãnh đạo, basic | Company, full | Company, full |
| Quản lý pipeline/convert Employee | Không | Không | Company | Company |
| Upload Document | Không | Team lãnh đạo | Company | Company |
| Đọc Document | Theo audience | Theo audience | Theo audience + HR confidential | Company |
| Gửi Recognition | Không | Team lãnh đạo | Company | Company |
| Cấp sao | Không | Team lãnh đạo | Company | Company |
| Xem leaderboard | Company | Company | Company | Company |
| Xem Star ledger | Own | Own | Own | Own |

Field policy Candidate:

- Leader nhận projection basic trong Team: tên, nguồn, stage, vị trí và lịch sử stage; không nhận contact/CV download trong baseline.
- HR/CEO nhận projection full theo capability.
- Staff không có Candidate endpoint.

Object rules quan trọng:

- Không tự Recognition hoặc tự cấp sao.
- Chỉ application `hired` chưa convert mới chuyển thành Employee.
- Document archived không nhận version mới; download vẫn phải qua audience hiện tại và trạng thái chưa xóa.
- Hiring Request đã duyệt/từ chối không được duyệt lại.
