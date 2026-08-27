# ADR-0001: Repository governance baseline

- Status: `Accepted`
- Date: `2026-08-27`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `AGENTS.md`, `CONTRIBUTING.md`, `docs/testing/test-strategy.md`, `docs/operations/configuration-and-secrets.md`
- Related open decision: `OD-20`
- Supersedes: `Không có`
- Superseded by: `Không có`
- Status rationale: `Người dùng yêu cầu triển khai repository governance baseline sau khi xem thứ tự công việc đề xuất.`

## Context

- **Đã chốt:** Phase 0 cần conventions, CI tối thiểu, secret handling và Definition of Done trước khi scaffold application.
- **Đề xuất mục tiêu:** dùng kiểm tra nhẹ, không cài dependency ứng dụng và phù hợp repository tài liệu hiện tại.
- **Chưa quyết định:** secret manager/config delivery production; đây không thuộc phạm vi ADR này.

## Decision drivers

- Dễ dùng cho một developer cùng AI.
- Chặn lỗi tài liệu và secret cơ bản trước khi merge.
- Chạy giống nhau ở local và CI.
- Không buộc lựa chọn frontend/backend package manager.
- Có thể mở rộng khi Phase 1 bắt đầu.

## Options considered

### Option A — Checker Python standard library và GitHub Actions

- Mô tả: một script nội bộ kiểm tra docs/repository; CI gọi script bằng Python 3.12.
- Ưu điểm: không thêm package, chạy local, logic nằm trong repo.
- Nhược điểm: không thay thế markdown linter hoặc secret scanner chuyên dụng.
- Rủi ro: checker tự viết có thể bỏ sót edge case.
- Migration/rollback: sửa hoặc thay checker qua ADR/source update khi nhu cầu tăng.

### Option B — Cài bộ linter/scanner bên thứ ba ngay

- Mô tả: thêm dependency và nhiều action chuyên dụng.
- Ưu điểm: rule phong phú hơn.
- Nhược điểm: tăng supply-chain surface và maintenance trước khi có application code.
- Rủi ro: cấu hình sớm không phù hợp cấu trúc Phase 1.
- Migration/rollback: chưa chọn trong Phase 0 hiện tại.

## Decision

Chọn Option A:

- `main` là nhánh tích hợp mặc định; ưu tiên branch ngắn hạn và pull request.
- Branch prefix: `docs`, `adr`, `feat`, `fix`, `chore`.
- Commit message theo dạng `<type>: <mô tả ngắn>`.
- Dùng `.gitattributes` để chuẩn hóa LF cho text phổ biến và CRLF cho batch Windows.
- Dùng `.gitignore`, file example và checker để bảo vệ secret/config ở mức repository.
- CI dùng GitHub Actions với quyền `contents: read`, Python 3.12 và không cài dependency ứng dụng.
- Checker xác minh đường đọc, relative link, duplicate heading, trailing whitespace, open-decision ID và secret hygiene tối thiểu.

ADR này không chọn Identity Provider, secret manager production, branch protection hoặc policy nghiệp vụ.

## Remaining open questions

- OD-21: secret manager và config delivery production.
- Branch protection/reviewer policy có thể được quyết định khi có thêm contributor hoặc application code.

## Consequences

### Positive

- Có một lệnh kiểm tra nhất quán giữa local và CI.
- Giảm rủi ro link hỏng, tài liệu lệch cấu trúc và commit secret phổ biến.
- Không cài dependency application trong Phase 0.

### Negative / trade-offs

- Checker chưa phải secret scanner toàn diện.
- Quy ước branch/commit cần được người đóng góp tuân thủ; CI chưa tự kiểm commit message.

### Risks and mitigations

- False negative khi scan secret: vẫn bắt buộc review diff và rotation khi nghi ngờ lộ.
- Action supply-chain: chỉ dùng action chính thức của GitHub và quyền token tối thiểu.

## Security and authorization impact

- Không thay đổi runtime Identity/authorization.
- Giảm nguy cơ commit credential nhưng không thay thế secret manager.

## Data and contract impact

- Không thay đổi data ownership hoặc API/event contract.

## Rollout and rollback

- Thêm governance files, checker và workflow vào `main`.
- Chạy checker local trước commit.
- Nếu CI có lỗi do checker, sửa checker bằng PR; không tắt kiểm tra để bỏ qua lỗi thật.

## Validation

- `python scripts/check_docs.py` thành công cục bộ.
- `git diff --check` thành công.
- GitHub Actions chạy thành công sau push.

Validation record: workflow `Repository quality`, run [33060797246](https://github.com/luuhavy121-bot/MRERP/actions/runs/33060797246), kết quả `success` ngày 2026-08-27.

## Documentation updates

- Cập nhật README, AGENTS, docs index, roadmap, test strategy và open decisions.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-27.
- Bằng chứng/xác nhận: Yêu cầu trực tiếp “triển khai” sau đề xuất repository governance baseline.
