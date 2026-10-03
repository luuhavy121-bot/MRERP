import { useEffect, useState } from 'react'
import { request } from '../api'
import type { Page, Recognition } from '../types'

export function EmployeeRecognition({ employee, month, canCreate }: {employee:string;month:string;canCreate:boolean}) {
  const [rows,setRows]=useState<Recognition[]>([])
  const [category,setCategory]=useState('')
  const [message,setMessage]=useState('')
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)
  const [reload,setReload]=useState(0)
  useEffect(()=>{let live=true;setRows([]);setError('');request<Page<Recognition>>(`/api/v1/rewards/recognitions/?employee_uuid=${employee}&month=${month}`).then(p=>{if(live)setRows(p.results)}).catch(e=>{if(live)setError(e.message)});return()=>{live=false}},[employee,month,reload])
  return <details className="employee-recognition"><summary>Ghi nhận đóng góp ({rows.length})</summary>
    <p>Những đóng góp được ghi nhận trong tháng. Ghi nhận không tự cộng sao hoặc điểm KPI.</p>
    {rows.map(r=><article key={r.uuid}><strong>{r.category} · {r.sender_name}</strong><p>{r.message}</p><small>{new Date(r.created_at).toLocaleDateString('vi-VN')}</small></article>)}
    {!rows.length&&<p>Chưa có ghi nhận trong kỳ này.</p>}
    {error&&<p role="alert">{error}</p>}
    {canCreate&&<form onSubmit={async e=>{e.preventDefault();setBusy(true);setError('');try{await request('/api/v1/rewards/recognitions/',{method:'POST',body:JSON.stringify({recipient_uuids:[employee],category,message})});setCategory('');setMessage('');setReload(n=>n+1)}catch(e){setError(e instanceof Error?e.message:'Không gửi được ghi nhận.')}finally{setBusy(false)}}}>
      <label>Chủ đề ghi nhận<input required maxLength={80} value={category} onChange={e=>setCategory(e.target.value)}/></label><label>Đóng góp của nhân sự<textarea required maxLength={3000} value={message} onChange={e=>setMessage(e.target.value)}/></label><p>Ghi nhận mới được lưu theo ngày hôm nay.</p><button className="secondary-button" disabled={busy}>Ghi nhận đóng góp</button>
    </form>}
  </details>
}
