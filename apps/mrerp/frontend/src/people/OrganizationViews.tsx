import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { Employee, Team, TeamLeader } from '../types'
import { initials, rankLabels } from './presentation'

async function fetchLeaderships(teams: Team[]) {
  const entries = await Promise.all(teams.map(async (team) => [team.uuid, await api.teamLeaders(team.uuid)] as const))
  return Object.fromEntries(entries)
}

export function OrganizationPanel({ teams, employees, canManage, reload, onSelectEmployee }: {
  teams: Team[]
  employees: Employee[]
  canManage: boolean
  reload: () => Promise<void>
  onSelectEmployee: (employee: Employee) => Promise<void>
}) {
  const [teamForm, setTeamForm] = useState({ code: '', name: '' })
  const [selectedTeamUuid, setSelectedTeamUuid] = useState(teams[0]?.uuid ?? '')
  const [teamEdit, setTeamEdit] = useState({ code: teams[0]?.code ?? '', name: teams[0]?.name ?? '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState('')
  const [selectedLeader, setSelectedLeader] = useState('')
  const [teamLeaders, setTeamLeaders] = useState<Record<string, TeamLeader[]>>({})
  const leaders = employees.filter((employee) => employee.rank === 'leader')
  const selectedTeam = teams.find((team) => team.uuid === selectedTeamUuid)
  const selectedMembers = selectedTeam ? employees.filter((employee) => employee.team === selectedTeam.uuid) : []

  useEffect(() => {
    let active = true
    fetchLeaderships(teams)
      .then((entries) => { if (active) setTeamLeaders(entries) })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : 'Không tải được Leader.') })
    return () => { active = false }
  }, [teams])

  async function run(key: string, action: () => Promise<void>) {
    setBusy(key)
    setError('')
    try {
      await action()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể hoàn tất thao tác.')
    } finally {
      setBusy('')
    }
  }

  async function loadLeaders() {
    setTeamLeaders(await fetchLeaderships(teams))
  }

  async function submitTeam(event: FormEvent) {
    event.preventDefault()
    await run('create-team', async () => {
      const created = await api.createTeam(teamForm)
      setTeamForm({ code: '', name: '' })
      setSelectedTeamUuid(created.uuid)
      setTeamEdit({ code: created.code, name: created.name })
      await reload()
    })
  }

  function chooseTeam(team: Team) {
    setSelectedTeamUuid(team.uuid)
    setTeamEdit({ code: team.code, name: team.name })
    setSelectedLeader('')
    setError('')
  }

  async function saveTeam() {
    if (!selectedTeam) return
    await run('save-team', async () => {
      const updated = await api.updateTeam(selectedTeam.uuid, teamEdit)
      setTeamEdit({ code: updated.code, name: updated.name })
      await reload()
    })
  }

  async function archiveTeam() {
    if (!selectedTeam || !window.confirm(`Archive Team ${selectedTeam.name}? Team sẽ không còn xuất hiện trong danh sách hoạt động.`)) return
    await run('archive-team', async () => {
      await api.archiveTeam(selectedTeam.uuid)
      setSelectedTeamUuid('')
      await reload()
    })
  }

  async function addLeader() {
    if (!selectedTeam || !selectedLeader) return
    await run('add-leader', async () => {
      await api.addLeader(selectedTeam.uuid, selectedLeader)
      setSelectedLeader('')
      await loadLeaders()
    })
  }

  async function removeLeader(employeeUuid: string) {
    if (!selectedTeam) return
    await run(`remove-${employeeUuid}`, async () => {
      await api.removeLeader(selectedTeam.uuid, employeeUuid)
      await loadLeaders()
    })
  }

  return <div className="team-split-view">
    <section className="panel team-list-panel"><div className="panel-head"><div><p className="eyebrow">CEO → TEAMS</p><h3>Danh sách Team</h3></div><span className="count-pill">{teams.length}</span></div>
      <div className="team-selector-list">{teams.length === 0 ? <div className="empty-state">Chưa có Team.</div> : teams.map((item) => {
        const members = employees.filter((employee) => employee.team === item.uuid)
        return <button className={`team-selector ${selectedTeam?.uuid === item.uuid ? 'active' : ''}`} key={item.uuid} onClick={() => chooseTeam(item)}><span className="org-icon org-icon--team">T</span><span><strong>{item.name}</strong><small>{item.code} · {members.length} nhân sự</small></span><b>›</b></button>
      })}</div>
      {canManage && <form className="team-create-form" onSubmit={submitTeam}><p>Tạo Team mới</p><div><input placeholder="Mã Team" value={teamForm.code} onChange={(event) => setTeamForm({ ...teamForm, code: event.target.value.toUpperCase() })} required /><input placeholder="Tên Team" value={teamForm.name} onChange={(event) => setTeamForm({ ...teamForm, name: event.target.value })} required /><button className="primary-button compact" disabled={busy === 'create-team'}>{busy === 'create-team' ? 'Đang thêm…' : 'Thêm'}</button></div></form>}
    </section>
    <section className="panel team-detail-panel">{selectedTeam ? <>
      <div className="team-detail-head"><div><p className="eyebrow">TEAM DETAIL</p><h3>{selectedTeam.name}</h3><small>{selectedTeam.code} · {selectedMembers.length} nhân sự</small></div><span className="count-pill">{selectedMembers.length}</span></div>
      {canManage && <div className="team-settings"><div className="section-title"><span>Thông tin Team</span><small>Đổi mã/tên hoặc archive Team trống</small></div><div className="team-settings__form"><input aria-label="Mã Team" value={teamEdit.code} onChange={(event) => setTeamEdit({ ...teamEdit, code: event.target.value.toUpperCase() })} /><input aria-label="Tên Team" value={teamEdit.name} onChange={(event) => setTeamEdit({ ...teamEdit, name: event.target.value })} /><button className="secondary-button compact" disabled={busy !== '' || !teamEdit.code.trim() || !teamEdit.name.trim()} onClick={saveTeam}>Lưu</button><button className="danger-button compact" disabled={busy !== '' || selectedMembers.length > 0 || (teamLeaders[selectedTeam.uuid] ?? []).length > 0} title="Phải chuyển hết nhân sự và gỡ Leader trước" onClick={archiveTeam}>Archive</button></div></div>}
      <div className="team-leadership-block"><div className="section-title"><span>Leader của Team</span><small>Một Team có thể có nhiều Leader</small></div><div className="leader-chip-list">{(teamLeaders[selectedTeam.uuid] ?? []).length === 0 ? <span className="muted">Chưa có Leader</span> : (teamLeaders[selectedTeam.uuid] ?? []).map((link) => <span className="leader-chip" key={link.uuid}>{link.leader_name || link.leader_code}{canManage && <button aria-label={`Gỡ ${link.leader_name || link.leader_code}`} disabled={busy !== ''} onClick={() => removeLeader(link.leader)}>×</button>}</span>)}</div>{canManage && <div className="leader-picker"><select aria-label={`Chọn Leader cho ${selectedTeam.name}`} value={selectedLeader} onChange={(event) => setSelectedLeader(event.target.value)}><option value="">Chọn nhân sự cấp Leader</option>{leaders.filter((leader) => !(teamLeaders[selectedTeam.uuid] ?? []).some((link) => link.leader === leader.uuid)).map((leader) => <option key={leader.uuid} value={leader.uuid}>{leader.display_name || leader.employee_code}</option>)}</select><button className="secondary-button compact" disabled={busy !== '' || !selectedLeader} onClick={addLeader}>Gán Leader</button></div>}</div>
      <div className="team-member-block"><div className="section-title"><span>Nhân sự trong Team</span><small>Bấm vào một người để mở hồ sơ</small></div>{selectedMembers.length === 0 ? <div className="empty-state">Team này chưa có nhân sự.</div> : <div className="team-member-list">{selectedMembers.map((employee) => <button key={employee.uuid} onClick={() => onSelectEmployee(employee)}><span className="avatar">{initials(employee)}</span><span><strong>{employee.display_name || 'Chưa bổ sung họ tên'}</strong><small>{employee.employee_code} · {rankLabels[employee.rank ?? 'staff'] ?? employee.rank ?? 'Staff'}</small></span><b className={`status status--${employee.employment_status ?? 'neutral'}`}>{employee.employment_status_label ?? 'Trong Team'}</b><i>›</i></button>)}</div>}</div>
    </> : <div className="empty-state">Chọn hoặc tạo một Team để xem nhân sự.</div>}{error && <div className="alert alert--error">{error}</div>}</section>
  </div>
}

export function OrganizationChart({ teams, employees }: { teams: Team[]; employees: Employee[] }) {
  const [teamLeaders, setTeamLeaders] = useState<Record<string, TeamLeader[]>>({})
  const [error, setError] = useState('')
  const visibleTeams = teams

  useEffect(() => {
    let active = true
    fetchLeaderships(visibleTeams)
      .then((entries) => { if (active) setTeamLeaders(entries) })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : 'Không tải được sơ đồ.') })
    return () => { active = false }
  }, [visibleTeams])

  return <section className="org-chart panel">
    <div className="org-chart__intro"><div><p className="eyebrow">ORGANIZATION MAP</p><h3>Sơ đồ tổ chức trong phạm vi của bạn</h3></div><span className="privacy-note">Dữ liệu đã lọc tại server</span></div>
    {error && <div className="alert alert--error">{error}</div>}
    <div className="company-tree"><article className="company-node">
      <header><span className="org-icon org-icon--ceo">C</span><div><strong>CEO</strong><small>Cơ cấu phẳng · {visibleTeams.length} Team</small></div></header>
      <div className="team-branches">{visibleTeams.length === 0 ? <p className="tree-empty">Chưa có Team trong phạm vi.</p> : visibleTeams.map((team) => {
        const members = employees.filter((employee) => employee.team === team.uuid)
        return <section className="team-node" key={team.uuid}>
          <div className="team-node__head"><div><span className="org-icon org-icon--team">T</span><span><strong>{team.name}</strong><small>{team.code}</small></span></div><b>{members.length} người</b></div>
          <div className="leader-strip"><span>Leader</span><strong>{(teamLeaders[team.uuid] ?? []).map((link) => link.leader_name || link.leader_code).join(' · ') || 'Chưa gán'}</strong></div>
          <div className="member-cloud">{members.length === 0 ? <small>Chưa có thành viên</small> : members.map((employee) => <span className="member-chip" key={employee.uuid}><i>{initials(employee)}</i><b>{employee.display_name || employee.employee_code}</b></span>)}</div>
        </section>
      })}</div>
    </article></div>
  </section>
}
