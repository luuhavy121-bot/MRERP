import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Employee, Session } from '../types'
import { initials, rankLabels } from '../people/presentation'

export function ProfileWorkspace({ session, onProfileUpdated }: { session: Session; onProfileUpdated: (employee: Employee) => void }) {
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [form, setForm] = useState({ display_name: '', date_of_birth: '', address: '' })
  const [password, setPassword] = useState({ current: '', next: '', confirm: '' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    api.me().then((result) => {
      setEmployee(result)
      setForm({ display_name: result.display_name ?? '', date_of_birth: result.date_of_birth ?? '', address: result.address ?? '' })
    }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được hồ sơ.')).finally(() => setLoading(false))
  }, [])

  async function saveProfile() {
    if (!employee?.version) return
    setSaving(true); setError(''); setMessage('')
    try {
      const updated = await api.updateMe({ ...form, date_of_birth: form.date_of_birth || null, expected_version: employee.version })
      setEmployee(updated)
      onProfileUpdated(updated)
      setMessage('Đã lưu thông tin cá nhân.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không lưu được hồ sơ.')
    } finally { setSaving(false) }
  }

  async function changePassword() {
    setError(''); setMessage('')
    if (password.next.length < 12) { setError('Mật khẩu mới cần ít nhất 12 ký tự.'); return }
    if (password.next !== password.confirm) { setError('Xác nhận mật khẩu chưa khớp.'); return }
    setSaving(true)
    try {
      await api.changeOwnPassword(password.current, password.next)
      setPassword({ current: '', next: '', confirm: '' })
      setEmployee((current) => current ? { ...current, must_change_password: false } : current)
      setMessage('Đã đổi mật khẩu. Phiên đăng nhập hiện tại vẫn được giữ an toàn.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không đổi được mật khẩu.')
    } finally { setSaving(false) }
  }

  if (loading) return <div className="empty-state panel">Đang tải hồ sơ của bạn…</div>
  if (!employee) return <div className="alert alert--error">{error || 'Không tìm thấy hồ sơ gắn với account này.'}</div>

  return <div className="profile-workspace">
    {employee.must_change_password && <div className="security-banner"><span>!</span><div><strong>Đây là mật khẩu tạm</strong><small>Hãy đổi mật khẩu trước khi tiếp tục sử dụng account lâu dài.</small></div></div>}
    {error && <div className="alert alert--error">{error}</div>}
    {message && <div className="alert alert--success">{message}</div>}
    <section className="profile-hero panel">
      <span className="avatar avatar--xl">{initials(employee)}</span>
      <div className="profile-hero__identity"><span>Hồ sơ của tôi</span><h2>{employee.display_name || 'Chưa bổ sung họ tên'}</h2><p>{employee.employee_code} · {employee.job_title || 'Chưa có vị trí'}</p></div>
      <dl className="profile-hero__facts"><div><dt>Team</dt><dd>{employee.team_name || 'Chưa vào Team'}</dd></div><div><dt>Cấp bậc</dt><dd>{rankLabels[employee.rank ?? 'staff'] ?? employee.rank}</dd></div><div><dt>Trạng thái</dt><dd className={`status status--${employee.employment_status}`}>{employee.employment_status_label}</dd></div></dl>
    </section>
    <div className="profile-layout">
      <section className="panel settings-card">
        <div className="panel-head"><div><p className="eyebrow">THÔNG TIN CÁ NHÂN</p><h3>Thông tin tôi có thể cập nhật</h3></div></div>
        <div className="settings-card__body form-grid">
          <label className="span-2">Họ và tên<input value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} /></label>
          <label>Ngày sinh<input type="date" value={form.date_of_birth} onChange={(event) => setForm({ ...form, date_of_birth: event.target.value })} /></label>
          <label>Mã nhân sự<input value={employee.employee_code} disabled /></label>
          <label className="span-2">Địa chỉ<textarea value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} /></label>
          <button className="primary-button span-2" disabled={saving} onClick={saveProfile}>{saving ? 'Đang lưu…' : 'Lưu hồ sơ của tôi'}</button>
        </div>
      </section>
      <section className="panel settings-card">
        <div className="panel-head"><div><p className="eyebrow">TÀI KHOẢN & BẢO MẬT</p><h3>Đăng nhập của tôi</h3></div><b className={`status ${employee.account_active ? 'status--official' : 'status--terminated'}`}>{employee.account_active ? 'Đang hoạt động' : 'Đã khóa'}</b></div>
        <div className="account-summary"><span><small>Tài khoản</small><strong>{employee.username || session.username || 'Chưa cấp'}</strong></span><span><small>Account được quản lý bởi</small><strong>Identity adapter</strong></span></div>
        {employee.has_account && <div className="settings-card__body password-form">
          <label>Mật khẩu hiện tại<input type="password" autoComplete="current-password" value={password.current} onChange={(event) => setPassword({ ...password, current: event.target.value })} /></label>
          <label>Mật khẩu mới<input type="password" autoComplete="new-password" value={password.next} onChange={(event) => setPassword({ ...password, next: event.target.value })} /></label>
          <label>Xác nhận mật khẩu<input type="password" autoComplete="new-password" value={password.confirm} onChange={(event) => setPassword({ ...password, confirm: event.target.value })} /></label>
          <small className="field-help">Tối thiểu 12 ký tự. Không chia sẻ mật khẩu qua chat hoặc ghi vào hồ sơ.</small>
          <button className="secondary-button" disabled={saving || !password.current || !password.next || !password.confirm} onClick={changePassword}>Đổi mật khẩu</button>
        </div>}
      </section>
    </div>
  </div>
}
