# AGENTS.md — MRERP Platform

**Cập nhật được duyệt 01/10/2026:** ưu tiên [Tuyển dụng công khai và đánh giá KPI](docs/product/hr-expansion-requirements.md) trước MKTLogin theo ADR-0017/0018. Quyền Leader với CV/pipeline và quy trình draft → gửi duyệt thay thế baseline tuyển dụng cũ ở phần bên dưới. Các phần khác giữ trạng thái riêng.

## 1. Phạm vi repository

Repository này dành cho hệ sinh thái MRERP mới. MRERP Core và MRECRM dự kiến nằm trong cùng monorepo nhưng là các deployable có ranh giới riêng. ASSETCONTROL và repository MREKANBAN hiện tại không được sao chép vào repository này ở Phase 0.

Phase 0 đã hoàn tất. People/HR Foundation của Phase 1 đã được nghiệm thu; các phần mở rộng Phase 1 và Phase 2 giữ trạng thái riêng theo source of truth. Phase 3 đã được hiện thực theo ADR-0013 và đang chờ nghiệm thu. Theo yêu cầu mới nhất, mục tiêu tích hợp tiếp theo là liên kết tài nguyên ASSETCONTROL với MKTLogin qua API theo ADR-0014. Công ty chỉ dùng MKTLogin trong phạm vi này; không đưa MKT City vào dự án và không xây lại đầy đủ MKTLogin. Không mở rộng sang Payroll, máy chấm công, reward redemption/catalog chưa chốt hoặc CRM nếu chưa có yêu cầu mới.

## 2. Thứ tự bắt buộc trước khi làm việc

1. Đọc file này.
2. Đọc [README.md](README.md).
3. Đọc đường đọc chính dành cho người sở hữu sản phẩm theo đúng thứ tự:
   1. [01 — Tổng quan sản phẩm](docs/01-tong-quan-san-pham.md).
   2. [02 — Yêu cầu sản phẩm](docs/02-yeu-cau-san-pham.md).
   3. [03 — Thiết kế kỹ thuật](docs/03-thiet-ke-ky-thuat.md).
   4. [04 — Tiêu chí nghiệm thu](docs/04-tieu-chi-nghiem-thu.md).
   5. [05 — Hướng dẫn và vận hành](docs/05-huong-dan-va-van-hanh.md).
   6. [06 — Kế hoạch triển khai](docs/06-ke-hoach-trien-khai.md).
4. Đọc [docs/README.md](docs/README.md) và các source of truth chuyên sâu liên quan đến task.
5. Đọc [docs/decisions/open-decisions.md](docs/decisions/open-decisions.md).
6. Đọc các ADR đã được chấp nhận có liên quan.
7. Chỉ sau đó mới kiểm tra code hoặc prototype liên quan.

Quy ước branch, commit, pull request và kiểm tra local nằm tại [CONTRIBUTING.md](CONTRIBUTING.md).

Prototype chỉ là tài liệu tham khảo giao diện. Không được dùng prototype để suy ra backend, database, Identity, authorization, security hoặc kiến trúc production.

## 3. Nhãn trạng thái quyết định

- **Đã chốt**: được phép dùng làm yêu cầu hoặc ràng buộc thiết kế.
- **Đề xuất mục tiêu**: hướng đi được lựa chọn để tiếp tục thiết kế, nhưng cần ADR được chấp nhận trước khi hiện thực nếu ảnh hưởng kiến trúc, bảo mật, dữ liệu hoặc vận hành.
- **Chưa quyết định**: không được tự biến thành quyết định. Phải dừng ở thiết kế, nêu lựa chọn và hỏi người dùng.
- **Không làm**: giới hạn chủ động của dự án.

Không được nâng trạng thái từ **Đề xuất mục tiêu** hoặc **Chưa quyết định** lên **Đã chốt** bằng suy luận.

## 4. Ưu tiên nguồn khi có mâu thuẫn

1. Xác nhận trực tiếp mới nhất của người dùng trong task hiện tại.
2. Source of truth chuyên sâu được liệt kê trong `docs/README.md`; các file `01–06` là đường đọc tóm tắt và phải dẫn về nguồn chịu trách nhiệm chính.
3. Code và kết quả chạy thực tế của product tương ứng.
4. ADR đã được chấp nhận và đã được phản ánh hoặc đang yêu cầu phản ánh vào source of truth.
5. Prototype, benchmark và tài liệu đề xuất cũ.
6. Suy luận của AI.

Chỉ viện dẫn “xác nhận trực tiếp mới nhất” khi xác nhận đó thực sự xuất hiện trong task hoặc tài liệu người dùng cung cấp. Khi phát hiện mâu thuẫn, phải nêu rõ các nguồn, trạng thái quyết định và tác động. Không âm thầm chọn một phương án nếu nó ảnh hưởng nghiệp vụ, quyền, dữ liệu, bảo mật, migration hoặc vận hành.

## 5. Ranh giới bắt buộc

- MRERP là nguồn chuẩn của Employee, Team, employment status và Task nghiệp vụ. Cấu hình MRE hiện dùng cơ cấu phẳng `CEO → Team → Employee`; Department không phải tầng tổ chức hoạt động.
- Identity Provider sở hữu credential, quy trình đăng nhập, subject và phiên SSO. Identity Provider cụ thể chưa được chọn.
- MRECRM sở hữu Customer, Order, Product, Channel, connector, FFM, đối soát và báo cáo CRM.
- ASSETCONTROL sở hữu Resource, Grant, Vault và audit tài nguyên; không gửi secret sang MRERP.
- MKTLogin là hệ thống bên ngoài vận hành môi trường/tài khoản Marketing. Mục tiêu cuối là tài nguyên được quản lý trong ASSETCONTROL liên kết với tài nguyên thật trong MKTLogin qua API; MRERP không clone MKTLogin và không sở hữu dữ liệu phiên của nó.
- MKT City không thuộc phạm vi dự án hiện tại.
- Hiện chỉ CEO và Leader được cấp quyền truy cập ASSETCONTROL. Việc mở cho đối tượng khác chưa được quyết định.
- MREKANBAN hiện tại chỉ tham chiếu Task MRERP bằng UUID và có thể sở hữu cấu hình view. Việc retire hay tiếp tục làm client/view chuyên sâu dài hạn chưa được quyết định.
- Không product nào đọc hoặc sửa trực tiếp database của product khác.
- Frontend không phải hàng rào bảo mật. Endpoint nhạy cảm phải fail-closed ở server.

## 6. Giới hạn chủ động

- Không phát triển MRERP trong repository hoặc permanent worktree ASSETCONTROL.
- Không import dữ liệu, secret hoặc Vault của Nhà ZUZU vào MRERP.
- Không chọn Identity Provider, service-to-service authentication, break-glass hoặc policy chưa chốt.
- Không chia microservice theo từng menu/module ở giai đoạn đầu.
- Không dùng link đơn thuần để tuyên bố đã tích hợp product.
- Không truyền access token qua URL hoặc lưu access token dài hạn trong `localStorage`.
- Không hard-code phòng ban, team hoặc cấp bậc MRE vào lõi authorization.
- Không gọi CRM hoặc ASSETCONTROL đồng bộ trong request tải Dashboard.

## 7. Yêu cầu khi thay đổi hệ thống

- Xác định product/module sở hữu dữ liệu trước khi sửa.
- Đọc [glossary](docs/glossary.md) và không tự tạo thuật ngữ cạnh tranh cho cùng một khái niệm.
- Ghi ADR cho quyết định kiến trúc thuộc nhóm **Đề xuất mục tiêu** hoặc khi giải quyết một mục **Chưa quyết định**.
- Nếu phát hiện khoảng trống mới có tác động dài hạn, bổ sung open decision thay vì âm thầm chọn phương án.
- Cập nhật source of truth liên quan khi ADR được chấp nhận.
- Với endpoint nhạy cảm, tối thiểu phải test allowed, thiếu capability, ngoài scope, field redaction và account/employment không hợp lệ.
- Không đưa secret hoặc dữ liệu production vào Git, fixture hay tài liệu công khai.
- Giữ MRERP hoạt động khi integration khác tạm lỗi.
- Trước commit, chạy `python scripts/check_docs.py` và `git diff --check`.

## 8. Definition of Done chung

Source of truth cho điều kiện đạt/không đạt là [docs/04-tieu-chi-nghiem-thu.md](docs/04-tieu-chi-nghiem-thu.md). Chiến lược test kỹ thuật nằm tại [docs/testing/test-strategy.md](docs/testing/test-strategy.md). Agent phải áp dụng hai tài liệu này thay vì tạo một Definition of Done cạnh tranh trong task hoặc code.

**Cập nhật được duyệt 01/10/2026:** [ADR-0019](docs/decisions/0019-attendance-excel-import.md) cho phép nhập kết quả chấm công Excel HR. Kết nối máy và payroll vẫn ngoài phạm vi.

**Cập nhật được duyệt 02/10/2026:** [ADR-0020](docs/decisions/0020-stars-redemption-and-recognition.md) mở catalog/đổi thưởng, hạn mức sao Team và ghi nhận trong Đánh giá nhân sự; thay giới hạn reward chưa chốt ở baseline trên. Ngân sách tiền mặt tổng CEO còn hoãn.
