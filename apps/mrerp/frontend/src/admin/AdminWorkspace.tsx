import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { AccessAccount, AuditEvent, Session } from '../types'

const bundleOptions = [
  { value: 'staff', label: 'Staff' },
  { value: 'leader', label: 'Leader' },
  { value: 'hr', label: 'HR' },
  { value: 'ceo', label: 'CEO' },
] as const

function currentBundle(account: AccessAccount) {
  const group = account.groups.find((name) => name.startsWith('People '))
  return (group?.replace('People ', '').toLowerCase() || 'staff') as 'staff' | 'leader' | 'hr' | 'ceo'
}

export function AdminWorkspace({ session }: { session: Session }) {
  const [accounts, setAccounts] = useState<AccessAccount[]>([])
  const [audit, setAudit] = useState<AuditEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [accessRows, auditPage] = await Promise.all([api.accessAccounts(), api.auditEvents()])
      setAccounts(accessRows)
      setAudit(auditPage.results)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được Admin Panel.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    Promise.all([api.accessAccounts(), api.auditEvents()]).then(([accessRows, auditPage]) => {
      setAccounts(accessRows)
      setAudit(auditPage.results)
    }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được Admin Panel.')).finally(() => setLoading(false))
  }, [])

  async function changeBundle(account: AccessAccount, bundle: 'staff' | 'leader' | 'hr' | 'ceo') {
    setBusy(account.employee_uuid); setError('')
    try { await api.updateAccessBundle(account.employee_uuid, bundle); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không cập nhật được access bundle.') }
    finally { setBusy('') }
  }

  if (loading) return <div className="empty-state panel">Đang tải quyền truy cập và audit…</div>
  return <div className="admin-workspace">
    <section className="admin-hero"><div><p className="eyebrow">CEO CONTROL PLANE</p><h2>Account & Access</h2><p>Quản lý access bundle cấp cao. Scope dữ liệu vẫn do quan hệ Team và server authorization quyết định.</p></div><div><strong>{accounts.filter((row) => row.account_active).length}</strong><span>account hoạt động</span></div></section>
    {error && <div className="alert alert--error">{error}</div>}
    <section className="panel access-panel">
      <div className="panel-head"><div><p className="eyebrow">ACCESS BUNDLE</p><h3>Quyền theo vai trò</h3></div><small>CEO không được tự đổi bundle của chính mình.</small></div>
      <div className="access-table"><div className="access-row access-row--head"><span>Nhân sự</span><span>Account</span><span>Team</span><span>Bundle</span><span>Capabilities</span></div>{accounts.map((account) => <div className="access-row" key={account.employee_uuid}><span><strong>{account.display_name}</strong><small>{account.employee_code}</small></span><span><strong>{account.username || 'Chưa cấp'}</strong><small>{account.account_active ? 'Đang hoạt động' : 'Chưa có / đã khóa'}</small></span><span>{account.team_name || '—'}</span><span><select aria-label={`Access bundle ${account.employee_code}`} disabled={!account.username || busy === account.employee_uuid || account.employee_uuid === session.employee_uuid} value={currentBundle(account)} onChange={(event) => changeBundle(account, event.target.value as 'staff' | 'leader' | 'hr' | 'ceo')}>{bundleOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></span><span><b>{account.capabilities.length}</b> quyền</span></div>)}</div>
    </section>
    <section className="panel audit-panel">
      <div className="panel-head"><div><p className="eyebrow">SECURITY AUDIT</p><h3>Thay đổi gần đây</h3></div><small>Không lưu password, token hoặc payload nhạy cảm.</small></div>
      <div className="audit-list">{audit.length === 0 ? <div className="empty-state">Chưa có audit event.</div> : audit.map((event) => <article key={event.uuid}><span className="audit-dot" /><div><strong>{event.action}</strong><small>{event.actor_name || 'Hệ thống'} · {new Date(event.created_at).toLocaleString('vi-VN')}</small></div><code>{event.target_type}</code></article>)}</div>
    </section>
  </div>
}
