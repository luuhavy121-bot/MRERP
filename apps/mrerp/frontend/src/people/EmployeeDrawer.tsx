import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { Employee, EmployeeHistory, Team } from '../types'
import { initials, rankLabels } from './presentation'
import { AppIcon } from '../components/AppIcon'

export function EmployeeDrawer({ employee, teams, canEdit, canPromote, canManageMembership, onClose, onChanged }: {
  employee: Employee
  teams: Team[]
  canEdit: boolean
  canPromote: boolean
  canManageMembership: boolean
  onClose: () => void
  onChanged: () => Promise<void>
}) {
  const drawerRef = useRef<HTMLElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const [form, setForm] = useState({ display_name: employee.display_name ?? '', national_id: employee.national_id ?? '', date_of_birth: employee.date_of_birth ?? '', address: employee.address ?? '', job_title: employee.job_title ?? '' })
  const [promotionNote, setPromotionNote] = useState('')
  const [employmentNote, setEmploymentNote] = useState('')
  const [username, setUsername] = useState('')
  const [team, setTeam] = useState(employee.team ?? '')
  const [history, setHistory] = useState<EmployeeHistory | null>(null)
  const [temporaryPassword, setTemporaryPassword] = useState(employee.temporary_password ?? '')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const canSeeHistory = canEdit || canManageMembership || Boolean(employee.can_reset_password)
  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const drawer = drawerRef.current
    closeButtonRef.current?.focus()
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') { event.preventDefault(); onClose(); return }
      if (event.key !== 'Tab' || !drawer) return
      const focusable = Array.from(drawer.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'))
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => { document.removeEventListener('keydown', handleKeyDown); previousFocus?.focus() }
  }, [onClose])
  useEffect(() => {
    if (!canSeeHistory) return
    api.employeeHistory(employee.uuid).then(setHistory).catch(() => setHistory(null))
  }, [employee.uuid, canSeeHistory])

  async function run(action: () => Promise<unknown>, success = 'Đã lưu thay đổi.') {
    setBusy(true); setError(''); setMessage(''); setTemporaryPassword('')
    try { await action(); await onChanged(); setMessage(success) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể lưu thay đổi.') }
    finally { setBusy(false) }
  }

  async function runPassword(action: () => Promise<{ temporary_password?: string }>, success: string) {
    setBusy(true); setError(''); setMessage(''); setTemporaryPassword('')
    try { const result = await action(); await onChanged(); setTemporaryPassword(result.temporary_password ?? ''); setMessage(success) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể xử lý account.') }
    finally { setBusy(false) }
  }

  function employmentAction(command: 'pause' | 'terminate' | 'reactivate', label: string) {
    if (command === 'terminate' && !window.confirm('Xác nhận cho nhân sự nghỉ việc? Tài khoản sẽ bị khóa, quyền truy cập bị thu hồi và hồ sơ vẫn được giữ lại.')) return
    void run(() => api.changeEmployment(employee.uuid, command, employmentNote), label)
  }

  return <div className="drawer-backdrop people-drawer-backdrop" onMouseDown={onClose}>
    <aside ref={drawerRef} role="dialog" aria-modal="true" className="drawer drawer--wide people-detail-drawer" aria-label="Hồ sơ nhân sự" onMouseDown={(event) => event.stopPropagation()}>
      <button ref={closeButtonRef} className="icon-button drawer-close" aria-label="Đóng hồ sơ" onClick={onClose}><AppIcon name="close" /></button>
      <div className="drawer-identity-band">
        <div className="profile-head"><div className="avatar avatar--large">{initials(employee)}</div><div><span className="code-chip">{employee.employee_code}</span><h2>{employee.display_name || 'Chưa bổ sung họ tên'}</h2><p>{employee.job_title || 'Chưa có vị trí'} · {employee.team_name || 'Chưa vào Team'}</p></div></div>
        <div className="profile-meta"><div><span>Trạng thái</span><strong className={`status status--${employee.employment_status ?? 'neutral'}`}>{employee.employment_status_label ?? 'Hồ sơ cơ bản'}</strong></div><div><span>Team</span><strong>{employee.team_name || 'Chưa gán'}</strong></div><div><span>Cấp bậc</span><strong>{rankLabels[employee.rank ?? 'staff'] ?? employee.rank ?? 'Staff'}</strong></div></div>
      </div>
      {message && <div className="alert alert--success">{message}</div>}
      {temporaryPassword && <div className="temporary-password"><div><strong>Mật khẩu tạm — chỉ hiển thị lần này</strong><code>{temporaryPassword}</code></div><button className="secondary-button compact" onClick={() => navigator.clipboard.writeText(temporaryPassword)}>Sao chép</button></div>}
      {error && <div className="alert alert--error">{error}</div>}

      {canPromote && employee.employment_status === 'probation' && <section className={`promotion-box promotion-box--prominent ${employee.can_promote ? '' : 'promotion-box--blocked'}`}><div className="section-title"><span>Chuyển trạng thái công việc</span><small>Thử việc → Chính thức</small></div>{employee.can_promote ? <><textarea aria-label="Ghi chú xác nhận chính thức" placeholder="Ghi chú xác nhận bắt buộc…" value={promotionNote} onChange={(event) => setPromotionNote(event.target.value)} /><button className="primary-button compact" disabled={busy || !promotionNote.trim()} onClick={() => run(() => api.promoteEmployee(employee.uuid, promotionNote), 'Đã chuyển nhân sự lên Chính thức.')}><AppIcon name="check" />Chuyển lên Chính thức</button></> : <div className="promotion-blocked-message"><span><AppIcon name="lock" /></span><p><strong>Chưa thể chuyển lên Chính thức</strong><small>Leader chỉ duyệt nhân sự thuộc Team mình lãnh đạo.</small></p><button className="secondary-button compact" disabled>Chuyển lên Chính thức</button></div>}</section>}

      {employee.can_change_employment && <section className="drawer-section employment-admin-section employment-admin-section--prominent"><div className="section-title"><span>Trạng thái công việc</span><small>HR/CEO · Có audit</small></div><div className="employment-current-state"><span>Hiện tại</span><strong className={`status status--${employee.employment_status ?? 'neutral'}`}>{employee.employment_status_label}</strong></div><textarea aria-label="Ghi chú thay đổi employment" placeholder="Nhập lý do thay đổi trạng thái…" value={employmentNote} onChange={(event) => setEmploymentNote(event.target.value)} /><div className="employment-actions">{['probation', 'official'].includes(employee.employment_status ?? '') && <button className="secondary-button" disabled={busy || !employmentNote.trim()} onClick={() => employmentAction('pause', 'Đã chuyển sang Tạm nghỉ.')}>Chuyển sang Tạm nghỉ</button>}{employee.employment_status !== 'terminated' && <button className="danger-button" disabled={busy || !employmentNote.trim()} onClick={() => employmentAction('terminate', 'Đã cho nhân sự nghỉ việc.')}>Cho nghỉ việc</button>}{['paused', 'terminated'].includes(employee.employment_status ?? '') && <button className="primary-button" disabled={busy || !employmentNote.trim()} onClick={() => employmentAction('reactivate', 'Đã kích hoạt lại employment.')}>Kích hoạt lại</button>}</div><p className="employment-help">Tạm nghỉ: khóa tài khoản nhưng giữ quyền. Nghỉ việc: khóa tài khoản và thu hồi quyền; hồ sơ, lịch sử vẫn được lưu.</p></section>}

      {(employee.has_account !== undefined || employee.can_provision_account) && <section className="drawer-section account-admin-section"><div className="section-title"><span>Tài khoản đăng nhập</span><small>Credential đi qua Identity adapter; không lưu trong Employee</small></div><div className="account-status-row"><span><small>Tài khoản</small><strong>{employee.username || (employee.has_account ? 'Đã cấp' : 'Chưa cấp')}</strong></span><b className={`status ${employee.account_active ? 'status--official' : 'status--terminated'}`}>{employee.has_account ? (employee.account_active ? 'Đang hoạt động' : 'Đã khóa') : 'Chưa có account'}</b></div>{!employee.has_account && employee.can_provision_account && <div className="inline-action"><input aria-label="Username cấp mới" placeholder="Tên đăng nhập" value={username} onChange={(event) => setUsername(event.target.value)} /><button className="primary-button" disabled={busy || !username.trim()} onClick={() => runPassword(() => api.provisionAccount(employee.uuid, username), 'Đã cấp account và tạo mật khẩu tạm.')}>Cấp account</button></div>}{employee.has_account && <div className="account-action-grid">{employee.can_reset_password && <button className="secondary-button" disabled={busy} onClick={() => runPassword(() => api.resetEmployeePassword(employee.uuid), 'Đã đặt lại mật khẩu.')}>Đặt lại mật khẩu</button>}{employee.can_manage_account && employee.account_active && <button className="secondary-button" disabled={busy} onClick={() => run(() => api.lockEmployeeAccount(employee.uuid), 'Đã khóa account.')}>Khóa account</button>}{employee.can_manage_account && !employee.account_active && ['probation', 'official'].includes(employee.employment_status ?? '') && <button className="secondary-button" disabled={busy} onClick={() => run(() => api.unlockEmployeeAccount(employee.uuid), 'Đã mở khóa account.')}>Mở khóa account</button>}</div>}</section>}

      {canEdit && <section className="drawer-section"><div className="section-title"><span>Hồ sơ HR</span><small>Chỉ HR và CEO nhận payload này</small></div><div className="form-grid"><label>Họ và tên<input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} /></label><label>CCCD<input value={form.national_id} onChange={(event) => setForm({ ...form, national_id: event.target.value })} /></label><label>Ngày sinh<input type="date" value={form.date_of_birth} onChange={(event) => setForm({ ...form, date_of_birth: event.target.value })} /></label><label>Vị trí<input value={form.job_title} onChange={(event) => setForm({ ...form, job_title: event.target.value })} /></label><label className="span-2">Địa chỉ<textarea value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} /></label></div><button className="primary-button compact" disabled={busy} onClick={() => run(() => api.updateEmployee(employee.uuid, { ...form, date_of_birth: form.date_of_birth || null, expected_version: employee.version }), 'Đã lưu hồ sơ chi tiết.')}>{busy ? 'Đang lưu…' : 'Lưu hồ sơ chi tiết'}</button></section>}
      {canManageMembership && <section className="drawer-section"><div className="section-title"><span>Team hiện tại</span><small>Mỗi nhân sự thuộc tối đa một Team</small></div><div className="inline-action"><select aria-label="Team hiện tại" value={team} onChange={(event) => setTeam(event.target.value)}><option value="">Chưa vào Team</option>{teams.map((item) => <option key={item.uuid} value={item.uuid}>{item.name}</option>)}</select><button className="secondary-button" disabled={busy || team === (employee.team ?? '')} onClick={() => run(() => api.assignTeam(employee.uuid, team || null), 'Đã cập nhật Team.')}>Cập nhật Team</button></div></section>}
      {history && (history.employment.length > 0 || history.membership.length > 0) && <section className="drawer-section"><div className="section-title"><span>Lịch sử nhân sự</span><small>Employment và Team membership</small></div><div className="history-list">{history.employment.map((item) => <article key={item.uuid}><span className="audit-dot" /><div><strong>{item.from_label} → {item.to_label}</strong><small>{item.actor_name} · {new Date(item.effective_at).toLocaleString('vi-VN')}</small><p>{item.note}</p></div></article>)}{history.membership.map((item) => <article key={item.uuid}><span className="audit-dot" /><div><strong>{item.from_team_name || 'Chưa có Team'} → {item.to_team_name || 'Chưa có Team'}</strong><small>{item.actor_name} · {new Date(item.effective_at).toLocaleString('vi-VN')}</small><p>Thay đổi Team</p></div></article>)}</div></section>}
    </aside>
  </div>
}
