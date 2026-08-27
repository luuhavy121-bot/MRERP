## Mục tiêu

Mô tả ngắn vấn đề và kết quả cần đạt.

## Trạng thái quyết định

- [ ] Chỉ hiện thực nội dung **Đã chốt**.
- [ ] Nội dung **Đề xuất mục tiêu** đã có ADR được chấp nhận nếu cần.
- [ ] Không tự lựa chọn mục **Chưa quyết định**.

Source of truth / ADR / open decision liên quan:

## Thay đổi chính

- <!-- Liệt kê thay đổi chính. -->

## Data, quyền và bảo mật

- Product/module sở hữu dữ liệu:
- Ảnh hưởng capability/scope/object/field policy:
- Secret hoặc dữ liệu production trong diff: Không

## Kiểm tra

- [ ] Đã chạy `python scripts/check_docs.py`.
- [ ] Đã chạy `git diff --check`.
- [ ] Đã bổ sung test tương xứng với rủi ro nếu có code.
- [ ] Đã kiểm tra allowed/denied/out-of-scope/redaction nếu có endpoint nhạy cảm.

## Migration và rollback

Không áp dụng, hoặc mô tả migration, dual-run, điều kiện rollback và bằng chứng kiểm tra.

## Tài liệu và vận hành

- [ ] Source of truth/ADR đã được cập nhật.
- [ ] Có hướng dẫn kiểm tra hoặc runbook nếu thay đổi ảnh hưởng vận hành.
- [ ] Integration lỗi không làm hỏng product khác.
