# Thuật ngữ MRERP

Tài liệu này chuẩn hóa cách dùng từ trong repository. Nó không thay đổi trạng thái quyết định và không thay thế source of truth chuyên sâu.

| Thuật ngữ | Nghĩa trong MRERP |
|---|---|
| Product | Ranh giới nghiệp vụ và data ownership, ví dụ MRERP, MRECRM, ASSETCONTROL |
| Module | Ranh giới workflow/code bên trong một product |
| Deployable | Đơn vị có thể build và triển khai độc lập; không tự động là microservice |
| Modular monolith | Một deployable chính có các module nội bộ và contract rõ |
| Source of truth | Product/tài liệu duy nhất chịu trách nhiệm chính cho một miền dữ liệu/thông tin |
| Snapshot/read model | Bản sao chỉ đọc phục vụ truy vấn; không trở thành nguồn chuẩn |
| Identity Provider (IdP) | Hệ thống sở hữu credential, login, subject và phiên SSO |
| Subject | Định danh người dùng do IdP cấp; được ánh xạ với `employee_uuid` |
| Capability | Quyền cụ thể đối với product hoặc action |
| Data scope | Phạm vi record được phép truy cập: bản thân, team, phòng ban hoặc scope được giao |
| Object rule | Quy tắc dựa trên trạng thái/ownership của một record |
| Field policy | Quy tắc field nào được phép xuất hiện trong payload |
| Deep link | Link điều hướng đến màn hình cụ thể; không tự thân là tích hợp đầy đủ |
| Contract | API/event/schema có version và compatibility rule |
| ADR | Hồ sơ ghi một quyết định kiến trúc và trade-off |
| Vertical slice | Một luồng nhỏ chạy xuyên UI, API, database, authorization, audit và test |
| Fail-closed | Khi thiếu thông tin/quyền hoặc có lỗi kiểm tra thì mặc định từ chối |
| Break-glass | Cơ chế truy cập khẩn cấp có kiểm soát; hiện chưa được quyết định cho ASSETCONTROL |

Tên product chuẩn trong tài liệu là **MRERP Core**, **MRECRM**, **ASSETCONTROL** và **MREKANBAN**. Tên thư mục/domain triển khai chỉ được chốt qua source of truth hoặc ADR tương ứng.
