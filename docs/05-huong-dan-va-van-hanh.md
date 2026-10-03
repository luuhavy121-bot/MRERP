# 05 — Hướng dẫn và vận hành

Tuyển dụng theo [ADR-0022](decisions/0022-short-recruitment-pipeline.md): điền kế hoạch sử dụng nhân sự trong phần nội bộ của bản nháp. Pipeline Mới → Sàng lọc → Phỏng vấn; sau phỏng vấn chọn Đã tuyển hoặc Từ chối. HR/CEO vẫn duyệt tin và chuyển hồ sơ đã tuyển thành Employee.

Repository đã có bản chạy local của People/HR Foundation trong Phase 1. Chưa có môi trường hoặc tài khoản production. Tài liệu này ghi phần có thể vận hành ở local và khung production cần hoàn thiện; chi tiết hạ tầng thuộc [Deployment và vận hành](operations/deployment.md).

## Dành cho người sử dụng

**Yêu cầu trải nghiệm đã chốt:**

1. Nhân sự mở MRERP và đăng nhập qua Identity chung.
2. Dashboard hiển thị không gian cá nhân theo quyền.
3. Người dùng mở CRM/ASSETCONTROL/MREKANBAN được cấp quyền mà không nhập lại mật khẩu.
4. Product đích vẫn tự kiểm quyền trước khi trả dữ liệu.

**Đề xuất mục tiêu:** thực hiện đăng nhập chung bằng OIDC/OAuth 2.0. Identity Provider và chi tiết session vẫn chưa quyết định.

**Đã có ở local:** đăng nhập mock bằng session cookie; People/Team/hồ sơ/account; Leave/Attendance baseline; Tổng quan general/private; Bảng tin audience company/Team/Employee; Task/Goal/recurrence; Phase 3 Recruitment, Documents, Recognition/Stars và Personal Settings. Protected file luôn tải qua API có ACL. Các phần chưa được người sở hữu sản phẩm chấp nhận vẫn `Implementation hoàn tất / Chờ nghiệm thu`.

Thanh trên cùng luôn hiển thị trung tâm thông báo cá nhân và menu **Cài đặt**. Người dùng có thể xem số thông báo chưa đọc từ mọi tab, đổi nền sáng/tối trên thiết bị hiện tại hoặc đăng xuất. Preference theme được lưu cục bộ; không chứa credential và không thay đổi capability.

Trong môi trường development/test, thanh trên cùng có bộ chọn **Xem theo vai trò** để đổi giữa các persona demo đã seed: CEO toàn quyền People, HR People, Leader Team Alpha, Staff Team Alpha và Staff Team Beta. Thao tác này tạo lại session ở backend và vì vậy dùng đúng capability, scope và field policy của persona được chọn; đây không phải cách frontend giả quyền. Danh sách persona là allow-list phía server, không nhận username tùy ý. Bộ chọn và endpoint tương ứng không khả dụng ngoài development/test. Captain và Manager chưa xuất hiện vì dự án chưa chốt capability/người dùng demo cho hai vai trò này.

Mục **Tiến độ** trong thanh điều hướng là bề mặt quản trị tạm thời: hiển thị phase, module, bằng chứng chất lượng, open decisions và cổng tiếp theo. Chỉ số lấy từ roadmap/source of truth và phải cập nhật cùng bằng chứng thực tế; mục này tự ẩn khi tổng tiến độ đạt 100%.

**Chưa có:** URL production đã duyệt, Identity production, tài khoản thật, hướng dẫn khôi phục mật khẩu và quy trình hỗ trợ người dùng.

## Chạy local

1. Backend: tạo Python 3.12 virtual environment, cài `apps/mrerp/backend/requirements.txt`, migrate và chạy server cổng 8000.
2. Seed tài khoản giả bằng lệnh `python manage.py seed_demo --password <mật-khẩu-local>`; không commit mật khẩu. Sau khi đăng nhập một tài khoản demo, có thể dùng **Xem theo vai trò** để kiểm tra nhanh các scope đã duyệt.
3. Frontend: cài đúng dependency từ lockfile bằng `npm ci`, sau đó `npm run dev`; Vite chạy cổng 4173 và proxy `/api` tới backend.
4. Có thể dùng `docker compose up --build` sau khi cấp `POSTGRES_PASSWORD` và `MRERP_SECRET_KEY` trong môi trường local. Compose chạy PostgreSQL, backend, frontend, Redis, Celery worker, Celery Beat và persistent media volume.

Chi tiết câu lệnh nằm tại README của [backend](../apps/mrerp/backend/README.md) và [frontend](../apps/mrerp/frontend/README.md).

## Dành cho người vận hành

Các runbook cần được tạo trước khi mở production:

- Deploy và rollback từng product.
- Backup và restore drill.
- IdP outage và session degradation.
- ASSETCONTROL emergency access sau khi policy được duyệt.
- CRM worker overload/queue backlog.
- Dashboard snapshot stale hoặc sync thất bại.
- MKTLogin API gián đoạn, mapping lệch hoặc đối soát thất bại sau khi integration được triển khai.
- Redis/worker gián đoạn: request Feed/Task vẫn hoạt động; kiểm queue/worker và xác nhận recurrence backfill sau khi phục hồi.
- Media volume đầy, file bị thiếu, Candidate anonymization hoặc Documents retention purge lỗi.
- Secret rotation và service credential rotation.
- Điều tra audit và sự cố lộ dữ liệu.

## Hành vi khi integration lỗi

**Đã chốt.** Dashboard vẫn hiển thị HR, Task và nghiệp vụ nội bộ; vùng dữ liệu CRM/ASSETCONTROL dùng snapshot gần nhất, timestamp và cảnh báo stale.

**Chưa quyết định.** Timeout, retry, stale threshold, SLA và escalation path cụ thể.

Đối với MKTLogin, mục tiêu resource linkage đã chốt nhưng contract vận hành vẫn **Chưa quyết định** theo OD-27. Không được báo “đã đồng bộ” nếu API không xác nhận; runbook cụ thể chỉ được hoàn thiện sau khi API/gói công ty đang dùng được kiểm kê.

Không được tạo runbook break-glass có thể thực thi trước khi OD-03 được người có thẩm quyền quyết định và ADR được chấp nhận.

## Backup và phục hồi

**Đề xuất mục tiêu bắt buộc.** Backup phải nằm ngoài VPS và phải diễn tập restore. Chỉ có snapshot hoặc file backup chưa chứng minh hệ thống phục hồi được.

**Đã chốt cục bộ:** local-media Feed/Task/Documents/Recruitment nằm trong persistent volume và phải vào backup; notification/file soft-delete giữ 30 ngày; ứng viên bị từ chối được ẩn danh sau sáu tháng. **Chưa quyết định:** công cụ backup, retention backup, RPO/RTO và object storage production.

## Quan sát hệ thống

**Đề xuất mục tiêu.** Cần structured logs, error tracking, uptime, resource/database/queue metrics và integration freshness.

**Chưa quyết định.** Công cụ monitoring/error tracking/reverse proxy cụ thể.

## Đọc sâu hơn

- [Deployment và vận hành](operations/deployment.md)
- [Quản lý cấu hình và secret](operations/configuration-and-secrets.md)
- [Identity và phân quyền](architecture/identity-and-authorization.md)
- [Tích hợp hệ sinh thái](architecture/ecosystem-integration.md)
- [Open decisions](decisions/open-decisions.md)

Tiếp theo: [06 — Kế hoạch triển khai](06-ke-hoach-trien-khai.md).

## Tuyển dụng công khai và đánh giá KPI

- Leader: Tuyển dụng → Yêu cầu tuyển → Tạo yêu cầu → Lưu nháp/Gửi duyệt. HR/CEO xem đầy đủ nội dung trước Duyệt; duyệt công khai ngay. Tin đang tuyển cung cấp link /careers/{slug}; Đóng tin ngừng nhận hồ sơ.
- Ứng viên: /careers → vị trí → thông tin, CV và consent → Gửi hồ sơ. Leader quản lý pipeline Team; chỉ HR/CEO chuyển thành Employee.
- Leader: Đánh giá nhân sự → tháng/nhân sự → tạo phiếu → KPI/trọng số/mức hoàn thành/nhận xét → chốt. Nhân sự xem Đánh giá của tôi và xác nhận. HR mở lại cần lý do; chốt lại sinh revision mới.
- Trước cập nhật local Docker: backup database/media, build backend/frontend, chạy migrate, rồi recreate backend/frontend. Migration cập nhật quyền group chuẩn hiện có, không cần seed lại và không đổi mật khẩu.
- Public careers chỉ truy cập được từ ngoài khi deployment được cấu hình public routing/HTTPS. Mock Identity hiện tại không dùng production. Proxy phải chuyển địa chỉ client tin cậy; Redis cache dùng chung để giới hạn 5 hồ sơ/IP/giờ. Public file tối đa 10 MB và không có download ẩn danh.
- Rollback: quay về image trước, giữ schema bổ sung; không reverse migration khi đã có dữ liệu mới. Database và media phải phục hồi cùng mốc nếu cần restore.

## Nhập bảng chấm công Excel

HR mở Nghỉ & Công → Chấm công → Chọn file Excel. Kiểm tra tháng/dữ liệu, ghép mỗi mã chấm công với một Employee, xác nhận nhập. Lần sau nhớ mapping. Nếu có ngày đã nhập, chọn xác nhận thay thế; khi báo dữ liệu thay đổi cần tải file để xem trước lại. Ô trống khác số 0. Công dự kiến vẫn có tab riêng và không điều chỉnh kết quả nhập.

Leader xem Team, nhân sự xem bản thân. Chọn tháng và bấm ngày để xem chi tiết; HR xem 100 đợt nhập gần nhất. Bản xuất không mặc định đã chốt công. Không tự nhập file thật để demo.

Trước migration ADR-0019, backup DB; build backend/worker/beat với dependency Excel, migrate rồi restart. Không seed lại DB có dữ liệu. Rollback app giữ schema bổ sung; phục hồi DB từ backup khi cần, không reverse migration làm mất công đã nhập. Snapshot đã phân tích nằm trong DB và đi cùng backup; không lưu Excel gốc.

## Sao & Đổi thưởng

HR/CEO tạo quà và đặt hạn mức sao Team/tháng tại Sao & Đổi thưởng. Mẫu gợi ý chỉ điền form; cần kiểm tra chi phí sao, tồn khả dụng và trạng thái hoạt động trước khi lưu. Leader cấp sao trong hạn mức; ghi nhận đóng góp thực hiện trong pane Đánh giá nhân sự theo Employee/tháng.

Nhân sự chọn quà, xác nhận chi phí và gửi yêu cầu: sao được giữ ngay. HR/CEO khác duyệt rồi xác nhận đã trao; hủy trước khi trao hoặc từ chối cần lý do, hoàn sao/tồn một lần. Sao khả dụng khác sao đang giữ; đổi thưởng không làm giảm điểm xếp hạng.

Trước migration ADR-0020, backup DB; migrate rồi cập nhật app. Không seed lại DB có dữ liệu hoặc tự kích hoạt catalog. Khi rollback, giữ schema bổ sung; không reverse migration xóa quà/yêu cầu/ledger đã phát sinh. Khi cần khôi phục dữ liệu, dùng backup cùng mốc và đối chiếu các quà đã trao thực tế. Ngân sách tiền mặt CEO chưa triển khai.

## Demo HR ngày 06/10

Theo [ADR-0021](decisions/0021-hr-demo-half-day-and-workflow.md): Leader tự nhập KPI, có thể chọn Sao chép KPI tháng trước rồi nhập mức hoàn thành mới. Khung có lịch sử các tháng và điều kiện chốt còn thiếu.

Tuyển dụng: nhập tin → Xem trước tin tuyển → gửi duyệt. Pipeline có tìm/lọc và khung Lịch phỏng vấn & ghi chú; Lưu trước khi chuyển stage. Thời gian nhập theo múi giờ thiết bị. Tên người phụ trách là thông tin lịch, không cấp quyền; chưa gửi email/SMS.

Xin nghỉ: chọn ngày và Từ buổi/Đến buổi; cùng ngày/cùng buổi là nửa ngày. Leader chọn duyệt/từ chối, nhập ghi chú rồi Xác nhận xử lý. Lịch nghỉ chỉ hiển thị đơn đã duyệt và giữ riêng lý do. Công chuẩn thứ Hai–thứ Bảy cả ngày; công thực tế Excel giữ nguyên.

Backup DB/media trước migrate và restart backend/worker/Beat/frontend; không seed lại hoặc đổi mật khẩu. Rollback giữ schema bổ sung; app cũ không được xử lý đơn nửa ngày. Mốc này demo local, không triển khai production.
