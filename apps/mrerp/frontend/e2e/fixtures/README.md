# Fixture kiểm thử demo HR

`hr_demo.py` chỉ tạo KPI tháng trước và ứng viên giả cho `hr-demo-upgrade.spec.ts`. Script từ chối PostgreSQL và SQLite ngoài thư mục `tmp/` của repository. Dùng database mới cho mỗi lượt vì bài test chốt/mở lại phiếu và duyệt nghỉ. Không chạy `seed_demo` trên database Docker đang dùng.

Từ root repository, dùng Python virtualenv đã cài `apps/mrerp/backend/requirements.txt`. Chuẩn bị trong một cửa sổ PowerShell riêng:

```powershell
$env:MRERP_DB_ENGINE = 'sqlite'
$taskDbName = 'hr-e2e-' + [guid]::NewGuid().ToString('N') + '.sqlite3'
$env:MRERP_SQLITE_PATH = Join-Path $PWD "tmp/$taskDbName"
$env:MRERP_MEDIA_ROOT = Join-Path $PWD "tmp/$taskDbName-media"
$env:MRERP_CSRF_TRUSTED_ORIGINS = 'http://127.0.0.1:4177'
$env:DJANGO_SETTINGS_MODULE = 'config.settings'
$env:PYTHONPATH = Join-Path $PWD 'apps/mrerp/backend'
.venv/Scripts/python.exe apps/mrerp/backend/manage.py migrate --noinput
.venv/Scripts/python.exe apps/mrerp/backend/manage.py seed_demo --password Playwright-Only-1234!
.venv/Scripts/python.exe apps/mrerp/frontend/e2e/fixtures/hr_demo.py
.venv/Scripts/python.exe apps/mrerp/backend/manage.py runserver 127.0.0.1:8007 --noreload
```

Mật khẩu trên chỉ dành cho tài khoản giả trong DB test. Mở cửa sổ PowerShell thứ hai tại root:

```powershell
$env:VITE_API_PROXY_TARGET = 'http://127.0.0.1:8007'
npm --prefix apps/mrerp/frontend run dev -- --host 127.0.0.1 --port 4177 --strictPort
```

Sau khi hai server sẵn sàng, cửa sổ thứ ba:

```powershell
$env:E2E_BASE_URL = 'http://127.0.0.1:4177'
npm --prefix apps/mrerp/frontend run e2e -- hr-demo-upgrade.spec.ts
```

Dừng hai server bằng Ctrl+C sau kiểm thử. Các file test/media nằm trong `tmp/` bị Git ignore; không thay database/media của Docker local. Bài test kiểm ba luồng KPI, phỏng vấn/pipeline và nghỉ nửa ngày thứ Bảy; không phải seed demo nghiệp vụ thật hay đánh giá tải production.
