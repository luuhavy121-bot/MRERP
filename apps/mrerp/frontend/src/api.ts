import type { Department, Employee, Page, Session, Team, TeamLeader } from './types'

function csrfToken() {
  return document.cookie
    .split('; ')
    .find((item) => item.startsWith('csrftoken='))
    ?.split('=')[1] ?? ''
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase()
  const response = await fetch(path, {
    credentials: 'include',
    ...init,
    headers: {
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...(method !== 'GET' ? { 'X-CSRFToken': csrfToken() } : {}),
      ...init.headers,
    },
  })
  if (response.status === 204) return undefined as T
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.detail ?? Object.values(payload).flat().join(' ') ?? 'Có lỗi xảy ra.'
    throw new Error(String(message))
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
  employees: (search = '') => request<Page<Employee>>(`/api/v1/people/employees/?search=${encodeURIComponent(search)}`),
  allEmployees: (search = '') => requestAll<Employee>(`/api/v1/people/employees/?search=${encodeURIComponent(search)}`),
  employee: (uuid: string) => request<Employee>(`/api/v1/people/employees/${uuid}/`),
  createEmployee: (payload: { employee_code: string; username: string; password: string }) =>
    request<Employee>('/api/v1/people/employees/', { method: 'POST', body: JSON.stringify(payload) }),
  updateEmployee: (uuid: string, payload: Record<string, unknown>) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/`, { method: 'PATCH', body: JSON.stringify(payload) }),
  promoteEmployee: (uuid: string, note: string) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/promote/`, { method: 'POST', body: JSON.stringify({ note }) }),
  assignTeam: (uuid: string, team_uuid: string | null) =>
    request<Employee>(`/api/v1/people/employees/${uuid}/membership/`, { method: 'PUT', body: JSON.stringify({ team_uuid }) }),
  departments: () => request<Page<Department>>('/api/v1/people/departments/'),
  allDepartments: () => requestAll<Department>('/api/v1/people/departments/'),
  createDepartment: (payload: { code: string; name: string }) =>
    request<Department>('/api/v1/people/departments/', { method: 'POST', body: JSON.stringify(payload) }),
  teams: () => request<Page<Team>>('/api/v1/people/teams/'),
  allTeams: () => requestAll<Team>('/api/v1/people/teams/'),
  createTeam: (payload: { code: string; name: string; department: string }) =>
    request<Team>('/api/v1/people/teams/', { method: 'POST', body: JSON.stringify(payload) }),
  addLeader: (teamUuid: string, employeeUuid: string) =>
    request<TeamLeader>(`/api/v1/people/teams/${teamUuid}/leaders/`, { method: 'POST', body: JSON.stringify({ employee_uuid: employeeUuid }) }),
  teamLeaders: (teamUuid: string) => request<TeamLeader[]>(`/api/v1/people/teams/${teamUuid}/leaders/`),
  removeLeader: (teamUuid: string, employeeUuid: string) =>
    request<void>(`/api/v1/people/teams/${teamUuid}/leaders/${employeeUuid}/`, { method: 'DELETE' }),
}
