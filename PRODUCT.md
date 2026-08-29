# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Toàn bộ nhân sự MRE là người dùng của MRERP. Mỗi người bắt đầu công việc từ cùng một cổng nhưng chỉ thấy dữ liệu, hành động và product phù hợp với account, employment status, capability và scope của mình.

Các nhóm sử dụng gồm Staff, Leader, HR và CEO. Cấp bậc không tự động thay thế capability; quyền thực tế luôn do server kiểm tra.

## Product Purpose

MRERP là cổng làm việc nội bộ và nguồn chuẩn cho Employee, Team, employment status và Task nghiệp vụ của MRE. Sản phẩm gom các luồng công việc hằng ngày vào một trải nghiệm chung, đồng thời kết nối đúng ranh giới với MRECRM, MREKANBAN và ASSETCONTROL.

Thành công nghĩa là nhân sự có thể đăng nhập một lần, tìm thấy đúng công việc và thông tin cần thiết, hoàn thành nghiệp vụ theo quyền, và không phải phụ thuộc vào các luồng rời rạc hoặc nguồn dữ liệu cạnh tranh.

## Positioning

MRERP không phải một bộ màn hình quản trị độc lập. Đây là điểm vào của hệ sinh thái làm việc MRE: một danh tính chung, một nguồn nhân sự chuẩn và các product chuyên biệt liên kết bằng contract rõ ràng nhưng vẫn tự sở hữu dữ liệu và authorization của mình.

MRECRM sở hữu nghiệp vụ CRM. MREKANBAN tham chiếu Task MRERP cho board/view chuyên sâu trong giai đoạn chuyển tiếp. ASSETCONTROL sở hữu Resource, Grant, Vault và audit tài nguyên; hiện chỉ CEO và Leader được cấp quyền truy cập.

## Operating Context

- Nhân sự dùng MRERP trong công việc hằng ngày để xem hồ sơ, Team, nghiệp vụ People/HR và các module được mở theo từng phase.
- Cấu trúc tổ chức hiện tại là `CEO → Team → Employee`; Department không phải tầng tổ chức hoạt động.
- HR quản lý hồ sơ nhân sự; Leader làm việc trong Team scope; CEO có company scope trong People nhưng hành động vẫn cần capability.
- Người dùng có thể chuyển sang product khác trong hệ sinh thái mà không coi deep link hoặc giao diện frontend là hàng rào bảo mật.
- Giao diện và nội dung chính dùng tiếng Việt.

## Capabilities and Constraints

- MRERP Core là modular monolith và được triển khai theo vertical slice đã duyệt.
- MRERP sở hữu Employee, Team, employment status và Task; product khác không được đọc hoặc sửa trực tiếp database MRERP.
- Identity Provider sở hữu credential, login, subject và phiên SSO. Provider production vẫn chưa quyết định.
- Endpoint nhạy cảm phải fail-closed tại server theo account/employment, product, action, scope, object và field policy.
- Không truyền access token qua URL, không lưu access token dài hạn trong `localStorage`, và không đưa secret hoặc dữ liệu production vào repository.
- Dashboard không gọi MRECRM hoặc ASSETCONTROL đồng bộ trong request tải trang; integration lỗi không được làm hỏng phần MRERP còn lại.
- MREKANBAN sẽ được giữ lâu dài hay retire vẫn là open decision.
- Việc mở ASSETCONTROL cho đối tượng ngoài CEO và Leader vẫn là open decision.

## Brand Commitments

- Tên product là **MRERP**; hệ sinh thái và thương hiệu doanh nghiệp thuộc **MR ECOM**.
- Logo MR ECOM do người sở hữu sản phẩm cung cấp trong phiên khởi tạo là tài sản thương hiệu cần được giữ nguyên về nhận diện: biểu tượng chim/cánh cách điệu màu đen, wordmark `MR ECOM`, đặt trong huy hiệu tròn màu vàng.
- Giao diện xanh–lime hiện tại là bằng chứng implementation, không phải cam kết thương hiệu đã chốt. Công việc thiết kế sau `init` phải lấy nhận diện MR ECOM đã cung cấp làm ràng buộc và không tự thay logo hoặc tên thương hiệu.

## Evidence on Hand

- Source of truth sản phẩm và kỹ thuật trong `README.md` và `docs/`.
- React/Vite frontend hiện có tại `apps/mrerp/frontend` với các bề mặt đăng nhập, People, Team, hồ sơ, nghỉ phép/chấm công và Admin.
- Django/DRF backend hiện có tại `apps/mrerp/backend`, bao gồm mock Identity development/test, authorization, audit và automated tests.
- Tài sản logo MR ECOM được người sở hữu sản phẩm cung cấp trực tiếp trong phiên `/impeccable init` ngày 29/08/2026.
- Chưa có logo MR ECOM bản vector hoặc brand guideline đầy đủ trong repository; công việc tương lai không được tự bịa thêm biến thể logo, claim, khách hàng, benchmark hoặc bằng chứng thương mại.

## Product Principles

1. Một cổng làm việc chung nhưng mỗi người chỉ thấy và làm được điều đúng với quyền của mình.
2. Mỗi miền dữ liệu có đúng một nguồn chuẩn; tích hợp không làm mờ ranh giới sở hữu.
3. Nghiệp vụ phải chạy xuyên UI, API, database, authorization, audit và test thay vì chỉ trình diễn giao diện.
4. MRERP vẫn hữu dụng khi product tích hợp tạm lỗi.
5. Mở rộng theo vertical slice đã duyệt, không âm thầm biến open decision thành policy production.
