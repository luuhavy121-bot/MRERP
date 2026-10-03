import { useCallback, useEffect, useRef, useState } from "react";
import { request } from "../api";
import type { Page, Session } from "../types";
import "../hr-expansion.css";
import "./performance-drawer.css";
import { EmployeeRecognition } from "./EmployeeRecognition";
import { AppIcon } from "../components/AppIcon";

type KPI = {
  title: string;
  description: string;
  weight: string;
  completion: string | null;
  comment: string;
};
type Review = {
  uuid: string;
  employee: string;
  employee_name: string;
  employee_code: string;
  team_name: string;
  leader_name: string;
  month: string;
  status: string;
  status_label: string;
  total_score: string | null;
  leader_comment: string;
  employee_feedback: string;
  version: number;
  kpis: KPI[];
  can_edit: boolean;
  can_reopen: boolean;
  can_acknowledge: boolean;
  revisions: Array<{
    uuid: string;
    event: string;
    reason: string;
    snapshot: {
      total_score: string | null;
      leader_comment: string;
      employee_feedback: string;
      kpis: KPI[];
    };
    created_at: string;
  }>;
};
type Member = {
  uuid: string;
  display_name: string;
  employee_code: string;
  team_name: string;
};
type ContextTask = {
  uuid: string;
  title: string;
  due_at: string;
  progress: number;
  status: string;
};
const blankKPI = (): KPI => ({
  title: "",
  description: "",
  weight: "100",
  completion: null,
  comment: "",
});
export function PerformanceWorkspace({ session }: { session: Session }) {
  const [month, setMonth] = useState(
    new Date().toLocaleDateString("sv-SE").slice(0, 7),
  );
  const [reviews, setReviews] = useState<Review[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [expanded, setExpanded] = useState<number[]>([0]);
  const [search, setSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("");
  const [selected, setSelected] = useState<Review | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [comment, setComment] = useState("");
  const [feedback, setFeedback] = useState("");
  const [reason, setReason] = useState("");
  const [history, setHistory] = useState<Review[]>([]);
  const [notice, setNotice] = useState("");
  const [tasks, setTasks] = useState<ContextTask[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const canManage = session.capabilities?.includes(
    "performance_domain.manage_team_reviews",
  );
  const company = session.capabilities?.includes(
    "performance_domain.view_company_reviews",
  );
  const directoryElement = useRef<HTMLDivElement | null>(null);
  const closeButton = useRef<HTMLButtonElement | null>(null);
  useEffect(() => { if (selected) closeButton.current?.focus(); }, [selected?.employee]);
  const loadSequence = useRef(0);
  const load = useCallback(async () => {
    const sequence = ++loadSequence.current;
    setLoading(true);
    try {
      let url: string | null = `/api/v1/performance/reviews/?month=${month}`;
      const rows: Review[] = [];
      while (url) {
        const u: URL = new URL(url, location.origin);
        const p: Page<Review> = await request<Page<Review>>(
          u.pathname + u.search,
        );
        rows.push(...p.results);
        url = p.next;
      }
      const options = await request<Member[]>(company && !canManage ? "/api/v1/rewards/audience-options/" : "/api/v1/performance/options/");
      if (sequence !== loadSequence.current) return;
      setReviews(rows);
      setMembers(options);

    } catch (e) {
      if (sequence === loadSequence.current) setError(e instanceof Error ? e.message : "Không tải được đánh giá.");
    } finally {
      if (sequence === loadSequence.current) setLoading(false);
    }
  }, [month, company, canManage]);
  useEffect(() => {
    setSelected(null);
    setReviews([]);
    setMembers([]);
    void load();
    return () => { loadSequence.current += 1; };
  }, [load]);
  function choose(r: Review) {
    setExpanded([0]);
    setSelected(r);
    setKpis(r.kpis);
    setComment(r.leader_comment);
    setFeedback(r.employee_feedback);
    setReason("");
    setTasks([]);
    setError("");
    setNotice("");
  }
  const dirty = !!selected && ((selected.can_edit && (comment !== selected.leader_comment || JSON.stringify(kpis) !== JSON.stringify(selected.kpis))) || feedback !== selected.employee_feedback || !!reason.trim());
  function mayLeaveDraft() {
    return !dirty || window.confirm("Bạn có thay đổi chưa lưu. Bỏ thay đổi và chuyển sang lựa chọn khác?");
  }
  useEffect(() => {
    if (!dirty) return;
    const preventLoss = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", preventLoss);
    return () => window.removeEventListener("beforeunload", preventLoss);
  }, [dirty]);
  function chooseMember(member: Member) {
    if (selected?.employee === member.uuid || !mayLeaveDraft()) return;
    const existing = reviews.find(r => r.employee === member.uuid);
    if (existing) { choose(existing); return; }
    choose({ uuid: "", employee: member.uuid, employee_name: member.display_name,
      employee_code: member.employee_code, team_name: member.team_name,
      leader_name: session.display_name ?? "", month, status: "draft", status_label: "Chưa lưu",
      total_score: null, leader_comment: "", employee_feedback: "", version: 1,
      kpis: canManage ? [blankKPI()] : [], can_edit: !!canManage, can_reopen: false, can_acknowledge: false, revisions: [] });
  }
  useEffect(() => {
    let live = true;
    if (selected?.can_edit) {
      request<ContextTask[]>(
        `/api/v1/performance/context/?employee_uuid=${selected.employee}&month=${selected.month}`,
      )
        .then((rows) => {
          if (live) setTasks(rows);
        })
        .catch(() => {
          if (live)
            setError(
              "Không tải được Task tham khảo; dữ liệu KPI vẫn sử dụng được.",
            );
        });
    }
    return () => {
      live = false;
    };
  }, [selected?.uuid, selected?.employee, selected?.month, selected?.can_edit]);
  useEffect(()=>{
    let live=true;
    setHistory([]);
    if(selected?.uuid) (async()=>{
      let url:string|null=`/api/v1/performance/reviews/?employee_uuid=${selected.employee}`;
      const rows:Review[]=[];
      while(url){const u:URL=new URL(url,location.origin);const page:Page<Review>=await request<Page<Review>>(u.pathname+u.search);rows.push(...page.results);url=page.next}
      if(live)setHistory(rows);
    })().catch(()=>{if(live)setError('Không tải được lịch sử các tháng.')});
    return()=>{live=false};
  },[selected?.employee,selected?.uuid,selected?.version]);
  async function copyPrevious() {
    if(!selected || !selected.can_edit || !mayLeaveDraft())return;
    setBusy(true);setError('');
    try {
      const source=await request<{month:string;kpis:KPI[]}>(`/api/v1/performance/reviews/kpi-source/?employee_uuid=${selected.employee}&month=${month}`);
      if(!source.kpis.length){setNotice(`Tháng ${source.month} chưa có KPI để sao chép.`);return}
      setKpis(source.kpis);setComment('');setExpanded([0]);setNotice(`Đã sao chép cấu trúc KPI tháng ${source.month}. Nhập mức hoàn thành mới rồi lưu.`);
    }catch(e){setError(e instanceof Error?e.message:'Không sao chép được KPI.')}finally{setBusy(false)}
  }
  async function run(action: () => Promise<Review>) {
    setBusy(true);
    setError("");
    try {
      const r = await action();
      await load();
      choose(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Không lưu được phiếu.");
    } finally {
      setBusy(false);
    }
  }
  async function save(finalize = false) {
    if (!selected) return;
    await run(async () => {
      let current = selected;
      if (!current.uuid) {
        current = await request<Review>("/api/v1/performance/reviews/", {
          method: "POST", body: JSON.stringify({ employee_uuid: selected.employee, month }),
        });
        setSelected(current);
      }
      let r = await request<Review>(
        `/api/v1/performance/reviews/${current.uuid}/`,
        {
          method: "PATCH",
          body: JSON.stringify({
            version: current.version,
            leader_comment: comment,
            kpis,
          }),
        },
      );
      choose(r);
      if (finalize)
        r = await request<Review>(
          `/api/v1/performance/reviews/${r.uuid}/finalize/`,
          { method: "POST", body: JSON.stringify({ version: r.version }) },
        );
      return r;
    });
  }
  function command(name: "acknowledge" | "reopen") {
    if (!selected) return;
    void run(() =>
      request<Review>(`/api/v1/performance/reviews/${selected.uuid}/${name}/`, {
        method: "POST",
        body: JSON.stringify({
          version: selected.version,
          employee_feedback: feedback,
          reason,
        }),
      }),
    );
  }
  const weight = kpis.reduce((sum, k) => sum + Number(k.weight || 0), 0);
  const complete = kpis.length > 0 && kpis.every(k => k.completion !== null && k.completion !== '' && Number.isFinite(Number(k.completion)) && Number(k.completion) >= 0 && Number(k.completion) <= 100 && k.weight.trim() !== '' && Number.isFinite(Number(k.weight)) && Number(k.weight) >= 0 && Number(k.weight) <= 100);
  const score = complete ? kpis.reduce((sum, k) => sum + Number(k.weight) * Number(k.completion) / 100, 0).toFixed(2) : '—';
  const directory = canManage || company ? [...members.map(m => ({ member: m, review: reviews.find(r => r.employee === m.uuid) })), ...reviews.filter(r => !members.some(m => m.uuid === r.employee)).map(r => ({ member: { uuid: r.employee, display_name: r.employee_name, employee_code: r.employee_code, team_name: r.team_name }, review: r }))] : reviews.map(r => ({ member: { uuid: r.employee, display_name: r.employee_name, employee_code: r.employee_code, team_name: r.team_name }, review: r }));
  const visible = directory.filter(({member:m,review:r}) => (!teamFilter || m.team_name === teamFilter) && (!statusFilter || (r?.status ?? 'none') === statusFilter) && `${m.display_name} ${m.employee_code}`.toLocaleLowerCase('vi').includes(search.toLocaleLowerCase('vi')));
  function updateKPI(i: number, field: keyof KPI, value: string | null) { setKpis(rows => rows.map((row, index) => index === i ? {...row, [field]:value} : row)); }
  function closePanel() { if (!busy && mayLeaveDraft()) { setSelected(null); requestAnimationFrame(() => { const button = Array.from(directoryElement.current?.querySelectorAll<HTMLButtonElement>('button[data-employee]') ?? []).find(node => node.dataset.employee === selected?.employee); (button ?? directoryElement.current)?.focus(); }); } }
  return <section className={`performance-desk ${selected ? 'has-review' : ''}`} aria-busy={busy || loading}>
    <div ref={directoryElement} tabIndex={-1} className="performance-directory">
      <header><h2>{canManage ? 'Đánh giá nhân sự' : company ? 'Kết quả đánh giá toàn công ty' : 'Đánh giá của tôi'}</h2><p>{canManage ? 'Đánh giá hiệu suất nhân sự trong team của bạn.' : company ? 'Theo dõi kết quả và mở lại phiếu khi cần điều chỉnh.' : 'Xem kết quả, phản hồi và xác nhận đánh giá của bạn.'}</p></header>
      <div className="performance-filters">
        <label>Tìm nhân sự<input type="search" placeholder="Tên hoặc mã nhân sự" value={search} onChange={e=>setSearch(e.target.value)}/></label>
        <label>Team<select value={teamFilter} onChange={e=>setTeamFilter(e.target.value)}><option value="">Tất cả Team</option>{[...new Set(directory.map(({member})=>member.team_name))].map(t=><option key={t}>{t}</option>)}</select></label>
        <label>Tháng đánh giá<input type="month" value={month} disabled={busy} onChange={e=>{if(e.target.value && mayLeaveDraft())setMonth(e.target.value)}}/></label>
        <label>Trạng thái<select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}><option value="">Tất cả trạng thái</option><option value="none">Chưa tạo</option><option value="draft">Bản nháp</option><option value="finalized">Đã chốt</option><option value="acknowledged">Đã xác nhận</option></select></label>
      </div>
      <p className="performance-summary">{directory.length} nhân sự · {reviews.filter(r=>r.status==='finalized'||r.status==='acknowledged').length} đã chốt · {reviews.filter(r=>r.status==='draft').length} bản nháp · {directory.filter(r=>!r.review).length} chưa tạo</p>
      {loading ? <p role="status">Đang tải nhân sự…</p> : <div className="performance-table-wrap"><table className="performance-table"><thead><tr><th>Nhân sự</th><th>Trạng thái</th><th>Điểm</th><th>Thao tác</th></tr></thead><tbody>{visible.map(({member:m,review:r})=><tr key={m.uuid} className={selected?.employee===m.uuid?'is-selected':''}><td><div className="performance-person"><span className="avatar" aria-hidden="true">{m.display_name.split(' ').map(n=>n[0]).slice(-2).join('')}</span><span><strong>{m.display_name||m.employee_code}</strong><small>{m.employee_code} · {m.team_name}</small></span></div></td><td><span className={`performance-status ${r?.status??''}`}>{r ? r.status==='draft'?'Bản nháp':r.status_label : 'Chưa tạo'}</span></td><td>{r?.total_score ?? '—'}</td><td><button data-employee={m.uuid} className="secondary-button" disabled={busy} aria-label={`${r?.can_edit || (!r && canManage) ? 'Đánh giá' : 'Xem'} ${m.display_name}`} onClick={()=>{if(r){if(mayLeaveDraft())choose(r)}else chooseMember(m)}}>{r?.can_edit || (!r && canManage) ? 'Đánh giá' : 'Xem'}</button></td></tr>)}</tbody></table>{!visible.length&&<p className="performance-note">{directory.length?'Không có nhân sự phù hợp bộ lọc.':'Chưa có nhân sự hoặc phiếu đánh giá trong phạm vi của bạn.'}</p>}</div>}
      {!selected && !canManage && !company && session.employee_uuid && session.capabilities?.includes('rewards_domain.view_rewards') && <EmployeeRecognition employee={session.employee_uuid} month={month} canCreate={false}/>}
      {!selected&&error&&<p role="alert" className="alert alert--error">{error}</p>}
    </div>
    {selected && <section className="performance-panel" aria-label="Chi tiết đánh giá" onKeyDown={e=>{if(e.key==='Escape')closePanel()}}>
      <button ref={closeButton} className="performance-close" aria-label="Đóng phiếu đánh giá" disabled={busy} onClick={closePanel}><AppIcon name="close"/></button>
      <header><h3>{selected.employee_name}</h3><span className={`performance-status ${selected.status}`}>{selected.uuid ? selected.status==='draft'?'Bản nháp':selected.status_label : 'Chưa lưu'}</span><p>{selected.employee_code} · {selected.team_name} · Tháng {selected.month.slice(5)}/{selected.month.slice(0,4)}</p></header>
      {error&&<p role="alert" className="alert alert--error">{error}</p>}
      {(selected.uuid || canManage) ? <form onSubmit={e=>{e.preventDefault();void save(false)}}>
        <div><h4>KPI đánh giá</h4>{selected.can_edit&&<button type="button" className="secondary-button" disabled={busy} onClick={()=>void copyPrevious()}>Sao chép KPI tháng trước</button>}{notice&&<p role="status" className="performance-note">{notice}</p>}<div className="performance-kpis"><div className="performance-kpi-head"><span>#</span><span>Tên KPI</span><span>Trọng số %</span><span>Hoàn thành %</span><span>Điểm</span><span/></div>
          {kpis.map((k,i)=><div className="performance-kpi" key={i}><div className="performance-kpi-row"><span className="performance-kpi-number">{i+1}</span><label className="performance-kpi-title"><span>Tên KPI</span><input aria-label={`Tên KPI ${i+1}`} required maxLength={180} disabled={!selected.can_edit||busy} value={k.title} onChange={e=>updateKPI(i,'title',e.target.value)}/></label><label className="performance-kpi-weight"><span>Trọng số %</span><input aria-label={`Trọng số KPI ${i+1}`} type="number" min="0" max="100" step="0.01" required disabled={!selected.can_edit||busy} value={k.weight} onChange={e=>updateKPI(i,'weight',e.target.value)}/></label><label className="performance-kpi-completion"><span>Hoàn thành %</span><input aria-label={`Hoàn thành KPI ${i+1}`} type="number" min="0" max="100" step="0.01" disabled={!selected.can_edit||busy} value={k.completion??''} onChange={e=>updateKPI(i,'completion',e.target.value||null)}/></label><div className="performance-kpi-score"><span>Điểm</span><strong>{k.completion===null||k.completion===''?'—':(Number(k.weight)*Number(k.completion)/100).toFixed(2)}</strong></div><button type="button" aria-label={`Chi tiết KPI ${i+1}`} aria-expanded={expanded.includes(i)} onClick={()=>setExpanded(expanded.includes(i)?expanded.filter(n=>n!==i):[...expanded,i])}>{expanded.includes(i)?'−':'+'}</button></div>{expanded.includes(i)&&<div className="performance-kpi-detail"><label>Mô tả KPI<textarea disabled={!selected.can_edit||busy} value={k.description} onChange={e=>updateKPI(i,'description',e.target.value)}/></label><label>Nhận xét KPI<textarea disabled={!selected.can_edit||busy} value={k.comment} onChange={e=>updateKPI(i,'comment',e.target.value)}/></label>{selected.can_edit&&<button type="button" className="secondary-button" disabled={busy} onClick={()=>{setKpis(kpis.filter((_,n)=>n!==i));setExpanded([0])}}>Xóa KPI {i+1}</button>}</div>}</div>)}
        </div></div>
        {selected.can_edit&&<button type="button" className="secondary-button" disabled={busy} onClick={()=>{setKpis([...kpis,{...blankKPI(),weight:'0'}]);setExpanded([...expanded,kpis.length])}}>Thêm KPI</button>}
        <div className="performance-totals"><span>Tổng trọng số <strong>{weight.toFixed(2)}%</strong></span><span>{selected.status==='draft'?'Điểm tạm tính':'Điểm đã chốt'} <strong>{selected.status==='draft'?score:selected.total_score??'—'} / 100</strong></span></div>
        <label>Nhận xét tổng kết<textarea aria-label="Nhận xét tổng kết" maxLength={5000} disabled={!selected.can_edit||busy} value={comment} onChange={e=>setComment(e.target.value)}/></label>
        {selected.can_edit&&<div className="performance-note" role="status"><strong>Điều kiện chốt</strong><ul>{!kpis.length&&<li>Thêm ít nhất một KPI.</li>}{Math.abs(weight-100)>0.001&&<li>Tổng trọng số hiện {weight.toFixed(2)}%; cần 100%.</li>}{!complete&&<li>Nhập đủ trọng số và mức hoàn thành từ 0–100.</li>}{kpis.some(k=>!k.title.trim())&&<li>Nhập tên cho mọi KPI.</li>}{!comment.trim()&&<li>Nhập nhận xét tổng kết.</li>}</ul>{complete&&Math.abs(weight-100)<=0.001&&comment.trim()&&kpis.every(k=>k.title.trim())&&<p>Đã đủ điều kiện chốt. Nhân sự sẽ thấy kết quả.</p>}</div>}
        {selected.can_edit&&<details><summary>Công việc tham khảo ({tasks.length})</summary><p>Chỉ tham khảo theo hạn hoàn thành, không tự tính điểm KPI.</p>{tasks.map(t=><p key={t.uuid}>{t.title} · {t.progress}% · {new Date(t.due_at).toLocaleDateString('vi-VN')}</p>)}</details>}
        {selected.can_edit&&<div className="performance-save"><button className="secondary-button" disabled={busy}>Lưu nháp đánh giá</button><button type="button" className="primary-button" disabled={busy||!complete||Math.abs(weight-100)>0.001||!comment.trim()||kpis.some(k=>!k.title.trim())} onClick={()=>void save(true)}>Chốt đánh giá</button></div>}
      </form> : <p>Chưa có phiếu KPI trong tháng này. Bạn có thể ghi nhận đóng góp bên dưới.</p>}
      <details><summary>Lịch sử các tháng ({history.length})</summary>{history.map(r=><p key={r.uuid}>Tháng {r.month} · {r.status_label} · Điểm {r.total_score??'—'}</p>)}</details>
      {session.capabilities?.includes('rewards_domain.view_rewards') && <EmployeeRecognition key={selected.employee+selected.month} employee={selected.employee} month={selected.month} canCreate={selected.employee !== session.employee_uuid && !!session.capabilities?.includes('rewards_domain.recognize_scoped')}/>}
            {selected.can_acknowledge ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  command("acknowledge");
                }}
              >
                <label>
                  Phản hồi của tôi
                  <textarea
                    maxLength={5000}
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                  />
                </label>
                <button className="primary-button" disabled={busy}>
                  Xác nhận đã đọc
                </button>
              </form>
            ) : (
              selected.employee_feedback && (
                <p className="preserve-lines">
                  Phản hồi: {selected.employee_feedback}
                </p>
              )
            )}
            {selected.can_reopen && (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  command("reopen");
                }}
              >
                <label>
                  Lý do mở lại
                  <textarea
                    required
                    maxLength={1000}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </label>
                <button
                  className="secondary-button"
                  disabled={busy || !reason.trim()}
                >
                  Mở lại phiếu
                </button>
              </form>
            )}
            {selected.revisions.length > 0 && (
              <details>
                <summary>
                  Lịch sử chốt và mở lại ({selected.revisions.length})
                </summary>
                {selected.revisions.map((rev) => (
                  <article className="review-revision" key={rev.uuid}>
                    <strong>
                      {rev.event === "finalized"
                        ? "Chốt đánh giá"
                        : "Mở lại phiếu"}{" "}
                      · {new Date(rev.created_at).toLocaleString("vi-VN")}
                    </strong>
                    <p>
                      Điểm: {rev.snapshot.total_score} · {rev.reason}
                    </p>
                    <p>{rev.snapshot.leader_comment}</p>
                    {rev.snapshot.employee_feedback && (
                      <p>Phản hồi: {rev.snapshot.employee_feedback}</p>
                    )}
                    {rev.snapshot.kpis.map((k, i) => (
                      <p key={i}>
                        {k.title} · Trọng số {k.weight}% · Hoàn thành{" "}
                        {k.completion}%
                      </p>
                    ))}
                  </article>
                ))}
              </details>
            )}

</section>}
</section>;
}
