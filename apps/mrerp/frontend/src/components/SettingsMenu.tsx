import { useEffect, useRef, useState } from 'react'
import { AppIcon } from './AppIcon'

export type Theme = 'light' | 'dark'

export function SettingsMenu({ theme, onThemeChange, onOpenSettings, onLogout }: { theme: Theme; onThemeChange: (theme: Theme) => void; onOpenSettings: () => void; onLogout: () => void }) {
  const wrapperRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)
  useEffect(() => {
    function dismiss(event: MouseEvent) { if (!wrapperRef.current?.contains(event.target as Node)) setOpen(false) }
    function escape(event: KeyboardEvent) { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', dismiss)
    document.addEventListener('keydown', escape)
    return () => { document.removeEventListener('mousedown', dismiss); document.removeEventListener('keydown', escape) }
  }, [])

  return <div className="settings-menu" ref={wrapperRef}>
    <button className="chrome-icon-button" aria-label="Cài đặt" aria-expanded={open} aria-controls="settings-popover" onClick={() => setOpen((value) => !value)}><AppIcon name="settings" size={20} /></button>
    {open && <section id="settings-popover" className="chrome-popover settings-popover" role="dialog" aria-label="Cài đặt hệ thống">
      <header><div><strong>Cài đặt</strong><span>Giao diện và phiên làm việc</span></div></header>
      <label className="theme-toggle"><span className="theme-toggle__icon"><AppIcon name={theme === 'dark' ? 'moon' : 'sun'} /></span><span><strong>Nền tối</strong><small>{theme === 'dark' ? 'Đang bật' : 'Đang tắt'}</small></span><input type="checkbox" checked={theme === 'dark'} onChange={(event) => onThemeChange(event.target.checked ? 'dark' : 'light')} /><i aria-hidden="true" /></label>
      <button className="settings-open" onClick={() => { setOpen(false); onOpenSettings() }}><AppIcon name="settings" /><span><strong>Cài đặt cá nhân</strong><small>Thông báo và trạng thái bảo mật</small></span></button>
      <button className="settings-logout" onClick={onLogout}><AppIcon name="logout" /><span><strong>Đăng xuất</strong><small>Kết thúc phiên trên thiết bị này</small></span></button>
    </section>}
  </div>
}
