import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { FeedAudienceOptions, FeedComment, FeedPost, ReactionKind, Session } from '../types'

const reactions: Array<{ value: ReactionKind; label: string }> = [
  { value: 'like', label: 'Thích' }, { value: 'love', label: 'Yêu thích' }, { value: 'celebrate', label: 'Chúc mừng' }, { value: 'support', label: 'Ủng hộ' }, { value: 'insightful', label: 'Hữu ích' },
]

function formatTime(value: string) {
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

function bytes(value: number) {
  return value < 1024 * 1024 ? `${Math.max(1, Math.round(value / 1024))} KB` : `${(value / 1024 / 1024).toFixed(1)} MB`
}

type AudienceValue = { company: boolean; employees: string[]; teams: string[] }

function AudiencePicker({ options, value, onChange, allowed, compact = false }: { options: FeedAudienceOptions; value: AudienceValue; onChange: (value: AudienceValue) => void; allowed?: { company: boolean; employees: Set<string>; teams: Set<string> }; compact?: boolean }) {
  const teams = allowed ? options.teams.filter((team) => allowed.teams.has(team.uuid)) : options.teams
  const employees = allowed ? options.employees.filter((employee) => allowed.employees.has(employee.uuid)) : options.employees
  function toggle(list: string[], uuid: string) { return list.includes(uuid) ? list.filter((item) => item !== uuid) : [...list, uuid] }
  return <div className={`audience-picker ${compact ? 'audience-picker--compact' : ''}`}>
    <label className={`audience-company ${value.company ? 'selected' : ''}`}><input type="checkbox" checked={value.company} disabled={allowed ? !allowed.company : false} onChange={(event) => onChange({ company: event.target.checked, employees: [], teams: [] })}/><span>Toàn công ty</span></label>
    {!value.company && <div className="audience-options">
      <div><strong>Team</strong><div>{teams.map((team) => <label key={team.uuid} className={value.teams.includes(team.uuid) ? 'selected' : ''}><input type="checkbox" checked={value.teams.includes(team.uuid)} onChange={() => onChange({ ...value, teams: toggle(value.teams, team.uuid) })}/><span>{team.name}</span></label>)}</div></div>
      <div><strong>Một vài người</strong><div className="audience-people">{employees.map((employee) => <label key={employee.uuid} className={value.employees.includes(employee.uuid) ? 'selected' : ''}><input type="checkbox" checked={value.employees.includes(employee.uuid)} onChange={() => onChange({ ...value, employees: toggle(value.employees, employee.uuid) })}/><span>{employee.display_name}<small>{employee.team_name ?? 'Chưa vào Team'}</small></span></label>)}</div></div>
    </div>}
  </div>
}

function CommentThread({ post, comment, onRefresh, depth = 0 }: { post: FeedPost; comment: FeedComment; onRefresh: () => Promise<void>; depth?: number }) {
  const [replying, setReplying] = useState(false)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  async function sendReply() {
    if (!text.trim()) return
    setBusy(true)
    try { await api.commentPost(post.uuid, text, comment.uuid); setText(''); setReplying(false); await onRefresh() } finally { setBusy(false) }
  }
  async function react(kind: ReactionKind) {
    await api.reactComment(comment.uuid, comment.reaction_summary.mine === kind ? null : kind)
    await onRefresh()
  }
  return <div className={`feed-comment ${depth ? 'feed-comment--reply' : ''}`}>
    <span className="avatar avatar--comment">{comment.author_name.slice(0, 2).toUpperCase()}</span>
    <div><div className="comment-bubble"><strong>{comment.author_name}</strong><p>{comment.content}</p></div>
      {!comment.deleted_at && <div className="comment-actions"><button onClick={() => react('like')}>{comment.reaction_summary.mine ? reactions.find((item) => item.value === comment.reaction_summary.mine)?.label : 'Thích'}</button>{depth === 0 && <button onClick={() => setReplying((value) => !value)}>Trả lời</button>}{comment.can_delete && <button className="danger-link" onClick={async () => { await api.deleteFeedComment(comment.uuid); await onRefresh() }}>Xóa</button>}<span>{formatTime(comment.created_at)}</span></div>}
      {replying && <div className="comment-reply-form"><input value={text} onChange={(event) => setText(event.target.value)} placeholder="Viết trả lời…"/><button disabled={busy || !text.trim()} onClick={sendReply}>Gửi</button></div>}
      {comment.replies.map((reply) => <CommentThread key={reply.uuid} post={post} comment={reply} onRefresh={onRefresh} depth={1}/>)}
    </div>
  </div>
}

function FeedPostCard({ post, options, onRefresh }: { post: FeedPost; options: FeedAudienceOptions; onRefresh: () => Promise<void> }) {
  const [comment, setComment] = useState('')
  const [sharing, setSharing] = useState(false)
  const [shareText, setShareText] = useState('')
  const [shareAudience, setShareAudience] = useState<AudienceValue>({ company: post.company_scope, employees: [], teams: post.audience_teams })
  const [busy, setBusy] = useState(false)
  const allowed = useMemo(() => {
    if (post.company_scope) return { company: true, employees: new Set(options.employees.map((item) => item.uuid)), teams: new Set(options.teams.map((item) => item.uuid)) }
    const teams = new Set(post.audience_teams)
    const employees = new Set([...post.audience_employees, ...options.employees.filter((item) => item.team_uuid && teams.has(item.team_uuid)).map((item) => item.uuid)])
    return { company: false, employees, teams }
  }, [post, options])
  const totalReactions = Object.values(post.reaction_summary.counts).reduce((sum, value) => sum + value, 0)

  async function refresh(action: () => Promise<unknown>) { setBusy(true); try { await action(); await onRefresh() } finally { setBusy(false) } }
  async function submitComment() { if (!comment.trim()) return; await refresh(() => api.commentPost(post.uuid, comment)); setComment('') }
  async function submitShare() { await refresh(() => api.sharePost(post.uuid, { content: shareText, company_scope: shareAudience.company, employee_uuids: shareAudience.employees, team_uuids: shareAudience.teams })); setSharing(false); setShareText('') }
  const scope = post.company_scope ? 'Toàn công ty' : [...post.audience_team_names, ...post.audience_employee_names].join(', ')

  return <article className={`feed-post-card ${post.is_official ? 'feed-post-card--official' : ''}`}>
    <header><span className="avatar">{post.author_name.slice(0, 2).toUpperCase()}</span><div><strong>{post.author_name}</strong><span>{post.is_official && <b>Thông báo chính thức</b>} {scope} · {formatTime(post.created_at)}</span></div>{post.can_delete && <button className="icon-action danger-action" aria-label="Xóa bài viết" disabled={busy} onClick={() => refresh(() => api.deleteFeedPost(post.uuid))}><AppIcon name="trash"/></button>}</header>
    {post.content && <p className="post-copy">{post.content}</p>}
    {post.shared_post && <div className={`shared-post ${post.shared_post.available ? '' : 'shared-post--missing'}`}><strong>{post.shared_post.available ? post.shared_post.author_name : 'Nội dung gốc không còn khả dụng'}</strong><p>{post.shared_post.content}</p></div>}
    {post.attachments.length > 0 && <div className="attachment-grid">{post.attachments.map((file) => <a key={file.uuid} href={file.download_url}><span className="attachment-icon"><AppIcon name="paperclip"/></span><span><strong>{file.original_name}</strong><small>{bytes(file.size)} · {file.content_type}</small></span></a>)}</div>}
    <div className="post-summary"><span>{totalReactions ? `${totalReactions} cảm xúc` : 'Chưa có cảm xúc'}</span><span>{post.comments.length} bình luận</span></div>
    <div className="post-actions">
      <div className="reaction-menu">{reactions.map((reaction) => <button key={reaction.value} className={post.reaction_summary.mine === reaction.value ? 'active' : ''} disabled={busy} onClick={() => refresh(() => api.reactPost(post.uuid, post.reaction_summary.mine === reaction.value ? null : reaction.value))}><span className={`reaction-dot reaction-dot--${reaction.value}`}/>{reaction.label}</button>)}</div>
      <button onClick={() => setSharing((value) => !value)}><AppIcon name="share"/>Chia sẻ</button>
    </div>
    {sharing && <div className="share-panel"><div><h4>Chia sẻ trong audience gốc</h4><button className="text-button" onClick={() => setSharing(false)}>Đóng</button></div><textarea value={shareText} onChange={(event) => setShareText(event.target.value)} placeholder="Thêm lời dẫn (không bắt buộc)"/><AudiencePicker compact options={options} value={shareAudience} allowed={allowed} onChange={setShareAudience}/><button className="primary-button compact" disabled={busy || (!shareAudience.company && !shareAudience.employees.length && !shareAudience.teams.length)} onClick={submitShare}>Chia sẻ an toàn</button></div>}
    <div className="comment-compose"><span className="avatar avatar--comment">Bạn</span><input value={comment} onChange={(event) => setComment(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') void submitComment() }} placeholder="Viết bình luận…"/><button disabled={busy || !comment.trim()} onClick={submitComment}>Gửi</button></div>
    <div className="comment-thread">{post.comments.map((item) => <CommentThread key={item.uuid} post={post} comment={item} onRefresh={onRefresh}/>)}</div>
  </article>
}

export function FeedWorkspace({ session }: { session: Session }) {
  const [posts, setPosts] = useState<FeedPost[]>([])
  const [options, setOptions] = useState<FeedAudienceOptions>({ employees: [], teams: [] })
  const [audience, setAudience] = useState<AudienceValue>({ company: true, employees: [], teams: [] })
  const [content, setContent] = useState('')
  const [official, setOfficial] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(true)
  const [publishing, setPublishing] = useState(false)
  const [error, setError] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)
  const canOfficial = session.capabilities?.includes('feed_domain.publish_official_post')

  async function load() {
    setError('')
    try { const [feed, audienceOptions] = await Promise.all([api.feedPosts(), api.feedAudience()]); setPosts(feed.results); setOptions(audienceOptions) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được Bảng tin.') }
    finally { setLoading(false) }
  }
  useEffect(() => {
    Promise.all([api.feedPosts(), api.feedAudience()]).then(([feed, audienceOptions]) => { setPosts(feed.results); setOptions(audienceOptions) }).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được Bảng tin.')).finally(() => setLoading(false))
  }, [])

  async function publish() {
    setPublishing(true); setError('')
    try {
      await api.createFeedPost({ content, company_scope: audience.company, employee_uuids: audience.employees, team_uuids: audience.teams, is_official: official, attachments: files })
      setContent(''); setFiles([]); setOfficial(false); if (fileInput.current) fileInput.current.value = ''; await load()
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Không đăng được bài viết.') }
    finally { setPublishing(false) }
  }

  const valid = (content.trim() || files.length) && (audience.company || audience.employees.length || audience.teams.length) && files.length <= 5 && files.every((file) => file.size <= 10 * 1024 * 1024)
  return <div className="feed-workspace">
    <section className="feed-composer">
      <div className="composer-author"><span className="avatar avatar--large">{(session.display_name ?? 'MR').slice(0, 2).toUpperCase()}</span><div><strong>Chia sẻ điều đang diễn ra</strong><span>Đúng người, đúng Team, đúng phạm vi.</span></div></div>
      <textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Thông báo, cập nhật công việc hoặc điều cần cả Team biết…"/>
      <AudiencePicker options={options} value={audience} onChange={(value) => { setAudience(value); if (!value.company) setOfficial(false) }}/>
      {files.length > 0 && <div className="selected-files">{files.map((file) => <span key={`${file.name}-${file.lastModified}`}><AppIcon name="paperclip"/>{file.name}<button aria-label={`Bỏ ${file.name}`} onClick={() => setFiles((current) => current.filter((item) => item !== file))}><AppIcon name="trash" size={12}/></button></span>)}</div>}
      <footer><div><label className="file-button"><AppIcon name="paperclip"/>Ảnh hoặc tệp<input ref={fileInput} type="file" multiple accept=".jpg,.jpeg,.png,.webp,.gif,.pdf,.txt,.csv,.docx,.xlsx,.pptx,.zip" onChange={(event) => setFiles(Array.from(event.target.files ?? []).slice(0, 5))}/></label>{canOfficial && audience.company && <label className="official-toggle"><input type="checkbox" checked={official} onChange={(event) => setOfficial(event.target.checked)}/><span>Thông báo chính thức</span></label>}</div><button className="primary-button" disabled={!valid || publishing} onClick={publish}>{publishing ? 'Đang đăng…' : 'Đăng bài'}</button></footer>
    </section>
    {error && <div className="alert alert--error">{error}</div>}
    {loading ? <div className="feed-loading"><span/><span/></div> : posts.length === 0 ? <div className="state-panel"><strong>Bảng tin đang trống</strong><p>Hãy đăng cập nhật đầu tiên cho Team hoặc công ty.</p></div> : <div className="feed-list">{posts.map((post) => <FeedPostCard key={post.uuid} post={post} options={options} onRefresh={load}/>)}</div>}
  </div>
}
