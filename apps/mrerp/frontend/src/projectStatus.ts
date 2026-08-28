export type ProgressTone = 'done' | 'active' | 'planned' | 'blocked' | 'prototype'

// Projection quản trị từ docs/06 và docs/product/roadmap; không phải nguồn sự thật nghiệp vụ.
// Khi cập nhật phase/module, phải đối chiếu source of truth và bằng chứng test trước khi đổi phần trăm.
export const projectStatus = {
  updatedAt: '28/08/2026',
  overallPercent: 20,
  currentPhase: 'Phase 1',
  currentPhaseName: 'People/HR Foundation',
  calculation: '6 phase có trọng số bằng nhau: round((100% + 20% + 0% + 0% + 0% + 0%) / 6).',
  phases: [
    { id: 'P0', name: 'Context & nền tài liệu', percent: 100, state: 'Hoàn tất', tone: 'done' as ProgressTone },
    { id: 'P1', name: 'Vertical slice nền tảng', percent: 20, state: 'Đang thực hiện', tone: 'active' as ProgressTone },
    { id: 'P2', name: 'Nghiệp vụ nội bộ', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
    { id: 'P3', name: 'Văn hóa & nhân sự', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
    { id: 'P4', name: 'Tích hợp hiện hữu', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
    { id: 'P5', name: 'MRECRM tối thiểu', percent: 0, state: 'Chưa bắt đầu', tone: 'planned' as ProgressTone },
  ],
  modules: [
    { name: 'Dashboard', phase: 'Phase 1–2', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Vertical slice Dashboard' },
    { name: 'People / HR', phase: 'Phase 1', percent: 75, tone: 'active' as ProgressTone, state: 'UI nối API thật', next: 'Nghiệm thu local' },
    { name: 'Attendance / Leave', phase: 'Phase 2', percent: 10, tone: 'planned' as ProgressTone, state: 'Đã có yêu cầu', next: 'Chờ refinement' },
    { name: 'Approvals', phase: 'Phase 2', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Chưa có backend' },
    { name: 'Tasks', phase: 'Phase 1–2', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Ứng viên slice kế tiếp' },
    { name: 'Recognition / Rewards', phase: 'Phase 3', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Chờ policy' },
    { name: 'Recruitment', phase: 'Phase 3', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Chờ refinement' },
    { name: 'Documents', phase: 'Phase 3', percent: 20, tone: 'prototype' as ProgressTone, state: 'Có prototype UI', next: 'Chờ storage decision' },
    { name: 'Personal Payroll', phase: 'Chưa xếp phase', percent: 10, tone: 'blocked' as ProgressTone, state: 'Chờ policy', next: 'Không thuộc slice hiện tại' },
    { name: 'Reporting', phase: 'Phase 5+', percent: 10, tone: 'planned' as ProgressTone, state: 'Đã có yêu cầu', next: 'Chờ read model' },
    { name: 'Admin Panel', phase: 'Phase 1', percent: 20, tone: 'blocked' as ProgressTone, state: 'Chờ quyết định quyền', next: 'OD-05/OD-19' },
    { name: 'Personal Settings', phase: 'Phase 3', percent: 15, tone: 'planned' as ProgressTone, state: 'Có khung UI', next: 'Chờ refinement' },
  ],
  quality: [
    { label: 'Source of truth', value: 100, state: 'Đã thiết lập' },
    { label: 'Repository governance', value: 100, state: 'CI đã cấu hình' },
    { label: 'People vertical slice', value: 75, state: '22 automated tests' },
    { label: 'Identity production', value: 0, state: 'Chưa chọn provider' },
  ],
  nextGates: [
    'Nghiệm thu People/HR Foundation trên môi trường local.',
    'Refinement vertical slice kế tiếp; Task đang là ứng viên.',
    'Chọn Identity Provider production bằng ADR riêng khi đến thời điểm.',
  ],
  decisions: { open: 20, resolved: 6, priority: 'OD-19 · Identity provisioning production' },
}

export const showProjectProgress = projectStatus.overallPercent < 100
