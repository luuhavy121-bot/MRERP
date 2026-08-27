# Tích hợp hệ sinh thái

Tài liệu này là source of truth chịu trách nhiệm chính cho cách các product giao tiếp và hành vi khi integration lỗi. Bản đọc ngắn nằm tại [03 — Thiết kế kỹ thuật](../03-thiet-ke-ky-thuat.md).

## 1. Nguyên tắc

**Đã chốt.** Một hệ sinh thái tích hợp cần SSO, authorization server-side, contract dữ liệu và shared identifier. Deep link đơn thuần không phải tích hợp đầy đủ.

Không product nào đọc database của product khác. Product nguồn chỉ chia sẻ dữ liệu tối thiểu theo quyền.

## 2. Chọn cơ chế giao tiếp

Đây là **Đề xuất mục tiêu cần được cụ thể hóa bằng contract/ADR**:

| Cơ chế | Khi dùng | Ví dụ |
|---|---|---|
| Deep link | Điều hướng đến đúng màn hình | MRERP mở đúng resource trong ASSETCONTROL |
| REST/OpenAPI | Cần phản hồi ngay hoặc command rõ | CRM tạo Task liên quan Order qua MRERP API |
| Event/queue | Thông báo thay đổi không cần phản hồi đồng bộ | CRM phát sự kiện đạt doanh số |
| Snapshot/read model | Dashboard/report cần tồn tại khi source lỗi | MRERP giữ aggregate CRM gần nhất |
| Đồng bộ định kỳ | Chấp nhận độ trễ vài phút | Cập nhật snapshot nhân sự ở product đích |

## 3. Dashboard integration

**Đã chốt.**

```text
CRM / ASSETCONTROL
        │
        │ event hoặc đồng bộ định kỳ
        ▼
MRERP snapshot/read model
        │
        ▼
Dashboard
```

Dashboard không gọi trực tiếp source product trong request tải trang. Khi source lỗi, Dashboard dùng snapshot gần nhất và báo stale state.

**Chưa quyết định.** Stale threshold, timeout, retry và SLA.

## 4. ASSETCONTROL integration

**Đã chốt về yêu cầu:**

- Nhận `employee_uuid` và snapshot tối thiểu từ MRERP.
- Tự kiểm authorization ở server.
- Không gửi Vault content/secret sang MRERP.
- Migration login phải dual-run, có UUID mapping, rollback và emergency access.

**Đề xuất mục tiêu.** SSO qua OIDC flow riêng cho ASSETCONTROL.

**Chưa quyết định.** Break-glass, thời gian giữ login cũ và quan hệ deployment/tenant ZUZU–MRE.

## 5. MREKANBAN integration

**Đã chốt.** MRERP là Task source dài hạn; MREKANBAN tham chiếu `task_uuid` và không tạo Task source cạnh tranh.

**Chưa quyết định.** Giữ MREKANBAN làm client/view chuyên sâu hay retire sau migration.

## 6. CRM integration

**Đã chốt về ownership:** CRM sở hữu Customer/Order/Product/Channel/FFM; MRERP sở hữu Task và Rewards.

- CRM có thể tạo Task qua MRERP contract.
- CRM phát event achievement; MRERP Rewards quyết định sao.
- CRM đồng bộ aggregate vào MRERP read model cho Dashboard/report.
- Worker adapter/import/report không giữ web request.

Contract endpoint/event cụ thể là **Đề xuất mục tiêu cần ADR/versioning**.

## 7. Contract rules

**Đã chốt về nguyên tắc:**

- Dùng UUID ổn định.
- Contract có version và compatibility rule.
- Snapshot không trở thành source of truth.
- Field/data được tối thiểu hóa theo authorization.
- Integration failure không làm hỏng product khác.

## 8. Service security

**Chưa quyết định.** Service account, token format, rotation và trust boundary cụ thể. Không dùng shared static production token.

## 9. Failure contract tối thiểu

**Đã chốt về nguyên tắc:** integration failure không được làm hỏng product khác.

| Tình huống | Hành vi bắt buộc | Chi tiết chưa chốt |
|---|---|---|
| CRM/ASSETCONTROL không phản hồi khi Dashboard tải | Đọc snapshot gần nhất; không gọi source trong request | Timeout, stale threshold, SLA |
| Event xử lý lỗi | Không mất lỗi âm thầm; phải có failure visibility | Queue/tool, retry count, dead-letter policy |
| Snapshot chưa từng đồng bộ | Hiển thị trạng thái chưa có dữ liệu, không giả số liệu | Copy/UI wording cuối cùng |
| Contract không tương thích | Từ chối fail-closed hoặc giữ version tương thích | Compatibility window và deprecation policy |

## 10. Tài liệu liên quan

- [Data ownership](data-ownership.md)
- [Identity và phân quyền](identity-and-authorization.md)
- [Deployment](../operations/deployment.md)
- [Open decisions](../decisions/open-decisions.md)
