export type ProgressTone = 'done' | 'active' | 'planned' | 'blocked' | 'prototype'

// Projection quản trị từ docs/06 và docs/product/roadmap; không phải nguồn sự thật nghiệp vụ.
// Khi cập nhật phase/module, phải đối chiếu source of truth và bằng chứng test trước khi đổi phần trăm.
export const projectStatus = {
  automatedTestCount: 100,
  updatedAt: '29/08/2026',
  overallPercent: 46,
  currentPhase: 'Phase 3',
  currentPhaseName: 'Văn hóa & vận hành nhân sự',
  calculation: '6 phase có trọng số bằng nhau: round((100% + 90% + 10% + 75% + 0% + 0%) / 6).',
  phases: [
    { id: 'P0', name: 'Context & nền tài liệu', percent: 100, state: 'Hoàn tất', tone: 'done' as ProgressTone },
    { id: 'P1', name: 'Nền tảng nghiệp vụ', percent: 90, state: 'Foundation đã nghiệm thu; các module mở rộng chờ nghiệm thu', tone: 'active' as ProgressTone },
    { id: 'P2', name: 'Nghiệp vụ nội bộ', percent: 10, state: 'Foundation Leave/Attendance đang triển khai', tone: 'active' as ProgressTone },
    { id: 'P3', name: 'Văn hóa & nhân sự', percent: 75, state: 'Implementation hoàn tất · Chờ nghiệm thu', tone: 'active' as ProgressTone },
    { id: 'P4', name: 'Tích hợp hiện hữu', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
    { id: 'P5', name: 'MRECRM tối thiểu', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
  ],
  modules: [
    { name: 'Dashboard', phase: 'Phase 1–2', percent: 90, tone: 'active' as ProgressTone, state: 'General/private + unread đã có', next: 'Chờ nghiệm thu' },
    { name: 'Bảng tin', phase: 'Phase 1', percent: 90, tone: 'active' as ProgressTone, state: 'Audience + tương tác + file đã có', next: 'Chờ nghiệm thu' },
    { name: 'People / HR Foundation', phase: 'Phase 1', percent: 100, tone: 'done' as ProgressTone, state: 'Đã nghiệm thu', next: 'Mở rộng chỉ qua slice mới' },
    { name: 'People Account & Employment', phase: 'Phase 1', percent: 90, tone: 'active' as ProgressTone, state: 'Implementation hoàn tất', next: 'Chờ người sở hữu nghiệm thu' },
    { name: 'Attendance / Leave', phase: 'Phase 1–2', percent: 85, tone: 'active' as ProgressTone, state: 'Edit + holiday + HR adjustment đã có', next: 'Kiểm thử UI và chờ nghiệm thu' },
    { name: 'Approvals', phase: 'Phase 2', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Chưa có backend' },
    { name: 'Tasks / Goal / Recurrence', phase: 'Phase 1–2', percent: 90, tone: 'active' as ProgressTone, state: 'Implementation xuyên worker đã có', next: 'Chờ nghiệm thu' },
    { name: 'Recognition / Stars', phase: 'Phase 3', percent: 85, tone: 'active' as ProgressTone, state: 'Recognition + ledger + leaderboard đã có', next: 'Chờ nghiệm thu; redemption vẫn mở' },
    { name: 'Recruitment', phase: 'Phase 3', percent: 85, tone: 'active' as ProgressTone, state: 'Request + pipeline + conversion đã có', next: 'Chờ nghiệm thu' },
    { name: 'Documents', phase: 'Phase 3', percent: 85, tone: 'active' as ProgressTone, state: 'ACL + version + retention đã có', next: 'Chờ nghiệm thu; object storage vẫn mở' },
    { name: 'Cài đặt cá nhân', phase: 'Phase 3', percent: 85, tone: 'active' as ProgressTone, state: 'Notification preference + security summary đã có', next: 'Chờ nghiệm thu' },
    { name: 'Personal Payroll', phase: 'Chưa xếp phase', percent: 10, tone: 'blocked' as ProgressTone, state: 'Chờ policy', next: 'Không thuộc slice hiện tại' },
    { name: 'Reporting', phase: 'Phase 5+', percent: 10, tone: 'planned' as ProgressTone, state: 'Đã có yêu cầu', next: 'Chờ read model' },
    { name: 'Admin Panel (People access)', phase: 'Phase 1', percent: 80, tone: 'active' as ProgressTone, state: 'CEO control plane đã có', next: 'Chờ nghiệm thu; IdP production vẫn mở' },
    { name: 'Hồ sơ của tôi', phase: 'Phase 1', percent: 90, tone: 'active' as ProgressTone, state: 'Hồ sơ + tài khoản đã có', next: 'Chờ nghiệm thu' },
  ],
  quality: [
    { label: 'Source of truth', value: 100, state: 'Đã thiết lập' },
    { label: 'Repository governance', value: 100, state: 'CI đã cấu hình' },
    { label: 'People Foundation', value: 100, state: 'Đã nghiệm thu' },
    { label: 'People account lifecycle', value: 90, state: '42 People tests + 2 E2E · Chờ nghiệm thu' },
    { label: 'Leave / Attendance', value: 90, state: '17 backend tests + 1 E2E · Chờ nghiệm thu' },
    { label: 'Dashboard / Feed / Task', value: 90, state: 'Backend + OpenAPI + 3 E2E · Chờ nghiệm thu' },
    { label: 'Phase 3 culture operations', value: 75, state: '4 module xuyên UI/API/DB · Chờ nghiệm thu' },
    { label: 'Identity production', value: 0, state: 'Chưa chọn provider' },
  ],
  nextGates: [
    'Nghiệm thu Recruitment request → pipeline → chuyển Employee thử việc.',
    'Nghiệm thu Documents: audience → protected download → version → archive/restore.',
    'Nghiệm thu Recognition, Star ledger/leaderboard và notification preference.',
    'Không mở catalog/redemption trước khi OD-05 và OD-13 được duyệt.',
    'Giữ object storage production ở OD-14; local-media chỉ là baseline VPS.',
  ],
  decisions: { open: 20, resolved: 9, priority: 'OD-05/OD-13 · Catalog và redemption; OD-14 · Object storage' },
}

export const showProjectProgress = projectStatus.overallPercent < 100
