import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import type { AttendanceRow, LeaveRequest, Session } from '../types'

type LeaveView = 'mine' | 'review' | 'attendance'

function todayMonth() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('vi-VN').format(new Date(`${value}T00:00:00`))
}

function statusClass(status: LeaveRequest['status']) {
  if (status === 'approved') return 'status status--official'
  if (status === 'rejected') return 'status leave-status--rejected'
  return 'status status--probation'
}

export function LeaveWorkspace({ session }: { session: Session }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session.capabilities])
  const canReview = capabilities.has('leave_domain.review_team_leave_request')
  const canViewAttendance = capabilities.has('leave_domain.view_company_attendance')
  const canAdjustAttendance = capabilities.has('leave_domain.adjust_company_attendance')
  const [view, setView] = useState<LeaveView>('mine')
  const [requests, setRequests] = useState<LeaveRequest[]>([])
  const [attendance, setAttendance] = useState<AttendanceRow[]>([])
  const [month, setMonth] = useState(todayMonth())
  const [form, setForm] = useState({ start_date: '', end_date: '', reason: '' })
  const [editing, setEditing] = useState<LeaveRequest | null>(null)
  const [adjusting, setAdjusting] = useState<AttendanceRow | null>(null)
  const [adjustment, setAdjustment] = useState({ days: 0, reason: '' })
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadRequests = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setRequests((await api.leaveRequests()).results)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được đơn nghỉ.')
    } finally {
      setLoading(false)
    }
  }, [])

  const loadAttendance = useCallback(async (monthValue: string) => {
    if (!canViewAttendance) return
    setLoading(true)
    setError('')
    try {
      setAttendance(await api.attendance(monthValue))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được bảng công.')
    } finally {
      setLoading(false)
    }
  }, [canViewAttendance])

  useEffect(() => {
    api.leaveRequests()
      .then((response) => setRequests(response.results))
      .catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được đơn nghỉ.'))
      .finally(() => setLoading(false))
  }, [])

  const ownRequests = requests.filter((item) => item.requester_code === session.employee_code)
  const reviewQueue = requests.filter((item) => item.can_review && item.status === 'pending')

  async function submitLeave(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      if (editing) await api.updateLeave(editing.uuid, { ...form, expected_version: editing.version })
      else await api.submitLeave(form)
      setForm({ start_date: '', end_date: '', reason: '' })
      setEditing(null)
      await loadRequests()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không gửi được đơn nghỉ.')
    } finally {
      setBusy(false)
    }
  }

  function startEditing(item: LeaveRequest) {
    setEditing(item)
    setForm({ start_date: item.start_date, end_date: item.end_date, reason: item.reason })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function cancelEditing() {
    setEditing(null)
    setForm({ start_date: '', end_date: '', reason: '' })
  }

  function startAdjustment(row: AttendanceRow) {
    setAdjusting(row)
    setAdjustment({ days: row.adjustment_days, reason: row.adjustment_reason })
  }

  async function saveAdjustment(event: React.FormEvent) {
    event.preventDefault()
    if (!adjusting) return
    setBusy(true)
    setError('')
    try {
      await api.adjustAttendance({ employee_uuid: adjusting.employee_uuid, month, ...adjustment })
      setAdjusting(null)
      await loadAttendance(month)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không lưu được điều chỉnh.')
    } finally {
      setBusy(false)
    }
  }

  async function review(uuid: string, decision: 'approved' | 'rejected') {
    setBusy(true)
    setError('')
    try {
      await api.reviewLeave(uuid, decision)
      await loadRequests()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không xử lý được ticket.')
    } finally {
      setBusy(false)
    }
  }

  const visibleRequests = view === 'review' ? reviewQueue : ownRequests

  return <section className="leave-workspace">
    <div className="leave-hero">
      <div><p className="eyebrow">LEAVE & ATTENDANCE</p><h2>Xin nghỉ, duyệt,<br />cập nhật ngày công.</h2><p>Nhân sự gửi đơn, Leader duyệt một cấp. Ngày nghỉ đã duyệt tự động trừ khỏi công dự kiến.</p></div>
      <div className="leave-hero__metric"><span>Đang chờ xử lý</span><strong>{canReview ? reviewQueue.length : ownRequests.filter((item) => item.status === 'pending').length}</strong><small>{canReview ? 'Ticket trong Team của bạn' : 'Đơn của bạn'}</small></div>
    </div>

    <div className="leave-tabs-row">
      <div className="segmented-tabs" role="tablist" aria-label="Chế độ Leave">
        <button className={view === 'mine' ? 'active' : ''} onClick={() => setView('mine')}>Đơn của tôi</button>
        {canReview && <button className={view === 'review' ? 'active' : ''} onClick={() => setView('review')}>Cần duyệt <b>{reviewQueue.length}</b></button>}
        {canViewAttendance && <button className={view === 'attendance' ? 'active' : ''} onClick={() => { setView('attendance'); void loadAttendance(month) }}>Bảng công</button>}
      </div>
      <span className="privacy-note">⌾ Quyền và Team được kiểm tra tại server</span>
    </div>

    {error && <div className="alert alert--error">{error}</div>}

    {view === 'mine' && <div className="leave-layout">
      <form className="panel leave-form" onSubmit={submitLeave}>
        <div className="panel-head"><div><p className="eyebrow">{editing ? 'CHỈNH SỬA' : 'TẠO TICKET'}</p><h3>{editing ? 'Sửa đơn đang chờ' : 'Xin nghỉ'}</h3></div><span className="org-icon">↗</span></div>
        <div className="leave-form__body">
          <div className="leave-date-grid"><label>Từ ngày<input aria-label="Từ ngày" type="date" required value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} /></label><label>Đến ngày<input aria-label="Đến ngày" type="date" required value={form.end_date} onChange={(event) => setForm({ ...form, end_date: event.target.value })} /></label></div>
          <label>Lý do<textarea aria-label="Lý do nghỉ" required maxLength={2000} placeholder="Mô tả ngắn gọn lý do xin nghỉ…" value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} /></label>
          <p className="form-note">Hiện hỗ trợ nghỉ nguyên ngày. Leader của Team tại thời điểm gửi sẽ nhận ticket.</p>
          <div className="leave-form__actions">{editing && <button type="button" className="secondary-button" disabled={busy} onClick={cancelEditing}>Hủy sửa</button>}<button className="primary-button" disabled={busy}>{busy ? 'Đang lưu…' : editing ? 'Lưu thay đổi' : 'Gửi đơn xin nghỉ'}</button></div>
        </div>
      </form>
      <LeaveList title="Lịch sử đơn của tôi" requests={visibleRequests} loading={loading} busy={busy} onReview={review} onEdit={startEditing} />
    </div>}

    {view === 'review' && <LeaveList title="Ticket cần bạn xử lý" requests={visibleRequests} loading={loading} busy={busy} onReview={review} reviewMode />}

    {view === 'attendance' && <section className="panel attendance-panel">
      <div className="panel-head attendance-head"><div><p className="eyebrow">ATTENDANCE PROJECTION</p><h3>Bảng công nhân sự</h3></div><label>Tháng<input aria-label="Tháng bảng công" type="month" value={month} onChange={(event) => { setMonth(event.target.value); void loadAttendance(event.target.value) }} /></label></div>
      {adjusting && <form className="attendance-adjustment" onSubmit={saveAdjustment}><div><strong>Điều chỉnh cho {adjusting.display_name}</strong><small>{month} · Số ngày có thể âm hoặc dương</small></div><label>Số ngày<input aria-label="Số ngày điều chỉnh" type="number" min="-31" max="31" value={adjustment.days} onChange={(event) => setAdjustment({ ...adjustment, days: Number(event.target.value) })} /></label><label className="adjustment-reason">Lý do<input aria-label="Lý do điều chỉnh" required maxLength={500} value={adjustment.reason} onChange={(event) => setAdjustment({ ...adjustment, reason: event.target.value })} /></label><button type="button" className="secondary-button compact" onClick={() => setAdjusting(null)}>Hủy</button><button className="primary-button compact" disabled={busy || !adjustment.reason.trim()}>Lưu</button></form>}
      {loading ? <div className="empty-state">Đang tải bảng công…</div> : <div className="attendance-table">
        <div className="attendance-row attendance-row--head"><span>Nhân sự</span><span>Team</span><span>Ngày lễ</span><span>Công chuẩn</span><span>Nghỉ duyệt</span><span>Điều chỉnh</span><span>Công dự kiến</span><span /></div>
        {attendance.map((row) => <div className="attendance-row" key={row.employee_uuid}><span><strong>{row.display_name}</strong><small>{row.employee_code}</small></span><span>{row.team_name ?? 'Chưa vào Team'}</span><span>{row.public_holiday_days}</span><span>{row.scheduled_workdays}</span><span className={row.approved_leave_days ? 'leave-days' : ''}>{row.approved_leave_days}</span><span title={row.adjustment_reason}>{row.adjustment_days > 0 ? `+${row.adjustment_days}` : row.adjustment_days}</span><span><strong>{row.projected_workdays}</strong></span><span>{canAdjustAttendance && <button className="secondary-button compact" onClick={() => startAdjustment(row)}>Điều chỉnh</button>}</span></div>)}
      </div>}
      <p className="attendance-disclaimer">Công chuẩn = thứ Hai–thứ Sáu trừ ngày lễ Việt Nam. Công dự kiến trừ đơn đã duyệt và cộng điều chỉnh HR; chưa phải bảng lương.</p>
    </section>}
  </section>
}

function LeaveList({ title, requests, loading, busy, onReview, onEdit, reviewMode = false }: { title: string; requests: LeaveRequest[]; loading: boolean; busy: boolean; onReview: (uuid: string, decision: 'approved' | 'rejected') => void; onEdit?: (item: LeaveRequest) => void; reviewMode?: boolean }) {
  return <section className="panel leave-list-panel">
    <div className="panel-head"><div><p className="eyebrow">{reviewMode ? 'APPROVAL QUEUE' : 'REQUEST HISTORY'}</p><h3>{title}</h3></div><span className="count-pill">{requests.length}</span></div>
    {loading ? <div className="empty-state">Đang tải ticket…</div> : requests.length === 0 ? <div className="empty-state"><strong>Chưa có ticket nào</strong><p>{reviewMode ? 'Không có đơn nào đang chờ bạn xử lý.' : 'Đơn mới sẽ xuất hiện tại đây.'}</p></div> : <div className="leave-ticket-list">{requests.map((item) => <article className="leave-ticket" key={item.uuid}>
      <div className="leave-ticket__date"><strong>{formatDate(item.start_date)}</strong>{item.start_date !== item.end_date && <span>→ {formatDate(item.end_date)}</span>}</div>
      <div className="leave-ticket__body"><div><strong>{reviewMode ? item.requester_name || item.requester_code : item.reason}</strong><span className={statusClass(item.status)}>{item.status_label}</span></div>{reviewMode && <p>{item.reason}</p>}<small>{item.team_name ?? 'Chưa vào Team'} · Gửi {formatDate(item.created_at.slice(0, 10))}</small></div>
      <div className="leave-ticket__actions">{!reviewMode && item.can_edit && onEdit && <button className="secondary-button compact" disabled={busy} onClick={() => onEdit(item)}>Sửa đơn</button>}{reviewMode && item.can_review && <><button className="secondary-button compact" disabled={busy} onClick={() => onReview(item.uuid, 'rejected')}>Từ chối</button><button className="primary-button compact" disabled={busy} onClick={() => onReview(item.uuid, 'approved')}>Duyệt</button></>}</div>
    </article>)}</div>}
  </section>
}
