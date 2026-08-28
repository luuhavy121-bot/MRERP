# MRERP Visual Prototype

Prototype này là bản dựng giao diện tham khảo ban đầu của MRERP. React app Phase 1 hiện đã được scaffold; prototype được giữ lại để đối chiếu các màn hình chưa chuyển thành vertical slice thật.

## Trạng thái và ranh giới

- **Đã chốt:** prototype nằm trong repository MRERP và dùng dữ liệu minh họa.
- **Đã chốt:** prototype không phải bằng chứng đã có backend, Identity, authorization hoặc integration production.
- **Đã chốt:** mọi quyền nhạy cảm sau này vẫn phải được backend kiểm tra fail-closed.
- **Đã chốt cho Phase 1:** frontend dùng React/TypeScript/Vite theo ADR-0003; prototype không phải nguồn quyết định stack.
- **Chưa quyết định:** policy nghiệp vụ, field matrix, role boundary và Identity Provider không được suy ra từ các màn hình minh họa.

## Phạm vi bản đầu

- App shell và điều hướng chung.
- Dashboard cá nhân với Task, lịch, phê duyệt và snapshot hệ sinh thái.
- Màn hình minh họa cho Công việc, Nhân sự, Phê duyệt, Tuyển dụng, Rewards, Tài liệu và Admin Panel.
- Màn hình Tiến độ tổng hợp Phase 0–5, đủ 12 module MRERP Core, các luồng hệ sinh thái, cổng chuyển phase và decision debt.
- Trạng thái loading, empty, stale và restricted ở mức giao diện.
- Theme sáng/tối và bố cục responsive.

## Chạy cục bộ

Không cần cài dependency. Có thể mở trực tiếp `index.html` hoặc chạy một static server:

```powershell
python -m http.server 4174 --directory prototype
```

Sau đó mở `http://localhost:4174/`. Cổng 4173 dành cho React app hiện hành.

## Dữ liệu tiến độ

`project-status.js` là read model thủ công dành riêng cho prototype, không phải source of truth mới. Dữ liệu phải được đối chiếu với `docs/04-tieu-chi-nghiem-thu.md`, `docs/06-ke-hoach-trien-khai.md`, roadmap, yêu cầu nghiệp vụ và open-decision register mỗi khi cập nhật.

Phần trăm toàn project dùng cách tính quản trị tạm: sáu phase có trọng số bằng nhau. UI phải luôn hiển thị công thức và không được coi prototype là production application đã hoàn thành.

Màn hình Tiến độ hiện đã được chuyển vào React app thật. Bản trong prototype chỉ còn là tham chiếu lịch sử; trạng thái vận hành hiện hành nằm trong `apps/mrerp/frontend/src/projectStatus.ts` và phải được đối chiếu `docs/06-ke-hoach-trien-khai.md` cùng roadmap trước khi cập nhật.

## Khi chuyển thành production

Mỗi màn hình phải được nối với API contract đã duyệt, thay dữ liệu mock bằng backend thật và bổ sung kiểm thử authorization tương ứng. Không được chuyển logic quyền trong prototype thành hàng rào bảo mật production.

Nguồn kiến trúc chịu trách nhiệm chính: [Kiến trúc kỹ thuật](../docs/architecture/technical-architecture.md). Điều kiện đạt/không đạt: [Tiêu chí nghiệm thu](../docs/04-tieu-chi-nghiem-thu.md).
