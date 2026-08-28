# ADR-0003: Application stack baseline cho Phase 1

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/technical-architecture.md`
- Related open decision: `OD-26`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project duyệt trực tiếp stack Phase 1 ngày 28/08/2026.`

## Context

- **Đã chốt:** MRERP Core là modular monolith và cần một vertical slice UI → API → database → authorization → audit → test.
- **Đề xuất mục tiêu:** React/TypeScript/Vite, Python 3.12, Django 5.2, DRF, PostgreSQL 16 và OpenAPI.
- **Đã chốt cho Phase 1:** chấp nhận stack/scaffold baseline nêu trong ADR này.

## Decision drivers

- Phù hợp một developer cùng AI.
- Có migration, admin/debug tooling, API schema và test ecosystem trưởng thành.
- Authorization và field projection phải thực thi ở server.
- Local/CI/deployment có đường nâng cấp rõ, không phụ thuộc prototype tĩnh.
- Không thêm queue/worker khi slice chưa có use case nền.

## Options considered

### Option A — Chấp nhận stack mục tiêu hiện tại cho slice

- Mô tả: React + TypeScript + Vite; Django 5.2 + DRF; PostgreSQL 16; OpenAPI; container/local workflow được quyết định trong scaffold plan.
- Ưu điểm: khớp source of truth hiện tại, phù hợp modular monolith và CRUD/policy/audit.
- Nhược điểm: cần vận hành hai toolchain frontend/backend.
- Rủi ro: cần duy trì hai toolchain và lockfile tương thích.
- Migration/rollback: scaffold trên branch riêng; chưa có production data.

### Option B — Chọn stack khác trước khi scaffold

- Mô tả: thay frontend/backend/database hoặc API approach sau đánh giá riêng.
- Ưu điểm: có thể phù hợp năng lực vận hành khác nếu có constraint mới.
- Nhược điểm: cần cập nhật technical architecture và toàn bộ kế hoạch test/deploy.
- Rủi ro: trì hoãn slice và tạo lệch với prototype/source hiện tại.
- Migration/rollback: chưa có application code nên đổi trước scaffold vẫn rẻ.

## Decision

Chọn Option A cho Phase 1: React/TypeScript/Vite, Django 5.2/DRF, PostgreSQL 16 và OpenAPI. Dùng npm cho frontend và Python virtual environment/requirements cho backend. Không thêm Celery/Redis khi People slice chưa có background-job use case.

## Remaining open questions

- Production database/schema topology không được chốt qua ADR này.
- Celery/Redis không thuộc slice People đầu tiên trừ khi có use case mới được duyệt.

## Consequences

### Positive

- Story có thể khóa công cụ migration, test và OpenAPI.

### Negative / trade-offs

- Dự án phải duy trì đồng thời Python và Node.js toolchain.

### Risks and mitigations

- Chọn theo prototype: prototype tiếp tục chỉ là UI reference.
- Cài dependency quá sớm: chỉ scaffold sau phê duyệt rõ.

## Security and authorization impact

- Backend framework phải hỗ trợ fail-closed guard và field projection test được.
- ADR không chọn IdP hoặc session policy.

## Data and contract impact

- PostgreSQL/OpenAPI đã được chấp nhận cho Phase 1.
- Không quyết định database/schema topology giữa MRERP và CRM.

## Rollout and rollback

- Scaffold trên branch ngắn hạn sau khi Phase 1 được mở.
- Xác minh smoke test, migration rỗng và CI trước merge.
- Rollback bằng cách không merge/xóa branch scaffold khi chưa có dữ liệu production.

## Validation

- Frontend/backend lint, unit test, API test và migration check được định nghĩa khi scaffold.
- Repository checker hiện tại tiếp tục chạy.

## Documentation updates

- Technical architecture, roadmap và readiness register phải phản ánh ADR này.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: trả lời trực tiếp “duyệt rồi” cho stack được hỏi trong task hiện tại.
