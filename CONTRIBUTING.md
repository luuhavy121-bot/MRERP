# Đóng góp cho MRERP

## 1. Trước khi thay đổi

1. Đọc [AGENTS.md](AGENTS.md).
2. Đọc đường `docs/01–06` theo thứ tự.
3. Đọc source of truth và open decision liên quan.
4. Xác định thay đổi thuộc **Đã chốt**, **Đề xuất mục tiêu** hay **Chưa quyết định**.

Không hiện thực mục **Chưa quyết định** nếu chưa có xác nhận và ADR phù hợp.

## 2. Branch

`main` là nhánh tích hợp mặc định. Ưu tiên tạo branch ngắn hạn theo mẫu:

- `docs/<mo-ta-ngan>` cho tài liệu.
- `adr/<mo-ta-ngan>` cho quyết định kiến trúc.
- `feat/<mo-ta-ngan>` cho tính năng.
- `fix/<mo-ta-ngan>` cho sửa lỗi.
- `chore/<mo-ta-ngan>` cho công việc repository/vận hành.

Dùng chữ thường, dấu gạch ngang và không đưa tên người hoặc secret vào tên branch.

## 3. Commit

Commit message dùng dạng:

```text
<type>: <mô tả ngắn ở thể mệnh lệnh>
```

Các `type` chính: `docs`, `adr`, `feat`, `fix`, `refactor`, `test`, `ci`, `chore`.

Mỗi commit nên có một mục đích rõ, không trộn thay đổi không liên quan và không chứa secret/dữ liệu production.

## 4. Pull request

- Ưu tiên pull request thay vì thay đổi trực tiếp `main`.
- Dùng [PR template](.github/pull_request_template.md).
- Dẫn source of truth, ADR và open decision liên quan.
- Nêu rõ data ownership, authorization, migration và rollback nếu bị ảnh hưởng.
- Chạy kiểm tra cục bộ trước khi yêu cầu review.

## 5. Kiểm tra cục bộ

Phase 0 không cài dependency ứng dụng. Chạy checker bằng Python standard library:

```powershell
python scripts/check_docs.py
git diff --check
```

Checker xác minh đường đọc `01–06`, Markdown link, heading trùng, whitespace, open-decision ID và secret hygiene tối thiểu.

## 6. Config và secret

- Chỉ commit file ví dụ như `.env.example`; không ghi giá trị thật.
- Không commit private key, credential, database dump hoặc Vault content.
- `.gitignore` chỉ là lớp bảo vệ phụ, không thay thế việc review và secret scanning.
- Nếu nghi ngờ secret đã bị commit, ưu tiên revoke/rotate ngay rồi mới xử lý lịch sử Git theo kế hoạch được duyệt.

Chi tiết: [Quản lý cấu hình và secret](docs/operations/configuration-and-secrets.md).

## 7. Điều kiện hoàn thành

Áp dụng [04 — Tiêu chí nghiệm thu](docs/04-tieu-chi-nghiem-thu.md) và [Test strategy](docs/testing/test-strategy.md). CI xanh không tự động chứng minh thay đổi đúng nghiệp vụ hoặc đủ authorization.
