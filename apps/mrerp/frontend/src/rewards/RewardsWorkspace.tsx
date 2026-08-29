import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { LeaderboardRow, Recognition, RewardAudienceMember, Session, StarBalance } from '../types'

type RewardView = 'recognition' | 'leaderboard' | 'ledger'
type Period = 'month' | 'quarter' | 'year'
function when(value: string) { return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value)) }

export function RewardsWorkspace({ session }: { session: Session }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session.capabilities])
  const canRecognize = capabilities.has('rewards_domain.recognize_scoped')
  const canGrant = capabilities.has('rewards_domain.grant_stars_scoped')
  const [view, setView] = useState<RewardView>('recognition')
  const [period, setPeriod] = useState<Period>('month')
  const [recognitions, setRecognitions] = useState<Recognition[]>([])
  const [audience, setAudience] = useState<RewardAudienceMember[]>([])
  const [balance, setBalance] = useState<StarBalance>({ balance: 0, ledger: [] })
  const [ranking, setRanking] = useState<LeaderboardRow[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [recognitionForm, setRecognitionForm] = useState({ recipient_uuids: [] as string[], category: '', message: '' })
  const [starForm, setStarForm] = useState({ employee_uuid: '', amount: 1, reason: '' })

  const load = useCallback(async (selectedPeriod: Period = period) => {
    setLoading(true); setError('')
    try {
      const [recognitionPage, people, myBalance, leaderboard] = await Promise.all([
        api.recognitions(), api.rewardAudience(), api.myStarBalance(), api.leaderboard(selectedPeriod),
      ])
      setRecognitions(recognitionPage.results); setAudience(people); setBalance(myBalance); setRanking(leaderboard)
      setStarForm((current) => ({ ...current, employee_uuid: current.employee_uuid || people[0]?.uuid || '' }))
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được Ghi nhận & Sao.') }
    finally { setLoading(false) }
  }, [period])

  useEffect(() => {
    const timeout = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timeout)
  }, [load])

  async function createRecognition(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.createRecognition(recognitionForm); setRecognitionForm({ recipient_uuids: [], category: '', message: '' }); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không gửi được lời ghi nhận.') }
    finally { setBusy(false) }
  }

  async function grantStars(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.grantStars(starForm); setStarForm({ employee_uuid: audience[0]?.uuid ?? '', amount: 1, reason: '' }); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không ghi được giao dịch sao.') }
    finally { setBusy(false) }
  }

  async function changePeriod(value: Period) { setPeriod(value); await load(value) }

  return <section className="rewards-workspace phase3-workspace" aria-busy={loading || busy}>
    <header className="rewards-hero">
      <div><span className="star-signal"><AppIcon name="rewards" size={28} /></span><div><h2>Ghi nhận điều tốt.<br />Sao vẫn minh bạch.</h2><p>Recognition và sao là hai hành động độc lập. Mỗi thay đổi số dư đều để lại ledger.</p></div></div>
      <div className="my-star-balance"><span>Số dư của bạn</span><strong>{balance.balance}</strong><small>sao · không hết hạn trong baseline</small></div>
    </header>
    <div className="reward-policy-banner"><AppIcon name="lock" /><div><strong>Đổi thưởng chưa được mở</strong><span>Người duyệt catalog và policy giữ/trừ/hoàn sao vẫn Chưa quyết định.</span></div></div>
    <div className="phase3-tabs" role="tablist" aria-label="Ghi nhận và Sao">
      <button role="tab" aria-selected={view === 'recognition'} className={view === 'recognition' ? 'active' : ''} onClick={() => setView('recognition')}>Ghi nhận</button>
      <button role="tab" aria-selected={view === 'leaderboard'} className={view === 'leaderboard' ? 'active' : ''} onClick={() => setView('leaderboard')}>Bảng xếp hạng</button>
      <button role="tab" aria-selected={view === 'ledger'} className={view === 'ledger' ? 'active' : ''} onClick={() => setView('ledger')}>Ledger của tôi</button>
    </div>
    {error && <div className="alert alert--error" role="alert">{error}</div>}
    {loading ? <div className="phase3-loading" role="status"><span className="visually-hidden">Đang tải Ghi nhận và Sao…</span><span /><span /><span /></div> : view === 'recognition' ? <div className="recognition-layout">
      <div className="recognition-actions">
        {canRecognize && <form className="phase3-form recognition-form" onSubmit={createRecognition}><header><div><h3>Gửi lời ghi nhận</h3><p>Không tự sinh sao.</p></div><AppIcon name="rewards" /></header><label>Người nhận<select multiple required value={recognitionForm.recipient_uuids} onChange={(event) => setRecognitionForm({ ...recognitionForm, recipient_uuids: Array.from(event.target.selectedOptions, (option) => option.value) })}>{audience.map((employee) => <option key={employee.uuid} value={employee.uuid}>{employee.display_name} · {employee.team_name ?? 'Chưa có Team'}</option>)}</select></label><label>Chủ đề<input required maxLength={80} placeholder="Ví dụ: Hợp tác, Chủ động" value={recognitionForm.category} onChange={(event) => setRecognitionForm({ ...recognitionForm, category: event.target.value })} /></label><label>Lời nhắn<textarea required maxLength={3000} value={recognitionForm.message} onChange={(event) => setRecognitionForm({ ...recognitionForm, message: event.target.value })} /></label><button className="primary-button" disabled={busy || recognitionForm.recipient_uuids.length === 0}>Gửi ghi nhận</button></form>}
        {canGrant && <form className="phase3-form star-grant-form" onSubmit={grantStars}><header><div><h3>Ghi giao dịch sao</h3><p>Số âm là điều chỉnh, không xóa lịch sử.</p></div><span className="star-amount-mark">±</span></header><label>Nhân sự<select required value={starForm.employee_uuid} onChange={(event) => setStarForm({ ...starForm, employee_uuid: event.target.value })}>{audience.map((employee) => <option key={employee.uuid} value={employee.uuid}>{employee.display_name} · {employee.team_name ?? 'Chưa có Team'}</option>)}</select></label><label>Số sao<input required type="number" min="-1000000" max="1000000" value={starForm.amount} onChange={(event) => setStarForm({ ...starForm, amount: Number(event.target.value) })} /></label><label>Lý do<input required maxLength={500} value={starForm.reason} onChange={(event) => setStarForm({ ...starForm, reason: event.target.value })} /></label><button className="secondary-button" disabled={busy || !starForm.employee_uuid}>Ghi vào ledger</button></form>}
      </div>
      <section className="recognition-stream"><header><h3>Dòng ghi nhận</h3><span>{recognitions.length} lời ghi nhận</span></header>{recognitions.length === 0 ? <div className="empty-state"><strong>Chưa có lời ghi nhận</strong><p>Những đóng góp được ghi nhận sẽ xuất hiện tại đây.</p></div> : recognitions.map((item) => <article key={item.uuid} className="recognition-entry"><span className="recognition-avatar">{item.sender_name.slice(0, 2).toUpperCase()}</span><div><header><strong>{item.sender_name}</strong><time>{when(item.created_at)}</time></header><p>{item.message}</p><footer><span>{item.category}</span><small>Gửi tới {item.recipient_names.join(', ')}</small></footer></div></article>)}</section>
    </div> : view === 'leaderboard' ? <section className="leaderboard-panel">
      <header><div><h3>Bảng xếp hạng sao</h3><p>Chỉ hiển thị tổng sao trong kỳ, không lộ giao dịch chi tiết.</p></div><div className="period-switcher">{(['month', 'quarter', 'year'] as Period[]).map((item) => <button key={item} className={period === item ? 'active' : ''} onClick={() => void changePeriod(item)}>{item === 'month' ? 'Tháng' : item === 'quarter' ? 'Quý' : 'Năm'}</button>)}</div></header>
      {ranking.length === 0 ? <div className="empty-state"><strong>Chưa có sao trong kỳ</strong><p>Giao dịch được ghi sẽ cập nhật bảng này.</p></div> : <div className="leaderboard-list">{ranking.map((row) => <article key={row.employee_uuid} className={row.employee_uuid === session.employee_uuid ? 'is-me' : ''}><span className="leaderboard-rank">{String(row.rank).padStart(2, '0')}</span><span className="avatar avatar--soft">{row.display_name.slice(0, 2).toUpperCase()}</span><div><strong>{row.display_name}</strong><small>{row.employee_code} · {row.team_name ?? 'Chưa có Team'}</small></div><strong className="leaderboard-stars">{row.stars}<small>sao</small></strong></article>)}</div>}
    </section> : <section className="my-ledger"><header><div><h3>Ledger của tôi</h3><p>Append-only · chỉ tài khoản này xem được chi tiết.</p></div><strong>{balance.balance} sao</strong></header>{balance.ledger.length === 0 ? <div className="empty-state"><strong>Chưa có giao dịch</strong><p>Sao được cấp hoặc điều chỉnh sẽ xuất hiện tại đây.</p></div> : balance.ledger.map((entry) => <article key={entry.uuid}><time>{when(entry.created_at)}</time><div><strong>{entry.reason}</strong><small>{entry.entry_type_label} bởi {entry.actor_name}</small></div><span className={entry.amount > 0 ? 'star-positive' : 'star-negative'}>{entry.amount > 0 ? '+' : ''}{entry.amount}</span></article>)}</section>}
  </section>
}
