# Phase 1 — People/HR readiness register

Tài liệu này đánh giá từng story People/HR theo [Definition of Ready](definition-of-ready.md). Nó không thay đổi Definition of Ready chung.

## 1. Kết luận hiện tại

**Đã chốt:** data owner/module owner là MRERP People/HR; Identity Provider không sở hữu hồ sơ nhân sự.

**Đề xuất mục tiêu:** phạm vi, contract, data model, capability catalog, migration và test scenarios đã đủ để người sở hữu sản phẩm review.

**Đã chốt thêm:** HR tạo Employee với initial status `Thử việc`; Leader quyết định transition `Thử việc → Chính thức`; HR chọn có tạo account hay không. Khi chọn tạo account, account và Employee phải cùng thành công; khi không chọn, Employee được phép chưa có Identity mapping.

**Đã chốt bổ sung:** stack, mock Identity, account cleanup, field/scope, organization cardinality, mã nhân sự linh hoạt và promotion rule đã được duyệt qua ADR-0003 đến ADR-0007.

Kết quả sau duyệt: P1-PLAT-01 và P1-PPL-01 đến P1-PPL-08 đạt `Ready` cho phạm vi slice đã khóa. Nội dung ngoài slice vẫn không được tự mở rộng.

## 2. Đánh giá story

| Story | Trạng thái | Đã rõ | Blocker cần duyệt |
|---|---|---|---|
| P1-PLAT-01 | `Ready` | Mock Identity dev/test, production guard, session actor | Không |
| P1-PPL-01 | `Ready` | Self-profile, basic projection, failure states | Không |
| P1-PPL-02 | `Ready` | Staff team scope, Leader company scope, pagination/search | Không |
| P1-PPL-03 | `Ready` | Basic/HR projection, UUID, no-leak rule | Không |
| P1-PPL-04 | `Ready` | HR create, account tùy chọn, cleanup khi có account, initial `Thử việc` | Không |
| P1-PPL-05 | `Ready` | HR detail edit, Leader team promotion, note/audit | Không |
| P1-PPL-06 | `Ready` | Leader organization management, UUID/audit | Không |
| P1-PPL-07 | `Ready` | Một Team/Employee, nhiều Leader/Team, audit | Không |
| P1-PPL-08 | `Ready` | Audit và authorization evidence | Không |

## 3. Cổng đưa story sang Ready

Story People chỉ chuyển `Ready` khi:

- ADR-0003 xác nhận application stack/scaffold baseline.
- ADR-0004 xác nhận mock Identity context và trust boundary.
- ADR-0005 xác nhận People authorization và field policy đủ cho story.
- API/data contract liên quan được người sở hữu sản phẩm duyệt.
- Open decision ảnh hưởng trực tiếp được giải quyết hoặc phần đó bị loại khỏi scope.
- Acceptance scenario tương ứng không còn placeholder policy.

Không nhất thiết phải giải quyết mọi open decision của toàn MRERP; chỉ cần giải quyết những mục chặn story cụ thể.

## 4. Thứ tự mở khóa đề xuất

1. Chốt provisioning production cho Employee chưa có account khi triển khai Admin Panel/IdP thật.
2. Chốt Leader scope và người quản trị organization.
3. Chốt field `basic`, người được đọc và scope.
4. Chốt các employment rule còn lại nếu nằm trong slice.
5. Chấp nhận mock Identity contract, stack và API contract.
6. Đánh giá lại từng story theo Definition of Ready.
