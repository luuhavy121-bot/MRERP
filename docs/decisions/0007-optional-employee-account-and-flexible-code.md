# ADR-0007: Tài khoản Employee tùy chọn và mã nhân sự linh hoạt

- Status: `Accepted`
- Date: `2026-08-28`
- Deciders: `Người sở hữu project MRERP`
- Related source of truth: `docs/architecture/people-data-contract.md`
- Related open decision: `OD-26`
- Supersedes: `ADR-0006 về yêu cầu luôn tạo account; quy tắc pattern mã trong ADR-0005`
- Superseded by: `Không có`
- Status rationale: `Người sở hữu project yêu cầu checkbox chọn có tạo tài khoản hay không và cho nhập tự do mã nhân sự, chỉ chống trùng.`

## Context

- **Đã chốt:** Employee thuộc MRERP; credential thuộc Identity; HR chỉ tạo Employee ban đầu ở trạng thái `Thử việc`.
- **Đã chốt mới:** tạo account là lựa chọn của HR, không còn là điều kiện bắt buộc để tạo Employee.
- **Đã chốt mới:** mã nhân sự không có pattern nghiệp vụ bắt buộc, nhưng phải có giá trị và duy nhất.
- **Chưa quyết định:** workflow cấp account production cho Employee được tạo mà chưa có account.

## Decision

`Employee.identity_user` được phép rỗng. Form có checkbox **Tạo tài khoản đăng nhập**, mặc định bật để hỗ trợ quick-create hiện tại. Khi bật, username/password bắt buộc và compensation của ADR-0006 tiếp tục áp dụng. Khi tắt, MRERP chỉ tạo Employee `Thử việc`, không tạo credential hoặc Identity account.

Mã nhân sự được giữ đúng nội dung đã trim, dài tối đa 64 ký tự, không áp regex. Database và API chống trùng không phân biệt hoa/thường; ví dụ `NDK13` và `ndk13` được coi là cùng mã.

## Remaining open questions

- Provision account về sau qua Admin Panel/IdP production vẫn thuộc OD-19.
- Policy đổi mã nhân sự sau khi tạo chưa được quyết định.

## Consequences

- HR có thể tạo hồ sơ trước khi người đó cần quyền đăng nhập.
- Mọi code đọc account mapping phải xử lý `null`; Employee không có account không thể trở thành actor đăng nhập.
- Audit tạo Employee ghi `account_created` nhưng không ghi password.

## Security and authorization impact

- Không có account thì không có session và không vượt qua account/employment gate.
- Checkbox không thay đổi capability tạo Employee; server vẫn yêu cầu `people_domain.add_employee`.

## Data and contract impact

- `identity_user` chuyển thành nullable one-to-one mapping.
- `POST /people/employees/` nhận `create_account`; `username/password` chỉ bắt buộc khi giá trị là `true`.
- `username` trong HR projection có thể là `null`.

## Rollout and rollback

- Migration nới nullable mapping và thay constraint mã nhân sự.
- Rollback chỉ an toàn khi không còn Employee thiếu account hoặc mã vượt constraint cũ; phải kiểm dữ liệu trước khi rollback schema.

## Validation

- Test tạo có/không có account, chống mã trùng không phân biệt hoa/thường, account cleanup và audit không chứa password.

## Approval record

- Người chấp nhận: Người sở hữu project MRERP.
- Ngày chấp nhận: 2026-08-28.
- Bằng chứng/xác nhận: yêu cầu trực tiếp trong task hiện tại về checkbox tạo tài khoản và mã nhân sự nhập tự do, chỉ chống trùng.
