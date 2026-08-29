# Nghiệm thu People account và employment lifecycle

## Trạng thái

**Đề xuất mục tiêu — Implementation hoàn tất, chờ người sở hữu sản phẩm nghiệm thu.** Tài liệu này không thay đổi trạng thái `Accepted` của People/HR Foundation trước đó và không chọn Identity Provider production.

## Điều kiện đạt

- `Hồ sơ của tôi` là một trang riêng; phần tài khoản và đổi mật khẩu nằm trong trang này, không tạo menu `Tài khoản của tôi` cạnh tranh.
- Staff chỉ sửa họ tên hiển thị, ngày sinh và địa chỉ của chính mình; server từ chối field ngoài allow-list.
- Khi HR tạo hoặc provision account, server sinh mật khẩu tạm, chỉ trả một lần và không ghi vào audit/log.
- HR/CEO reset, khóa và mở khóa account toàn công ty; Leader chỉ reset account của Employee trong Team mình lãnh đạo; server fail-closed ngoài scope.
- `Tạm nghỉ` khóa account nhưng giữ access bundle; `Nghỉ việc` khóa account và thu hồi bundle; `Kích hoạt lại` phục hồi trạng thái/bundle đã lưu.
- Không actor nào tự khóa account, tự đổi employment hoặc tự đổi access bundle qua endpoint quản trị.
- CSV import là all-or-nothing, chỉ tạo Employee `Thử việc` không account; CSV export không có password hay field nhạy cảm.
- HR thấy People audit được giới hạn; CEO thấy toàn bộ People audit và quản lý access bundle trong Admin Panel.
- Migration chạy `forward → reverse → forward`; OpenAPI validation, frontend lint/build, backend tests và E2E đều đạt.

## Điều kiện không đạt

- UI ẩn nút nhưng gọi API trực tiếp vẫn vượt scope.
- Password, token, CCCD hoặc địa chỉ xuất hiện trong security log/audit/CSV.
- Account bị cấp một phần khi Employee creation thất bại, hoặc ngược lại.
- Tạm nghỉ/nghỉ việc không khóa account, hoặc kích hoạt lại làm mất bundle trước đó.
- Admin Panel xuất hiện hoặc endpoint access bundle cho actor không có capability CEO.
- Tài liệu/màn hình Tiến độ tự đánh dấu `Accepted` trước khi người sở hữu sản phẩm nghiệm thu.

## Bằng chứng tự động hiện tại

- 60 backend tests đạt; People có 42 tests.
- Ba Playwright E2E đạt; hai luồng dành cho People Foundation và People account/employment lifecycle.
- OpenAPI validation không warning/error; frontend lint/build đạt.
- Migration `0005` đã chạy thành công theo thứ tự `forward → reverse → forward` trên database tạm.

## Còn ngoài phạm vi

- Identity Provider production và chính sách phiên/break-glass: **Chưa quyết định**.
- UI đọc lịch sử đăng nhập từ IdP production: **Chưa quyết định**.
- Payroll, công thức lương, loại phép và policy nghỉ: **Chưa quyết định** hoặc ngoài phạm vi hiện tại.

## Căn cứ

- [ADR-0010](../decisions/0010-people-account-and-employment-lifecycle.md)
- [People authorization matrix](../architecture/people-authorization-matrix.md)
- [People data contract](../architecture/people-data-contract.md)
- [Tiêu chí nghiệm thu chung](../04-tieu-chi-nghiem-thu.md)
