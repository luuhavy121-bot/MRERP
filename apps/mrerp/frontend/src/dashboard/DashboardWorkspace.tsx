import { useEffect, useState } from 'react'
import { api } from '../api'
import { AppIcon } from '../components/AppIcon'
import type { DashboardData, DashboardNotification } from '../types'

type Destination = 'profile' | 'feed' | 'tasks' | 'leave' | 'recruitment' | 'documents' | 'rewards'

function when(value: string) {
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

function targetFor(notification: DashboardNotification): Destination {
  if (notification.target_type === 'post') return 'feed'
  if (notification.target_type === 'task' || notification.target_type === 'goal') return 'tasks'
  if (notification.target_type === 'leave') return 'leave'
  if (notification.target_type === 'recruitment') return 'recruitment'
  if (notification.target_type === 'document') return 'documents'
  if (notification.target_type === 'recognition') return 'rewards'
  return 'profile'
}

export function DashboardWorkspace({ onNavigate }: { onNavigate: (target: Destination) => void }) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try { setData(await api.dashboard()) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Không tải được Tổng quan.') }
    finally { setLoading(false) }
  }

  useEffect(() => {
    api.dashboard().then(setData).catch((reason) => setError(reason instanceof Error ? reason.message : 'Không tải được Tổng quan.')).finally(() => setLoading(false))
    function refreshNotifications() { void load() }
    window.addEventListener('mrerp:notifications-changed', refreshNotifications)
    return () => window.removeEventListener('mrerp:notifications-changed', refreshNotifications)
  }, [])

  async function openNotification(notification: DashboardNotification) {
    onNavigate(targetFor(notification))
    if (!notification.is_read) {
      setData((current) => current ? { ...current, private: { ...current.private, unread_count: Math.max(0, current.private.unread_count - 1), notifications: current.private.notifications.map((item) => item.uuid === notification.uuid ? { ...item, is_read: true } : item) } } : current)
      try {
        await api.readNotification(notification.uuid)
      } catch {
        setActionError('Đã mở nội dung nhưng chưa thể lưu trạng thái đã đọc. Bạn có thể thử lại sau.')
      }
    }
  }

  async function readAll() {
    setActionError('')
    try {
      await api.readAllNotifications()
      setData((current) => current ? { ...current, private: { ...current.private, unread_count: 0, notifications: current.private.notifications.map((item) => ({ ...item, is_read: true })) } } : current)
    } catch {
      setActionError('Chưa thể đánh dấu tất cả đã đọc. Vui lòng thử lại.')
    }
  }

  if (loading) return <div className="dashboard-skeleton" aria-label="Đang tải Tổng quan"><span /><span /><span /></div>
  if (error) return <div className="state-panel state-panel--error"><strong>Chưa tải được Tổng quan</strong><p>{error}</p><button className="secondary-button" onClick={load}>Thử lại</button></div>
  if (!data) return null

  return <div className="dashboard-workspace">
    <section className="dashboard-welcome" aria-labelledby="dashboard-welcome-title">
      <div><h2 id="dashboard-welcome-title">Mọi điều cần biết để bắt đầu ngày làm việc.</h2><p>Thông tin toàn công ty ở bên trái. Việc chỉ liên quan đến bạn ở bên phải.</p></div>
      <div className="dashboard-welcome__signal" aria-label={`${data.private.unread_count} thông báo chưa đọc`}><AppIcon name="bell" size={22}/><span><strong>{data.private.unread_count}</strong><small>chưa đọc</small></span></div>
    </section>
    <div className="dashboard-columns">
      <section className="dashboard-stream dashboard-stream--general">
        <header className="stream-heading"><div><h3>Thông báo chung</h3><p>Mọi nhân sự đều nhìn thấy</p></div><span className="scope-chip">Công ty</span></header>
        <div className="guide-strip">
          {data.general.guides.map((guide) => <button key={guide.id} onClick={() => onNavigate(guide.target)}><AppIcon name={guide.id === 'profile' ? 'profile' : guide.id === 'security' ? 'admin' : 'share'} /><span><strong>{guide.title}</strong><small>{guide.body}</small></span></button>)}
        </div>
        <div className="company-update-list">
          {data.general.company_posts.length === 0 ? <div className="empty-inline"><strong>Chưa có thông báo công ty</strong><span>Bài viết phạm vi công ty sẽ xuất hiện tại đây.</span></div> : data.general.company_posts.map((post) => <button key={post.uuid} className={`company-update ${post.is_official ? 'company-update--official' : ''}`} onClick={() => onNavigate('feed')}>
            <span className="avatar avatar--soft">{post.author_name.slice(0, 2).toUpperCase()}</span><span><span className="company-update__meta">{post.is_official && <b>Chính thức</b>} {post.author_name} · {when(post.created_at)}</span><strong>{post.content || `Bài viết có ${post.attachment_count} file đính kèm`}</strong></span>
          </button>)}
        </div>
      </section>
      <section className="dashboard-stream dashboard-stream--private">
        <header className="stream-heading"><div><h3>Thông báo riêng</h3><p>Chỉ dành cho tài khoản này</p></div>{data.private.unread_count > 0 && <button className="text-button" onClick={readAll}>Đánh dấu đã đọc</button>}</header>
        {actionError && <div className="alert alert--error dashboard-action-error" role="status">{actionError}</div>}
        {data.private.warnings.map((warning) => <button key={warning.id} className="personal-warning" onClick={() => onNavigate(warning.target)}><AppIcon name="admin"/><span><strong>{warning.title}</strong><small>{warning.body}</small></span></button>)}
        <div className="notification-list">
          {data.private.notifications.length === 0 ? <div className="empty-inline"><strong>Bạn đã xử lý hết</strong><span>Task, đơn nghỉ và tương tác liên quan sẽ xuất hiện tại đây.</span></div> : data.private.notifications.map((item) => <button key={item.uuid} className={`notification-item ${item.is_read ? '' : 'notification-item--unread'}`} onClick={() => openNotification(item)}>
            <span className="notification-item__icon"><AppIcon name={item.kind === 'task' ? 'tasks' : item.kind === 'goal' ? 'goal' : item.kind === 'leave' ? 'leave' : item.kind === 'account' ? 'profile' : 'feed'} /></span>
            <span><span className="notification-item__meta">{item.kind_label} · {when(item.created_at)}</span><strong>{item.title}</strong>{item.body && <small>{item.body}</small>}</span>{!item.is_read && <><span className="visually-hidden">Chưa đọc</span><i aria-hidden="true" /></>}
          </button>)}
        </div>
      </section>
    </div>
  </div>
}
