import { useEffect, useRef, useState } from 'react'
import { request } from '../api'
import type { Session } from '../types'
import './actual-attendance.css'

type Day = { date: string; punches: (string | null)[]; workdays: string | null; hours: string | null; late: string | null; early: string | null; overtime1: string | null; overtime2: string | null; overtime3: string | null; imported_at?: string }
type Member = { uuid: string; code: string; name: string; team: string; days: Day[]; totals: Omit<Day, 'date' | 'punches'>; incomplete: boolean }
type Source = { month: string; employees: { code: string; name: string; rows: Day[] }[]; row_count: number; errors: string[] }
type Batch = { uuid: string; filename: string; month: string; created_at: string; committed_at: string | null; row_count: number; replaced_count: number; imported_by: string }
type Preview = Batch & { source: Source; mappings: Record<string, string>; employee_options: { uuid: string; code: string; name: string; team: string }[]; existing_days: Record<string, string[]> }
const base = '/api/v1/leave/'
const value = (text: string | null | undefined) => text == null ? '—' : new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 8 }).format(Number(text))
const when = (text: string) => new Date(text).toLocaleString('vi-VN')

export function ActualAttendance({ session }: { session: Session }) {
  const canImport = session.capabilities?.includes('leave_domain.import_attendance')
  const now = new Date()
  const [month, setMonth] = useState(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)
  const [members, setMembers] = useState<Member[]>([])
  const [search, setSearch] = useState('')
  const [team, setTeam] = useState('')
  const [preview, setPreview] = useState<Preview | null>(null)
  const [mapping, setMapping] = useState<Record<string, string>>({})
  const [replace, setReplace] = useState(false)
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [history, setHistory] = useState<Batch[]>([])
  const [selected, setSelected] = useState<{ member: string; day: Day } | null>(null)
  const [refresh, setRefresh] = useState(0)
  const detail = useRef<HTMLDivElement>(null)
  const dayTrigger = useRef<HTMLButtonElement | null>(null)
  function changeMonth(next: string) {
    setLoading(true); setError(''); setSelected(null); setTeam(''); setMonth(next)
  }
  useEffect(() => {
    let active = true
    request<{ employees: Member[] }>(`${base}actual-attendance/?month=${encodeURIComponent(month)}`)
      .then(data => { if (active) setMembers(data.employees) })
      .catch(reason => { if (active) { setMembers([]); setError(String(reason.message)) } })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [month, refresh])
  useEffect(() => {
    if (!canImport) return
    let active = true
    request<Batch[]>(`${base}attendance-imports/`).then(data => { if (active) setHistory(data) }).catch(reason => { if (active) setError(reason.message) })
    return () => { active = false }
  }, [canImport, refresh])
  useEffect(() => { if (selected) detail.current?.focus() }, [selected])

  async function upload(file?: File) {
    if (!file) return
    setBusy(true); setError(''); setNotice(''); setPreview(null)
    try {
      const form = new FormData(); form.append('file', file)
      const result = await request<Preview>(`${base}attendance-imports/preview/`, { method: 'POST', body: form })
      setPreview(result); setMapping(result.mappings); setReplace(false)
      if (month !== result.month) changeMonth(result.month)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không đọc được file.') }
    finally { setBusy(false) }
  }
  const conflicts = preview?.source.employees.reduce((sum, e) => sum + e.rows.filter(d => preview.existing_days[mapping[e.code]]?.includes(d.date)).length, 0) ?? 0
  const complete = preview && preview.source.employees.every(e => mapping[e.code]) && new Set(Object.values(mapping).filter(Boolean)).size === preview.source.employees.length
  async function commit() {
    if (!preview) return
    setBusy(true); setError('')
    try {
      const result = await request<Batch>(`${base}attendance-imports/${preview.uuid}/commit/`, { method: 'POST', body: JSON.stringify({ mappings: mapping, replace_existing: replace }) })
      changeMonth(result.month); setPreview(null); setRefresh(n => n + 1)
      setNotice(`Đã nhập ${result.row_count} dòng chấm công tháng ${result.month}${result.replaced_count ? `, thay thế ${result.replaced_count} dòng cũ` : ''}.`)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không nhập được bảng công.') }
    finally { setBusy(false) }
  }
  const days = Array.from({ length: new Date(Number(month.slice(0, 4)), Number(month.slice(5, 7)), 0).getDate() }, (_, i) => `${month}-${String(i + 1).padStart(2, '0')}`)
  const visible = members.filter(m => (!team || m.team === team) && `${m.code} ${m.name}`.toLocaleLowerCase('vi-VN').includes(search.toLocaleLowerCase('vi-VN')))
  return <section className="actual-attendance" aria-label="Chấm công từ file HR">
    <div className="actual-heading"><div><h2>Chấm công</h2><p>Theo file HR · Chọn ngày để xem giờ vào, ra và chi tiết công.</p></div><label>Tháng chấm công<input type="month" value={month} disabled={busy || Boolean(preview)} onChange={e => { if (e.target.value && e.target.value !== month) changeMonth(e.target.value) }} /></label></div>
    {notice && <div className="alert" role="status">{notice}</div>}
    {error && <div className="alert alert--error" role="alert">{error}</div>}
    {canImport && <div className="actual-import">
      <div><strong>Nhập bảng chấm công</strong><p>File .xlsx xuất từ HR, sheet Chi Tiet. Tối đa 10 MB.</p></div>
      <label className="actual-upload">{busy ? 'Đang xử lý…' : 'Chọn file Excel'}<input aria-label="Chọn file Excel" type="file" accept=".xlsx" disabled={busy} onChange={e => { void upload(e.target.files?.[0]); e.target.value = '' }} /></label>
    </div>}
    {preview && <section className="actual-preview" aria-label="Xem trước nhập công">
      <h3>Xem trước tháng {preview.month}</h3><p>{preview.filename} · {preview.source.employees.length} nhân sự · {preview.row_count} dòng. Chưa ghi vào bảng công.</p>
      <p>Ghép mã chấm công với nhân sự MRERP. Liên kết đã lưu sẽ được dùng lại ở lần nhập sau.</p>
      {preview.source.errors.length > 0 && <div className="alert alert--error" role="alert"><strong>File còn lỗi, chưa thể nhập</strong><ul>{preview.source.errors.map((e, i) => <li key={i}>{e}</li>)}</ul></div>}
      <div className="actual-mapping">{preview.source.employees.map(e => <div className="actual-mapping-row" key={e.code}>
        <div><strong>{e.name}</strong><small>Mã chấm công {e.code} · {e.rows.length} ngày</small></div>
        <label>Nhân sự MRERP<select aria-label={`Ghép mã ${e.code}`} disabled={busy || Boolean(preview.mappings[e.code])} value={mapping[e.code] ?? ''} onChange={event => { setMapping({ ...mapping, [e.code]: event.target.value }); setReplace(false) }}>
          <option value="">Chọn nhân sự…</option>{preview.employee_options.map(o => <option key={o.uuid} value={o.uuid} disabled={Object.entries(mapping).some(([code, id]) => code !== e.code && id === o.uuid)}>{o.code} · {o.name} · {o.team}</option>)}
        </select></label>
        <details><summary>Xem dữ liệu nguồn</summary><div className="actual-source-scroll"><table><thead><tr><th>Ngày</th><th>Vào / Ra</th><th>Công</th><th>Giờ</th><th>Trễ / Sớm</th></tr></thead><tbody>{e.rows.map(d => <tr key={d.date}><td>{d.date}</td><td>{d.punches.map(p => p ?? '—').join(' / ')}</td><td>{value(d.workdays)}</td><td>{value(d.hours)}</td><td>{value(d.late)} / {value(d.early)}</td></tr>)}</tbody></table></div></details>
      </div>)}</div>
      {conflicts > 0 && <label className="actual-replace"><input type="checkbox" checked={replace} disabled={busy} onChange={e => setReplace(e.target.checked)} />Tôi xác nhận thay thế {conflicts} ngày đã có bằng dữ liệu trong file này. Lịch sử nhập cũ được giữ lại.</label>}
      <div className="actual-actions"><button className="secondary-button" disabled={busy} onClick={() => setPreview(null)}>Hủy nhập</button><button className="primary-button" disabled={busy || !complete || preview.source.errors.length > 0 || (conflicts > 0 && !replace)} onClick={() => void commit()}>{busy ? 'Đang nhập…' : 'Xác nhận nhập công'}</button></div>
    </section>}
    <div className="actual-filters"><label>Tìm nhân sự<input placeholder="Tên hoặc mã nhân sự" value={search} onChange={e => setSearch(e.target.value)} /></label><label>Team<select value={team} onChange={e => setTeam(e.target.value)}><option value="">Tất cả Team được xem</option>{[...new Set(members.map(m => m.team))].map(t => <option key={t}>{t}</option>)}</select></label><span>{visible.length} nhân sự · Đơn vị: ngày công</span></div>
    {loading ? <p role="status">Đang tải bảng công…</p> : !members.length ? <div className="actual-empty"><h3>Chưa có dữ liệu tháng này</h3><p>{canImport ? 'Chọn file Excel để xem trước và nhập bảng công.' : 'HR chưa nhập công cho bạn hoặc Team trong tháng đã chọn.'}</p></div> : !visible.length ? <p>Không có nhân sự khớp bộ lọc.</p> : <div className="actual-grid" tabIndex={0} aria-label="Bảng công theo ngày, cuộn ngang để xem cả tháng"><table><thead><tr><th scope="col">Nhân sự</th><th scope="col">Tổng công</th>{days.map((d, i) => <th scope="col" key={d}>{i + 1}<small>{new Intl.DateTimeFormat('vi-VN', { weekday: 'short' }).format(new Date(`${d}T00:00:00`))}</small></th>)}</tr></thead><tbody>{visible.map(m => <tr key={m.uuid}><th scope="row"><strong>{m.name}</strong><small>{m.code} · {m.team}</small></th><td className="actual-total">{value(m.totals.workdays)}{m.incomplete && <small>Thiếu dữ liệu</small>}</td>{days.map(d => { const day = m.days.find(v => v.date === d); return <td key={d}>{day ? <button className={selected?.member === m.name && selected.day.date === d ? 'selected' : ''} aria-label={`${m.name}, ngày ${d}, ${value(day.workdays)} công`} onClick={event => { dayTrigger.current = event.currentTarget; setSelected({ member: m.name, day }) }}>{value(day.workdays)}{(Number(day.late) > 0 || Number(day.early) > 0) && <span className="actual-flag" aria-label="Có trễ hoặc sớm" />}</button> : <span title="Chưa nhập ngày này">—</span>}</td> })}</tr>)}</tbody></table></div>}
    <p className="actual-note">— là chưa có dữ liệu; 0 là giá trị có trong file. Chấm nhỏ đánh dấu trễ hoặc về sớm. Kết quả giữ nguyên từ HR, chưa phải công đã duyệt hay bảng lương.</p>
    {selected && <div className="actual-detail" ref={detail} tabIndex={-1}>
      <div className="actual-heading"><h3>{selected.member} · {selected.day.date.split('-').reverse().join('/')}</h3><button className="secondary-button" onClick={() => { setSelected(null); dayTrigger.current?.focus() }}>Đóng chi tiết</button></div>
      <dl><div><dt>Công</dt><dd>{value(selected.day.workdays)}</dd></div><div><dt>Tổng giờ</dt><dd>{value(selected.day.hours)}</dd></div><div><dt>Trễ / sớm (phút)</dt><dd>{value(selected.day.late)} / {value(selected.day.early)}</dd></div><div><dt>Tăng ca 1 / 2 / 3</dt><dd>{value(selected.day.overtime1)} / {value(selected.day.overtime2)} / {value(selected.day.overtime3)}</dd></div></dl>
      <div className="actual-punches">{[0, 1, 2].map(i => <p key={i}>Cặp {i + 1}: <strong>{selected.day.punches[i * 2] ?? '—'} → {selected.day.punches[i * 2 + 1] ?? '—'}</strong></p>)}</div>
      {selected.day.imported_at && <small>Nhập lúc {when(selected.day.imported_at)}</small>}
    </div>}
    {canImport && <details className="actual-history"><summary>Lịch sử nhập ({history.length} đợt gần nhất)</summary>{history.length ? history.map(h => <div key={h.uuid}><strong>{h.filename}</strong><span>Tháng {h.month} · {h.row_count} dòng · thay thế {h.replaced_count}</span><small>{h.imported_by} · {when(h.committed_at!)}</small></div>) : <p>Chưa có lần nhập nào được xác nhận.</p>}</details>}
  </section>
}
