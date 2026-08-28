# Test strategy

Tài liệu này chịu trách nhiệm chính về chiến lược kiểm thử kỹ thuật. Điều kiện đạt/không đạt cấp sản phẩm nằm tại [04 — Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md).

## 1. Trạng thái

**Đề xuất mục tiêu.** Chiến lược application dưới đây cần được cụ thể hóa theo từng vertical slice. Phase 0 chưa có application code; kiểm tra repository hiện được thực thi bằng `scripts/check_docs.py` và GitHub Actions.

## 2. Các lớp kiểm thử

- Unit test cho policy, service/use case và logic thuần.
- API test cho contract, validation và authorization.
- Integration test cho database, queue và adapter trong phạm vi kiểm soát.
- Contract test giữa MRERP, CRM, ASSETCONTROL và MREKANBAN.
- E2E cho các luồng nghiệp vụ quan trọng.
- Migration/rollback test khi thay đổi dữ liệu hoặc identity mapping.
- Load/resilience test cho CRM worker, Dashboard snapshot và integration failure.

## 3. Authorization test bắt buộc

**Đã chốt.** Mỗi endpoint nhạy cảm tối thiểu phải có:

- Allowed.
- Denied do thiếu capability.
- Denied do ngoài scope.
- Field redaction hoặc absence.
- Denied khi account khóa hoặc employment kết thúc.

Thêm object-state/ownership test khi endpoint có object rule. Không tin role, team, owner hoặc capability từ client.

## 4. Contract và data ownership

Test phải chứng minh:

- UUID/mapping ổn định.
- Product không đọc database chéo.
- Snapshot không trở thành nguồn chuẩn.
- Contract version tương thích theo policy được duyệt.
- Payload không chứa field hoặc secret ngoài quyền.

## 5. Resilience

Các test cần có khi module tương ứng xuất hiện:

- CRM lỗi nhưng Dashboard vẫn tải snapshot.
- Snapshot hiển thị timestamp/stale state.
- Worker retry có giới hạn và không xử lý trùng.
- Queue backlog/resource limit không kéo sập MRERP.
- Backup có thể restore thành môi trường chạy được.

Ngưỡng timeout, retry, stale, RPO/RTO và tải mục tiêu vẫn **Chưa quyết định**.

## 6. Bằng chứng nghiệm thu

- Test command và kết quả.
- Test data không chứa dữ liệu production.
- Contract diff khi payload thay đổi.
- Migration/rollback evidence.
- Authorization matrix cho phạm vi đã hiện thực.
- Load/restore evidence khi thay đổi có rủi ro tương ứng.

Story chỉ được đưa sang `Ready` khi đạt [Definition of Ready](definition-of-ready.md). Đây là cổng đầu vào của backlog, không thay thế Definition of Done hoặc điều kiện đạt/không đạt cấp sản phẩm.

## 7. Kiểm tra tài liệu trong Phase 0

Phase 0 chưa có application test suite, nhưng thay đổi tài liệu vẫn phải được kiểm tra:

- Tất cả relative Markdown link resolve được.
- Có đúng một đường đọc `01–06` và mỗi file dẫn tới tài liệu chuyên sâu.
- Mọi statement quyết định quan trọng có nhãn trạng thái.
- Open decision ID không trùng và được tham chiếu từ source liên quan.
- Không có scaffold/dependency ngoài phạm vi được yêu cầu.
- Không có secret, credential thật hoặc dữ liệu production.
- Không có mô tả biến prototype thành production source.

Lệnh chuẩn:

```text
python scripts/check_docs.py
git diff --check
```

Workflow `.github/workflows/repository-quality.yml` chạy checker khi push vào `main`, khi có pull request và khi được kích hoạt thủ công.

## 8. Tài liệu liên quan

- [Tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md)
- [Definition of Ready](definition-of-ready.md)
- [Task acceptance scenarios Phase 1](phase-1-task-acceptance.md)
- [Identity và phân quyền](../architecture/identity-and-authorization.md)
- [Deployment](../operations/deployment.md)
