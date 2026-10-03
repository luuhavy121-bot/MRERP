import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { HiringEditor } from './HiringEditor'
import { api, request } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { HiringRequest, JobOpening, RecruitmentApplication, Session } from '../types'

type RecruitmentView = 'pipeline' | 'requests' | 'openings'
const stages: Array<{ key: RecruitmentApplication['stage']; label: string }> = [
  { key: 'new', label: 'Mới' }, { key: 'screening', label: 'Sàng lọc' }, { key: 'interview', label: 'Phỏng vấn' },
  { key: 'hired', label: 'Đã tuyển' }, { key: 'rejected', label: 'Từ chối' },
]
const nextStages: Record<RecruitmentApplication['stage'], RecruitmentApplication['stage'][]> = {
  new: ['screening', 'rejected'], screening: ['interview', 'rejected'], interview: ['hired', 'rejected'],
  hired: [], rejected: [],
}

function shortDate(value: string) { return new Intl.DateTimeFormat('vi-VN').format(new Date(value)) }

export function RecruitmentWorkspace({ session }: { session: Session }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session.capabilities])
  const canCreateRequest = capabilities.has('recruitment_domain.create_hiring_request')
  const canApprove = capabilities.has('recruitment_domain.approve_hiring_request')
  const canManage = capabilities.has('recruitment_domain.manage_candidates')
  const [view, setView] = useState<RecruitmentView>('pipeline')
  const [mobileStage, setMobileStage] = useState<RecruitmentApplication['stage']>('new')
  const [requests, setRequests] = useState<HiringRequest[]>([])
  const [openings, setOpenings] = useState<JobOpening[]>([])
  const [applications, setApplications] = useState<RecruitmentApplication[]>([])
  const [teams, setTeams] = useState<Array<{ uuid: string; code: string; name: string }>>([])
  const [selected, setSelected] = useState<RecruitmentApplication | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState<HiringRequest | null | undefined>(undefined)
  const [candidateForm, setCandidateForm] = useState({ opening_uuid: '', full_name: '', email: '', phone: '', source: '' })
  const [search, setSearch] = useState('')
  const [teamFilter, setTeamFilter] = useState('')
  const [stateFilter, setStateFilter] = useState('')
  const [openingFilter, setOpeningFilter] = useState('')
  const [interview, setInterview] = useState({interview_at:'',interviewer_name:'',recruiter_note:''})
  const [stageNote, setStageNote] = useState('')
  const [conversion, setConversion] = useState({ employee_code: '', create_account: false, username: '' })
  const [candidateFiles, setCandidateFiles] = useState<File[]>([])
  const [temporaryCredential, setTemporaryCredential] = useState<{ applicationUuid: string; password: string } | null>(null)
  const inspectorRef = useRef<HTMLElement | null>(null)
  const returnFocusRef = useRef<HTMLElement | null>(null)
  const selectedUuid = selected?.uuid

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [requestPage, openingPage, applicationPage, options] = await Promise.all([
        api.recruitmentRequests(), api.recruitmentOpenings(), api.recruitmentApplications(), canCreateRequest ? api.recruitmentOptions() : Promise.resolve({ teams: [] }),
      ])
      setRequests(requestPage.results)
      setOpenings(openingPage.results)
      setApplications(applicationPage.results)
      setTeams(options.teams)
      setSelected((current) => current ? applicationPage.results.find((item) => item.uuid === current.uuid) ?? null : null)
      setCandidateForm((current) => ({ ...current, opening_uuid: current.opening_uuid || openingPage.results[0]?.uuid || '' }))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được Tuyển dụng.')
    } finally {
      setLoading(false)
    }
  }, [canCreateRequest])

  useEffect(() => {
    const timeout = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timeout)
  }, [load])

  useEffect(() => {
    if (selectedUuid) inspectorRef.current?.focus()
  }, [selectedUuid])

  async function run(action: () => Promise<unknown>, fallback: string) {
    setBusy(true); setError('')
    try { await action(); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : fallback) }
    finally { setBusy(false) }
  }

  async function createCandidate(event: React.FormEvent) {
    event.preventDefault()
    await run(async () => {
      await api.createRecruitmentApplication(candidateForm)
      setCandidateForm({ opening_uuid: openings[0]?.uuid ?? '', full_name: '', email: '', phone: '', source: '' })
    }, 'Không thêm được ứng viên.')
  }

  async function transition(stage: RecruitmentApplication['stage']) {
    if (!selected) return
    if(interviewDirty()){setError('Lưu lịch/ghi chú trước khi chuyển pipeline.');return}
    await run(async () => { await api.transitionRecruitmentApplication(selected.uuid, stage, stageNote); setStageNote('') }, 'Không chuyển được pipeline.')
  }

  async function uploadCandidateFiles() {
    if (!selected || candidateFiles.length === 0) return
    await run(async () => { await api.uploadCandidateAttachments(selected.uuid, candidateFiles); setCandidateFiles([]) }, 'Không tải được file ứng viên.')
  }

  async function convert(event: React.FormEvent) {
    event.preventDefault()
    if (!selected) return
    const applicationUuid = selected.uuid
    await run(async () => {
      const result = await api.convertRecruitmentApplication(applicationUuid, conversion)
      setConversion({ employee_code: '', create_account: false, username: '' })
      setTemporaryCredential(result.temporary_password ? { applicationUuid, password: result.temporary_password } : null)
    }, 'Không chuyển được ứng viên thành nhân sự.')
  }

  function openCandidate(application: RecruitmentApplication) {
    returnFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
    if(selected && interviewDirty() && !window.confirm('Bỏ thay đổi lịch phỏng vấn/ghi chú chưa lưu?'))return;
    setInterview({interview_at:localDateTime(application.interview_at),interviewer_name:application.interviewer_name??'',recruiter_note:application.recruiter_note??''});
    setSelected(application)
    setStageNote('')
    setCandidateFiles([])
    setConversion({ employee_code: '', create_account: false, username: '' })
    setTemporaryCredential(null)
  }

  function interviewDirty() {return !!selected&&(interview.interview_at!==localDateTime(selected.interview_at)||interview.interviewer_name!==(selected.interviewer_name??'')||interview.recruiter_note!==(selected.recruiter_note??''))}
  function localDateTime(value?:string|null) {if(!value)return '';const d=new Date(value);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}T${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`}
  async function saveInterview(e:React.FormEvent) {e.preventDefault();if(!selected)return;await run(async()=>{const updated=await request<RecruitmentApplication>(`/api/v1/recruitment/applications/${selected.uuid}/interview/`,{method:'POST',body:JSON.stringify({...interview,interview_at:interview.interview_at?new Date(interview.interview_at).toISOString():null,version:selected.version})});setSelected(updated)},'Không lưu được lịch phỏng vấn/ghi chú.')}
  function closeCandidate() {
    if(interviewDirty()&&!window.confirm('Bỏ thay đổi lịch phỏng vấn/ghi chú chưa lưu?'))return;

    setSelected(null)
    setStageNote('')
    setCandidateFiles([])
    setConversion({ employee_code: '', create_account: false, username: '' })
    setTemporaryCredential(null)
    returnFocusRef.current?.focus()
  }

  const match=(text:string,team:string,state:string)=>text.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi'))&&(!teamFilter||team===teamFilter)&&(!stateFilter||state===stateFilter);
  const visibleRequests=requests.filter(r=>match(r.title,r.team_name,r.status));
  const visibleOpenings=openings.filter(o=>match(o.title,o.team_name,openingState(o)));
  const visibleApplications=applications.filter(a=>match(`${a.candidate_name} ${a.opening_title} ${a.candidate_email??''} ${a.candidate_phone??''}`,a.team_name,a.stage)&&(!openingFilter||a.opening===openingFilter));
  function openingState(o:JobOpening): 'open'|'closed'|'expired'|'internal' {return o.status==='closed'?'closed':o.hiring_request_deadline&&o.hiring_request_deadline<new Date().toLocaleDateString('sv-SE')?'expired':o.slug?'open':'internal'}
  const pending = requests.filter((item) => item.status === 'pending').length
  const active = applications.filter((item) => !['hired', 'rejected'].includes(item.stage)).length

  return <section className="recruitment-workspace phase3-workspace" aria-busy={loading || busy}>
    <header className="phase3-intro recruitment-intro">
      <div><h2>Một pipeline rõ ràng,<br />từ nhu cầu đến nhân sự.</h2><p>Leader và HR phối hợp tuyển dụng từ tin đăng đến hồ sơ ứng viên.</p></div>
      <div className="phase3-summary"><span><strong>{active}</strong> đang xử lý</span><span><strong>{pending}</strong> chờ duyệt</span><span><strong>{openings.length}</strong> vị trí mở</span></div>
    </header>
    <div className="phase3-tabs" role="tablist" aria-label="Tuyển dụng">
      <button role="tab" aria-selected={view === 'pipeline'} className={view === 'pipeline' ? 'active' : ''} onClick={() => {setView('pipeline');setStateFilter('')}}>Pipeline ứng viên</button>
      <button role="tab" aria-selected={view === 'requests'} className={view === 'requests' ? 'active' : ''} onClick={() => {setView('requests');setStateFilter('')}}>Yêu cầu tuyển <b>{pending}</b></button>
      <button role="tab" aria-selected={view === 'openings'} className={view === 'openings' ? 'active' : ''} onClick={() => {setView('openings');setStateFilter('')}}>Tin đang tuyển</button>
    </div>
    <div className="hr-demo-filters"><label>Tìm kiếm<input type="search" placeholder="Vị trí, ứng viên, email hoặc điện thoại" value={search} onChange={e=>setSearch(e.target.value)}/></label><label>Team<select value={teamFilter} onChange={e=>setTeamFilter(e.target.value)}><option value="">Tất cả Team được xem</option>{[...new Set([...requests.map(r=>r.team_name),...openings.map(o=>o.team_name)])].map(t=><option key={t}>{t}</option>)}</select></label><label>Trạng thái<select value={stateFilter} onChange={e=>setStateFilter(e.target.value)}><option value="">Tất cả trạng thái</option>{(view==='pipeline'?stages:view==='requests'?[{key:'draft',label:'Bản nháp'},{key:'pending',label:'Chờ duyệt'},{key:'approved',label:'Đã duyệt'},{key:'rejected',label:'Từ chối'}]:[{key:'open',label:'Đang mở'},{key:'expired',label:'Hết hạn'},{key:'closed',label:'Đã đóng'},{key:'internal',label:'Nội bộ'}]).map(s=><option key={s.key} value={s.key}>{s.label}</option>)}</select></label>{view==='pipeline'&&<label>Vị trí<select value={openingFilter} onChange={e=>setOpeningFilter(e.target.value)}><option value="">Tất cả vị trí</option>{openings.map(o=><option key={o.uuid} value={o.uuid}>{o.title}</option>)}</select></label>}</div>
    {error && <div className="alert alert--error" role="alert">{error}</div>}
    {loading ? <div className="phase3-loading" role="status"><span className="visually-hidden">Đang tải Tuyển dụng…</span><span /><span /><span /></div> : view === 'requests' ? <div className="recruitment-requests-layout">
      {canCreateRequest && <div>{editing === undefined ? <button className="primary-button" onClick={()=>setEditing(null)}>Tạo yêu cầu tuyển</button> : <HiringEditor key={editing?.uuid ?? 'new'} teams={teams} item={editing} done={load} cancel={()=>setEditing(undefined)}/>}</div>}
      <section className="recruitment-request-ledger">
        <header><h3>Lịch sử yêu cầu</h3><span>{requests.length} yêu cầu</span></header>
        {requests.length === 0 ? <div className="empty-state"><strong>Chưa có yêu cầu tuyển</strong><p>Nhu cầu mới sẽ xuất hiện tại đây.</p></div> : visibleRequests.map((item) => <article key={item.uuid} className="recruitment-request-row">
          <div><span className={`status recruitment-status--${item.status}`}>{item.status_label}</span><strong>{item.title}</strong><small>{item.team_name} · {item.headcount} người · {item.requester_name}</small></div>
          <p>{item.justification}</p>
          {item.utilization_plan && <details><summary>Kế hoạch sử dụng nhân sự</summary><p className="preserve-lines">{item.utilization_plan}</p></details>}
          <details><summary>Nội dung tin tuyển</summary><p>{item.location} · {item.employment_type} · Hạn: {item.deadline || 'Chưa đặt'}</p><h4>Mô tả công việc</h4><p className="preserve-lines">{item.description}</p><h4>Yêu cầu</h4><p className="preserve-lines">{item.requirements}</p><h4>Quyền lợi</h4><p className="preserve-lines">{item.benefits}</p></details>
          {item.status === 'draft' && canCreateRequest && <button className="secondary-button" onClick={()=>setEditing(item)}>Sửa bản nháp</button>}
          <time>{shortDate(item.created_at)}</time>
          {canApprove && item.status === 'pending' && <div className="row-actions"><button className="secondary-button compact" disabled={busy} onClick={() => void run(() => api.reviewRecruitmentRequest(item.uuid, 'rejected'), 'Không từ chối được yêu cầu.')}>Từ chối</button><button className="primary-button compact" disabled={busy} onClick={() => void run(() => api.reviewRecruitmentRequest(item.uuid, 'approved'), 'Không duyệt được yêu cầu.')}>Duyệt</button></div>}
        </article>)}
      </section>
    </div> : view === 'openings' ? <section className="recruitment-request-ledger"><h3>Tin tuyển dụng</h3><a href="/careers" target="_blank" rel="noreferrer">Mở trang tuyển dụng</a>{openings.length === 0 && <p>Chưa có vị trí được duyệt.</p>}{visibleOpenings.map(o=><article className="recruitment-request-row" key={o.uuid}><div><strong>{o.title}</strong><small>{o.team_name} · {{open:'Đang mở',closed:'Đã đóng',expired:'Hết hạn',internal:'Nội bộ'}[openingState(o)]}</small>{o.slug ? <a href={`/careers/${o.slug}`} target="_blank" rel="noreferrer">Xem tin công khai</a> : <span>Tin nội bộ</span>}</div>{o.status === 'open' && canManage && <button className="secondary-button" disabled={busy} onClick={()=>void run(()=>request(`/api/v1/recruitment/openings/${o.uuid}/close/`,{method:'POST'}),'Không đóng được tin.')}>Đóng tin</button>}</article>)}</section> : <>
      {canManage && <form className="candidate-quick-create" onSubmit={createCandidate}>
        <div><strong>Thêm ứng viên</strong><span>Thông tin ứng viên chỉ hiển thị trong phạm vi được cấp quyền.</span></div>
        <label>Vị trí tuyển<select required value={candidateForm.opening_uuid} onChange={(event) => setCandidateForm({ ...candidateForm, opening_uuid: event.target.value })}><option value="">Chọn vị trí</option>{openings.filter(o=>o.status==='open').map((opening) => <option key={opening.uuid} value={opening.uuid}>{opening.title} · {opening.team_name}</option>)}</select></label>
        <label>Họ tên ứng viên<input required placeholder="Nguyễn Văn A" value={candidateForm.full_name} onChange={(event) => setCandidateForm({ ...candidateForm, full_name: event.target.value })} /></label>
        <label>Email ứng viên<input type="email" placeholder="email@congty.vn" value={candidateForm.email} onChange={(event) => setCandidateForm({ ...candidateForm, email: event.target.value })} /></label>
        <label>Số điện thoại ứng viên<input placeholder="Số điện thoại" value={candidateForm.phone} onChange={(event) => setCandidateForm({ ...candidateForm, phone: event.target.value })} /></label>
        <label>Nguồn ứng viên<input placeholder="Nguồn ứng viên" value={candidateForm.source} onChange={(event) => setCandidateForm({ ...candidateForm, source: event.target.value })} /></label>
        <button className="primary-button compact" disabled={busy || openings.length === 0}><AppIcon name="plus" />Thêm</button>
      </form>}
      {!visibleApplications.length&&<p role="status">Không có ứng viên phù hợp bộ lọc.</p>}
      <div className={`recruitment-board-layout ${selected ? 'has-detail' : ''}`}>
        <label className="pipeline-stage-picker">Giai đoạn<select value={mobileStage} onChange={(event) => setMobileStage(event.target.value as RecruitmentApplication['stage'])}>{stages.map((stage) => <option key={stage.key} value={stage.key}>{stage.label} · {applications.filter((item) => item.stage === stage.key).length}</option>)}</select></label>
        <div className="recruitment-board" role="region" tabIndex={0} aria-label="Pipeline ứng viên theo giai đoạn">
          {stages.map((stage) => { const items = visibleApplications.filter((item) => item.stage === stage.key); return <section className={`pipeline-column pipeline-column--${stage.key} ${mobileStage === stage.key ? 'mobile-active' : ''}`} key={stage.key}>
            <header><h3>{stage.label}</h3><span>{items.length}</span></header>
            <div>{items.length === 0 ? <p className="pipeline-empty">Chưa có ứng viên</p> : items.map((item) => <button key={item.uuid} className={`candidate-card ${selected?.uuid === item.uuid ? 'selected' : ''}`} aria-expanded={selected?.uuid === item.uuid} aria-controls="candidate-inspector" onClick={() => openCandidate(item)}>
              <strong>{item.candidate_name}</strong><span>{item.opening_title}</span><small>{item.team_name} · {item.candidate_source || 'Chưa có nguồn'}</small>
            </button>)}</div>
          </section> })}
        </div>
        {selected && <aside className="candidate-inspector" id="candidate-inspector" ref={inspectorRef} role="dialog" aria-modal="false" aria-label={`Chi tiết ứng viên ${selected.candidate_name}`} tabIndex={-1} onKeyDown={(event) => { if (event.key === 'Escape') closeCandidate() }}>
          <button className="inspector-close" aria-label="Đóng chi tiết ứng viên" onClick={closeCandidate}><AppIcon name="close" /></button>
          <header><span className="candidate-monogram">{selected.candidate_name.slice(0, 2).toUpperCase()}</span><div><h3>{selected.candidate_name}</h3><p>{selected.opening_title} · {selected.team_name}</p></div></header>
          {selected.introduction && <p className="preserve-lines">{selected.introduction}</p>}
          <dl><div><dt>Trạng thái</dt><dd>{selected.stage_label}</dd></div><div><dt>Nguồn</dt><dd>{selected.candidate_source || 'Chưa có'}</dd></div>{selected.candidate_email !== undefined && <><div><dt>Email</dt><dd>{selected.candidate_email || 'Chưa có'}</dd></div><div><dt>Điện thoại</dt><dd>{selected.candidate_phone || 'Chưa có'}</dd></div></>}</dl>
          {selected.can_manage && !['hired','rejected'].includes(selected.stage) && <form className="inspector-action" onSubmit={saveInterview}><h4>Lịch phỏng vấn & ghi chú</h4><label>Thời gian phỏng vấn<input type="datetime-local" value={interview.interview_at} onChange={e=>setInterview({...interview,interview_at:e.target.value})}/></label><small>Theo múi giờ thiết bị: {Intl.DateTimeFormat().resolvedOptions().timeZone}</small><label>Người phụ trách (tên)<input maxLength={160} required={!!interview.interview_at} value={interview.interviewer_name} onChange={e=>setInterview({...interview,interviewer_name:e.target.value})}/></label><label>Ghi chú nội bộ<textarea aria-label="Ghi chú nội bộ" maxLength={2000} value={interview.recruiter_note} onChange={e=>setInterview({...interview,recruiter_note:e.target.value})}/></label><button className="secondary-button" disabled={busy}>Lưu lịch & ghi chú</button></form>}
          {selected.can_manage&&['hired','rejected'].includes(selected.stage)&&<section className="inspector-action"><h4>Lịch & ghi chú đã lưu</h4><p>{selected.interview_at?new Date(selected.interview_at).toLocaleString('vi-VN'):'Chưa đặt lịch'} · {selected.interviewer_name}</p><p className="preserve-lines">{selected.recruiter_note}</p></section>}
          {!!selected.transitions.length&&<details><summary>Lịch sử xử lý ({selected.transitions.length})</summary>{selected.transitions.map(t=><p key={t.uuid}>{shortDate(t.created_at)} · {t.to_label}<br/>{t.note}</p>)}</details>}
          {selected.can_manage && nextStages[selected.stage].length > 0 && <section className="inspector-action"><h4>Chuyển pipeline</h4><input aria-label="Ghi chú chuyển pipeline" placeholder="Ghi chú tùy chọn" value={stageNote} onChange={(event) => setStageNote(event.target.value)} /><div>{nextStages[selected.stage].map((stage) => <button key={stage} className={stage === 'rejected' ? 'secondary-button compact' : 'primary-button compact'} disabled={busy} onClick={() => void transition(stage)}>{stages.find((item) => item.key === stage)?.label}</button>)}</div></section>}
          {selected.can_manage && <section className="inspector-action"><h4>CV & hồ sơ</h4><input aria-label="File ứng viên" type="file" accept=".pdf,.doc,.docx" multiple onChange={(event) => setCandidateFiles(Array.from(event.target.files ?? []))} /><button className="secondary-button" disabled={busy || candidateFiles.length === 0} onClick={() => void uploadCandidateFiles()}>Tải {candidateFiles.length || ''} file</button>{selected.attachments?.map((file) => <a key={file.uuid} href={file.download_url}><AppIcon name="paperclip" />{file.original_name}</a>)}</section>}
          {temporaryCredential?.applicationUuid === selected.uuid && <div className="temporary-secret" role="status"><strong>Mật khẩu tạm thời</strong><code>{temporaryCredential.password}</code><p>Chỉ hiển thị trong phiên này. Hãy chuyển qua kênh an toàn.</p><button className="secondary-button compact" onClick={() => setTemporaryCredential(null)}>Đã lưu</button></div>}
          {selected.can_convert && <form className="inspector-action conversion-form" onSubmit={convert}><h4>Chuyển thành Employee</h4><input required placeholder="Mã nhân sự" value={conversion.employee_code} onChange={(event) => setConversion({ ...conversion, employee_code: event.target.value })} /><label className="inline-check"><input type="checkbox" checked={conversion.create_account} onChange={(event) => setConversion({ ...conversion, create_account: event.target.checked })} />Tạo account ngay</label>{conversion.create_account && <input required placeholder="Tài khoản" value={conversion.username} onChange={(event) => setConversion({ ...conversion, username: event.target.value })} />}<button className="primary-button" disabled={busy}>Tạo nhân sự thử việc</button></form>}
          {!selected.can_manage && <p className="field-policy-note"><AppIcon name="lock" />Bạn chưa được cấp quyền xem liên hệ và CV.</p>}
        </aside>}
      </div>
    </>}
  </section>
}
