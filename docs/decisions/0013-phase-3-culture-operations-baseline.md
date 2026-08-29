# ADR-0013: Phase 3 — Văn hóa và vận hành nhân sự

- Status: `Accepted`
- Date: `2026-08-29`
- Deciders: `Người sở hữu sản phẩm MRERP`
- Related source of truth: `docs/product/phase-3-requirements.md`
- Related open decisions: `OD-05, OD-13, OD-14 (chỉ giải quyết một phần; không đóng)`
- Supersedes: `Không có`
- Superseded by: `Không có`

## Context

Người sở hữu sản phẩm yêu cầu ưu tiên Phase 3 trước phần còn lại của Phase 2 và đã trả lời một lượt các policy cần thiết cho Recruitment, Documents, Recognition, Stars và Personal Settings. Hai policy về người quản trị catalog/duyệt đổi thưởng và thời điểm giữ/trừ/hoàn sao khi đổi thưởng chưa được quyết định.

## Decision

**Đã chốt cục bộ cho Phase 3:**

- Recruitment là module code riêng dưới navigation Nhân sự. Leader tạo yêu cầu cho Team mình; HR/CEO tạo toàn công ty. Yêu cầu của Leader do HR duyệt một cấp; yêu cầu HR/CEO tạo được duyệt ngay.
- HR/CEO xem toàn bộ ứng viên; Leader chỉ xem ứng viên thuộc vị trí của Team mình. Pipeline nền là `Mới → Sàng lọc → Phỏng vấn → Đề nghị → Đã tuyển/Từ chối`.
- Chỉ HR/CEO chuyển ứng viên thành Employee; Employee bắt đầu `Thử việc`, account vẫn tùy chọn. Ứng viên bị từ chối được ẩn danh sau sáu tháng.
- Chỉ Leader, HR và CEO upload Documents. Audience gồm Employee, Team, company và HR confidential. Mỗi version tối đa 10 file, 25 MB/file; hỗ trợ allow-list ảnh, PDF, Office, TXT, CSV và ZIP.
- Documents có version history, soft-delete 30 ngày và protected download. Local-media persistent volume là baseline hiện tại; object storage production vẫn mở theo OD-14.
- Chỉ Leader/HR/CEO gửi Recognition; không tự gửi cho mình. Recognition không tự sinh sao.
- Leader cấp sao trong Team lãnh đạo; HR/CEO cấp toàn công ty; không tự cấp. Sao không hết hạn trong baseline; điều chỉnh bằng ledger entry có audit.
- Leaderboard tháng/quý/năm hiển thị cho toàn công ty nhưng không lộ giao dịch chi tiết của người khác.
- Notification xã hội có thể tắt; notification account, security, Task, Leave và Recruitment liên quan vẫn bắt buộc. Phase 3 chỉ gửi notification trong MRERP.
- Personal Settings chỉ bổ sung notification preferences và security summary; không xây lại Profile, Account hoặc theme.

## Deliberately unresolved

**Chưa quyết định:**

- Ai quản trị reward catalog và duyệt đổi thưởng.
- Sao bị giữ, trừ hoặc hoàn ở thời điểm nào trong workflow đổi thưởng.

Vì vậy baseline được phép hiện thực Recognition, Star ledger, balance và leaderboard; không được bật catalog management hoặc redemption workflow.

## Consequences

- Thêm bốn module modular-monolith: `preferences_domain`, `recruitment_domain`, `documents_domain`, `rewards_domain`.
- Candidate PII, protected file và star ledger cần authorization/audit riêng; không kế thừa permission từ People hoặc Task bằng suy luận.
- Phase 2 giữ nguyên trạng thái hiện tại; việc ưu tiên Phase 3 không phải nghiệm thu Phase 2.

## Validation

- Mỗi endpoint nhạy cảm có allowed, thiếu capability, ngoài scope, object state, field absence và account/employment gate tests.
- Protected download không lộ storage key; upload kiểm count/size/MIME/path traversal.
- Star ledger append-only, không self-grant và không lộ ledger người khác.
- Có E2E cho Recruitment, Documents, Recognition/Stars và Personal Settings.
- Migration được kiểm tra forward → reverse → forward trên database tạm.

## Approval record

- Người chấp nhận: Người sở hữu sản phẩm MRERP.
- Ngày chấp nhận: 2026-08-29.
- Bằng chứng: câu trả lời `1A, 2A, 3A, 4A, 5A, 6B, 7B, 8A, 9A, 10A, 11A, 12A, 13B, 14A, 15A, 16A, 17A, 20A, 21A, 22A` và yêu cầu tiếp theo `triển khai phase 3 luôn` trong task hiện tại.
