import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { Employee, Goal, Recurrence, Session, Team, WorkTask } from '../types'

function localInputDate(value: Date) {
  const offset = value.getTimezoneOffset() * 60000
  return new Date(value.getTime() - offset).toISOString().slice(0, 16)
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

function GoalCard({ goal }: { goal: Goal }) {
  return <article className="goal-card"><div><span className="goal-card__scope">{goal.scope === 'company' ? 'Công ty' : goal.team_name}</span><span>{goal.period === 'quarter' ? 'Quý' : goal.period === 'month' ? 'Tháng' : goal.period === 'week' ? 'Tuần' : 'Ngày'}</span></div><h3>{goal.title}</h3><p>{goal.description || 'Chưa có mô tả.'}</p><div className="goal-progress"><span><b>{goal.progress}%</b><small>{goal.task_count} Task liên kết</small></span><div><i style={{ width: `${goal.progress}%` }}/></div></div></article>
}

function TaskCard({ task, session, onRefresh }: { task: WorkTask; session: Session; onRefresh: () => Promise<void> }) {
  const [progress, setProgress] = useState(task.progress)
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [renderedAt] = useState(() => Date.now())
  async function run(action: () => Promise<unknown>) {
    setBusy(true); setError('')
    try { await action(); await onRefresh() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thực hiện được thao tác.') }
    finally { setBusy(false) }
  }
  async function upload(files: FileList | null, kind: 'brief' | 'evidence') {
    if (!files?.length) return
    await run(() => api.uploadTaskAttachments(task.uuid, kind, Array.from(files).slice(0, 5)))
  }
  const overdue = new Date(task.due_at).getTime() < renderedAt && task.status !== 'completed'
  const canAddBrief = task.creator === session.employee_uuid || Boolean(session.capabilities?.includes('task_domain.view_team_tasks') || session.capabilities?.includes('task_domain.view_company_tasks'))
  return <article className={`work-task ${overdue ? 'work-task--overdue' : ''}`}>
    <header><div><span className={`task-status task-status--${task.status}`}>{task.status_label}</span>{task.recurrence && <span className="recurring-badge">Lặp</span>}</div><span className={overdue ? 'due-date due-date--overdue' : 'due-date'}><AppIcon name="calendar"/>{formatDateTime(task.due_at)}</span></header>
    <h3>{task.title}</h3>{task.description && <p>{task.description}</p>}
    <div className="task-ownership"><span><small>Người giao</small><strong>{task.creator_name}</strong></span><span><small>Người thực hiện</small><strong>{task.assignee_name}</strong></span><span><small>Team</small><strong>{task.team_name}</strong></span>{task.goal_title && <span><small>Mục tiêu</small><strong>{task.goal_title}</strong></span>}</div>
    <div className="task-progress-control"><div><strong>Tiến độ</strong><output>{progress}%</output></div><input aria-label={`Tiến độ ${task.title}`} type="range" min="0" max="100" value={progress} disabled={!task.can_submit || busy} onChange={(event) => setProgress(Number(event.target.value))}/>{task.can_submit && progress !== task.progress && <button className="text-button" onClick={() => run(() => api.updateTask(task.uuid, { progress }))}>Lưu tiến độ</button>}</div>
    {task.attachments.length > 0 && <div className="task-files">{task.attachments.map((file) => <div className="task-file" key={file.uuid}><a href={file.download_url}><AppIcon name="paperclip"/><span><strong>{file.original_name}</strong><small>{file.kind === 'brief' ? 'Yêu cầu' : 'Kết quả'} · {file.uploaded_by_name}</small></span></a>{file.can_delete && <button aria-label={`Xóa ${file.original_name}`} onClick={() => run(() => api.deleteTaskAttachment(file.uuid))}><AppIcon name="trash" size={14}/></button>}</div>)}</div>}
    <div className="task-command-row">
      {canAddBrief && <label className="file-button file-button--small"><AppIcon name="paperclip"/>Thêm yêu cầu<input type="file" multiple onChange={(event) => void upload(event.target.files, 'brief')}/></label>}{task.can_submit && <><label className="file-button file-button--small"><AppIcon name="paperclip"/>Thêm kết quả<input type="file" multiple onChange={(event) => void upload(event.target.files, 'evidence')}/></label><button className="primary-button compact" disabled={busy} onClick={() => run(() => api.transitionTask(task.uuid, 'submit'))}>Gửi xác nhận</button></>}
      {task.can_review && <><input value={note} onChange={(event) => setNote(event.target.value)} placeholder="Ghi chú khi xác nhận hoặc yêu cầu làm lại"/><button className="secondary-button compact" disabled={busy || !note.trim()} onClick={() => run(() => api.transitionTask(task.uuid, 'rework', note))}>Làm lại</button><button className="primary-button compact" disabled={busy} onClick={() => run(() => api.transitionTask(task.uuid, 'accept', note))}>Xác nhận hoàn thành</button></>}
    </div>
    {task.review_note && <div className="review-note"><strong>Ghi chú xác nhận</strong><span>{task.review_note}</span></div>}
    {error && <div className="alert alert--error">{error}</div>}
  </article>
}

type CreationMode = 'task' | 'goal' | 'recurrence'

function CreationPanel({ mode, session, employees, teams, goals, onClose, onCreated }: { mode: CreationMode; session: Session; employees: Employee[]; teams: Team[]; goals: Goal[]; onClose: () => void; onCreated: () => Promise<void> }) {
  const canAssignTeam = session.capabilities?.includes('task_domain.view_team_tasks') || session.capabilities?.includes('task_domain.view_company_tasks')
  const allowedEmployees = canAssignTeam ? employees : employees.filter((item) => item.uuid === session.employee_uuid)
  const defaultAssignee = allowedEmployees.find((item) => item.uuid !== session.employee_uuid)?.uuid ?? session.employee_uuid ?? ''
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [assignee, setAssignee] = useState(defaultAssignee)
  const [goal, setGoal] = useState('')
  const [dueAt, setDueAt] = useState(() => localInputDate(new Date(Date.now() + 24 * 60 * 60 * 1000)))
  const [scope, setScope] = useState<'team' | 'company'>('team')
  const [team, setTeam] = useState(teams[0]?.uuid ?? '')
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'quarter'>('week')
  const [startsOn, setStartsOn] = useState(() => new Date().toISOString().slice(0, 10))
  const [endsOn, setEndsOn] = useState(() => new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10))
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'monthly'>('weekly')
  const [interval, setInterval] = useState(1)
  const [deadlineOffset, setDeadlineOffset] = useState(1440)
  const [endDate, setEndDate] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    setBusy(true); setError('')
    try {
      if (mode === 'task') await api.createTask({ title, description, assignee_uuid: assignee, due_at: new Date(dueAt).toISOString(), goal_uuid: goal || null })
      if (mode === 'goal') await api.createGoal({ title, description, scope, team_uuid: scope === 'team' ? team : null, period, starts_on: startsOn, ends_on: endsOn })
      if (mode === 'recurrence') await api.createRecurrence({ title, description, assignee_uuid: assignee, goal_uuid: goal || null, frequency, interval, start_at: new Date(dueAt).toISOString(), deadline_offset_minutes: deadlineOffset, end_date: endDate || null })
      await onCreated(); onClose()
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thể tạo dữ liệu.') }
    finally { setBusy(false) }
  }
  const heading = mode === 'task' ? 'Tạo công việc' : mode === 'goal' ? 'Thiết lập mục tiêu' : 'Tạo lịch lặp'
  return <section className="creation-panel"><header><div><h2>{heading}</h2><p>{mode === 'task' ? 'Giao đúng người và gắn với mục tiêu khi cần.' : mode === 'goal' ? 'Đặt timebox rõ để tiến độ được tính từ Task.' : 'Hệ thống tự sinh đủ occurrence, kể cả sau khi worker gián đoạn.'}</p></div><button className="text-button" onClick={onClose}>Đóng</button></header>
    <div className="creation-grid"><label className="span-2">Tiêu đề<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder={mode === 'goal' ? 'Ví dụ: Hoàn tất chiến dịch quý III' : 'Công việc cần hoàn thành'}/></label><label className="span-2">Mô tả<textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Kết quả mong đợi và thông tin cần biết"/></label>
      {mode !== 'goal' && <><label>Người thực hiện<select value={assignee} onChange={(event) => setAssignee(event.target.value)}>{allowedEmployees.map((item) => <option key={item.uuid} value={item.uuid}>{item.display_name || item.employee_code} · {item.team_name ?? 'Chưa vào Team'}</option>)}</select></label><label>{mode === 'task' ? 'Deadline' : 'Kỳ đầu tiên'}<input type="datetime-local" value={dueAt} onChange={(event) => setDueAt(event.target.value)}/></label><label className="span-2">Mục tiêu liên kết<select value={goal} onChange={(event) => setGoal(event.target.value)}><option value="">Không liên kết</option>{goals.map((item) => <option key={item.uuid} value={item.uuid}>{item.title}</option>)}</select></label></>}
      {mode === 'goal' && <><label>Phạm vi<select value={scope} onChange={(event) => setScope(event.target.value as 'team' | 'company')}><option value="team">Team</option>{session.capabilities?.includes('task_domain.manage_company_goals') && <option value="company">Công ty</option>}</select></label>{scope === 'team' && <label>Team<select value={team} onChange={(event) => setTeam(event.target.value)}>{teams.map((item) => <option key={item.uuid} value={item.uuid}>{item.name}</option>)}</select></label>}<label>Chu kỳ<select value={period} onChange={(event) => setPeriod(event.target.value as typeof period)}><option value="day">Ngày</option><option value="week">Tuần</option><option value="month">Tháng</option><option value="quarter">Quý</option></select></label><label>Bắt đầu<input type="date" value={startsOn} onChange={(event) => setStartsOn(event.target.value)}/></label><label>Kết thúc<input type="date" value={endsOn} onChange={(event) => setEndsOn(event.target.value)}/></label></>}
      {mode === 'recurrence' && <><label>Tần suất<select value={frequency} onChange={(event) => setFrequency(event.target.value as typeof frequency)}><option value="daily">Hằng ngày</option><option value="weekly">Hằng tuần</option><option value="monthly">Hằng tháng</option></select></label><label>Lặp mỗi<input type="number" min="1" max="365" value={interval} onChange={(event) => setInterval(Number(event.target.value))}/></label><label>Hạn sau kỳ (phút)<input type="number" min="1" value={deadlineOffset} onChange={(event) => setDeadlineOffset(Number(event.target.value))}/></label><label>Ngày dừng (tùy chọn)<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)}/></label></>}
    </div>{error && <div className="alert alert--error">{error}</div>}<footer><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={busy || !title.trim() || (mode !== 'goal' && !assignee)} onClick={submit}>{busy ? 'Đang lưu…' : heading}</button></footer>
  </section>
}

function RecurrenceCard({ item, onRefresh }: { item: Recurrence; onRefresh: () => Promise<void> }) {
  const [busy, setBusy] = useState(false)
  async function command(value: 'pause' | 'resume' | 'stop') { setBusy(true); try { await api.recurrenceCommand(item.uuid, value); await onRefresh() } finally { setBusy(false) } }
  return <article className="recurrence-row"><span className={`recurrence-state recurrence-state--${item.status}`}>{item.status_label}</span><div><strong>{item.title}</strong><span>{item.assignee_name} · {item.team_name}</span></div><div><strong>{item.frequency_label}, mỗi {item.interval} kỳ</strong><span>Kỳ tiếp: {formatDateTime(item.next_occurrence_at)}</span></div><div>{item.status === 'active' && <button disabled={busy} onClick={() => command('pause')}>Tạm dừng</button>}{item.status === 'paused' && <button disabled={busy} onClick={() => command('resume')}>Tiếp tục</button>}{item.status !== 'stopped' && <button disabled={busy} className="danger-link" onClick={() => command('stop')}>Dừng hẳn</button>}</div></article>
}

export function TaskWorkspace({ session }: { session: Session }) {
  const [tasks, setTasks] = useState<WorkTask[]>([])
  const [goals, setGoals] = useState<Goal[]>([])
  const [recurrences, setRecurrences] = useState<Recurrence[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [view, setView] = useState<'mine' | 'team' | 'goals' | 'recurrences'>('mine')
  const [creating, setCreating] = useState<CreationMode | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canTeam = session.capabilities?.includes('task_domain.view_team_tasks') || session.capabilities?.includes('task_domain.view_company_tasks')
  const canGoals = session.capabilities?.includes('task_domain.manage_goals') || session.capabilities?.includes('task_domain.manage_company_goals')
  const canRecurrence = session.capabilities?.includes('task_domain.manage_recurrences')

  async function load() {
    setError('')
    try {
      const [taskPage, goalPage, recurrencePage, people, teamList] = await Promise.all([api.tasks(), api.goals(), api.recurrences(), api.allEmployees(), api.allTeams()])
      setTasks(taskPage.results); setGoals(goalPage.results); setRecurrences(recurrencePage.results); setEmployees(people); setTeams(teamList)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được Công việc.') }
    finally { setLoading(false) }
  }
  useEffect(() => {
    Promise.all([api.tasks(), api.goals(), api.recurrences(), api.allEmployees(), api.allTeams()]).then(([taskPage, goalPage, recurrencePage, people, teamList]) => { setTasks(taskPage.results); setGoals(goalPage.results); setRecurrences(recurrencePage.results); setEmployees(people); setTeams(teamList) }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được Công việc.')).finally(() => setLoading(false))
  }, [])
  const visibleTasks = useMemo(() => view === 'mine' ? tasks.filter((item) => item.assignee === session.employee_uuid || item.creator === session.employee_uuid) : tasks, [tasks, view, session.employee_uuid])

  if (loading) return <div className="dashboard-skeleton"><span/><span/><span/></div>
  return <div className="task-workspace">
    <section className="work-overview"><div><h2>Mục tiêu và công việc trong một nhịp.</h2><p>Tiến độ mục tiêu được tính trực tiếp từ các Task liên kết — không nhập tay.</p></div><div className="work-overview__actions"><button className="primary-button" onClick={() => setCreating('task')}><AppIcon name="plus"/>Tạo Task</button>{canGoals && <button className="secondary-button" onClick={() => setCreating('goal')}><AppIcon name="goal"/>Mục tiêu</button>}{canRecurrence && <button className="secondary-button" onClick={() => setCreating('recurrence')}><AppIcon name="calendar"/>Lịch lặp</button>}</div></section>
    {creating && <CreationPanel mode={creating} session={session} employees={employees} teams={teams} goals={goals} onClose={() => setCreating(null)} onCreated={load}/>} {error && <div className="alert alert--error">{error}</div>}
    <section className="current-goals"><header><div><h3>Mục tiêu hiện tại</h3><p>Công ty và Team của bạn</p></div><button className="text-button" onClick={() => setView('goals')}>Xem tất cả</button></header>{goals.length ? <div className="goal-row">{goals.slice(0, 3).map((goal) => <GoalCard key={goal.uuid} goal={goal}/>)}</div> : <div className="empty-inline"><strong>Chưa có mục tiêu trong scope</strong><span>Leader hoặc CEO có thể tạo mục tiêu theo ngày, tuần, tháng hoặc quý.</span></div>}</section>
    <div className="work-tabs" role="tablist"><button className={view === 'mine' ? 'active' : ''} onClick={() => setView('mine')}>Việc của tôi <span>{tasks.filter((item) => item.assignee === session.employee_uuid).length}</span></button>{canTeam && <button className={view === 'team' ? 'active' : ''} onClick={() => setView('team')}>Việc Team <span>{tasks.length}</span></button>}<button className={view === 'goals' ? 'active' : ''} onClick={() => setView('goals')}>Mục tiêu</button>{canRecurrence && <button className={view === 'recurrences' ? 'active' : ''} onClick={() => setView('recurrences')}>Lịch lặp</button>}</div>
    {view === 'goals' ? <div className="goal-library">{goals.map((goal) => <GoalCard key={goal.uuid} goal={goal}/>)}</div> : view === 'recurrences' ? <div className="recurrence-list">{recurrences.length ? recurrences.map((item) => <RecurrenceCard key={item.uuid} item={item} onRefresh={load}/>) : <div className="state-panel"><strong>Chưa có lịch lặp</strong><p>Lịch daily, weekly hoặc monthly sẽ xuất hiện tại đây.</p></div>}</div> : <div className="task-list">{visibleTasks.length ? visibleTasks.map((task) => <TaskCard key={task.uuid} task={task} session={session} onRefresh={load}/>) : <div className="state-panel"><strong>Không có công việc trong danh sách này</strong><p>Tạo Task mới hoặc đổi sang một phạm vi khác.</p></div>}</div>}
  </div>
}
