# Quản lý cấu hình và secret

Tài liệu này là source of truth cho baseline quản lý config/secret trong repository. Baseline được chấp nhận tại [ADR-0001](../decisions/0001-repository-governance-baseline.md).

## 1. Phân loại cấu hình

### Có thể commit

- Giá trị mặc định không nhạy cảm.
- Schema/config template.
- File ví dụ như `.env.example`, chỉ chứa tên biến và giá trị giả an toàn.
- Tài liệu mô tả nguồn cấp config.

### Không được commit

- Password, access token, refresh token, OTP hoặc API key thật.
- Private key, keystore và signing secret.
- Credential database, channel/shop hoặc service account.
- Nội dung ASSETCONTROL Vault.
- Database dump, backup hoặc dữ liệu production.
- File `.env` dùng cục bộ hoặc production.

## 2. Quy tắc repository

**Đã chốt qua ADR-0001.**

- `.env` và biến thể cục bộ bị ignore; file `*.example` được phép theo dõi.
- Private-key container và database backup phổ biến bị ignore.
- CI từ chối tracked `.env` thật, private-key marker, key container và database backup.
- `.gitignore` và CI chỉ là lớp bảo vệ phụ; người tạo thay đổi vẫn chịu trách nhiệm kiểm tra diff.

## 3. Local development

Khi application được scaffold, mỗi deployable phải cung cấp file ví dụ chỉ chứa biến cần thiết và mô tả cách nhận giá trị thật ngoài Git. Không đưa secret thật vào test fixture hoặc tài liệu.

## 4. Production

**Chưa quyết định (OD-21).** Secret manager, cơ chế inject config, certificate automation, rotation và quyền vận hành production cụ thể.

Điều đã chốt là secret production không nằm trong Git và product chỉ nhận credential tối thiểu cần thiết.

## 5. Khi nghi ngờ lộ secret

1. Không đăng secret vào issue, PR hoặc chat công khai.
2. Revoke/rotate credential tại hệ thống nguồn càng sớm càng tốt.
3. Xác định product, dữ liệu và log có thể bị ảnh hưởng.
4. Lưu bằng chứng audit phù hợp mà không sao chép secret.
5. Lập kế hoạch xử lý lịch sử Git/backup nếu cần.
6. Cập nhật runbook sau sự cố.

Việc xóa một commit không làm secret hết hiệu lực; rotation/revocation là bước ưu tiên.
