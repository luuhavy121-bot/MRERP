# 02 — Yêu cầu sản phẩm

Tài liệu này giúp người sở hữu sản phẩm hiểu hệ thống cần làm được gì. Chi tiết module và policy nghiệp vụ được quản lý tại [Yêu cầu nghiệp vụ chuyên sâu](product/business-requirements.md); điều kiện đạt/không đạt nằm tại [04 — Tiêu chí nghiệm thu](04-tieu-chi-nghiem-thu.md).

## Trải nghiệm chung

**Đã chốt.**

- Mọi nhân sự bắt đầu ngày làm việc từ MRERP.
- Dashboard hiển thị công việc, thông báo và thông tin cá nhân hóa.
- Người dùng chuyển sang product được cấp quyền mà không phải nhập lại mật khẩu.
- Người dùng chỉ nhận record và field cần thiết cho công việc.

## Các nhóm nghiệp vụ MRERP

**Đã chốt về miền nghiệp vụ; chi tiết workflow/policy triển khai theo phase.** MRERP cần hỗ trợ:

- Dashboard/Tổng quan.
- Nhân sự và cơ cấu tổ chức.
- Nghỉ phép và chấm công.
- Phê duyệt theo từng loại yêu cầu.
- Task với List, Calendar và view cơ bản.
- Ghi nhận văn hóa và Rewards.
- Tuyển dụng.
- Tài liệu nội bộ.
- Lương cá nhân theo policy được duyệt.
- Báo cáo từ read model được phép.
- Admin Panel và cài đặt cá nhân.

**Đề xuất mục tiêu.** Tuyển dụng có thể nằm dưới nhóm điều hướng Nhân sự nhưng là code module riêng.

## CRM

**Đã chốt về nguyên tắc.** Sales, Marketing/Ads và Kế toán có thể cùng dùng CRM nhưng không mặc nhiên nhận cùng payload. Server CRM phải áp dụng capability, scope và field policy.

**Chưa quyết định.** Ma trận field cụ thể cho từng nhóm.

## Task và Kanban

**Đã chốt.** MRERP sở hữu Task dài hạn. MREKANBAN không được tạo nguồn Task cạnh tranh; nó tham chiếu `task_uuid` và có thể quản lý cấu hình view chuyên sâu.

**Đã chốt trong phạm vi Task Phase 1.** Captain có permission nền như Staff; Leader có team scope; Manager tương lai có department scope nhưng ban đầu không có user Manager; CEO có company scope nhưng hành động vẫn cần capability. Luồng tạo, giao, cập nhật, gửi xác nhận và self-task chi tiết nằm tại [ma trận phân quyền Task](architecture/task-authorization-matrix.md).

**Chưa quyết định.** Quyền đọc Task nền của Staff/Captain và policy hủy/xóa Task.

**Chưa quyết định.** MREKANBAN sẽ được retire hay tiếp tục làm client/view chuyên sâu.

## ASSETCONTROL

**Đã chốt.** Hiện chỉ CEO và Leader được cấp quyền. ASSETCONTROL tự kiểm tra quyền ở server và không gửi nội dung Vault sang MRERP.

**Chưa quyết định.** Đối tượng khác có được truy cập trong tương lai hay không.

## Những policy chưa được phép tự chọn

- Ranh giới Captain/Leader/Manager ngoài policy Task Phase 1.
- Người được vào Admin Panel và quản trị Rewards.
- Field matrix CRM.
- Công thức lương, chấm công, phép và đổi thưởng.
- Cơ cấu/capability chính thức của MRE.

## Đọc sâu hơn

- [Yêu cầu nghiệp vụ chi tiết](product/business-requirements.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [Open decisions](decisions/open-decisions.md)

Tiếp theo: [03 — Thiết kế kỹ thuật](03-thiet-ke-ky-thuat.md).
