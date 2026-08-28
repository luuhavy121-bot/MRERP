import { useCallback, useEffect, useMemo, useState } from 'react'
import type { CSSProperties, FormEvent } from 'react'
import './App.css'
import { api } from './api'
import { projectStatus, showProjectProgress } from './projectStatus'
import type { Department, Employee, Session, Team, TeamLeader } from './types'

const labels: Record<string, string> = {
  staff: 'Staff', captain: 'Captain', leader: 'Leader', manager: 'Manager', ceo: 'CEO',
}

function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [username, setUsername] = useState('hr.demo')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setLoading(true); setError('')
    try { onLogin(await api.login(username, password)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể đăng nhập.') }
    finally { setLoading(false) }
  }

  return <main className="login-shell">
    <section className="login-story">
      <span className="brand-mark">MRE<span>•</span></span>
      <p className="eyebrow">MRERP WORKSPACE</p>
      <h1>Một nơi để đội ngũ<br />làm việc rõ ràng hơn.</h1>
      <p className="lead">People Foundation đầu tiên đã nối giao diện với API, dữ liệu, quyền và audit. Mock Identity chỉ hoạt động trong môi trường phát triển.</p>
      <div className="trust-row"><span>Session cookie</span><span>Server authorization</span><span>Audit trail</span></div>
    </section>
    <section className="login-card-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="login-card__top"><span className="live-dot" /> DEVELOPMENT IDENTITY</div>
        <h2>Chào mừng trở lại</h2>
        <p>Đăng nhập bằng tài khoản demo đã được seed cục bộ.</p>
        <label>Tài khoản<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" /></label>
        <label>Mật khẩu<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" /></label>
        {error && <div className="alert alert--error">{error}</div>}
        <button className="primary-button" disabled={loading}>{loading ? 'Đang xác thực…' : 'Đăng nhập MRERP'}</button>
        <small>Mock login tự động bị khóa khi cấu hình production.</small>
      </form>
    </section>
  </main>
}

function initials(employee?: Employee) {
  const value = employee?.display_name || employee?.employee_code || 'MR'
  return value.split(' ').map((part) => part[0]).join('').slice(-2).toUpperCase()
}

function EmployeeDrawer({ employee, departments, teams, canEdit, canPromote, canManageMembership, onClose, onChanged }: {
  employee: Employee; departments: Department[]; teams: Team[]; canEdit: boolean; canPromote: boolean; canManageMembership: boolean; onClose: () => void; onChanged: () => void
}) {
  const [form, setForm] = useState({
    display_name: employee.display_name ?? '', national_id: employee.national_id ?? '',
    date_of_birth: employee.date_of_birth ?? '', address: employee.address ?? '',
    job_title: employee.job_title ?? '', department: employee.department ?? '',
  })
  const [note, setNote] = useState('')
  const [team, setTeam] = useState(employee.team ?? '')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function run(action: () => Promise<unknown>) {
    setBusy(true); setError('')
    try { await action(); onChanged() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể lưu thay đổi.') }
    finally { setBusy(false) }
  }

  return <div className="drawer-backdrop" onMouseDown={onClose}>
    <aside className="drawer" onMouseDown={(event) => event.stopPropagation()}>
      <button className="icon-button drawer-close" onClick={onClose}>×</button>
      <div className="profile-head">
        <div className="avatar avatar--large">{initials(employee)}</div>
        <div><span className="code-chip">{employee.employee_code}</span><h2>{employee.display_name || 'Chưa bổ sung họ tên'}</h2><p>{employee.job_title || 'Chưa có vị trí'} · {employee.team_name || 'Chưa vào Team'}</p></div>
      </div>
      <div className="profile-meta">
        <div><span>Trạng thái</span><strong className={`status status--${employee.employment_status ?? 'neutral'}`}>{employee.employment_status_label ?? 'Hồ sơ cơ bản'}</strong></div>
        <div><span>Phòng ban</span><strong>{employee.department_name || 'Chưa gán'}</strong></div>
        <div><span>Cấp bậc</span><strong>{labels[employee.rank ?? 'staff'] ?? employee.rank ?? 'Staff'}</strong></div>
      </div>
      {canPromote && employee.employment_status === 'probation' && <section className={`promotion-box promotion-box--prominent ${employee.can_promote ? '' : 'promotion-box--blocked'}`}>
        <div className="section-title"><span>Chuyển trạng thái công việc</span><small>Thử việc → Chính thức</small></div>
        {employee.can_promote ? <>
          <textarea aria-label="Ghi chú xác nhận chính thức" placeholder="Ghi chú xác nhận bắt buộc…" value={note} onChange={(e) => setNote(e.target.value)} />
          <button className="primary-button compact" disabled={busy || !note.trim()} onClick={() => run(() => api.promoteEmployee(employee.uuid, note))}>✓ Chuyển lên Chính thức</button>
        </> : <div className="promotion-blocked-message"><span>🔒</span><p><strong>Chưa thể chuyển lên Chính thức</strong><small>Leader chỉ duyệt nhân sự thuộc Team mình lãnh đạo. Hãy cập nhật Team phù hợp trước.</small></p><button className="secondary-button compact" disabled>Chuyển lên Chính thức</button></div>}
      </section>}
      {canEdit && <section className="drawer-section">
        <div className="section-title"><span>Hồ sơ HR</span><small>Chỉ HR nhận payload này</small></div>
        <div className="form-grid">
          <label>Họ và tên<input value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} /></label>
          <label>CCCD<input value={form.national_id} onChange={(e) => setForm({ ...form, national_id: e.target.value })} /></label>
          <label>Ngày sinh<input type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} /></label>
          <label>Vị trí<input value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} /></label>
          <label>Phòng ban<select value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })}><option value="">Chưa gán</option>{departments.map((item) => <option key={item.uuid} value={item.uuid}>{item.name}</option>)}</select></label>
          <label className="span-2">Địa chỉ<textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} /></label>
        </div>
        <button className="primary-button compact" disabled={busy} onClick={() => run(() => api.updateEmployee(employee.uuid, { ...form, department: form.department || null, date_of_birth: form.date_of_birth || null, expected_version: employee.version }))}>Lưu hồ sơ chi tiết</button>
      </section>}
      {canManageMembership && <section className="drawer-section">
        <div className="section-title"><span>Team hiện tại</span><small>Mỗi nhân sự thuộc tối đa một Team</small></div>
        <div className="inline-action"><select value={team} onChange={(e) => setTeam(e.target.value)}><option value="">Chưa vào Team</option>{teams.map((item) => <option key={item.uuid} value={item.uuid}>{item.name}</option>)}</select><button className="secondary-button" disabled={busy} onClick={() => run(() => api.assignTeam(employee.uuid, team || null))}>Cập nhật Team</button></div>
      </section>}
      {error && <div className="alert alert--error">{error}</div>}
    </aside>
  </div>
}

function CreateEmployeeModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ employee_code: '', create_account: true, username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.createEmployee(form); onCreated() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể tạo nhân sự.') }
    finally { setBusy(false) }
  }
  return <div className="modal-backdrop" onMouseDown={onClose}><form className="modal" onSubmit={submit} onMouseDown={(e) => e.stopPropagation()}>
    <div className="modal-head"><div><p className="eyebrow">QUICK CREATE</p><h2>Thêm nhân sự thử việc</h2></div><button type="button" className="icon-button" onClick={onClose}>×</button></div>
    <p className="muted">Employee luôn được tạo ở trạng thái Thử việc. Có thể tạo tài khoản ngay; luồng cấp tài khoản về sau chưa thuộc slice hiện tại.</p>
    <label>Mã nhân sự<input placeholder="VD: NDK13 hoặc MRE-HR-013" value={form.employee_code} onChange={(e) => setForm({ ...form, employee_code: e.target.value })} required /></label>
    <label className="checkbox-row"><input type="checkbox" checked={form.create_account} onChange={(e) => setForm({ ...form, create_account: e.target.checked })} /><span><strong>Tạo tài khoản đăng nhập</strong><small>Bỏ chọn nếu hiện tại chỉ cần tạo hồ sơ nhân sự.</small></span></label>
    {form.create_account && <><label>Tài khoản<input placeholder="nguyen.dang.khoa" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required /></label>
    <label>Mật khẩu khởi tạo<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label></>}
    <label>Trạng thái<input value="Thử việc" disabled /></label>
    {error && <div className="alert alert--error">{error}</div>}
    <div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={busy}>{busy ? 'Đang tạo…' : form.create_account ? 'Tạo tài khoản + Employee' : 'Tạo Employee'}</button></div>
  </form></div>
}

function OrganizationPanel({ departments, teams, employees, canManage, reload }: { departments: Department[]; teams: Team[]; employees: Employee[]; canManage: boolean; reload: () => void }) {
  const [departmentForm, setDepartmentForm] = useState({ code: '', name: '' })
  const [teamForm, setTeamForm] = useState({ code: '', name: '', department: '' })
  const [error, setError] = useState('')
  const [selectedLeaders, setSelectedLeaders] = useState<Record<string, string>>({})
  const [teamLeaders, setTeamLeaders] = useState<Record<string, TeamLeader[]>>({})
  const leaders = employees.filter((employee) => employee.rank === 'leader')
  async function loadLeaders() {
    const entries = await Promise.all(teams.map(async (team) => [team.uuid, await api.teamLeaders(team.uuid)] as const))
    setTeamLeaders(Object.fromEntries(entries))
  }
  useEffect(() => {
    let active = true
    Promise.all(teams.map(async (team) => [team.uuid, await api.teamLeaders(team.uuid)] as const))
      .then((entries) => { if (active) setTeamLeaders(Object.fromEntries(entries)) })
      .catch((e) => { if (active) setError(e instanceof Error ? e.message : 'Không tải được Leader.') })
    return () => { active = false }
  }, [teams])
  async function submitDepartment(event: FormEvent) { event.preventDefault(); try { await api.createDepartment(departmentForm); setDepartmentForm({ code: '', name: '' }); reload() } catch (e) { setError(e instanceof Error ? e.message : 'Có lỗi.') } }
  async function submitTeam(event: FormEvent) { event.preventDefault(); try { await api.createTeam(teamForm); setTeamForm({ code: '', name: '', department: '' }); reload() } catch (e) { setError(e instanceof Error ? e.message : 'Có lỗi.') } }
  return <div className="organization-grid">
    <section className="panel"><div className="panel-head"><div><p className="eyebrow">ORGANIZATION</p><h3>Phòng ban</h3></div><span className="count-pill">{departments.length}</span></div>
      <div className="stack-list">{departments.map((item) => <div className="stack-row" key={item.uuid}><span className="org-icon">D</span><div><strong>{item.name}</strong><small>{item.code}</small></div><span className="status status--official">Hoạt động</span></div>)}</div>
      {canManage && <form className="inline-form" onSubmit={submitDepartment}><input placeholder="Mã" value={departmentForm.code} onChange={(e) => setDepartmentForm({ ...departmentForm, code: e.target.value.toUpperCase() })} required /><input placeholder="Tên phòng ban" value={departmentForm.name} onChange={(e) => setDepartmentForm({ ...departmentForm, name: e.target.value })} required /><button className="primary-button compact">Thêm</button></form>}
    </section>
    <section className="panel"><div className="panel-head"><div><p className="eyebrow">TEAM MAP</p><h3>Teams</h3></div><span className="count-pill">{teams.length}</span></div>
      <div className="stack-list">{teams.map((item) => <div className="stack-row stack-row--team" key={item.uuid}><span className="org-icon org-icon--team">T</span><div><strong>{item.name}</strong><small>{item.department_name} · {employees.filter((employee) => employee.team === item.uuid).length} thành viên · {(teamLeaders[item.uuid] ?? []).map((link) => link.leader_name || link.leader_code).join(', ') || 'Chưa có Leader'}</small></div>{canManage && <div className="leader-actions"><select aria-label={`Chọn Leader cho ${item.name}`} value={selectedLeaders[item.uuid] ?? ''} onChange={(e) => setSelectedLeaders({ ...selectedLeaders, [item.uuid]: e.target.value })}><option value="">Chọn Leader</option>{leaders.filter((leader) => !(teamLeaders[item.uuid] ?? []).some((link) => link.leader === leader.uuid)).map((leader) => <option key={leader.uuid} value={leader.uuid}>{leader.display_name || leader.employee_code}</option>)}</select><button className="text-button" disabled={!selectedLeaders[item.uuid]} onClick={() => api.addLeader(item.uuid, selectedLeaders[item.uuid]).then(() => { setSelectedLeaders({ ...selectedLeaders, [item.uuid]: '' }); reload(); return loadLeaders() }).catch((e) => setError(e.message))}>+ Leader</button>{(teamLeaders[item.uuid] ?? []).length > 0 && <button className="text-button text-button--danger" onClick={() => api.removeLeader(item.uuid, teamLeaders[item.uuid][teamLeaders[item.uuid].length - 1].leader).then(() => { reload(); return loadLeaders() }).catch((e) => setError(e.message))}>Gỡ cuối</button>}</div>}</div>)}</div>
      {canManage && <form className="inline-form inline-form--team" onSubmit={submitTeam}><input placeholder="Mã" value={teamForm.code} onChange={(e) => setTeamForm({ ...teamForm, code: e.target.value.toUpperCase() })} required /><input placeholder="Tên Team" value={teamForm.name} onChange={(e) => setTeamForm({ ...teamForm, name: e.target.value })} required /><select value={teamForm.department} onChange={(e) => setTeamForm({ ...teamForm, department: e.target.value })} required><option value="">Phòng ban</option>{departments.map((item) => <option key={item.uuid} value={item.uuid}>{item.name}</option>)}</select><button className="primary-button compact">Thêm</button></form>}
      {error && <div className="alert alert--error">{error}</div>}
    </section>
  </div>
}

function OrganizationChart({ departments, teams, employees }: { departments: Department[]; teams: Team[]; employees: Employee[] }) {
  const [teamLeaders, setTeamLeaders] = useState<Record<string, TeamLeader[]>>({})
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    Promise.all(teams.map(async (team) => [team.uuid, await api.teamLeaders(team.uuid)] as const))
      .then((entries) => { if (active) setTeamLeaders(Object.fromEntries(entries)) })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : 'Không tải được sơ đồ.') })
    return () => { active = false }
  }, [teams])

  return <section className="org-chart panel">
    <div className="org-chart__intro"><div><p className="eyebrow">ORGANIZATION MAP</p><h3>Sơ đồ tổ chức trong phạm vi của bạn</h3></div><span className="privacy-note">Dữ liệu đã lọc tại server</span></div>
    {error && <div className="alert alert--error">{error}</div>}
    <div className="department-tree">{departments.map((department) => {
      const departmentTeams = teams.filter((team) => team.department === department.uuid)
      return <article className="department-node" key={department.uuid}>
        <header><span className="org-icon">D</span><div><strong>{department.name}</strong><small>{department.code} · {departmentTeams.length} Team</small></div></header>
        <div className="team-branches">{departmentTeams.length === 0 ? <p className="tree-empty">Chưa có Team trong phạm vi.</p> : departmentTeams.map((team) => {
          const members = employees.filter((employee) => employee.team === team.uuid)
          return <section className="team-node" key={team.uuid}>
            <div className="team-node__head"><div><span className="org-icon org-icon--team">T</span><span><strong>{team.name}</strong><small>{team.code}</small></span></div><b>{members.length} người</b></div>
            <div className="leader-strip"><span>Leader</span><strong>{(teamLeaders[team.uuid] ?? []).map((link) => link.leader_name || link.leader_code).join(' · ') || 'Chưa gán'}</strong></div>
            <div className="member-cloud">{members.length === 0 ? <small>Chưa có thành viên</small> : members.map((employee) => <span className="member-chip" key={employee.uuid}><i>{initials(employee)}</i><b>{employee.display_name || employee.employee_code}</b></span>)}</div>
          </section>
        })}</div>
      </article>
    })}</div>
  </section>
}

function ProjectProgress() {
  const completedModules = projectStatus.modules.filter((module) => module.percent === 100).length
  return <div className="progress-dashboard">
    <section className="progress-hero">
      <div className="progress-hero__copy">
        <p className="eyebrow">PROJECT DELIVERY · CẬP NHẬT {projectStatus.updatedAt}</p>
        <h2>MRERP đang được xây đến đâu?</h2>
        <p>Tiến độ được đối chiếu với roadmap, story, code và bằng chứng kiểm thử. Prototype không được tính như một tính năng production đã hoàn thành.</p>
        <div className="phase-chip"><span className="live-dot" />{projectStatus.currentPhase} · {projectStatus.currentPhaseName}</div>
      </div>
      <div className="progress-orbit" style={{ '--progress': `${projectStatus.overallPercent * 3.6}deg` } as CSSProperties}>
        <div><strong>{projectStatus.overallPercent}%</strong><span>toàn dự án</span></div>
      </div>
    </section>

    <section className="progress-summary-grid">
      <article><span>Modules theo kế hoạch</span><strong>{projectStatus.modules.length}</strong><small>{completedModules} module hoàn tất 100%</small></article>
      <article><span>Quyết định đã giải quyết</span><strong>{projectStatus.decisions.resolved}</strong><small>{projectStatus.decisions.open} open decisions còn lại</small></article>
      <article><span>Automated tests People</span><strong>25</strong><small>SQLite và PostgreSQL đã xanh</small></article>
      <article><span>Ưu tiên quyết định</span><strong>OD-19</strong><small>Identity production vẫn chưa chốt</small></article>
    </section>

    <section className="progress-section">
      <div className="progress-section__head"><div><p className="eyebrow">ROADMAP</p><h3>Tiến độ theo phase</h3></div><small>{projectStatus.calculation}</small></div>
      <div className="phase-track">{projectStatus.phases.map((phase) => <article className={`phase-card phase-card--${phase.tone}`} key={phase.id}>
        <div><span>{phase.id}</span><b>{phase.percent}%</b></div><strong>{phase.name}</strong><small>{phase.state}</small><div className="mini-progress"><i style={{ width: `${phase.percent}%` }} /></div>
      </article>)}</div>
    </section>

    <section className="progress-layout">
      <div className="progress-section">
        <div className="progress-section__head"><div><p className="eyebrow">12 MODULES</p><h3>Bản đồ hoàn thiện</h3></div><span className="legend"><i /> Production slice <i /> Prototype/kế hoạch</span></div>
        <div className="module-progress-grid">{projectStatus.modules.map((module) => <article className="module-progress-card" key={module.name}>
          <div className="module-progress-card__top"><span className={`progress-state progress-state--${module.tone}`}>{module.state}</span><b>{module.percent}%</b></div>
          <h4>{module.name}</h4><small>{module.phase}</small>
          <div className="mini-progress"><i className={`tone--${module.tone}`} style={{ width: `${module.percent}%` }} /></div>
          <p>{module.next}</p>
        </article>)}</div>
      </div>
      <aside className="progress-side">
        <section className="progress-section">
          <p className="eyebrow">QUALITY SIGNALS</p><h3>Bằng chứng hiện tại</h3>
          <div className="quality-list">{projectStatus.quality.map((item) => <div key={item.label}><span><b>{item.label}</b><em>{item.state}</em></span><strong>{item.value}%</strong><div className="mini-progress"><i style={{ width: `${item.value}%` }} /></div></div>)}</div>
        </section>
        <section className="progress-section next-gates">
          <p className="eyebrow">NEXT GATES</p><h3>Việc cần làm tiếp</h3>
          <ol>{projectStatus.nextGates.map((gate) => <li key={gate}>{gate}</li>)}</ol>
          <div className="decision-note"><span>Decision debt ưu tiên</span><strong>{projectStatus.decisions.priority}</strong></div>
        </section>
      </aside>
    </section>
    <p className="progress-disclaimer">Màn hình Tiến độ là công cụ quản trị tạm thời và sẽ tự ẩn khi tổng tiến độ đạt 100%.</p>
  </div>
}

function Workspace({ session, onLogout, onSwitchSession }: { session: Session; onLogout: () => void; onSwitchSession: (session: Session) => void }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session])
  const canCreate = capabilities.has('people_domain.add_employee')
  const canEdit = capabilities.has('people_domain.change_employee')
  const canPromote = capabilities.has('people_domain.promote_employee')
  const canManageOrg = capabilities.has('people_domain.manage_organization')
  const canManageMembership = capabilities.has('people_domain.manage_membership')
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [selected, setSelected] = useState<Employee | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [tab, setTab] = useState<'people' | 'progress'>('people')
  const [peopleView, setPeopleView] = useState<'directory' | 'chart' | 'teams'>('directory')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [switchingPersona, setSwitchingPersona] = useState(false)
  const [personaError, setPersonaError] = useState('')

  async function switchPersona(username: string) {
    if (!username || username === session.username) return
    setSwitchingPersona(true); setPersonaError('')
    try { onSwitchSession(await api.switchPersona(username)) }
    catch (reason) { setPersonaError(reason instanceof Error ? reason.message : 'Không chuyển được persona debug.') }
    finally { setSwitchingPersona(false) }
  }

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [people, departmentItems, teamItems] = await Promise.all([api.allEmployees(search), api.allDepartments(), api.allTeams()])
      setEmployees(people); setDepartments(departmentItems); setTeams(teamItems)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được dữ liệu.') }
    finally { setLoading(false) }
  }, [search])

  useEffect(() => { const timer = window.setTimeout(load, 180); return () => window.clearTimeout(timer) }, [load])

  const probation = employees.filter((item) => item.employment_status === 'probation').length
  const promotionCandidates = employees.filter((item) => item.can_promote)
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">MRE<span>•</span></span><small>WORKSPACE</small></div>
      <nav><button className="nav-link"><span>⌂</span>Tổng quan</button>{showProjectProgress && <button className={`nav-link ${tab === 'progress' ? 'active' : ''}`} onClick={() => setTab('progress')}><span>↗</span>Tiến độ<strong>{projectStatus.overallPercent}%</strong></button>}<button className={`nav-link ${tab === 'people' ? 'active' : ''}`} onClick={() => setTab('people')}><span>◎</span>Nhân sự<strong>{employees.length}</strong></button><button className="nav-link"><span>✓</span>Công việc<em>Sắp tới</em></button></nav>
      <div className="sidebar-foot"><div className="mock-badge"><span className="live-dot" />Mock Identity</div><button className="user-card" onClick={onLogout}><span className="avatar">{(session.display_name ?? 'MR').slice(0, 2).toUpperCase()}</span><span><strong>{session.display_name}</strong><small>{session.employee_code} · Đăng xuất</small></span></button></div>
    </aside>
    <main className="workspace">
      <header className="topbar"><div><p className="eyebrow">PHASE 1 · PEOPLE FOUNDATION</p><h1>{tab === 'people' ? 'Nhân sự' : 'Tiến độ dự án'}</h1></div><div className="top-actions">{session.mock_identity && (session.debug_personas?.length ?? 0) > 0 && <label className="debug-role-switcher"><span><i className="live-dot" />Xem theo vai trò</span><select aria-label="Xem theo vai trò debug" value={session.username} disabled={switchingPersona} onChange={(event) => switchPersona(event.target.value)}>{session.debug_personas?.map((persona) => <option key={persona.username} value={persona.username}>{persona.label}</option>)}</select></label>}<button className="icon-button">◐</button></div></header>
      {personaError && <div className="alert alert--error persona-error">{personaError}</div>}
      {tab === 'progress' ? <ProjectProgress /> : <>
        <div className="people-tabs-row"><div className="segmented-tabs" role="tablist" aria-label="Các chế độ xem Nhân sự"><button className={peopleView === 'directory' ? 'active' : ''} onClick={() => setPeopleView('directory')}>Danh bạ</button><button className={peopleView === 'chart' ? 'active' : ''} onClick={() => setPeopleView('chart')}>Sơ đồ tổ chức</button><button className={peopleView === 'teams' ? 'active' : ''} onClick={() => setPeopleView('teams')}>Team</button></div>{canCreate && <button className="primary-button" onClick={() => setShowCreate(true)}>＋ Thêm nhân sự</button>}</div>
        {peopleView === 'directory' && <>
          {promotionCandidates.length > 0 && <section className="approval-strip"><div><span className="approval-strip__icon">✓</span><span><strong>{promotionCandidates.length} nhân sự chờ xác nhận chính thức</strong><small>Chỉ hiển thị người thuộc Team bạn đang lãnh đạo.</small></span></div><div className="approval-strip__people">{promotionCandidates.map((employee) => <button key={employee.uuid} onClick={async () => setSelected(await api.employee(employee.uuid))}>{employee.display_name || employee.employee_code}<span>Duyệt →</span></button>)}</div></section>}
          <section className="metric-grid"><article><span>Tổng hồ sơ trong scope</span><strong>{employees.length}</strong><small>Server đã lọc theo quyền</small></article><article><span>Đang thử việc</span><strong>{probation}</strong><small>{capabilities.has('people_domain.promote_employee') ? 'Chờ Leader cùng Team xác nhận' : 'Theo projection được cấp'}</small></article><article><span>Teams hiển thị</span><strong>{new Set(employees.map((item) => item.team).filter(Boolean)).size}</strong><small>{capabilities.has('people_domain.view_company_directory') ? 'Company scope' : 'Team scope'}</small></article></section>
          <section className="panel employee-panel"><div className="table-toolbar"><div className="search-box">⌕<input placeholder="Tìm theo mã, tên, vị trí…" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="privacy-note">⌾ Payload đã áp dụng field policy</div></div>
            {error && <div className="alert alert--error">{error}</div>}
            {loading ? <div className="empty-state">Đang tải dữ liệu theo scope…</div> : employees.length === 0 ? <div className="empty-state">Không có nhân sự phù hợp.</div> : <div className="employee-table"><div className="table-row table-head"><span>Nhân sự</span><span>Phòng ban</span><span>Team</span><span>Cấp bậc</span><span>Trạng thái</span><span /></div>{employees.map((employee) => <button className={`table-row ${employee.can_promote ? 'table-row--actionable' : ''}`} key={employee.uuid} onClick={async () => setSelected(await api.employee(employee.uuid))}><span className="person-cell"><span className="avatar">{initials(employee)}</span><span><strong>{employee.display_name || 'Chưa có họ tên'}</strong><small>{employee.employee_code} · {employee.job_title || 'Chưa có vị trí'}</small></span></span><span>{employee.department_name || '—'}</span><span>{employee.team_name || 'Chưa gán'}</span><span>{employee.rank ? labels[employee.rank] ?? employee.rank : '—'}</span><span>{employee.employment_status_label ? <b className={`status status--${employee.employment_status}`}>{employee.employment_status_label}</b> : <b className="status status--neutral">Trong scope</b>}</span><span className="view-action">{employee.can_promote ? 'Duyệt →' : 'Xem →'}</span></button>)}</div>}
          </section>
        </>}
        {peopleView === 'chart' && (loading ? <div className="empty-state panel">Đang dựng sơ đồ theo scope…</div> : <OrganizationChart departments={departments} teams={teams} employees={employees} />)}
        {peopleView === 'teams' && (loading ? <div className="empty-state panel">Đang tải Team…</div> : <OrganizationPanel departments={departments} teams={teams} employees={employees} canManage={canManageOrg && canManageMembership} reload={load} />)}
      </>}
    </main>
    {showCreate && <CreateEmployeeModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); load() }} />}
    {selected && <EmployeeDrawer employee={selected} departments={departments} teams={teams} canEdit={canEdit} canPromote={canPromote} canManageMembership={canManageMembership} onClose={() => setSelected(null)} onChanged={async () => { const refreshed = await api.employee(selected.uuid); setSelected(refreshed); setEmployees(await api.allEmployees(search)) }} />}
  </div>
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => { api.session().then(setSession).finally(() => setLoading(false)) }, [])
  if (loading) return <div className="boot-screen"><span className="brand-mark">MRE<span>•</span></span><p>Đang khởi tạo workspace…</p></div>
  if (!session?.authenticated) return <Login onLogin={setSession} />
  return <Workspace key={session.username} session={session} onSwitchSession={setSession} onLogout={async () => { await api.logout(); setSession({ authenticated: false }) }} />
}
