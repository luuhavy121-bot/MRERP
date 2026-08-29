# Contract Phase 3

Tài liệu này chịu trách nhiệm chính cho data/API boundary của Phase 3. Policy nghiệp vụ nằm tại [Yêu cầu Phase 3](../product/phase-3-requirements.md); quyền nằm tại [ma trận Phase 3](phase-3-authorization-matrix.md).

## Module ownership

| Module | Sở hữu |
|---|---|
| `preferences_domain` | Notification preference của Employee |
| `recruitment_domain` | HiringRequest, JobOpening, Candidate, Application, pipeline transition và CV metadata |
| `documents_domain` | Document, audience, version và file metadata |
| `rewards_domain` | Recognition và StarLedgerEntry |

Employee, Team và employment status tiếp tục thuộc `people_domain`. Binary file nằm trong storage service; database chỉ giữ metadata/storage key nội bộ.

## API baseline

- Settings: `GET|PATCH /api/v1/settings/me/`.
- Recruitment: requests, applications, transition, attachments và convert-to-employee dưới `/api/v1/recruitment/`.
- Documents: list/create/retrieve/archive, version upload và protected download dưới `/api/v1/documents/`.
- Rewards: recognitions, star grants, balance/ledger cá nhân và leaderboard dưới `/api/v1/rewards/`.

Mọi response lỗi dùng error envelope/correlation ID chung. API không trả password, candidate retention internals, storage path hoặc ledger người khác.

## Retention

- Candidate rejected: anonymize sau sáu tháng.
- Document/file soft-delete: purge sau 30 ngày.
- Star ledger: không tự hết hạn hoặc purge trong baseline.
