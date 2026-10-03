# Contract HR mở rộng

MRERP sở hữu recruitment_domain và performance_domain. [Yêu cầu](../product/hr-expansion-requirements.md) và [OpenAPI](../../apps/mrerp/backend/openapi.yaml) là contract nghiệp vụ/API.

## Quyền

| Hành động | Staff | Leader | HR/CEO |
|---|---|---|---|
| Tạo/sửa/gửi tuyển | Không | Team lãnh đạo | Company |
| Duyệt tuyển | Không | Không | Company |
| Liên hệ/CV/pipeline/đóng tin | Không | Team lãnh đạo | Company |
| Convert Employee | Không | Không | Company |
| Tạo/chấm phiếu KPI | Không | Team lãnh đạo, không tự chấm | Không |
| Xem phiếu | Own đã chốt | Team + own đã chốt | Company |
| Xác nhận | Own đã chốt | Own đã chốt | Own đã chốt |
| Mở lại | Không | Không | Company |

performance_domain: PerformanceReview unique employee/month, PerformanceKPI và append-only PerformanceReviewRevision. Transaction khóa phiếu, so version trước ghi. API /api/v1/performance/reviews/ và finalize/acknowledge/reopen; /context/ chỉ tham khảo Task; /options/ trả nhân sự đủ điều kiện.

Tuyển dụng: requests PATCH/submit/review; openings close. /api/v1/public/recruitment/openings/ chỉ tin đã xuất bản, còn mở/chưa hết hạn; applications multipart nhận một CV. Throttle 5 submissions/IP/hour; cache Redis dùng chung khi MRERP_REDIS_URL được cấu hình, local single-process dùng memory. Reverse proxy phải cấu hình địa chỉ client tin cậy trước public deployment. Rate limit là giảm spam, không phải hàng rào chống DDoS.

Migration thêm cột nullable, giữ opening cũ không public. Permission migration cập nhật các group chuẩn hiện có và tạo permission cần thiết; seed_demo dùng cùng capability mapping. Không reset account/password hiện có.

## Bổ sung ADR-0021

Pipeline theo [ADR-0022](../decisions/0022-short-recruitment-pipeline.md): HiringRequest create/PATCH và DTO nội bộ thêm `utilization_plan` tùy chọn, tối đa 3.000 ký tự, chỉ sửa draft với ACL hiện có. Public DTO không trả field này. Stage mới chỉ có new/screening/interview/hired/rejected; chuyển interview→hired trực tiếp. `offer` gửi mới trả 400. Migration chuyển application offer→interview và tăng version; lịch sử transition offer giữ nguyên với nhãn lịch sử. Quyền convert-to-employee không thay đổi.

GET `/api/v1/performance/reviews/kpi-source/?employee_uuid=UUID&month=YYYY-MM` chỉ Leader được đánh giá Employee đó; trả cấu trúc KPI tháng liền trước, completion null/comment rỗng. GET reviews hỗ trợ employee_uuid, kết hợp ACL gốc, không mở draft cho Staff. Thông báo performance chốt/mở lại/xác nhận có dedup key theo version.

POST `/api/v1/recruitment/applications/{uuid}/interview/`: version, interview_at (ISO datetime có timezone hoặc null), interviewer_name (160), recruiter_note (2.000). MANAGE_CANDIDATES và Team scope; stale=409, hồ sơ kết thúc/ẩn danh=400. Không tự chuyển stage. GET quản lý Application trả ba trường; projection không có manage_candidates loại chúng. Public DTO không thay đổi. Opening nội bộ trả thêm hiring_request_deadline để phân biệt hết hạn. Notification hồ sơ mới/yêu cầu duyệt tới người có capability và scope tương ứng; không chứa PII ứng viên.
