import type { CSSProperties } from 'react'
import { projectStatus } from '../projectStatus'

export function ProjectProgress() {
  const completedModules = projectStatus.modules.filter((module) => module.percent === 100).length
  return <div className="progress-dashboard">
    <section className="progress-hero">
      <div className="progress-hero__copy">
        <p className="eyebrow">PROJECT DELIVERY · CẬP NHẬT {projectStatus.updatedAt}</p>
        <h2>MRERP đang được xây đến đâu?</h2>
        <p>Tiến độ được đối chiếu với roadmap, story, code và bằng chứng kiểm thử. Prototype không được tính như một tính năng production đã hoàn thành.</p>
        <div className="phase-chip"><span className="live-dot" />{projectStatus.currentPhase} · {projectStatus.currentPhaseName}</div>
      </div>
      <div className="progress-orbit" style={{ '--progress': `${projectStatus.overallPercent * 3.6}deg` } as CSSProperties}>
        <div><strong>{projectStatus.overallPercent}%</strong><span>toàn dự án</span></div>
      </div>
    </section>
    <section className="progress-summary-grid">
      <article><span>Modules theo kế hoạch</span><strong>{projectStatus.modules.length}</strong><small>{completedModules} module hoàn tất 100%</small></article>
      <article><span>Quyết định đã giải quyết</span><strong>{projectStatus.decisions.resolved}</strong><small>{projectStatus.decisions.open} open decisions còn lại</small></article>
      <article><span>Backend tests tự động</span><strong>{projectStatus.automatedTestCount}</strong><small>6 luồng E2E chạy riêng trên Chromium</small></article>
      <article><span>Ưu tiên quyết định</span><strong>OD-13</strong><small>Policy công, phép và lương vẫn mở</small></article>
    </section>
    <section className="progress-section">
      <div className="progress-section__head"><div><p className="eyebrow">ROADMAP</p><h3>Tiến độ theo phase</h3></div><small>{projectStatus.calculation}</small></div>
      <div className="phase-track">{projectStatus.phases.map((phase) => <article className={`phase-card phase-card--${phase.tone}`} key={phase.id}>
        <div><span>{phase.id}</span><b>{phase.percent}%</b></div><strong>{phase.name}</strong><small>{phase.state}</small><div className="mini-progress"><i style={{ width: `${phase.percent}%` }} /></div>
      </article>)}</div>
    </section>
    <section className="progress-layout">
      <div className="progress-section">
        <div className="progress-section__head"><div><p className="eyebrow">12 MODULES</p><h3>Bản đồ hoàn thiện</h3></div><span className="legend"><i /> Production slice <i /> Prototype/kế hoạch</span></div>
        <div className="module-progress-grid">{projectStatus.modules.map((module) => <article className="module-progress-card" key={module.name}>
          <div className="module-progress-card__top"><span className={`progress-state progress-state--${module.tone}`}>{module.state}</span><b>{module.percent}%</b></div>
          <h4>{module.name}</h4><small>{module.phase}</small><div className="mini-progress"><i className={`tone--${module.tone}`} style={{ width: `${module.percent}%` }} /></div><p>{module.next}</p>
        </article>)}</div>
      </div>
      <aside className="progress-side">
        <section className="progress-section"><p className="eyebrow">QUALITY SIGNALS</p><h3>Bằng chứng hiện tại</h3><div className="quality-list">{projectStatus.quality.map((item) => <div key={item.label}><span><b>{item.label}</b><em>{item.state}</em></span><strong>{item.value}%</strong><div className="mini-progress"><i style={{ width: `${item.value}%` }} /></div></div>)}</div></section>
        <section className="progress-section next-gates"><p className="eyebrow">NEXT GATES</p><h3>Việc cần làm tiếp</h3><ol>{projectStatus.nextGates.map((gate) => <li key={gate}>{gate}</li>)}</ol><div className="decision-note"><span>Decision debt ưu tiên</span><strong>{projectStatus.decisions.priority}</strong></div></section>
      </aside>
    </section>
    <p className="progress-disclaimer">Màn hình Tiến độ là công cụ quản trị tạm thời và sẽ tự ẩn khi tổng tiến độ đạt 100%.</p>
  </div>
}
