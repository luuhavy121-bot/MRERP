import { useEffect, useState } from 'react'
import './App.css'
import { api } from './api'
import { Login } from './components/Login'
import { ProjectProgress } from './components/ProjectProgress'
import { PeopleWorkspace } from './people/PeopleWorkspace'
import { LeaveWorkspace } from './leave/LeaveWorkspace'
import { ProfileWorkspace } from './profile/ProfileWorkspace'
import { AdminWorkspace } from './admin/AdminWorkspace'
import { DashboardWorkspace } from './dashboard/DashboardWorkspace'
import { FeedWorkspace } from './feed/FeedWorkspace'
import { TaskWorkspace } from './tasks/TaskWorkspace'
import { AppIcon } from './components/AppIcon'
import { GlobalNotifications } from './components/GlobalNotifications'
import { SettingsMenu, type Theme } from './components/SettingsMenu'
import { showProjectProgress } from './projectStatus'
import { SettingsWorkspace } from './settings/SettingsWorkspace'
import { RecruitmentWorkspace } from './recruitment/RecruitmentWorkspace'
import { DocumentsWorkspace } from './documents/DocumentsWorkspace'
import { RewardsWorkspace } from './rewards/RewardsWorkspace'
import { PerformanceWorkspace } from './performance/PerformanceWorkspace'
import './crm/crm.css'
import { CRMApp } from './crm/CRMApp'
import type { Session } from './types'

function Workspace({ session, theme, onThemeChange, onLogout, onSwitchSession }: { session: Session; theme: Theme; onThemeChange: (theme: Theme) => void; onLogout: () => void; onSwitchSession: (session: Session) => void }) {
  const [tab, setTab] = useState<'dashboard' | 'feed' | 'tasks' | 'people' | 'leave' | 'progress' | 'profile' | 'admin' | 'settings' | 'recruitment' | 'documents' | 'rewards' | 'performance'>(() => { const view = new URLSearchParams(window.location.search).get('workspace'); return view === 'profile' || view === 'settings' ? view : 'dashboard' })
  const isCRM = /^\/crm(?:\/|$)/.test(window.location.pathname)
  const [switchingPersona, setSwitchingPersona] = useState(false)
  const [personaError, setPersonaError] = useState('')

  async function switchPersona(username: string) {
    if (!username || username === session.username) return
    setSwitchingPersona(true)
    setPersonaError('')
    try {
      onSwitchSession(await api.switchPersona(username))
    } catch (reason) {
      setPersonaError(reason instanceof Error ? reason.message : 'Không chuyển được persona debug.')
    } finally {
      setSwitchingPersona(false)
    }
  }

  const pageTitle = tab === 'performance' ? 'Đánh giá nhân sự' : tab === 'dashboard' ? 'Tổng quan' : tab === 'feed' ? 'Bảng tin' : tab === 'tasks' ? 'Công việc' : tab === 'people' ? 'Nhân sự' : tab === 'leave' ? 'Nghỉ & Công' : tab === 'profile' ? 'Hồ sơ của tôi' : tab === 'admin' ? 'Admin Panel' : tab === 'settings' ? 'Cài đặt cá nhân' : tab === 'recruitment' ? 'Tuyển dụng' : tab === 'documents' ? 'Tài liệu' : tab === 'rewards' ? 'Sao & Đổi thưởng' : 'Tiến độ dự án'

  if (isCRM) return <CRMApp session={session} theme={theme} onThemeChange={onThemeChange} onLogout={onLogout} />

  return <div className={`app-shell app-shell--${isCRM ? 'crm' : tab}`}>
    <header className="product-bar">
      <button className="product-brand" aria-label="Về Tổng quan MRERP" onClick={() => isCRM ? window.location.assign('/') : setTab('dashboard')}>
        <img src="/brand/mr-ecom-logo.png" alt="" />
        <strong>MR ECOM</strong>
      </button>
      <nav className="product-switcher" aria-label="Hệ sinh thái MR ECOM">
        <a href="/" className={`product-switcher__item ${isCRM ? '' : 'active'}`} aria-current={isCRM ? undefined : 'page'}>
          <span className="product-grid-icon" aria-hidden="true"><i /><i /><i /><i /></span>
          <span className="product-switcher__label">MRERP</span>
        </a>
        <a className="product-switcher__item product-switcher__item--external" href="https://trello.mrecomapp.click/mrekanban/" target="_blank" rel="noopener noreferrer" aria-label="Mở MREKANBAN trong tab mới">
          <span className="product-switcher__label">MREKANBAN</span><span className="product-switcher__short" aria-hidden="true">KB</span><AppIcon name="external" size={14}/>
        </a>
        {session.product_entitlements?.includes('assetcontrol') && <a className="product-switcher__item product-switcher__item--external" href="https://www.mrecomapp.click/" target="_blank" rel="noopener noreferrer" aria-label="Mở ASSETCONTROL trong tab mới">
          <span className="product-switcher__label">ASSETCONTROL</span><span className="product-switcher__short" aria-hidden="true">AC</span><AppIcon name="external" size={14}/>
        </a>}
        <a className={`product-switcher__item product-switcher__item--external ${isCRM ? 'active' : ''}`} href="/crm" target={isCRM ? undefined : '_blank'} rel="noopener noreferrer" aria-current={isCRM ? 'page' : undefined} aria-label="MRECRM"><span className="product-switcher__label">MRECRM</span><span className="product-switcher__short" aria-hidden="true">CRM</span>{!isCRM && <AppIcon name="external" size={14}/>}</a>
      </nav>
      <details className="product-mobile-switcher"><summary>{isCRM ? 'MRECRM' : 'MRERP'}</summary><nav aria-label="Chuyển sản phẩm"><a href="/" aria-current={isCRM ? undefined : 'page'}>MRERP</a><a href="https://trello.mrecomapp.click/mrekanban/" target="_blank" rel="noopener noreferrer">MREKANBAN</a>{session.product_entitlements?.includes('assetcontrol') && <a href="https://www.mrecomapp.click/" target="_blank" rel="noopener noreferrer">ASSETCONTROL</a>}<a href="/crm" target={isCRM ? undefined : '_blank'} rel="noopener noreferrer" aria-current={isCRM ? 'page' : undefined}>MRECRM</a></nav></details>
      <div className="product-bar__actions">
        {session.mock_identity && (session.debug_personas?.length ?? 0) > 0 && <label className="debug-role-switcher debug-role-switcher--dark"><span><i className="live-dot" />Vai trò</span><select aria-label="Xem theo vai trò debug" value={session.username} disabled={switchingPersona} onChange={(event) => switchPersona(event.target.value)}>{session.debug_personas?.map((persona) => <option key={persona.username} value={persona.username}>{persona.label}</option>)}</select></label>}
        {!isCRM && <GlobalNotifications refreshKey={tab} onNavigate={(target) => setTab(target)} />}
        <SettingsMenu theme={theme} onThemeChange={onThemeChange} onOpenSettings={() => isCRM ? window.location.assign('/?workspace=settings') : setTab('settings')} onLogout={onLogout} />
        <button className="product-user" aria-label={`Mở hồ sơ của ${session.display_name}`} onClick={() => isCRM ? window.location.assign('/?workspace=profile') : setTab('profile')}>
          <span className="avatar">{(session.display_name ?? 'MR').slice(0, 2).toUpperCase()}</span>
          <span><strong>{session.display_name}</strong><small>{session.employee_code}</small></span>
        </button>
      </div>
    </header>
    {!isCRM && <aside className="sidebar">
      <nav><button className={`nav-link ${tab === 'dashboard' ? 'active' : ''}`} onClick={() => setTab('dashboard')}><AppIcon name="home"/>Tổng quan</button><button className={`nav-link ${tab === 'feed' ? 'active' : ''}`} onClick={() => setTab('feed')}><AppIcon name="feed"/>Bảng tin</button><button className={`nav-link ${tab === 'tasks' ? 'active' : ''}`} onClick={() => setTab('tasks')}><AppIcon name="tasks"/>Công việc</button><button className={`nav-link ${tab === 'profile' ? 'active' : ''}`} onClick={() => isCRM ? window.location.assign('/?workspace=profile') : setTab('profile')}><AppIcon name="profile"/>Hồ sơ của tôi</button><button className={`nav-link ${tab === 'people' ? 'active' : ''}`} onClick={() => setTab('people')}><AppIcon name="people"/>Nhân sự</button><button className={`nav-link ${tab === 'leave' ? 'active' : ''}`} onClick={() => setTab('leave')}><AppIcon name="leave"/>Nghỉ & Công</button>{session.capabilities?.some(c=>c.startsWith('performance_domain.')) && <button className={`nav-link ${tab === 'performance' ? 'active' : ''}`} onClick={()=>setTab('performance')}><AppIcon name="people"/>Đánh giá nhân sự</button>}{session.capabilities?.includes('recruitment_domain.view_scoped_recruitment') && <button className={`nav-link ${tab === 'recruitment' ? 'active' : ''}`} onClick={() => setTab('recruitment')}><AppIcon name="recruitment"/>Tuyển dụng</button>}{session.capabilities?.includes('documents_domain.view_documents') && <button className={`nav-link ${tab === 'documents' ? 'active' : ''}`} onClick={() => setTab('documents')}><AppIcon name="documents"/>Tài liệu</button>}{session.capabilities?.includes('rewards_domain.view_rewards') && <button className={`nav-link ${tab === 'rewards' ? 'active' : ''}`} onClick={() => setTab('rewards')}><AppIcon name="rewards"/>Sao & Đổi thưởng</button>}{session.capabilities?.includes('people_domain.view_people_admin_panel') && <button className={`nav-link ${tab === 'admin' ? 'active' : ''}`} onClick={() => setTab('admin')}><AppIcon name="admin"/>Admin Panel</button>}{showProjectProgress && <button className={`nav-link ${tab === 'progress' ? 'active' : ''}`} onClick={() => setTab('progress')}><AppIcon name="progress"/>Tiến độ</button>}</nav>
      <div className="sidebar-foot"><div className="mock-badge"><span className="live-dot" />Mock Identity</div></div>
    </aside>}
    <main className="workspace">
      {!isCRM && tab !== 'people' && tab !== 'performance' && tab !== 'rewards' && <header className="topbar"><div><h1>{pageTitle}</h1><p className="topbar-context">{tab === 'dashboard' ? 'Bắt đầu ngày làm việc tại đây' : tab === 'feed' ? 'Cập nhật nội bộ theo đúng phạm vi' : tab === 'tasks' ? 'Mục tiêu, Task và lịch lặp' : tab === 'recruitment' ? 'Nhu cầu, ứng viên và pipeline có kiểm soát' : tab === 'documents' ? 'Thư viện nội bộ với protected download' : 'MRERP · Workspace nội bộ'}</p></div></header>}
      {personaError && <div className="alert alert--error persona-error">{personaError}</div>}
      {tab === 'performance' ? <PerformanceWorkspace session={session}/> : tab === 'dashboard' ? <DashboardWorkspace onNavigate={(target) => setTab(target)} /> : tab === 'feed' ? <FeedWorkspace session={session} /> : tab === 'tasks' ? <TaskWorkspace session={session} /> : tab === 'progress' ? <ProjectProgress /> : tab === 'leave' ? <LeaveWorkspace session={session} /> : tab === 'profile' ? <ProfileWorkspace session={session} onProfileUpdated={(employee) => onSwitchSession({ ...session, display_name: employee.display_name })} /> : tab === 'settings' ? <SettingsWorkspace session={session} /> : tab === 'recruitment' ? <RecruitmentWorkspace session={session} /> : tab === 'documents' ? <DocumentsWorkspace session={session} /> : tab === 'rewards' ? <RewardsWorkspace session={session} /> : tab === 'admin' ? <AdminWorkspace session={session} /> : <PeopleWorkspace session={session} />}
    </main>
  </div>
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [theme, setTheme] = useState<Theme>(() => window.localStorage.getItem('mrerp-theme') === 'dark' ? 'dark' : 'light')
  const [loading, setLoading] = useState(true)
  useEffect(() => { api.session().then(setSession).finally(() => setLoading(false)) }, [])
  useEffect(() => { document.documentElement.dataset.theme = theme; document.documentElement.style.colorScheme = theme; window.localStorage.setItem('mrerp-theme', theme) }, [theme])
  if (loading) return <div className="boot-screen"><img className="boot-brand-logo" src="/brand/mr-ecom-logo.png" alt="MR ECOM" /><p>Đang khởi tạo workspace…</p></div>
  if (!session?.authenticated) return <Login onLogin={setSession} />
  return <Workspace key={session.username} session={session} theme={theme} onThemeChange={setTheme} onSwitchSession={setSession} onLogout={async () => { await api.logout(); setSession({ authenticated: false }) }} />
}
