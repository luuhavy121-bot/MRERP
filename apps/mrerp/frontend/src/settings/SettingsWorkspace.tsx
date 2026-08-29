import { useEffect, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { PersonalPreferences, Session } from '../types'

const mandatoryLabels: Record<string, string> = {
  account: 'Tài khoản', security: 'Bảo mật', task: 'Công việc', leave: 'Nghỉ phép', recruitment: 'Tuyển dụng',
}

export function SettingsWorkspace({ session }: { session: Session }) {
  const [preferences, setPreferences] = useState<PersonalPreferences | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.preferences().then(setPreferences).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được cài đặt.')).finally(() => setLoading(false))
  }, [])

  async function updateSocial(enabled: boolean) {
    if (!preferences) return
    const previous = preferences
    setSaving(true)
    setError('')
    setSaved(false)
    setPreferences({ ...preferences, social_notifications_enabled: enabled })
    try {
      setPreferences(await api.updatePreferences(enabled))
      setSaved(true)
    } catch (reason) {
      setPreferences(previous)
      setError(reason instanceof Error ? reason.message : 'Không lưu được cài đặt.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="phase3-loading" role="status"><span className="visually-hidden">Đang tải Cài đặt…</span><span /><span /><span /></div>
  if (!preferences) return <div className="state-panel state-panel--error"><strong>Chưa tải được cài đặt</strong><p>{error}</p></div>

  return <section className="settings-workspace phase3-workspace" aria-busy={saving}>
    <header className="phase3-intro">
      <div><h2>Cài đặt của bạn,<br />không ảnh hưởng người khác.</h2><p>Quản lý tín hiệu xã hội và kiểm tra nhanh trạng thái bảo mật của phiên hiện tại.</p></div>
      <span className="phase3-index">P3 · SETTINGS</span>
    </header>
    {error && <div className="alert alert--error" role="alert">{error}</div>}
    {saved && <div className="alert alert--success" role="status">Đã lưu cài đặt thông báo.</div>}
    <div className="settings-ledger">
      <section className="settings-ledger__section">
        <header><div><h3>Thông báo xã hội</h3><p>Áp dụng cho tương tác Bảng tin và lời ghi nhận mới.</p></div><AppIcon name="bell" /></header>
        <label className="preference-row">
          <span><strong>Nhận thông báo xã hội</strong><small>Tắt để giảm reaction, comment và Recognition trong Trung tâm thông báo.</small></span>
          <input aria-label="Nhận thông báo xã hội" type="checkbox" checked={preferences.social_notifications_enabled} disabled={saving} onChange={(event) => void updateSocial(event.target.checked)} />
          <i aria-hidden="true" />
        </label>
        <div className="mandatory-notice"><AppIcon name="lock" /><div><strong>Thông báo bắt buộc luôn được giữ</strong><p>{preferences.mandatory_notifications.map((item) => mandatoryLabels[item] ?? item).join(' · ')}</p></div></div>
      </section>
      <section className="settings-ledger__section settings-security">
        <header><div><h3>Trạng thái bảo mật</h3><p>Dữ liệu từ account và employment gate của server.</p></div><AppIcon name="settings" /></header>
        <dl>
          <div><dt>Tài khoản</dt><dd className={preferences.account_active ? 'signal-ok' : 'signal-danger'}>{preferences.account_active ? 'Đang hoạt động' : 'Đã khóa'}</dd></div>
          <div><dt>Trạng thái công việc</dt><dd>{preferences.employment_status_label}</dd></div>
          <div><dt>Mật khẩu</dt><dd className={preferences.must_change_password ? 'signal-warning' : 'signal-ok'}>{preferences.must_change_password ? 'Cần đổi mật khẩu' : 'Không có cảnh báo'}</dd></div>
          <div><dt>Phiên hiện tại</dt><dd>{session.mock_identity ? 'Mock Identity · Local only' : 'Identity session'}</dd></div>
        </dl>
        <p className="settings-security__note">Identity Provider production vẫn chưa được chọn. Trang này không tự tạo quản lý phiên SSO hoặc MFA.</p>
      </section>
    </div>
  </section>
}
