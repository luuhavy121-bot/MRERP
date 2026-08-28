export type Session = {
  authenticated: boolean
  username?: string
  employee_uuid?: string
  employee_code?: string
  display_name?: string
  rank?: string
  capabilities?: string[]
  csrf_token?: string
  mock_identity?: boolean
  debug_personas?: Array<{ username: string; label: string }>
}

export type Department = {
  uuid: string
  code: string
  name: string
  is_active: boolean
}

export type Team = {
  uuid: string
  code: string
  name: string
  department: string
  department_name: string
  is_active: boolean
  leader_count: number
}

export type TeamLeader = {
  uuid: string
  leader: string
  leader_name: string
  leader_code: string
  created_at: string
}

export type Employee = {
  uuid: string
  employee_code: string
  display_name: string
  job_title: string
  department: string | null
  department_name: string | null
  team: string | null
  team_name: string | null
  employment_status?: 'probation' | 'official'
  employment_status_label?: string
  rank?: string
  username?: string
  national_id?: string | null
  date_of_birth?: string | null
  address?: string
  version?: number
}

export type Page<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
