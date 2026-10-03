export type Session = {
  authenticated: boolean
  username?: string
  employee_uuid?: string
  employee_code?: string
  display_name?: string
  rank?: string
  capabilities?: string[]
  product_entitlements?: string[]
  csrf_token?: string
  mock_identity?: boolean
  debug_personas?: Array<{ username: string; label: string }>
  must_change_password?: boolean
}

export type Team = {
  uuid: string
  code: string
  name: string
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
  team: string | null
  team_name: string | null
  employment_status?: 'probation' | 'official' | 'paused' | 'terminated'
  employment_status_label?: string
  can_promote?: boolean
  rank?: string
  username?: string
  national_id?: string | null
  date_of_birth?: string | null
  address?: string
  version?: number
  has_account?: boolean | null
  account_active?: boolean | null
  can_reset_password?: boolean
  can_manage_account?: boolean
  can_change_employment?: boolean
  can_provision_account?: boolean
  must_change_password?: boolean
  created_at?: string
  updated_at?: string
  temporary_password?: string
}

export type EmploymentHistory = {
  uuid: string
  from_status: string
  from_label: string
  to_status: string
  to_label: string
  note: string
  actor_name: string
  effective_at: string
}

export type MembershipHistory = {
  uuid: string
  from_team: string | null
  from_team_name: string | null
  to_team: string | null
  to_team_name: string | null
  actor_name: string
  effective_at: string
}

export type EmployeeHistory = {
  employment: EmploymentHistory[]
  membership: MembershipHistory[]
}

export type AccountCommandResponse = {
  employee: Employee
  temporary_password?: string
}

export type AccessAccount = {
  employee_uuid: string
  employee_code: string
  display_name: string
  team_name: string | null
  username: string | null
  account_active: boolean
  groups: string[]
  capabilities: string[]
}

export type AuditEvent = {
  uuid: string
  actor_name: string | null
  action: string
  target_type: string
  target_uuid: string
  changes: Record<string, unknown>
  correlation_id: string | null
  created_at: string
}

export type Page<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type LeaveRequest = {
  uuid: string
  start_period: 'am' | 'pm'
  end_period: 'am' | 'pm'
  requester_code: string
  requester_name: string
  team_name: string | null
  start_date: string
  end_date: string
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  status_label: string
  reviewer_name: string | null
  review_note: string
  reviewed_at: string | null
  can_review: boolean
  can_edit: boolean
  version: number
  created_at: string
  updated_at: string
}

export type AttendanceRow = {
  employee_uuid: string
  employee_code: string
  display_name: string
  team_name: string | null
  month: string
  scheduled_workdays: number
  public_holiday_days: number
  approved_leave_days: number
  adjustment_days: number
  adjustment_reason: string
  projected_workdays: number
}

export type DashboardNotification = {
  uuid: string
  kind: 'feed' | 'task' | 'goal' | 'leave' | 'account' | 'recruitment' | 'performance' | 'document' | 'recognition'
  kind_label: string
  title: string
  body: string
  target_type: 'post' | 'task' | 'goal' | 'leave' | 'profile' | 'recruitment' | 'document' | 'recognition' | 'performance'
  target_uuid: string | null
  is_read: boolean
  read_at: string | null
  created_at: string
}

export type DashboardData = {
  general: {
    guides: Array<{ id: string; title: string; body: string; target: 'profile' | 'feed' }>
    company_posts: Array<{ uuid: string; author_name: string; content: string; is_official: boolean; attachment_count: number; created_at: string }>
  }
  private: {
    notifications: DashboardNotification[]
    unread_count: number
    warnings: Array<{ id: string; title: string; body: string; target: 'profile' }>
  }
}

export type ReactionKind = 'like' | 'love' | 'celebrate' | 'support' | 'insightful'
export type ReactionSummary = { counts: Record<ReactionKind, number>; mine: ReactionKind | null }

export type FeedAttachment = {
  uuid: string
  original_name: string
  content_type: string
  size: number
  download_url: string
}

export type FeedComment = {
  uuid: string
  author_name: string
  author_code: string
  parent: string | null
  content: string
  deleted_at: string | null
  deletion_mode: string
  reaction_summary: ReactionSummary
  replies: FeedComment[]
  can_delete: boolean
  created_at: string
}

export type FeedPost = {
  uuid: string
  author: string
  author_name: string
  author_code: string
  content: string
  company_scope: boolean
  audience_employees: string[]
  audience_employee_names: string[]
  audience_teams: string[]
  audience_team_names: string[]
  is_official: boolean
  shared_post: null | { uuid: string; author_name: string; content: string; available: boolean; created_at: string }
  attachments: FeedAttachment[]
  comments: FeedComment[]
  reaction_summary: ReactionSummary
  deleted_at: string | null
  deletion_mode: string
  can_delete: boolean
  created_at: string
}

export type FeedAudienceOptions = {
  employees: Array<{ uuid: string; employee_code: string; display_name: string; team_uuid: string | null; team_name: string | null }>
  teams: Array<{ uuid: string; code: string; name: string }>
}

export type Phase3AudienceOptions = {
  employees: Array<{ uuid: string; employee_code: string; display_name: string; team_name: string | null }>
  teams: Array<{ uuid: string; code: string; name: string }>
}

export type TaskAttachment = {
  uuid: string
  kind: 'brief' | 'evidence'
  original_name: string
  content_type: string
  size: number
  uploaded_by_name: string
  download_url: string
  can_delete: boolean
  created_at: string
}

export type WorkTask = {
  uuid: string
  title: string
  description: string
  creator: string
  creator_name: string
  assignee: string
  assignee_name: string
  assignee_code: string
  team: string
  team_name: string
  goal: string | null
  goal_title: string | null
  due_at: string
  progress: number
  status: 'in_progress' | 'pending_review' | 'completed' | 'rework'
  status_label: string
  review_note: string
  recurrence: string | null
  scheduled_for: string | null
  version: number
  attachments: TaskAttachment[]
  can_submit: boolean
  can_review: boolean
  created_at: string
  updated_at: string
}

export type Goal = {
  uuid: string
  title: string
  description: string
  scope: 'team' | 'company'
  team: string | null
  team_name: string | null
  period: 'day' | 'week' | 'month' | 'quarter'
  starts_on: string
  ends_on: string
  created_by_name: string
  is_active: boolean
  progress: number
  task_count: number
  created_at: string
  updated_at: string
}

export type Recurrence = {
  uuid: string
  title: string
  description: string
  creator_name: string
  assignee: string
  assignee_name: string
  team: string
  team_name: string
  goal: string | null
  frequency: 'daily' | 'weekly' | 'monthly'
  frequency_label: string
  interval: number
  start_at: string
  next_occurrence_at: string
  deadline_offset_minutes: number
  end_date: string | null
  status: 'active' | 'paused' | 'stopped'
  status_label: string
  created_at: string
}

export type PersonalPreferences = {
  social_notifications_enabled: boolean
  mandatory_notifications: string[]
  account_active: boolean
  employment_status: string
  employment_status_label: string
  must_change_password: boolean
  updated_at: string
}

export type HiringRequest = {
  location: string
  employment_type: string
  description: string
  requirements: string
  benefits: string
  deadline: string | null
  uuid: string
  team: string
  team_name: string
  title: string
  headcount: number
  justification: string
  utilization_plan: string
  requester_name: string
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'closed'
  status_label: string
  review_note: string
  reviewed_at: string | null
  opening_uuid: string | null
  created_at: string
  updated_at: string
}

export type JobOpening = {
  hiring_request_deadline?: string | null
  slug: string | null
  published_at: string | null
  closed_at: string | null
  uuid: string
  hiring_request: string
  team: string
  team_name: string
  title: string
  status: 'open' | 'closed'
  status_label: string
  created_at: string
}

export type CandidateAttachment = {
  uuid: string
  original_name: string
  content_type: string
  size: number
  download_url: string
  created_at: string
}

export type ApplicationTransition = {
  uuid: string
  from_stage: string
  to_stage: string
  to_label: string
  note: string
  created_at: string
}

export type RecruitmentApplication = {
  interview_at?: string | null
  interviewer_name?: string
  recruiter_note?: string
  introduction?: string
  uuid: string
  candidate_name: string
  candidate_email?: string
  candidate_phone?: string
  candidate_source: string
  opening: string
  opening_title: string
  team_uuid: string
  team_name: string
  stage: 'new' | 'screening' | 'interview' | 'hired' | 'rejected'
  stage_label: string
  converted_employee_uuid: string | null
  version: number
  attachments?: CandidateAttachment[]
  transitions: ApplicationTransition[]
  can_manage: boolean
  can_convert: boolean
  created_at: string
  updated_at: string
}

export type DocumentFile = {
  uuid: string
  original_name: string
  content_type: string
  size: number
  download_url: string
  created_at: string
}

export type DocumentVersion = {
  uuid: string
  number: number
  note: string
  uploaded_by_name: string
  files: DocumentFile[]
  created_at: string
}

export type InternalDocument = {
  uuid: string
  title: string
  description: string
  category: string
  owner: string
  owner_name: string
  scope: 'company' | 'teams' | 'employees' | 'hr_confidential'
  scope_label: string
  audience_teams: string[]
  audience_team_names: string[]
  audience_employees: string[]
  audience_employee_names: string[]
  versions: DocumentVersion[]
  can_manage: boolean
  is_archived: boolean
  archived_at: string | null
  created_at: string
  updated_at: string
}

export type Recognition = {
  uuid: string
  sender: string
  sender_name: string
  sender_code: string
  recipients: string[]
  recipient_names: string[]
  category: string
  message: string
  created_at: string
}

export type RewardAudienceMember = {
  uuid: string
  employee_code: string
  display_name: string
  team_name: string | null
}

export type StarLedgerEntry = {
  uuid: string
  employee: string
  employee_name: string
  amount: number
  entry_type: 'grant' | 'adjustment'
  entry_type_label: string
  reason: string
  actor_name: string
  created_at: string
}

export type StarBalance = { balance: number; ledger: StarLedgerEntry[] }

export type LeaderboardRow = {
  rank: number
  employee_uuid: string
  display_name: string
  employee_code: string
  team_name: string | null
  stars: number
}
