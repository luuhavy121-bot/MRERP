# Architecture Decision Records

Thư mục này lưu các quyết định kiến trúc có ảnh hưởng đáng kể đến product boundary, dữ liệu, security, integration, deployment hoặc vận hành.

## Khi nào cần ADR

- Hiện thực một mục có nhãn **Đề xuất mục tiêu**.
- Giải quyết một mục **Chưa quyết định**.
- Thay đổi data ownership hoặc contract liên product.
- Chọn Identity Provider, database topology, service authentication hoặc break-glass.
- Thay đổi ranh giới deployable/repository.
- Chấp nhận một trade-off có tác động dài hạn.

## Trạng thái ADR

- `Proposed`: đang đề nghị; chưa được dùng làm quyết định production.
- `Accepted`: đã được người có thẩm quyền chấp nhận.
- `Rejected`: không được chọn.
- `Superseded`: đã được ADR mới thay thế.
- `Deprecated`: không còn nên dùng nhưng chưa bị thay thế hoàn toàn.

## Quy tắc

1. Sao chép [ADR-TEMPLATE.md](ADR-TEMPLATE.md) thành `NNNN-ten-ngan-gon.md`.
2. Không đánh dấu `Accepted` nếu chưa có xác nhận rõ ràng.
3. ADR phải phân biệt facts, constraints, options và decision.
4. Mục **Chưa quyết định** không được lén đặt vào phần Decision.
5. Khi ADR được chấp nhận, cập nhật source of truth liên quan và [open-decisions.md](open-decisions.md).
6. Nếu ADR và source of truth mâu thuẫn, nêu mâu thuẫn và đồng bộ tài liệu trước khi triển khai.

## Vòng đời quyết định

```text
Open decision
    ↓
ADR Proposed
    ↓ người có thẩm quyền duyệt
ADR Accepted / Rejected
    ↓
Cập nhật source of truth và open-decision register
    ↓
Mới được hiện thực nếu các cổng khác đã đạt
```

Một xác nhận trong chat chỉ được dùng khi thực sự xuất hiện trong task hiện tại hoặc được lưu lại bằng ADR/source-of-truth update. Không tạo ADR hồi tố để hợp thức hóa một lựa chọn đã tự triển khai.

## Danh sách ADR

- [ADR-0001: Repository governance baseline](0001-repository-governance-baseline.md) — `Accepted`.
