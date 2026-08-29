import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { InternalDocument, Phase3AudienceOptions, Session } from '../types'

function formatBytes(size: number) {
  if (size < 1024 * 1024) return `${Math.ceil(size / 1024)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}
function formatDate(value: string) { return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value)) }

export function DocumentsWorkspace({ session }: { session: Session }) {
  const capabilities = useMemo(() => new Set(session.capabilities ?? []), [session.capabilities])
  const canUpload = capabilities.has('documents_domain.upload_documents')
  const canManageAll = capabilities.has('documents_domain.manage_all_documents')
  const [documents, setDocuments] = useState<InternalDocument[]>([])
  const [audience, setAudience] = useState<Phase3AudienceOptions>({ employees: [], teams: [] })
  const [selected, setSelected] = useState<InternalDocument | null>(null)
  const [showComposer, setShowComposer] = useState(false)
  const [includeArchived, setIncludeArchived] = useState(false)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState<{ title: string; description: string; category: string; scope: InternalDocument['scope']; team_uuids: string[]; employee_uuids: string[]; note: string; files: File[] }>({ title: '', description: '', category: '', scope: 'teams', team_uuids: [], employee_uuids: [], note: '', files: [] })
  const [versionForm, setVersionForm] = useState<{ note: string; files: File[] }>({ note: '', files: [] })
  const inspectorRef = useRef<HTMLElement | null>(null)
  const returnFocusRef = useRef<HTMLElement | null>(null)
  const selectedUuid = selected?.uuid

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [page, options] = await Promise.all([api.documents(includeArchived), canUpload ? api.documentAudience() : Promise.resolve({ employees: [], teams: [] })])
      setDocuments(page.results)
      setAudience(options)
      setSelected((current) => current ? page.results.find((item) => item.uuid === current.uuid) ?? null : null)
      setForm((current) => ({ ...current, team_uuids: current.team_uuids.length ? current.team_uuids : options.teams[0] ? [options.teams[0].uuid] : [] }))
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được thư viện tài liệu.') }
    finally { setLoading(false) }
  }, [canUpload, includeArchived])

  useEffect(() => {
    const timeout = window.setTimeout(() => void load(), 0)
    return () => window.clearTimeout(timeout)
  }, [load])

  useEffect(() => {
    if (selectedUuid) inspectorRef.current?.focus()
  }, [selectedUuid])

  async function create(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const created = await api.createDocument(form)
      setForm({ title: '', description: '', category: '', scope: 'teams', team_uuids: audience.teams[0] ? [audience.teams[0].uuid] : [], employee_uuids: [], note: '', files: [] })
      setShowComposer(false)
      await load()
      setSelected(created)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tạo được tài liệu.') }
    finally { setBusy(false) }
  }

  async function addVersion(event: React.FormEvent) {
    event.preventDefault()
    if (!selected) return
    setBusy(true); setError('')
    try { await api.addDocumentVersion(selected.uuid, versionForm.note, versionForm.files); setVersionForm({ note: '', files: [] }); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thêm được phiên bản.') }
    finally { setBusy(false) }
  }

  async function toggleArchive(document: InternalDocument) {
    setBusy(true); setError('')
    try { if (document.is_archived) await api.restoreDocument(document.uuid); else await api.archiveDocument(document.uuid); await load() }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không thay đổi được trạng thái tài liệu.') }
    finally { setBusy(false) }
  }

  function openDocument(document: InternalDocument) {
    returnFocusRef.current = window.document.activeElement instanceof HTMLElement ? window.document.activeElement : null
    setSelected(document)
    setVersionForm({ note: '', files: [] })
  }

  function closeDocument() {
    setSelected(null)
    setVersionForm({ note: '', files: [] })
    returnFocusRef.current?.focus()
  }

  return <section className="documents-workspace phase3-workspace" aria-busy={loading || busy}>
    <header className="phase3-intro documents-intro">
      <div><h2>Tài liệu đúng người,<br />đúng phiên bản.</h2><p>Mọi file được tải qua server có ACL; link không thay thế quyền truy cập.</p></div>
      <div className="documents-actions">{canUpload && <button className="primary-button" onClick={() => setShowComposer((value) => !value)}><AppIcon name="plus" />{showComposer ? 'Đóng biểu mẫu' : 'Tạo tài liệu'}</button>}<label className="archive-toggle"><input type="checkbox" checked={includeArchived} onChange={(event) => setIncludeArchived(event.target.checked)} />Hiện tài liệu lưu trữ</label></div>
    </header>
    {error && <div className="alert alert--error" role="alert">{error}</div>}
    {showComposer && <form className="document-composer" onSubmit={create}>
      <header><div><h3>Phát hành tài liệu</h3><p>Tối đa 10 file, 25 MB/file. Version đầu được tạo cùng tài liệu.</p></div><AppIcon name="documents" size={24} /></header>
      <div className="document-composer__grid">
        <label>Tiêu đề<input required maxLength={180} value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} /></label>
        <label>Phân loại<input maxLength={80} placeholder="Ví dụ: Hướng dẫn, Chính sách" value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} /></label>
        <label>Phạm vi<select value={form.scope} onChange={(event) => setForm({ ...form, scope: event.target.value as InternalDocument['scope'], team_uuids: [], employee_uuids: [] })}><option value="teams">Team</option><option value="employees">Nhân sự cụ thể</option>{canManageAll && <option value="company">Toàn công ty</option>}{canManageAll && <option value="hr_confidential">HR confidential</option>}</select></label>
        {form.scope === 'teams' && <label>Team<select multiple required value={form.team_uuids} onChange={(event) => setForm({ ...form, team_uuids: Array.from(event.target.selectedOptions, (option) => option.value) })}>{audience.teams.map((team) => <option key={team.uuid} value={team.uuid}>{team.name}</option>)}</select></label>}
        {form.scope === 'employees' && <label>Người nhận<select multiple required value={form.employee_uuids} onChange={(event) => setForm({ ...form, employee_uuids: Array.from(event.target.selectedOptions, (option) => option.value) })}>{audience.employees.map((employee) => <option key={employee.uuid} value={employee.uuid}>{employee.display_name || employee.employee_code} · {employee.team_name ?? 'Chưa có Team'}</option>)}</select></label>}
        <label className="span-two">Mô tả<textarea maxLength={5000} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
        <label>Ghi chú version<input maxLength={500} placeholder="Bản phát hành đầu tiên" value={form.note} onChange={(event) => setForm({ ...form, note: event.target.value })} /></label>
        <label>File<input required type="file" multiple onChange={(event) => setForm({ ...form, files: Array.from(event.target.files ?? []) })} /><small>{form.files.length ? `${form.files.length} file đã chọn` : 'Chưa chọn file'}</small></label>
      </div>
      <button className="primary-button" disabled={busy || form.files.length === 0}>Phát hành version 1</button>
    </form>}
    {loading ? <div className="phase3-loading" role="status"><span className="visually-hidden">Đang tải Tài liệu…</span><span /><span /><span /></div> : <div className={`document-library ${selected ? 'has-detail' : ''}`}>
      <section className="document-ledger">
        <header className="document-ledger__head"><span>Tài liệu</span><span>Phạm vi</span><span>Version</span><span>Cập nhật</span></header>
        {documents.length === 0 ? <div className="empty-state"><strong>Chưa có tài liệu trong scope</strong><p>Tài liệu được chia sẻ cho bạn sẽ xuất hiện tại đây.</p></div> : documents.map((document) => <button key={document.uuid} className={`document-row ${selected?.uuid === document.uuid ? 'selected' : ''} ${document.is_archived ? 'archived' : ''}`} aria-expanded={selected?.uuid === document.uuid} aria-controls="document-inspector" onClick={() => openDocument(document)}>
          <span><i className="document-file-mark"><AppIcon name="documents" /></i><span><strong>{document.title}</strong><small>{document.category || 'Chưa phân loại'} · {document.owner_name}</small></span></span>
          <span>{document.scope_label}</span><span>v{document.versions[0]?.number ?? 0}</span><time>{formatDate(document.updated_at)}</time>
        </button>)}
      </section>
      {selected && <aside className="document-detail" id="document-inspector" ref={inspectorRef} role="dialog" aria-modal="false" aria-label={`Chi tiết tài liệu ${selected.title}`} tabIndex={-1} onKeyDown={(event) => { if (event.key === 'Escape') closeDocument() }}>
        <button className="inspector-close" aria-label="Đóng chi tiết tài liệu" onClick={closeDocument}><AppIcon name="close" /></button>
        <header><span className="document-detail__mark"><AppIcon name="documents" size={28} /></span><div><h3>{selected.title}</h3><p>{selected.scope_label} · {selected.owner_name}</p></div></header>
        {selected.description && <p className="document-description">{selected.description}</p>}
        <div className="document-audience"><strong>Ai đang được xem?</strong><p>{selected.scope === 'company' ? 'Toàn công ty' : selected.scope === 'hr_confidential' ? 'HR confidential' : [...selected.audience_team_names, ...selected.audience_employee_names].join(' · ')}</p></div>
        <section className="version-timeline"><h4>Lịch sử phiên bản</h4>{selected.versions.map((version) => <article key={version.uuid}><header><strong>Version {version.number}</strong><span>{formatDate(version.created_at)} · {version.uploaded_by_name}</span></header>{version.note && <p>{version.note}</p>}<div>{version.files.map((file) => <a key={file.uuid} href={file.download_url}><AppIcon name="paperclip" /><span>{file.original_name}<small>{formatBytes(file.size)}</small></span></a>)}</div></article>)}</section>
        {selected.can_manage && !selected.is_archived && <form className="new-version-form" onSubmit={addVersion}><h4>Thêm version mới</h4><input maxLength={500} placeholder="Ghi chú thay đổi" value={versionForm.note} onChange={(event) => setVersionForm({ ...versionForm, note: event.target.value })} /><input required type="file" multiple onChange={(event) => setVersionForm({ ...versionForm, files: Array.from(event.target.files ?? []) })} /><button className="secondary-button" disabled={busy || versionForm.files.length === 0}>Tải version mới</button></form>}
        {selected.can_manage && <button className={selected.is_archived ? 'primary-button document-archive-action' : 'secondary-button document-archive-action'} disabled={busy} onClick={() => void toggleArchive(selected)}>{selected.is_archived ? 'Khôi phục tài liệu' : 'Lưu trữ 30 ngày'}</button>}
      </aside>}
    </div>}
  </section>
}
