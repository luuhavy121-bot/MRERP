# MRERP frontend

React/TypeScript/Vite client cho MRERP People/HR Foundation. Authorization không được quyết định ở đây; frontend chỉ ẩn/hiện thao tác theo capability để cải thiện UX, còn API luôn kiểm tra lại ở server.

## Chạy local

Yêu cầu Node.js tương thích lockfile.

```text
npm ci
npm run dev
```

Mặc định Vite phục vụ tại `http://localhost:4173` và proxy `/api` tới `http://127.0.0.1:8000`. Có thể đổi đích proxy bằng `VITE_API_PROXY_TARGET`.

## Kiểm tra

```text
npm run lint
npm run build
```

Không lưu access token trong `localStorage`. Local mock Identity dùng session cookie HttpOnly do backend cấp.
