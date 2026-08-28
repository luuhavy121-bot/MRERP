# Product backlog MRERP

Tài liệu này là source of truth cho cấu trúc Epic, trạng thái backlog và phạm vi được refinement. Thứ tự phase vẫn do [Roadmap MRERP](roadmap.md) chịu trách nhiệm chính; yêu cầu nghiệp vụ vẫn thuộc [Yêu cầu nghiệp vụ](business-requirements.md).

## 1. Chiến lược backlog

**Đã chốt.** Backlog dùng mô hình:

- Epic ở mức toàn roadmap để người sở hữu sản phẩm nhìn thấy toàn cảnh.
- Story chi tiết chỉ được viết cho phase sắp triển khai.
- Hiện chỉ Phase 1 được refinement xuống story.
- Không viết chi tiết toàn bộ MRERP quá sớm vì policy và scope còn thay đổi.

## 2. Trạng thái backlog

| Trạng thái | Ý nghĩa |
|---|---|
| `Idea` | Có trong định hướng nhưng chưa refinement |
| `Refining` | Đang làm rõ outcome, quyền, dữ liệu và acceptance criteria |
| `Ready` | Đạt [Definition of Ready](../testing/definition-of-ready.md) |
| `In progress` | Đang được hiện thực trong production code |
| `Accepted` | Đạt acceptance criteria và có bằng chứng kiểm thử |
| `Blocked` | Có blocker được ghi rõ; không được âm thầm giả định |

Visual prototype không tự chuyển story sang `In progress` hoặc `Accepted`.

## 3. Epic toàn roadmap

| Epic | Outcome | Phase mục tiêu | Trạng thái hiện tại |
|---|---|---|---|
| EPIC-00 | Source of truth, ADR, governance và repository quality | Phase 0 | `In progress` — chưa đóng Phase 0 |
| EPIC-01 | Identity contract, capability, scope và guard fail-closed | Phase 1 | `Ready` trong phạm vi mock Identity dev/test |
| EPIC-02 | Employee, Department, Team và employment status | Phase 1 | `Ready` — bắt đầu implementation |
| EPIC-03 | Task vertical slice chạy xuyên UI, API, DB, quyền, audit và test | Phase 1 | `Refining` |
| EPIC-04 | MRERP shell và Dashboard tối thiểu, sau đó snapshot/fallback | Phase 1–2 | `Refining` |
| EPIC-05 | Attendance/Leave và Approval theo từng loại | Phase 2 | `Idea` |
| EPIC-06 | Recognition và Rewards | Phase 3 | `Idea` — policy chưa quyết định |
| EPIC-07 | Recruitment, Documents và Personal Settings | Phase 3 | `Idea` |
| EPIC-08 | ASSETCONTROL và MREKANBAN transition | Phase 4 | `Idea` — cần audit product hiện hữu |
| EPIC-09 | MRECRM tối thiểu, worker, field policy và reporting read model | Phase 5 | `Idea` — cần ADR trước scaffold |

## 4. Phase 1 đang refinement

### EPIC-01 — Identity và permission foundation

**Đề xuất mục tiêu.** Cung cấp identity context giả lập có contract, account/employment gate, capability, data scope và audit actor mà không chọn Identity Provider thật.

ADR-0003 và ADR-0004 đã được chấp nhận; foundation đạt `Ready` trong dev/test, không chốt IdP production.

### EPIC-02 — People foundation

**Đề xuất mục tiêu.** Có dữ liệu tối thiểu cho Employee, Team, Department, employment status và quan hệ quản lý dùng trong Task authorization.

**Chưa quyết định:** danh mục cơ cấu MRE chính thức thuộc OD-16. Slice chỉ được dùng fixture/config đã duyệt, không hard-code vào permission core.

Theo yêu cầu ngày 28/08/2026, People/HR Foundation là vertical slice nghiệp vụ được refinement trước Task. Story chi tiết: [Phase 1 — People/HR Foundation](stories/phase-1-people-foundation.md). Trạng thái Ready/Blocked nằm tại [People readiness register](../testing/phase-1-people-readiness.md).

### EPIC-03 — Task vertical slice

**Đã chốt về data ownership.** MRERP sở hữu Task dài hạn.

**Đã chốt về permission baseline trong slice.** Áp dụng [ADR-0002](../decisions/0002-task-authorization-baseline.md) và [ma trận quyền Task](../architecture/task-authorization-matrix.md).

Story chi tiết: [Phase 1 — Task vertical slice](stories/phase-1-task-vertical-slice.md).

### EPIC-04 — Shell và Dashboard tối thiểu

**Đề xuất mục tiêu.** Shell hiển thị navigation theo capability; Dashboard ban đầu chỉ dùng dữ liệu MRERP. Snapshot CRM/ASSETCONTROL chưa thuộc slice đầu tiên.

## 5. Cách tính tiến độ backlog

**Đề xuất mục tiêu.** Khi Phase 1 có estimate được duyệt, tiến độ release dùng story point hoặc trọng số story đã `Accepted` chia tổng scope release đã commit. Không dùng số màn hình, dòng code hoặc số menu làm bằng chứng hoàn thành.

**Chưa quyết định.** Công cụ backlog, đơn vị estimate, cadence và release scope chính thức.

## 6. Tài liệu liên quan

- [Roadmap](roadmap.md)
- [Yêu cầu nghiệp vụ](business-requirements.md)
- [Definition of Ready](../testing/definition-of-ready.md)
- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Open decisions](../decisions/open-decisions.md)
