import { useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { Session } from '../types'

export function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [username, setUsername] = useState('hr.demo')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      onLogin(await api.login(username, password))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Không thể đăng nhập.')
    } finally {
      setLoading(false)
    }
  }

  return <main className="login-shell">
    <section className="login-story">
      <img className="login-brand-logo" src="/brand/mr-ecom-logo.png" alt="MR ECOM" />
      <p className="eyebrow">MRERP WORKSPACE</p>
      <h1>Một nơi để đội ngũ<br />làm việc rõ ràng hơn.</h1>
      <p className="lead">Tổng quan, Bảng tin, Nhân sự và Công việc được nối xuyên giao diện, API, dữ liệu, quyền và audit. Mock Identity chỉ hoạt động trong môi trường phát triển.</p>
      <div className="trust-row"><span>Session cookie</span><span>Server authorization</span><span>Audit trail</span></div>
    </section>
    <section className="login-card-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="login-card__top"><span className="live-dot" /> DEVELOPMENT IDENTITY</div>
        <h2>Chào mừng trở lại</h2>
        <p>Đăng nhập bằng tài khoản demo đã được seed cục bộ.</p>
        <label>Tài khoản<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label>
        <label>Mật khẩu<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /></label>
        {error && <div className="alert alert--error">{error}</div>}
        <button className="primary-button" disabled={loading}>{loading ? 'Đang xác thực…' : 'Đăng nhập MRERP'}</button>
        <small>Mock login tự động bị khóa khi cấu hình production.</small>
      </form>
    </section>
  </main>
}
