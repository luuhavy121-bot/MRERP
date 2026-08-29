import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { DashboardNotification } from '../types'
import { AppIcon } from './AppIcon'

type Destination = 'profile' | 'feed' | 'tasks' | 'leave' | 'recruitment' | 'documents' | 'rewards'

function destinationFor(notification: DashboardNotification): Destination {
  if (notification.target_type === 'post') return 'feed'
  if (notification.target_type === 'task' || notification.target_type === 'goal') return 'tasks'
  if (notification.target_type === 'leave') return 'leave'
  if (notification.target_type === 'recruitment') return 'recruitment'
  if (notification.target_type === 'document') return 'documents'
  if (notification.target_type === 'recognition') return 'rewards'
  return 'profile'
}

function when(value: string) {
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

export function GlobalNotifications({ refreshKey, onNavigate }: { refreshKey: string; onNavigate: (target: Destination) => void }) {
  const wrapperRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)
  const [notifications, setNotifications] = useState<DashboardNotification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    try {
      const data = await api.dashboard()
      setError('')
      setNotifications(data.private.notifications)
      setUnreadCount(data.private.unread_count)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không tải được thông báo.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    api.dashboard()
      .then((data) => {
        if (cancelled) return
        setError('')
        setNotifications(data.private.notifications)
        setUnreadCount(data.private.unread_count)
      })
      .catch((reason) => { if (!cancelled) setError(reason instanceof Error ? reason.message : 'Không tải được thông báo.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [refreshKey])
  useEffect(() => {
    function dismiss(event: MouseEvent) {
      if (!wrapperRef.current?.contains(event.target as Node)) setOpen(false)
    }
    function escape(event: KeyboardEvent) { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', dismiss)
    document.addEventListener('keydown', escape)
    return () => { document.removeEventListener('mousedown', dismiss); document.removeEventListener('keydown', escape) }
  }, [])

  async function openNotification(notification: DashboardNotification) {
    setOpen(false)
    onNavigate(destinationFor(notification))
    if (notification.is_read) return
    try {
      await api.readNotification(notification.uuid)
      setNotifications((items) => items.map((item) => item.uuid === notification.uuid ? { ...item, is_read: true } : item))
      setUnreadCount((count) => Math.max(0, count - 1))
      window.dispatchEvent(new Event('mrerp:notifications-changed'))
    } catch {
      setError('Đã mở nội dung nhưng chưa lưu được trạng thái đã đọc.')
    }
  }

  async function readAll() {
    try {
      await api.readAllNotifications()
      setNotifications((items) => items.map((item) => ({ ...item, is_read: true })))
      setUnreadCount(0)
      window.dispatchEvent(new Event('mrerp:notifications-changed'))
    } catch {
      setError('Chưa thể đánh dấu tất cả đã đọc.')
    }
  }

  return <div className="global-notifications" ref={wrapperRef}>
    <button className="chrome-icon-button notification-trigger" aria-label={`Thông báo${unreadCount ? `, ${unreadCount} chưa đọc` : ''}`} aria-expanded={open} aria-controls="global-notification-panel" onClick={() => { setOpen((value) => !value); if (!open) void load() }}>
      <AppIcon name="bell" size={20} />
      {unreadCount > 0 && <span className="notification-badge" aria-hidden="true">{unreadCount > 99 ? '99+' : unreadCount}</span>}
    </button>
    {open && <section id="global-notification-panel" className="chrome-popover notification-popover" role="dialog" aria-label="Thông báo của tôi">
      <header><div><strong>Thông báo</strong><span>{unreadCount ? `${unreadCount} chưa đọc` : 'Đã đọc hết'}</span></div>{unreadCount > 0 && <button className="text-button" onClick={readAll}>Đọc tất cả</button>}</header>
      {error && <div className="chrome-popover__error" role="status">{error}</div>}
      {loading ? <div className="chrome-popover__empty">Đang tải thông báo…</div> : notifications.length === 0 ? <div className="chrome-popover__empty"><AppIcon name="bell" /><strong>Chưa có thông báo mới</strong><span>Task, đơn nghỉ và tương tác liên quan sẽ xuất hiện tại đây.</span></div> : <div className="global-notification-list">{notifications.slice(0, 10).map((item) => <button key={item.uuid} className={item.is_read ? '' : 'unread'} onClick={() => openNotification(item)}><span className="notification-item__icon"><AppIcon name={item.kind === 'task' ? 'tasks' : item.kind === 'goal' ? 'goal' : item.kind === 'leave' ? 'leave' : item.kind === 'account' ? 'profile' : item.kind === 'recruitment' ? 'recruitment' : item.kind === 'document' ? 'documents' : item.kind === 'recognition' ? 'rewards' : 'feed'} /></span><span><small>{item.kind_label} · {when(item.created_at)}</small><strong>{item.title}</strong>{item.body && <em>{item.body}</em>}</span>{!item.is_read && <i aria-label="Chưa đọc" />}</button>)}</div>}
      <footer><button onClick={() => { setOpen(false); onNavigate('profile') }}>Mở hồ sơ của tôi</button></footer>
    </section>}
  </div>
}
