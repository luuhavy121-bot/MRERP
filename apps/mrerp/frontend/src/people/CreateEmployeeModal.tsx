import { useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { Employee } from '../types'

export function CreateEmployeeModal({ onClose, onCreated }: { onClose: () => void; onCreated: (employee: Employee) => Promise<void> }) {
  const [form, setForm] = useState({ employee_code: '', create_account: true, username: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await onCreated(await api.createEmployee(form))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể tạo nhân sự.')
    } finally {
      setBusy(false)
    }
  }

  return <div className="modal-backdrop" onMouseDown={onClose}><form className="modal" aria-label="Thêm nhân sự" onSubmit={submit} onMouseDown={(event) => event.stopPropagation()}>
    <div className="modal-head"><div><p className="eyebrow">QUICK CREATE</p><h2>Thêm nhân sự thử việc</h2></div><button type="button" className="icon-button" aria-label="Đóng" onClick={onClose}>×</button></div>
    <p className="muted">Employee luôn được tạo ở trạng thái Thử việc. Nếu tạo account, hệ thống sinh mật khẩu tạm và chỉ hiển thị một lần.</p>
    <label>Mã nhân sự<input placeholder="VD: NDK13 hoặc MRE-HR-013" value={form.employee_code} onChange={(event) => setForm({ ...form, employee_code: event.target.value })} required /></label>
    <label className="checkbox-row"><input type="checkbox" checked={form.create_account} onChange={(event) => setForm({ ...form, create_account: event.target.checked })} /><span><strong>Tạo tài khoản đăng nhập</strong><small>Bỏ chọn nếu hiện tại chỉ cần tạo hồ sơ nhân sự.</small></span></label>
    {form.create_account && <label>Tài khoản<input placeholder="nguyen.dang.khoa" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} required /></label>}
    <label>Trạng thái<input value="Thử việc" disabled /></label>
    {error && <div className="alert alert--error">{error}</div>}
    <div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={busy}>{busy ? 'Đang tạo…' : form.create_account ? 'Tạo tài khoản + Employee' : 'Tạo Employee'}</button></div>
  </form></div>
}
