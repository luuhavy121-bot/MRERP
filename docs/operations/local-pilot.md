# Chuẩn bị pilot MRERP trên local

**Phạm vi được người sở hữu sản phẩm xác nhận 03/10/2026:** hoàn thiện và kiểm tra local trước; nhân sự dùng tài khoản do công ty cấp riêng. Hướng hosting sau là dùng chung VPS ASSETCONTROL, nhưng chưa xác minh đủ tải và chưa chốt topology/Identity production. Không triển khai lên VPS trong đợt này.

Đây là runbook thao tác local. Điều kiện đạt/không đạt vẫn theo [tiêu chí nghiệm thu](../04-tieu-chi-nghiem-thu.md), [test strategy](../testing/test-strategy.md) và [readiness production](deployment.md#9-readiness-trước-production), không tạo cổng nghiệm thu cạnh tranh.

## Kiểm tra hiện trạng

Từ root repository, với Docker đang chạy:

```powershell
docker compose up -d
python scripts/local_ops.py check
```

Nếu mới cập nhật công cụ, rebuild backend trước: `docker compose up -d --build backend`. Báo cáo chỉ in số lượng/tình trạng, không xuất mật khẩu, tên, email hoặc hồ sơ nhân sự. Công cụ kiểm tra môi trường development/test, PostgreSQL, migration, các dịch vụ và dữ liệu tổ chức. Command Django tương ứng là `docker compose exec -T backend python manage.py local_readiness`.

Hồ sơ chưa có tài khoản là trường hợp được hỗ trợ, không tự coi là lỗi hoặc tự tạo tài khoản. HR/Leader chọn đúng 5–10 người pilot, kiểm tra Team và quyền theo ma trận đã duyệt. Dữ liệu mẫu và hồ sơ thật phải được rà soát thủ công; không tự xóa theo tên/mã hoặc seed lại để dọn dữ liệu. Chức năng cấp tài khoản local hiện có không thay thế Identity Provider production.

## Backup local và diễn tập khôi phục

```powershell
python scripts/local_ops.py snapshot
python scripts/local_ops.py restore-drill --snapshot backups/local-YYYYMMDDTHHMMSSZ-xxxxxxxx
```

Dùng đúng đường dẫn được lệnh snapshot in ra. Snapshot tạm dừng backend/worker/Beat, xác minh chúng đã dừng, chụp PostgreSQL và media, rồi khởi động lại đúng những dịch vụ trước đó đang chạy trong `finally`. Đợt backup có gián đoạn local; không thao tác/ghi dữ liệu bằng công cụ khác trong lúc chụp. Frontend/database/Redis được giữ chạy. Nếu thao tác lỗi, kiểm tra `docker compose ps` và khởi động dịch vụ cần thiết; không dùng folder có `FAILED.txt`.

Backup nằm trong `backups/` đã bị Git ignore, gồm dump, media nén, bản media đã copy và manifest SHA-256. Đây là bản sao **chưa mã hóa**, chỉ nằm trên máy local, không đáp ứng backup ngoài VPS. Hạn chế quyền truy cập thư mục bằng quyền hệ điều hành; không gửi dump, media hoặc manifest ra Git/chat công khai. Lịch backup, retention, mã hóa và nơi lưu ngoài host chưa được chọn.

Restore drill kiểm checksum/path, tạo database `mrerp_drill_` với UUID ngẫu nhiên, restore vào database đó, so số dòng của mọi bảng, giải nén media vào thư mục drill riêng và kiểm schema/application bằng Django. Lệnh không restore vào database đang dùng, không seed, không chạy migration hoặc worker trên bản restore. Database drill tự xóa sau kiểm tra; media/evidence local được giữ trong `backups/drills/`. Không coi số dòng/checksum là nghiệm thu đầy đủ nghiệp vụ hoặc bảo đảm production rollback. Nếu cleanup bị lỗi, chỉ xử lý đúng database drill ghi trong thư mục evidence sau khi xác minh tên; không đụng database chính.

## Luồng cần HR/Leader nghiệm thu

Kiểm thử tự động trên PostgreSQL local:

```powershell
docker compose exec -T backend python manage.py test --noinput
python scripts/test_local_ops.py
python scripts/check_docs.py
git diff --check
```

Smoke test đồng thời có thể chạy riêng bằng `docker compose exec -T backend python manage.py test people_domain.test_local_pilot_load --noinput`. Bài test dùng database test riêng, 10 tài khoản giả và 500 Task; thực hiện 150 lượt đọc HTTP đã đăng nhập qua Django LiveServer, kiểm tra trạng thái HTTP và phạm vi Task của từng tài khoản. Không seed/reset tài khoản của database đang dùng. Đây là kiểm tra đọc trong môi trường test, chưa đo thao tác ghi đồng thời, upload, Celery hoặc năng lực production/VPS; chưa có SLA được chốt.

**Bằng chứng local ngày 03/10/2026:** snapshot và restore drill đã khớp số dòng của 57 bảng, khôi phục 55 file media và đạt kiểm tra ứng dụng/schema trên database riêng. Smoke test riêng đạt 150/150 lượt đọc với 10 tài khoản đồng thời, không lỗi HTTP; p50 123,18 ms, p95 380,34 ms, tối đa 421,10 ms trên máy kiểm thử. Thời gian phụ thuộc cấu hình máy và tải tại thời điểm chạy, không phải cam kết độ trễ. Evidence backup chi tiết chỉ lưu local trong `backups/`.

Toàn bộ 143 backend tests cũng đạt trên PostgreSQL (35,54 giây); smoke test trong lần chạy tổng thể có p95 410,34 ms. Các kết quả tự động này không thay thế nghiệm thu nghiệp vụ của HR/Leader bên dưới.

- Nhân sự/Team: đúng người, mã, Team và Leader; cấp/khóa tài khoản và employment theo [People acceptance](../testing/people-account-lifecycle-acceptance.md).
- Nghỉ & Công: gửi/duyệt phép, nhập file, preview, mapping và phạm vi xem theo [Leave/Attendance acceptance](../testing/leave-attendance-acceptance.md).
- Đánh giá/tuyển dụng: Leader chỉ trong Team, ứng viên công khai và HR duyệt theo [HR expansion acceptance](../testing/hr-expansion-acceptance.md).
- Sao & Đổi thưởng: quota, giữ/hoàn, duyệt/giao quà theo [Phase 3 acceptance](../testing/phase-3-acceptance.md).
- Công việc: giao/nhận/hoàn thành, file và scope theo [Dashboard/Feed/Task acceptance](../testing/dashboard-feed-task-acceptance.md).

Ghi kết quả/ngoại lệ vào acceptance tương ứng. CRM hiện là demo dữ liệu giả; không đưa vào dữ liệu vận hành của pilot.

## Các quyết định cần chốt trước VPS

- Tài khoản công ty cấp đã chốt về trải nghiệm, **chưa chọn IdP**, subject mapping, provisioning/reset/revoke hoặc hành vi khi IdP lỗi (OD-01/02/19).
- Dùng chung host ASSETCONTROL là hướng người dùng chọn để đánh giá. Cần kiểm kê tài nguyên, dung lượng, backup và kiểm tải; không cam kết VPS hiện tại đủ, không đọc Vault hoặc database chéo product.
- Domain/HTTPS/proxy, secret delivery, backup ngoài host và chỉ tiêu phục hồi cần duyệt (OD-12/15/21 và [deployment](deployment.md)).
- Không dùng nguyên Compose local, không bỏ guard Mock Identity, không bật persona demo trên Internet để chạy pilot production.

## Kịch bản demo HR ngày 06/10

Theo [ADR-0021](../decisions/0021-hr-demo-half-day-and-workflow.md), mở MRERP local và dùng tài khoản demo hoặc tài khoản pilot đã được kiểm tra đúng Team/quyền:

1. **Leader — Đánh giá nhân sự:** chọn tháng và nhân sự trong Team; nhập KPI hoặc sao chép cấu trúc tháng trước. Nhập mức hoàn thành, nhận xét; xem tổng trọng số, điểm và điều kiện chốt. Chốt để nhân sự xem/xác nhận; HR mở lại với lý do khi cần. Lịch sử cũ vẫn còn.
2. **Leader/HR — Tuyển dụng:** Leader tạo bản nháp, xem trước và gửi duyệt; HR duyệt để tin xuất hiện ở `/careers`. Nộp hồ sơ giả có CV rồi kiểm tra pipeline, tìm/lọc, ghi chú và lịch phỏng vấn. Tên người phụ trách nhập tự do; chưa gửi email hay đồng bộ lịch ngoài hệ thống.
3. **Nhân sự/Leader — Nghỉ & Công:** gửi đơn sáng hoặc chiều, Leader duyệt đúng Team. Xem lịch nghỉ đã duyệt; lịch này không hiển thị lý do riêng tư. HR xem công dự kiến: thứ Hai–thứ Bảy cả ngày, trừ ngày lễ và các buổi nghỉ đã duyệt. Công thực tế nhập Excel được giữ nguyên và xem riêng.

**Bằng chứng kỹ thuật 03/10/2026:** 152 backend tests đạt trên PostgreSQL; sau thay đổi kiểm phạm vi thông báo, 4 tests Interview chạy lại đạt, gồm test mới chặn người có capability nhưng ngoài Team/company scope. Sáu luồng E2E đạt qua các lượt chạy trên database SQLite giả riêng; ba luồng nâng cấp mới chạy lại cùng một lượt sau sửa giao diện, 3/3 đạt. Frontend build đạt, lint không có lỗi (7 warnings React), OpenAPI validate không có lỗi (6 warnings đặt tên enum), migration drift không có và docs/diff checks đạt. Reviewer giao diện chấm hai sửa cuối về ô buổi nghỉ và nhập KPI mobile là resolved; đây là bằng chứng kỹ thuật, chưa thay nghiệm thu HR/Leader.

Docker local đã backup trước khi áp dụng ba migration bổ sung, các dịch vụ đang chạy và không còn migration chờ. Không seed/reset tài khoản hay nhập hồ sơ thật vào database đang dùng trong các bài E2E. Cách chạy lại các luồng giả nằm trong [hướng dẫn fixture E2E](../../apps/mrerp/frontend/e2e/fixtures/README.md).
