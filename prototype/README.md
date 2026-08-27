# MRERP Visual Prototype

Prototype này là bản dựng giao diện mới hoàn toàn cho MRERP. Mục đích của nó là giúp người sở hữu sản phẩm nhìn thấy hướng thiết kế, bố cục và trạng thái màn hình trước khi frontend production được scaffold.

## Trạng thái và ranh giới

- **Đã chốt:** prototype nằm trong repository MRERP và dùng dữ liệu minh họa.
- **Đã chốt:** prototype không phải bằng chứng đã có backend, Identity, authorization hoặc integration production.
- **Đã chốt:** mọi quyền nhạy cảm sau này vẫn phải được backend kiểm tra fail-closed.
- **Chưa quyết định:** frontend stack production vẫn tuân theo source of truth và ADR; prototype này không tự chốt stack.
- **Chưa quyết định:** policy nghiệp vụ, field matrix, role boundary và Identity Provider không được suy ra từ các màn hình minh họa.

## Phạm vi bản đầu

- App shell và điều hướng chung.
- Dashboard cá nhân với Task, lịch, phê duyệt và snapshot hệ sinh thái.
- Màn hình minh họa cho Công việc, Nhân sự, Phê duyệt, Tuyển dụng, Rewards, Tài liệu và Admin Panel.
- Trạng thái loading, empty, stale và restricted ở mức giao diện.
- Theme sáng/tối và bố cục responsive.

## Chạy cục bộ

Không cần cài dependency. Có thể mở trực tiếp `index.html` hoặc chạy một static server:

```powershell
python -m http.server 4173 --directory prototype
```

Sau đó mở `http://localhost:4173/`.

## Khi chuyển thành production

Mỗi màn hình phải được nối với API contract đã duyệt, thay dữ liệu mock bằng backend thật và bổ sung kiểm thử authorization tương ứng. Không được chuyển logic quyền trong prototype thành hàng rào bảo mật production.

Nguồn kiến trúc chịu trách nhiệm chính: [Kiến trúc kỹ thuật](../docs/architecture/technical-architecture.md). Điều kiện đạt/không đạt: [Tiêu chí nghiệm thu](../docs/04-tieu-chi-nghiem-thu.md).
