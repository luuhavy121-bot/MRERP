import type { AccessAccount, AccountCommandResponse, AttendanceRow, AuditEvent, CandidateAttachment, DashboardData, DocumentVersion, Employee, EmployeeHistory, FeedAudienceOptions, FeedComment, FeedPost, Goal, HiringRequest, InternalDocument, JobOpening, LeaderboardRow, LeaveRequest, Page, PersonalPreferences, Phase3AudienceOptions, ReactionKind, Recognition, RecruitmentApplication, Recurrence, RewardAudienceMember, Session, StarBalance, StarLedgerEntry, TaskAttachment, Team, TeamLeader, WorkTask } from './types'

function csrfToken() {
  return document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrftoken='))
    ?.split('=')[1] ?? ''
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase()
  const response = await fetch(path, {
    credentials: 'include',
    ...init,
    headers: {
      ...(init.body && !(init.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
      ...(method !== 'GET' ? { 'X-CSRFToken': csrfToken() } : {}),
      ...init.headers,
    },
  })
  if (response.status === 204) return undefined as T
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const errorDetails = payload.errors && typeof payload.errors === 'object'
      ? Object.values(payload.errors as Record<string, unknown>).flat(2).join(' ')
      : ''
    const message = errorDetails || payload.detail || 'CÃ³ lá»—i xáº£y ra.'
    const correlation = payload.correlation_id ? ` (MÃ£ lá»—i: ${payload.correlation_id})` : ''
    throw new Error(`${String(message)}${correlation}`)
  }
  return payload as T
}

async function requestAll<T>(path: string): Promise<T[]> {
  const results: T[] = []
  let next: string | null = path
  while (next) {
    const normalized = new URL(next, window.location.origin)
    const page: Page<T> = await request(`${normalized.pathname}${normalized.search}`)
    results.push(...page.results)
    next = page.next
  }
  return results
}

export const api = {
  session: () => request<Session>('/api/v1/auth/session/'),
  login: (username: string, password: string) => request<Session>('/api/v1/auth/login/', {
    method: 'POST', body: JSON.stringify({ username, password }),
  }),
  logout: () => request<void>('/api/v1/auth/logout/', { method: 'POST' }),
  switchPersona: (username: string) => request<Session>('/api/v1/auth/debug/switch/', {
    method: 'POST', body: JSON.stringify({ username }),
  }),
  me: () => request<Employee>('/api/v1/people/employees/me/'),
  updateMe: (payload: { display_name: string; date_of_birth: string | null; address: string; expected_version: number }) =>
    request<Employee>('/api/v1/people/employees/me/', { method: 'PATCH', body: JSON.stringify(payload) }),
  changeOwnPassword: (current_password: string, new_password: string) =>
    request<void>('/api/v1/people/employees/me/change-password/', { method: 'POST', body: JSON.stringify({ current_password, new_password }) }),
  employees: ({ search = '', team = '', page = 1 }: { search?: string; team?: string; page?: number } = {}) => {
    const params = new URLSearchParams({ page: String(page) })
    if (search) params.set('search', search)
    if (team) params.set('team', team)
    return request<Page<Employee>>(`/api/v1/people/employees/?${params}`)
  },
  allEmployees: (search = '') => requestAll<Employee>(`/api/v1/people/employees/?search=${encodeURIComponent(search)}`),
  employee: (uuid: string) => request<Employee>(`/api/v1/people/employees/${uuid}/`),
  createEmployee: (payload: { employee_code: string; create_account: boolean; username: string }) =>
    request<Employee>('/api/v1/people/employees/', { method: 'POST', body: JSON.stringify(payload) }),
  updateEmployee: (uuid: string, payload: Record<string, unknown>) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  promoteEmployee: (uuid: string, note: string) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/promote/`, { method: 'POST', body: JSON.stringify({ note }) }),
  assignTeam: (uuid: string, team_uuid: string | null) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/membership/`, { method: 'PUT', body: JSON.stringify({ team_uuid }) }),
  employeeHistory: (uuid: string) => request<EmployeeHistory>(`/api/v1/people/employees/${uuid}/history/`),
  provisionAccount: (uuid: string, username: string) =>
    request<AccountCommandResponse>(`/api/v1/people/employees/${uuid}/account/provision/`, { method: 'POST', body: JSON.stringify({ username }) }),
  resetEmployeePassword: (uuid: string) =>
    request<AccountCommandResponse>(`/api/v1/people/employees/${uuid}/account/reset-password/`, { method: 'POST' }),
  lockEmployeeAccount: (uuid: string) =>
    request<AccountCommandResponse>(`/api/v1/people/employees/${uuid}/account/lock/`, { method: 'POST' }),
  unlockEmployeeAccount: (uuid: string) =>
    request<AccountCommandResponse>(`/api/v1/people/employees/${uuid}/account/unlock/`, { method: 'POST' }),
  changeEmployment: (uuid: string, command: 'pause' | 'terminate' | 'reactivate', note: string) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/employment/`, { method: 'POST', body: JSON.stringify({ command, note }) }),
  importEmployees: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request<{ created: number }>('/api/v1/people/employees/import-csv/', { method: 'POST', body: formData })
  },
  exportEmployees: async () => {
    const response = await fetch('/api/v1/people/employees/export-csv/', { credentials: 'include' })
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}))
      throw new Error(payload.detail || 'KhÃ´ng thá»ƒ xuáº¥t danh sÃ¡ch nhÃ¢n sá»±.')
    }
    return response.blob()
  },
  accessAccounts: () => request<AccessAccount[]>('/api/v1/people/access/'),
  updateAccessBundle: (employee_uuid: string, bundle: 'staff' | 'leader' | 'hr' | 'ceo') =>
    request<void>('/api/v1/people/access/bundle/', { method: 'PUT', body: JSON.stringify({ employee_uuid, bundle }) }),
  auditEvents: () => request<Page<AuditEvent>>('/api/v1/people/audit/'),
  teams: () => request<Page<Team>>('/api/v1/people/teams/'),
  allTeams: () => requestAll<Team>('/api/v1/people/teams/'),
  createTeam: (payload: { code: string; name: string }) =>
    request<Team>('/api/v1/people/teams/', { method: 'POST', body: JSON.stringify(payload) }),
  updateTeam: (uuid: string, payload: { code: string; name: string }) =>
    request<Team>(`/api/v1/people/teams/${uuid}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  archiveTeam: (uuid: string) =>
    request<Team>(`/api/v1/people/teams/${uuid}/archive/`, { method: 'POST' }),
  addLeader: (teamUuid: string, employeeUuid: string) =>
    request<TeamLeader>(`/api/v1/people/teams/${teamUuid}/leaders/`, { method: 'POST', body: JSON.stringify({ employee_uuid: employeeUuid }) }),
  teamLeaders: (teamUuid: string) => request<TeamLeader[]>(`/api/v1/people/teams/${teamUuid}/leaders/`),
  removeLeader: (teamUuid: string, employeeUuid: string) =>
    request<void>(`/api/v1/people/teams/${teamUuid}/leaders/${employeeUuid}/`, { method: 'DELETE' }),
  leaveRequests: async () => ({ results: await requestAll<LeaveRequest>('/api/v1/leave/requests/') }),
  submitLeave: (payload: { start_date: string; end_date: string; start_period?: string; end_period?: string; reason: string }) =>
    request<LeaveRequest>('/api/v1/leave/requests/', { method: 'POST', body: JSON.stringify(payload) }),
  updateLeave: (uuid: string, payload: { start_date: string; end_date: string; start_period?: string; end_period?: string; reason: string; expected_version: number }) =>
    request<LeaveRequest>(`/api/v1/leave/requests/${uuid}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  reviewLeave: (uuid: string, decision: 'approved' | 'rejected', note = '') =>
    request<LeaveRequest>(`/api/v1/leave/requests/${uuid}/review/`, { method: 'POST', body: JSON.stringify({ decision, note }) }),
  attendance: (month: string) => request<AttendanceRow[]>(`/api/v1/leave/attendance/?month=${encodeURIComponent(month)}`),
  adjustAttendance: (payload: { employee_uuid: string; month: string; days: number; reason: string }) =>
    request<AttendanceRow>('/api/v1/leave/attendance/adjust/', { method: 'POST', body: JSON.stringify(payload) }),
  dashboard: () => request<DashboardData>('/api/v1/dashboard/'),
  readNotification: (uuid: string) => request<void>(`/api/v1/dashboard/notifications/${uuid}/read/`, { method: 'POST' }),
  readAllNotifications: () => request<void>('/api/v1/dashboard/notifications/read-all/', { method: 'POST' }),
  feedPosts: (page = 1) => request<Page<FeedPost>>(`/api/v1/feed/posts/?page=${page}`),
  feedAudience: () => request<FeedAudienceOptions>('/api/v1/feed/audience-options/'),
  createFeedPost: (payload: { content: string; company_scope: boolean; employee_uuids: string[]; team_uuids: string[]; is_official: boolean; attachments: File[] }) => {
    const form = new FormData()
    form.append('content', payload.content)
    form.append('company_scope', String(payload.company_scope))
    form.append('employee_uuids', JSON.stringify(payload.employee_uuids))
    form.append('team_uuids', JSON.stringify(payload.team_uuids))
    form.append('is_official', String(payload.is_official))
    payload.attachments.forEach((file) => form.append('attachments', file))
    return request<FeedPost>('/api/v1/feed/posts/', { method: 'POST', body: form })
  },
  deleteFeedPost: (uuid: string) => request<void>(`/api/v1/feed/posts/${uuid}/`, { method: 'DELETE' }),
  commentPost: (uuid: string, content: string, parent_uuid?: string) => request<FeedComment>(`/api/v1/feed/posts/${uuid}/comments/`, { method: 'POST', body: JSON.stringify({ content, parent_uuid }) }),
  deleteFeedComment: (uuid: string) => request<void>(`/api/v1/feed/comments/${uuid}/`, { method: 'DELETE' }),
  reactPost: (uuid: string, kind: ReactionKind | null) => request<void>(`/api/v1/feed/posts/${uuid}/reaction/`, kind ? { method: 'PUT', body: JSON.stringify({ kind }) } : { method: 'DELETE' }),
  reactComment: (uuid: string, kind: ReactionKind | null) => request<void>(`/api/v1/feed/comments/${uuid}/reaction/`, kind ? { method: 'PUT', body: JSON.stringify({ kind }) } : { method: 'DELETE' }),
  sharePost: (uuid: string, payload: { content: string; company_scope: boolean; employee_uuids: string[]; team_uuids: string[] }) => request<FeedPost>(`/api/v1/feed/posts/${uuid}/share/`, { method: 'POST', body: JSON.stringify(payload) }),
  tasks: () => request<Page<WorkTask>>('/api/v1/tasks/tasks/'),
  createTask: (payload: { title: string; description: string; assignee_uuid: string; due_at: string; goal_uuid: string | null }) => request<WorkTask>('/api/v1/tasks/tasks/', { method: 'POST', body: JSON.stringify(payload) }),
  updateTask: (uuid: string, payload: Record<string, unknown>) => request<WorkTask>(`/api/v1/tasks/tasks/${uuid}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  transitionTask: (uuid: string, action: 'submit' | 'accept' | 'rework', note = '') => request<WorkTask>(`/api/v1/tasks/tasks/${uuid}/transition/`, { method: 'POST', body: JSON.stringify({ action, note }) }),
  uploadTaskAttachments: (uuid: string, kind: 'brief' | 'evidence', files: File[]) => {
    const form = new FormData()
    form.append('kind', kind)
    files.forEach((file) => form.append('attachments', file))
    return request<TaskAttachment[]>(`/api/v1/tasks/tasks/${uuid}/attachments/`, { method: 'POST', body: form })
  },
  deleteTaskAttachment: (uuid: string) => request<void>(`/api/v1/tasks/attachments/${uuid}/`, { method: 'DELETE' }),
  goals: () => request<Page<Goal>>('/api/v1/tasks/goals/'),
  createGoal: (payload: { title: string; description: string; scope: 'team' | 'company'; team_uuid: string | null; period: 'day' | 'week' | 'month' | 'quarter'; starts_on: string; ends_on: string }) => request<Goal>('/api/v1/tasks/goals/', { method: 'POST', body: JSON.stringify(payload) }),
  recurrences: () => request<Page<Recurrence>>('/api/v1/tasks/recurrences/'),
  createRecurrence: (payload: { title: string; description: string; assignee_uuid: string; goal_uuid: string | null; frequency: 'daily' | 'weekly' | 'monthly'; interval: number; start_at: string; deadline_offset_minutes: number; end_date: string | null }) => request<Recurrence>('/api/v1/tasks/recurrences/', { method: 'POST', body: JSON.stringify(payload) }),
  recurrenceCommand: (uuid: string, command: 'pause' | 'resume' | 'stop') => request<Recurrence>(`/api/v1/tasks/recurrences/${uuid}/${command}/`, { method: 'POST' }),
  preferences: () => request<PersonalPreferences>('/api/v1/settings/me/'),
  updatePreferences: (social_notifications_enabled: boolean) => request<PersonalPreferences>('/api/v1/settings/me/', {
    method: 'PATCH', body: JSON.stringify({ social_notifications_enabled }),
  }),
  recruitmentOptions: () => request<{ teams: Phase3AudienceOptions['teams'] }>('/api/v1/recruitment/options/'),
  recruitmentRequests: async () => ({ results: await requestAll<HiringRequest>('/api/v1/recruitment/requests/') }),
  createRecruitmentRequest: (payload: { team_uuid: string; title: string; headcount: number; justification: string; utilization_plan?: string }) =>
    request<HiringRequest>('/api/v1/recruitment/requests/', { method: 'POST', body: JSON.stringify(payload) }),
  reviewRecruitmentRequest: (uuid: string, decision: 'approved' | 'rejected', note = '') =>
    request<HiringRequest>(`/api/v1/recruitment/requests/${uuid}/review/`, { method: 'POST', body: JSON.stringify({ decision, note }) }),
  recruitmentOpenings: async () => ({ results: await requestAll<JobOpening>('/api/v1/recruitment/openings/') }),
  recruitmentApplications: async () => ({ results: await requestAll<RecruitmentApplication>('/api/v1/recruitment/applications/') }),
  createRecruitmentApplication: (payload: { opening_uuid: string; full_name: string; email: string; phone: string; source: string }) =>
    request<RecruitmentApplication>('/api/v1/recruitment/applications/', { method: 'POST', body: JSON.stringify(payload) }),
  transitionRecruitmentApplication: (uuid: string, stage: RecruitmentApplication['stage'], note = '') =>
    request<RecruitmentApplication>(`/api/v1/recruitment/applications/${uuid}/transition/`, { method: 'POST', body: JSON.stringify({ stage, note }) }),
  convertRecruitmentApplication: (uuid: string, payload: { employee_code: string; create_account: boolean; username: string }) =>
    request<AccountCommandResponse>(`/api/v1/recruitment/applications/${uuid}/convert-to-employee/`, { method: 'POST', body: JSON.stringify(payload) }),
  uploadCandidateAttachments: (uuid: string, files: File[]) => {
    const form = new FormData()
    files.forEach((file) => form.append('attachments', file))
    return request<CandidateAttachment[]>(`/api/v1/recruitment/applications/${uuid}/attachments/`, { method: 'POST', body: form })
  },
  documentAudience: () => request<Phase3AudienceOptions>('/api/v1/documents/audience-options/'),
  documents: (includeArchived = false) => request<Page<InternalDocument>>(`/api/v1/documents/documents/${includeArchived ? '?include_archived=true' : ''}`),
  createDocument: (payload: { title: string; description: string; category: string; scope: InternalDocument['scope']; team_uuids: string[]; employee_uuids: string[]; note: string; files: File[] }) => {
    const form = new FormData()
    form.append('title', payload.title)
    form.append('description', payload.description)
    form.append('category', payload.category)
    form.append('scope', payload.scope)
    form.append('team_uuids', JSON.stringify(payload.team_uuids))
    form.append('employee_uuids', JSON.stringify(payload.employee_uuids))
    form.append('note', payload.note)
    payload.files.forEach((file) => form.append('attachments', file))
    return request<InternalDocument>('/api/v1/documents/documents/', { method: 'POST', body: form })
  },
  addDocumentVersion: (uuid: string, note: string, files: File[]) => {
    const form = new FormData()
    form.append('note', note)
    files.forEach((file) => form.append('attachments', file))
    return request<DocumentVersion>(`/api/v1/documents/documents/${uuid}/versions/`, { method: 'POST', body: form })
  },
  archiveDocument: (uuid: string) => request<InternalDocument>(`/api/v1/documents/documents/${uuid}/archive/`, { method: 'POST' }),
  restoreDocument: (uuid: string) => request<InternalDocument>(`/api/v1/documents/documents/${uuid}/restore/`, { method: 'POST' }),
  recognitions: () => request<Page<Recognition>>('/api/v1/rewards/recognitions/'),
  rewardAudience: () => request<RewardAudienceMember[]>('/api/v1/rewards/audience-options/'),
  createRecognition: (payload: { recipient_uuids: string[]; category: string; message: string }) =>
    request<Recognition>('/api/v1/rewards/recognitions/', { method: 'POST', body: JSON.stringify(payload) }),
  grantStars: (payload: { employee_uuid: string; amount: number; reason: string }) =>
    request<StarLedgerEntry>('/api/v1/rewards/stars/grant/', { method: 'POST', body: JSON.stringify(payload) }),
  myStarBalance: () => request<StarBalance>('/api/v1/rewards/stars/me/'),
  leaderboard: (period: 'month' | 'quarter' | 'year') => request<LeaderboardRow[]>(`/api/v1/rewards/leaderboard/?period=${period}`),
}
