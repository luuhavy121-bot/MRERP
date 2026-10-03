# Contract Phase 3

Tài liệu này chịu trách nhiệm chính cho data/API boundary của Phase 3. Policy nghiệp vụ nằm tại [Yêu cầu Phase 3](../product/phase-3-requirements.md); quyền nằm tại [ma trận Phase 3](phase-3-authorization-matrix.md).

## Module ownership

| Module | Sở hữu |
|---|---|
| `preferences_domain` | Notification preference của Employee |
| `recruitment_domain` | HiringRequest, JobOpening, Candidate, Application, pipeline transition và CV metadata |
| `documents_domain` | Document, audience, version và file metadata |
| `rewards_domain` | Recognition, StarLedgerEntry, RewardGift, RewardRedemption và TeamStarAllowance |

Employee, Team và employment status tiếp tục thuộc `people_domain`. Binary file nằm trong storage service; database chỉ giữ metadata/storage key nội bộ.

## API baseline

- Settings: `GET|PATCH /api/v1/settings/me/`.
- Recruitment: requests, applications, transition, attachments và convert-to-employee dưới `/api/v1/recruitment/`.
- Documents: list/create/retrieve/archive, version upload và protected download dưới `/api/v1/documents/`.
- Rewards: recognitions, star grants, balance/ledger cá nhân và leaderboard dưới `/api/v1/rewards/`.

## Contract Sao & Đổi thưởng theo ADR-0020

**Đã chốt.** Mọi endpoint dưới `/api/v1/rewards/` dùng account/employment gate và capability tại server.

| Endpoint | Dữ liệu và hành vi |
|---|---|
| `GET recognitions/?employee_uuid=<uuid>&month=YYYY-MM` | Lọc ghi nhận theo nhân sự/tháng; người khác phải nằm trong scope ghi nhận của actor; không sao chép Recognition sang Performance |
| `GET/POST gifts/`, `PATCH gifts/<uuid>/` | Catalog: `title`, `description`, `category`, `cost` sao dương, `stock` khả dụng không âm, `active`; chỉ company capability được ghi/đọc quà ngừng hoạt động |
| `GET/POST redemptions/` | GET phân trang `count/next/previous/results`, own hoặc company cho người xử lý; frontend đọc đủ các trang. POST gửi `gift_uuid`, UUID `request_key`, `expected_cost`; không nhận Employee/giá snapshot từ client |
| `POST redemptions/<uuid>/decision/` | `action`: approve/reject/cancel/fulfill; `note` bắt buộc khi hủy/từ chối; kiểm ownership và trạng thái |
| `GET/POST allowances/` | Hạn mức `team_uuid`, `month` ngày đầu tháng, `limit`; đọc Team lãnh đạo hoặc company; ghi chỉ company |
| `GET stars/me/` | `balance` khả dụng, `held` tổng chi phí pending/approved, ledger own |

RewardRedemption giữ Employee, Gift và snapshot `gift_title`/`cost`; catalog sửa không thay lịch sử. `request_key` retry cùng Employee/quà/chi phí trả lại yêu cầu cũ, dùng cho nội dung khác bị từ chối. Hold/refund có idempotency key riêng. Transaction khóa Employee, Gift, yêu cầu và hạn mức khi liên quan để ngăn chi vượt số dư/tồn/quota; hoàn tồn/ledger chỉ một lần. Approve/fulfill không tạo lần trừ mới. Leaderboard chỉ đọc `grant/adjustment`.

Migration bổ sung bảng/field, giữ ledger cũ và không seed catalog có hiệu lực hoặc giá tiền. API không trả ledger của người khác kể cả khi cho HR/CEO xử lý yêu cầu. Quyền chi tiết theo [ma trận Phase 3](phase-3-authorization-matrix.md).

Quyền ghi nhận độc lập với quyền chỉnh KPI: HR/CEO lấy danh sách nhân sự từ Rewards audience khi không có quyền quản lý KPI, kể cả Employee chưa có phiếu đánh giá. Staff chưa có phiếu vẫn xem ghi nhận own trong tháng. Không tạo phiếu KPI chỉ để đọc/ghi Recognition.

Mọi response lỗi dùng error envelope/correlation ID chung. API không trả password, candidate retention internals, storage path hoặc ledger người khác.

## Retention

- Candidate rejected: anonymize sau sáu tháng.
- Document/file soft-delete: purge sau 30 ngày.
- Star ledger: không tự hết hạn hoặc purge trong baseline.
