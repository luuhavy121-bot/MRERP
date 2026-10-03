# Mockup MRECRM để duyệt với Leader

Bản mẫu độc lập, giữ giao diện MRERP và dùng **dữ liệu minh họa**. Không thay khung CRM tại cổng 4173, không có API, database, đăng nhập, nhập file hoặc kết nối nguồn.

**Làm rõ 03/10/2026:** MRECRM có khung riêng gồm header MRECRM và menu CRM, không hiển thị thanh sản phẩm hoặc menu ERP. Chỉ có liên kết “Về MRERP”. Đây là hướng giao diện được xác nhận; domain, deployment và phiên đăng nhập CRM thật chưa được chốt bởi bản mẫu.

**Triển khai tiếp theo được duyệt 03/10/2026:** giao diện và bộ dữ liệu minh họa này đã được chuyển sang React tại `/crm` trong app local cổng 4173, có kiểm tra phiên đăng nhập hiện có. Bản static này vẫn độc lập để tham khảo. Đây là demo trong app, không phải kết nối dữ liệu hoặc hoàn tất nghiệp vụ CRM.

Mở trực tiếp `index.html` hoặc từ root repository chạy:

```powershell
python -m http.server 4175 --directory prototype/crm --bind 127.0.0.1
```

Truy cập `http://localhost:4175/`. Các trang dùng hash để mở trực tiếp và Back/Forward không cần cấu hình server.

Ảnh gửi Leader: [đơn hàng và chi tiết](overview.png), [thống kê](reports.png). Đây là ảnh chụp Chromium từ bản mẫu, có metadata nguồn gốc, không phải dữ liệu thực tế.

## Nội dung

- 60 đơn giả trong tháng 10/2026, 72 bản ghi nguồn. 12 đơn được khai báo ở hai nguồn để minh họa đếm trùng.
- Tìm kiếm, lọc ngày/nguồn/giao hàng, phân trang, chi tiết bên phải, đóng bằng Escape.
- Thống kê dùng cùng bộ lọc và cùng dữ liệu với danh sách đơn.
- Quảng cáo/Kế toán trình bày dữ liệu còn thiếu; ROAS, chi phí mỗi đơn, lợi nhuận và COD chưa nhận chưa tính.
- Trang Nội dung cần duyệt gồm quy trình thực tế, nguồn chuẩn và quyền theo từng nhóm.

Trạng thái, trường dữ liệu, nhận dạng đơn trùng và quy tắc nhóm theo nguồn đầu tiên chỉ là **đề xuất minh họa**. Nguồn Webcake/POS/Google Sheet không đồng nghĩa kênh bán hàng. Không dùng số điện thoại hoặc địa chỉ giả để liên hệ/giao hàng. Các bộ lọc không lưu sau tải lại; chỉ đường dẫn trang được giữ.

Tỷ lệ giao/hoàn/hủy dùng tổng số đơn đã lọc làm mẫu số. Giá trị đơn là tổng giá sản phẩm nhân số lượng, không gồm phí/giảm giá/hoàn tiền; giá trị giao thành công không phải tiền thực nhận. Danh sách và báo cáo dùng snapshot trạng thái giả, không phải thống kê chuyển trạng thái trong kỳ.

Kiến trúc và quyền CRM thật vẫn theo [data ownership](../../docs/architecture/data-ownership.md) và [open decisions](../../docs/decisions/open-decisions.md). Không suy ra backend hoặc policy từ mockup.
