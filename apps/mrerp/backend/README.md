# MRERP backend

Django/DRF modular monolith cho People/HR Foundation. SQLite chỉ là đường chạy nhanh local; PostgreSQL 16 là database mục tiêu của Phase 1.

## Chạy nhanh bằng SQLite

Từ thư mục repository:

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r apps\mrerp\backend\requirements.txt
.venv\Scripts\python apps\mrerp\backend\manage.py migrate
.venv\Scripts\python apps\mrerp\backend\manage.py seed_demo --password <mật-khẩu-local>
.venv\Scripts\python apps\mrerp\backend\manage.py runserver 127.0.0.1:8000
```

Lệnh seed tạo dữ liệu giả và bắt buộc nhận mật khẩu từ CLI; không commit mật khẩu. Mock Identity chỉ được bật ở development/test và cấu hình production sẽ fail-fast nếu nó còn bật.

## Kiểm tra

```text
.venv\Scripts\python apps\mrerp\backend\manage.py check
.venv\Scripts\python apps\mrerp\backend\manage.py makemigrations --check --dry-run
.venv\Scripts\python apps\mrerp\backend\manage.py test people_domain mock_identity
.venv\Scripts\python apps\mrerp\backend\manage.py spectacular --validate --file apps\mrerp\backend\openapi.yaml
```

## PostgreSQL qua Docker Compose

Đặt `POSTGRES_PASSWORD` và `MRERP_SECRET_KEY` trong môi trường local, sau đó chạy `docker compose up --build`. Không dùng credential development cho production.
