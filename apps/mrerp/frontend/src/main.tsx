import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { Careers } from './recruitment/Careers'
import './App.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/^\/careers(?:\/|$)/.test(window.location.pathname) ? <Careers /> : <App />}
  </StrictMode>,
)
import './hr-demo.css'
