import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import type { AuditEvent, Employee, Page, Session, Team } from '../types'
import { CreateEmployeeModal } from './CreateEmployeeModal'
import { EmployeeDrawer } from './EmployeeDrawer'
import { OrganizationChart, OrganizationPanel } from './OrganizationViews'
import { initials, rankLabels } from './presentation'
import { AppIcon } from '../components/AppIcon'

const emptyPage: Page<Employee> = { count: 0, next: null, previous: null, results: [] }

export function PeopleWorkspace({ session }: { session: Session }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session.capabilities])
  const canCreate = capabilities.has('people_domain.add_employee')
  const canEdit = capabilities.has('people_domain.change_employee')
  const canPromote = capabilities.has('people_domain.promote_employee')
  const canManageOrg = capabilities.has('people_domain.manage_organization')
  const canManageMembership = capabilities.has('people_domain.manage_membership')
  const canImportExport = capabilities.has('people_domain.import_export_employee')
  const canViewAudit = capabilities.has('people_domain.view_people_audit')
  const [directory, setDirectory] = useState<Page<Employee>>(emptyPage)
  const [organizationEmployees, setOrganizationEmployees] = useState<Employee[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [selected, setSelected] = useState<Employee | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [peopleView, setPeopleView] = useState<'directory' | 'chart' | 'teams' | 'audit'>('directory')
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([])
  const fileInput = useRef<HTMLInputElement>(null)
  const [search, setSearch] = useState('')
  const [teamFilter, setTeamFilter] = useState('')
  const [page, setPage] = useState(1)
  const [directoryLoading, setDirectoryLoading] = useState(true)
  const [organizationLoading, setOrganizationLoading] = useState(false)
  const [error, setError] = useState('')
  const closeEmployee = useCallback(() => setSelected(null), [])

  const loadDirectory = useCallback(async () => {
    setDirectoryLoading(true)
    setError('')
    try {
      setDirectory(await api.employees({ search, team: teamFilter, page }))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được danh bạ.')
    } finally {
      setDirectoryLoading(false)
    }
  }, [page, search, teamFilter])

  const loadOrganization = useCallback(async () => {
    setOrganizationLoading(true)
    setError('')
    try {
      const [employees, teamItems] = await Promise.all([api.allEmployees(), api.allTeams()])
      setOrganizationEmployees(employees)
      setTeams(teamItems)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được dữ liệu tổ chức.')
    } finally {
      setOrganizationLoading(false)
    }
  }, [])

  useEffect(() => {
    api.allTeams().then(setTeams).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được Team.'))
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(loadDirectory, 180)
    return () => window.clearTimeout(timer)
  }, [loadDirectory])

  async function refreshAll() {
    await loadDirectory()
    if (peopleView !== 'directory' || organizationEmployees.length > 0) await loadOrganization()
  }

  async function openEmployee(employee: Employee) {
    setError('')
    try {
      setSelected(await api.employee(employee.uuid))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không mở được hồ sơ.')
    }
  }

  function changeView(nextView: 'directory' | 'chart' | 'teams' | 'audit') {
    setPeopleView(nextView)
    if (nextView !== 'directory') void loadOrganization()
    if (nextView === 'audit') api.auditEvents().then((result) => setAuditEvents(result.results)).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được audit.'))
  }

  async function importCsv(file?: File) {
    if (!file) return
    setError('')
    try { const result = await api.importEmployees(file); await refreshAll(); window.alert(`Đã tạo ${result.created} hồ sơ thử việc. Không account nào được tự động tạo.`) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không nhập được CSV.') }
    finally { if (fileInput.current) fileInput.current.value = '' }
  }

  async function exportCsv() {
    setError('')
    try {
      const blob = await api.exportEmployees()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a'); link.href = url; link.download = 'mrerp-employees.csv'; link.click()
      URL.revokeObjectURL(url)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không xuất được CSV.') }
  }

  const probationOnPage = directory.results.filter((item) => item.employment_status === 'probation').length
  const promotionCandidates = directory.results.filter((item) => item.can_promote)
  const totalPages = Math.max(1, Math.ceil(directory.count / 20))

  return <section className={`people-workspace ${selected ? 'people-workspace--detail-open' : ''}`}>
    <header className="people-command-stage">
      <div className="people-command-stage__identity">
        <h1>NHÂN SỰ</h1>
        <div className="people-metrics" aria-label="Tổng quan danh bạ">
          <span><strong>{String(directory.count).padStart(2, '0')}</strong><small>hồ sơ</small></span>
          <span><strong>{String(probationOnPage).padStart(2, '0')}</strong><small>thử việc</small></span>
          <span><strong>{String(teams.length).padStart(2, '0')}</strong><small>Team</small></span>
        </div>
      </div>
      <div className="people-command-tools">
        <label className="people-search"><span className="visually-hidden">Tìm nhân sự</span><input aria-label="Tìm nhân sự" placeholder="Tìm kiếm nhân sự…" value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} /></label>
        <label className="people-filter"><span>Bộ lọc</span><select aria-label="Lọc theo Team" value={teamFilter} onChange={(event) => { setTeamFilter(event.target.value); setPage(1) }}><option value="">Tất cả Team</option>{teams.map((team) => <option key={team.uuid} value={team.uuid}>{team.name}</option>)}</select></label>
        {canCreate && <button className="primary-button people-create-button" onClick={() => setShowCreate(true)}><AppIcon name="plus" />Thêm nhân sự</button>}
      </div>
    </header>
    <div className="people-tabs-row"><div className="segmented-tabs" role="tablist" aria-label="Các chế độ xem Nhân sự"><button role="tab" aria-selected={peopleView === 'directory'} className={peopleView === 'directory' ? 'active' : ''} onClick={() => changeView('directory')}>Danh bạ</button><button role="tab" aria-selected={peopleView === 'chart'} className={peopleView === 'chart' ? 'active' : ''} onClick={() => changeView('chart')}>Sơ đồ tổ chức</button><button role="tab" aria-selected={peopleView === 'teams'} className={peopleView === 'teams' ? 'active' : ''} onClick={() => changeView('teams')}>Team</button>{canViewAudit && <button role="tab" aria-selected={peopleView === 'audit'} className={peopleView === 'audit' ? 'active' : ''} onClick={() => changeView('audit')}>Nhật ký</button>}</div><div className="people-actions">{canImportExport && <><input ref={fileInput} className="visually-hidden" type="file" accept=".csv,text/csv" onChange={(event) => void importCsv(event.target.files?.[0])} /><button className="secondary-button" onClick={() => fileInput.current?.click()}>Nhập CSV</button><button className="secondary-button" onClick={exportCsv}>Xuất CSV</button></>}</div></div>
    {error && <div className="alert alert--error">{error}</div>}
    {peopleView === 'directory' && <>
      {promotionCandidates.length > 0 && <section className="approval-strip"><div><span className="approval-strip__icon"><AppIcon name="check" /></span><span><strong>{promotionCandidates.length} nhân sự chờ xác nhận chính thức trên trang này</strong><small>Chỉ hiển thị người thuộc Team bạn đang lãnh đạo.</small></span></div><div className="approval-strip__people">{promotionCandidates.map((employee) => <button key={employee.uuid} onClick={() => openEmployee(employee)}>{employee.display_name || employee.employee_code}<span>Duyệt →</span></button>)}</div></section>}
      <section className="panel employee-panel">
        {directoryLoading ? <div className="empty-state">Đang tải dữ liệu theo scope…</div> : directory.results.length === 0 ? <div className="empty-state">Không có nhân sự phù hợp.</div> : <div className="employee-table"><div className="table-row table-head"><span>Nhân sự</span><span>Team</span><span>Cấp bậc</span><span>Trạng thái</span><span>Xem</span></div>{directory.results.map((employee) => <button aria-pressed={selected?.uuid === employee.uuid} className={`table-row ${employee.can_promote ? 'table-row--actionable' : ''} ${selected?.uuid === employee.uuid ? 'table-row--selected' : ''}`} key={employee.uuid} onClick={() => openEmployee(employee)}><span className="person-cell"><span className="avatar">{initials(employee)}</span><span><strong>{employee.display_name || 'Chưa có họ tên'}</strong><small>{employee.employee_code} · {employee.job_title || 'Chưa có vị trí'}</small></span></span><span>{employee.team_name || 'Chưa gán'}</span><span>{employee.rank ? rankLabels[employee.rank] ?? employee.rank : '—'}</span><span>{employee.employment_status_label ? <b className={`status status--${employee.employment_status}`}>{employee.employment_status_label}</b> : <b className="status status--neutral">Trong scope</b>}</span><span className="view-action">{selected?.uuid === employee.uuid ? 'Đang mở' : employee.can_promote ? 'Duyệt →' : 'Xem →'}</span></button>)}</div>}
        <div className="pagination"><button className="secondary-button compact" disabled={!directory.previous || directoryLoading} onClick={() => setPage((value) => Math.max(1, value - 1))}>← Trước</button><span>Trang {page}/{totalPages} · {directory.count} hồ sơ</span><button className="secondary-button compact" disabled={!directory.next || directoryLoading} onClick={() => setPage((value) => value + 1)}>Sau →</button></div>
      </section>
    </>}
    {peopleView === 'chart' && (organizationLoading ? <div className="empty-state panel">Đang dựng sơ đồ theo scope…</div> : <OrganizationChart teams={teams} employees={organizationEmployees} />)}
    {peopleView === 'teams' && (organizationLoading ? <div className="empty-state panel">Đang tải Team…</div> : <OrganizationPanel teams={teams} employees={organizationEmployees} canManage={canManageOrg && canManageMembership} reload={loadOrganization} onSelectEmployee={openEmployee} />)}
    {peopleView === 'audit' && <section className="panel audit-panel"><div className="panel-head"><div><p className="eyebrow">PEOPLE AUDIT</p><h3>Nhật ký thao tác</h3></div><small>HR chỉ thấy Employee, account, employment và membership.</small></div><div className="audit-list">{auditEvents.length === 0 ? <div className="empty-state">Chưa có audit event trong scope.</div> : auditEvents.map((event) => <article key={event.uuid}><span className="audit-dot" /><div><strong>{event.action}</strong><small>{event.actor_name || 'Hệ thống'} · {new Date(event.created_at).toLocaleString('vi-VN')}</small></div><code>{event.target_type}</code></article>)}</div></section>}
    {showCreate && <CreateEmployeeModal onClose={() => setShowCreate(false)} onCreated={async (employee) => { setShowCreate(false); await refreshAll(); setSelected(employee) }} />}
    {selected && <EmployeeDrawer employee={selected} teams={teams} canEdit={canEdit} canPromote={canPromote} canManageMembership={canManageMembership} onClose={closeEmployee} onChanged={async () => { const refreshed = await api.employee(selected.uuid); setSelected(refreshed); await refreshAll() }} />}
  </section>
}
