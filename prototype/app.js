const pageContent = document.querySelector("#page-content");
const navItems = [...document.querySelectorAll(".nav-item[data-view]")];
const themeToggle = document.querySelector("#theme-toggle");
const createDialog = document.querySelector("#create-dialog");
const createButton = document.querySelector("#create-button");
const toast = document.querySelector("#toast");
const toastMessage = document.querySelector("#toast-message");
const profileButton = document.querySelector("#profile-button");
const profilePopover = document.querySelector("#profile-popover");
const sidebar = document.querySelector("#sidebar");
const sidebarBackdrop = document.querySelector("#sidebar-backdrop");
const mobileMenu = document.querySelector("#mobile-menu");
const globalSearch = document.querySelector("#global-search");

let toastTimer;
let currentView = "dashboard";
const projectStatus = window.MRERP_PROJECT_STATUS || {
  overallPercent: 0,
  currentPhase: "Chưa xác định",
  phases: [],
  modules: [],
  ecosystem: [],
  phase0Gates: [],
  quality: [],
  nextGates: [],
  sources: [],
  decisionSummary: { open: 0, resolved: 0, priority: 0, priorityNote: "" },
  calculation: { summary: "Chưa có dữ liệu.", formula: "", confidence: "Thấp", note: "" },
};

const preferenceStorage = {
  get(key) {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // Direct file previews may block storage; the current session still works.
    }
  },
};

const mockPeople = [
  ["NT", "Nguyễn Thảo", "HR Operations", "People", "Leader", "Đang làm việc", "avatar--coral"],
  ["PM", "Phạm Minh", "Performance Marketing", "Marketing", "Captain", "Đang làm việc", "avatar--blue"],
  ["AL", "Anh Lê", "Product Designer", "Product", "Staff", "Thử việc", "avatar--violet"],
  ["TK", "Trần Khoa", "Accountant", "Finance", "Staff", "Đang làm việc", "avatar--green"],
  ["VN", "Vũ Ngọc", "Sales Executive", "Sales", "Staff", "Đang làm việc", "avatar--coral"],
  ["HL", "Hoàng Linh", "Talent Acquisition", "People", "Staff", "Nghỉ phép", "avatar--blue"],
];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  toastMessage.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
}

function pageHeading(eyebrow, title, description, meta = "Dữ liệu mô phỏng") {
  return `
    <div class="page-heading">
      <div>
        <span class="eyebrow">${eyebrow}</span>
        <h1>${title}</h1>
        <p>${description}</p>
      </div>
      <div class="page-heading__meta"><span class="live-dot"></span>${meta}</div>
    </div>
  `;
}

function dashboardView() {
  const today = new Intl.DateTimeFormat("vi-VN", {
    weekday: "long",
    day: "2-digit",
    month: "long",
  }).format(new Date());

  return `
    <div class="page-wrap">
      ${pageHeading(
        "Không gian cá nhân",
        "Chào buổi sáng, Hà.",
        "Một nơi để nắm nhịp công việc, xử lý việc cần duyệt và đi tiếp mà không bị phân tán.",
        today.charAt(0).toUpperCase() + today.slice(1),
      )}

      <div class="dashboard-grid">
        <div class="dashboard-main">
          <section class="focus-card" aria-labelledby="focus-title">
            <div class="focus-card__copy">
              <span class="eyebrow">Ưu tiên hôm nay</span>
              <h2 id="focus-title">Giữ đà cho ba việc quan trọng nhất.</h2>
              <p>Bạn có 6 công việc đang mở, 2 việc cần hoàn thành trước 17:00 và một phê duyệt đang chờ phản hồi.</p>
              <div class="focus-card__actions">
                <button class="button button--light" type="button" data-view="tasks">Mở danh sách việc <span>→</span></button>
                <button class="button button--ghost-light" type="button" data-action="Chế độ tập trung sẽ được nối với preference backend sau.">Bắt đầu tập trung</button>
              </div>
            </div>
            <div class="focus-score">
              <div class="progress-ring" id="progress-ring" style="--progress: 72"><strong id="progress-value">72%</strong></div>
              <div class="focus-score__copy">
                <small>Nhịp tuần này</small>
                <strong>Đang đi đúng hướng</strong>
                <span>18/25 việc đã hoàn thành</span>
              </div>
            </div>
          </section>

          <section class="metric-row" aria-label="Tổng quan chỉ số">
            <article class="metric-card">
              <div class="metric-card__head"><span>Công việc đang mở</span><span class="metric-card__icon">✓</span></div>
              <strong class="metric-card__value">06</strong>
              <div class="metric-card__foot"><strong>2 ưu tiên</strong><span>trong hôm nay</span></div>
            </article>
            <article class="metric-card metric-card--coral">
              <div class="metric-card__head"><span>Chờ bạn phê duyệt</span><span class="metric-card__icon">⌁</span></div>
              <strong class="metric-card__value">03</strong>
              <div class="metric-card__foot"><strong>1 mới</strong><span>trong 2 giờ qua</span></div>
            </article>
            <article class="metric-card metric-card--gold">
              <div class="metric-card__head"><span>Sao ghi nhận</span><span class="metric-card__icon">◇</span></div>
              <strong class="metric-card__value">248</strong>
              <div class="metric-card__foot"><strong>+32</strong><span>trong tháng này</span></div>
            </article>
            <article class="metric-card metric-card--blue">
              <div class="metric-card__head"><span>Ngày phép còn lại</span><span class="metric-card__icon">☼</span></div>
              <strong class="metric-card__value">08</strong>
              <div class="metric-card__foot"><span>Cập nhật theo kỳ công</span></div>
            </article>
          </section>

          <div class="content-pair">
            <section class="panel">
              <div class="panel__head">
                <div><h2>Việc cần chú ý</h2><p>Ưu tiên theo deadline và phạm vi của bạn</p></div>
                <button class="text-link" type="button" data-view="tasks">Xem tất cả →</button>
              </div>
              <div class="panel__body panel__body--flush">
                <ul class="task-list">
                  <li class="task-item">
                    <button class="task-check" type="button" aria-label="Đánh dấu hoàn thành">✓</button>
                    <span><strong class="task-item__title">Duyệt kế hoạch nội dung tuần 36</strong><small class="task-item__meta">Marketing · Hôm nay, 10:30</small></span>
                    <span class="tag tag--coral">Ưu tiên cao</span>
                  </li>
                  <li class="task-item">
                    <button class="task-check" type="button" aria-label="Đánh dấu hoàn thành">✓</button>
                    <span><strong class="task-item__title">Chốt phạm vi Task vertical slice</strong><small class="task-item__meta">MRERP · Hôm nay, 15:00</small></span>
                    <span class="tag tag--green">Sản phẩm</span>
                  </li>
                  <li class="task-item is-done">
                    <button class="task-check" type="button" aria-label="Bỏ đánh dấu hoàn thành">✓</button>
                    <span><strong class="task-item__title">Review danh sách vị trí đang tuyển</strong><small class="task-item__meta">People · Đã hoàn thành</small></span>
                    <span class="tag tag--blue">Nhân sự</span>
                  </li>
                  <li class="task-item">
                    <button class="task-check" type="button" aria-label="Đánh dấu hoàn thành">✓</button>
                    <span><strong class="task-item__title">Phản hồi đề xuất ngân sách Q4</strong><small class="task-item__meta">Finance · Ngày mai, 09:00</small></span>
                    <span class="tag tag--gold">Phê duyệt</span>
                  </li>
                </ul>
              </div>
            </section>

            <section class="panel">
              <div class="panel__head">
                <div><h2>Nhịp kinh doanh</h2><p>Snapshot MRECRM · dữ liệu minh họa</p></div>
                <button class="text-link" type="button" data-view="crm">Mở CRM ↗</button>
              </div>
              <div class="panel__body">
                <div class="snapshot-summary">
                  <span><strong>1.284</strong><small>Đơn ghi nhận trong 7 ngày</small></span>
                  <span class="delta">↑ 12,4%</span>
                </div>
                <div class="mini-chart" aria-label="Biểu đồ đơn hàng minh họa">
                  <span style="--h: 43%"></span><span style="--h: 58%"></span><span style="--h: 48%"></span>
                  <span style="--h: 70%"></span><span style="--h: 66%"></span><span style="--h: 83%"></span><span style="--h: 76%"></span>
                </div>
                <div class="freshness"><span class="freshness__dot"></span>Snapshot cập nhật 7 phút trước · Không gọi CRM khi tải trang</div>
              </div>
            </section>
          </div>
        </div>

        <aside class="dashboard-rail" aria-label="Thông tin bổ sung">
          <section class="panel">
            <div class="panel__head"><div><h3>Lịch hôm nay</h3><p>3 điểm chạm tiếp theo</p></div><button class="text-link" type="button" data-view="calendar">Mở lịch</button></div>
            <div class="panel__body">
              <ul class="agenda-list">
                <li class="agenda-item"><span class="agenda-item__time">09:30</span><span class="agenda-item__copy"><strong>Product weekly</strong><span>Phòng họp Olive · 45 phút</span></span></li>
                <li class="agenda-item"><span class="agenda-item__time">13:30</span><span class="agenda-item__copy"><strong>Review chiến dịch 9.9</strong><span>Google Meet · Marketing</span></span></li>
                <li class="agenda-item"><span class="agenda-item__time">16:00</span><span class="agenda-item__copy"><strong>1:1 cùng Leader People</strong><span>Focus room · 30 phút</span></span></li>
              </ul>
            </div>
          </section>

          <section class="panel">
            <div class="panel__head"><div><h3>Chờ phê duyệt</h3><p>Chỉ hiển thị đúng scope minh họa</p></div><span class="tag tag--coral">3 yêu cầu</span></div>
            <div class="panel__body">
              <ul class="approval-list">
                <li class="approval-item"><span class="avatar avatar--coral">NT</span><span><strong>Nguyễn Thảo</strong><small>Nghỉ phép · 02/09</small></span><button class="text-link" type="button" data-action="Đã mở bản xem trước yêu cầu nghỉ phép.">Xem</button></li>
                <li class="approval-item"><span class="avatar avatar--blue">PM</span><span><strong>Phạm Minh</strong><small>Ngân sách Ads · 24 triệu</small></span><button class="text-link" type="button" data-action="Đã mở bản xem trước yêu cầu ngân sách.">Xem</button></li>
                <li class="approval-item"><span class="avatar avatar--violet">AL</span><span><strong>Anh Lê</strong><small>Mua thiết bị · Màn hình</small></span><button class="text-link" type="button" data-action="Đã mở bản xem trước yêu cầu thiết bị.">Xem</button></li>
              </ul>
            </div>
          </section>

          <section class="panel">
            <div class="panel__head"><div><h3>Tạo nhanh</h3><p>Bắt đầu một luồng mới</p></div></div>
            <div class="panel__body">
              <div class="quick-actions">
                <button class="quick-action" type="button" data-create-shortcut="Công việc"><span>✓</span><strong>Giao việc</strong></button>
                <button class="quick-action" type="button" data-create-shortcut="Đơn nghỉ"><span>☼</span><strong>Xin nghỉ</strong></button>
                <button class="quick-action" type="button" data-create-shortcut="Ghi nhận"><span>◇</span><strong>Ghi nhận</strong></button>
                <button class="quick-action" type="button" data-create-shortcut="Tài liệu"><span>▤</span><strong>Tài liệu</strong></button>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  `;
}

function progressView() {
  const completedGates = projectStatus.phase0Gates.filter((gate) => gate.done).length;
  const modulesWithPrototype = projectStatus.modules.filter((module) => module.ui.includes("prototype")).length;
  const blockedModules = projectStatus.modules.filter((module) => module.group === "blocked").length;

  return `
    <div class="page-wrap progress-page">
      ${pageHeading(
        "Project control room",
        "Tiến độ MRERP",
        "Một góc nhìn trung thực về phần đã có, phần mới chỉ là prototype và những cổng còn chặn production.",
        `Đối chiếu ${projectStatus.updatedAt}`,
      )}

      <section class="project-progress-hero" aria-labelledby="project-progress-title">
        <div class="project-progress-hero__copy">
          <span class="eyebrow">Tiến độ toàn kế hoạch</span>
          <h2 id="project-progress-title">${projectStatus.overallPercent}% <small>hoàn thiện</small></h2>
          <p>Project đang ở <strong>${projectStatus.currentPhase} — ${projectStatus.currentPhaseName}</strong>. Production application chưa được scaffold; phần nhìn thấy hiện tại là visual prototype.</p>
          <div class="progress-hero-pills">
            <span><strong>${completedGates}/${projectStatus.phase0Gates.length}</strong> cổng Phase 0 đạt</span>
            <span><strong>${projectStatus.modules.length}</strong> module lõi trong kế hoạch</span>
            <span><strong>${projectStatus.decisionSummary.open}</strong> quyết định đang mở</span>
          </div>
        </div>
        <div class="project-progress-visual">
          <div class="project-orbit" style="--project-progress:${projectStatus.overallPercent}">
            <div><strong>${projectStatus.overallPercent}%</strong><small>Toàn project</small></div>
          </div>
          <span class="project-progress-visual__caption">Không tính UI prototype là backend hoàn thành</span>
        </div>
      </section>

      <section class="method-strip">
        <span class="method-strip__icon">ƒ</span>
        <div><strong>Cách tính đang dùng</strong><p>${projectStatus.calculation.summary} <code>${projectStatus.calculation.formula}</code></p></div>
        <span class="confidence-badge">Độ tin cậy: ${projectStatus.calculation.confidence}</span>
      </section>

      <section class="progress-section" aria-labelledby="roadmap-title">
        <div class="progress-section__head"><div><span class="eyebrow">Roadmap 0–5</span><h2 id="roadmap-title">Sáu chặng của kế hoạch</h2></div><span class="progress-note">Chưa có ETA vì lịch và ngân sách chưa được chốt</span></div>
        <div class="phase-track">
          ${projectStatus.phases.map((phase, index) => `
            <article class="phase-step phase-step--${phase.tone}">
              <div class="phase-step__line"><span>${phase.id}</span></div>
              <div class="phase-step__content">
                <strong>${phase.name}</strong>
                <span>${phase.state}</span>
                <div class="slim-progress"><i style="width:${phase.percent}%"></i></div>
                <small>${phase.percent}%</small>
              </div>
              ${index < projectStatus.phases.length - 1 ? '<span class="phase-step__connector"></span>' : ""}
            </article>
          `).join("")}
        </div>
      </section>

      <div class="project-insight-grid">
        <section class="panel progress-panel">
          <div class="panel__head"><div><h2>Chất lượng nền hiện tại</h2><p>Không cộng trực tiếp các số này thành tiến độ nghiệp vụ</p></div><span class="pulse-status"><i></i> Có bằng chứng</span></div>
          <div class="panel__body quality-list">
            ${projectStatus.quality.map((item) => `
              <div class="quality-item"><div><strong>${item.label}</strong><span>${item.state}</span></div><div class="quality-meter"><i style="width:${item.value}%"></i></div><b>${item.value}%</b></div>
            `).join("")}
          </div>
        </section>

        <section class="panel progress-panel">
          <div class="panel__head"><div><h2>Cổng cần mở tiếp theo</h2><p>Hoàn thành trước khi scaffold Phase 1</p></div><span class="tag tag--gold">${projectStatus.nextGates.length} việc</span></div>
          <div class="panel__body next-gate-list">
            ${projectStatus.nextGates.map((gate, index) => `<div class="next-gate"><span>${String(index + 1).padStart(2, "0")}</span><strong>${gate}</strong></div>`).join("")}
          </div>
        </section>

        <section class="decision-card">
          <span class="eyebrow">Decision debt</span>
          <div class="decision-card__number">${projectStatus.decisionSummary.open}</div>
          <h2>quyết định đang mở</h2>
          <p>${projectStatus.decisionSummary.priorityNote}</p>
          <div class="decision-card__stats"><span><strong>${projectStatus.decisionSummary.resolved}</strong> đã giải quyết</span><span><strong>${projectStatus.decisionSummary.priority}</strong> ưu tiên gần</span></div>
          <button class="button button--ghost-light" type="button" data-action="Danh sách chuẩn nằm tại docs/decisions/open-decisions.md.">Xem nguồn quyết định</button>
        </section>
      </div>

      <section class="progress-section" aria-labelledby="module-progress-title">
        <div class="progress-section__head progress-section__head--modules">
          <div><span class="eyebrow">${projectStatus.modules.length} module MRERP Core</span><h2 id="module-progress-title">Bản đồ hoàn thiện module</h2><p>Mỗi module chỉ có tối đa 20% khi mới dừng ở yêu cầu và prototype; phần còn lại phải đến từ production slice, quyền, test và vận hành.</p></div>
          <div class="module-filters" aria-label="Lọc trạng thái module">
            <button class="is-active" type="button" data-module-filter="all">Tất cả <span>${projectStatus.modules.length}</span></button>
            <button type="button" data-module-filter="prototype">Có UI <span>${modulesWithPrototype}</span></button>
            <button type="button" data-module-filter="planned">Đã lên kế hoạch</button>
            <button type="button" data-module-filter="blocked">Đang chờ <span>${blockedModules}</span></button>
          </div>
        </div>
        <div class="module-progress-grid" id="module-progress-grid">
          ${projectStatus.modules.map((module, index) => `
            <article class="module-progress-card" data-module-group="${module.group}">
              <div class="module-progress-card__top">
                <span class="module-index">${String(index + 1).padStart(2, "0")}</span>
                <span class="tag ${module.group === "blocked" ? "tag--coral" : module.group === "prototype" ? "tag--green" : "tag--blue"}">${module.phase}</span>
              </div>
              <h3>${module.name}</h3>
              <p>${module.description}</p>
              <div class="module-status-row"><span>${module.ui}</span><span>${module.delivery}</span></div>
              <div class="module-completion"><div class="slim-progress"><i style="width:${module.percent}%"></i></div><strong>${module.percent}%</strong></div>
            </article>
          `).join("")}
        </div>
      </section>

      <section class="progress-section" aria-labelledby="ecosystem-progress-title">
        <div class="progress-section__head"><div><span class="eyebrow">Nền tảng & hệ sinh thái</span><h2 id="ecosystem-progress-title">Các luồng nằm ngoài 12 module lõi</h2></div></div>
        <div class="ecosystem-progress-list">
          ${projectStatus.ecosystem.map((item) => `
            <article><span class="ecosystem-progress-list__dot"></span><div><strong>${item.name}</strong><small>${item.blocker}</small></div><span class="tag">${item.phase}</span><b>${item.state}</b></article>
          `).join("")}
        </div>
      </section>

      <section class="evidence-footer">
        <div><span class="eyebrow">Evidence, không phải cảm tính</span><h2>Con số chỉ thay đổi khi bằng chứng thay đổi.</h2><p>${projectStatus.calculation.note}</p><div class="source-chips">${projectStatus.sources.map((source) => `<code>${source}</code>`).join("")}</div></div>
        <button class="button button--primary" id="copy-progress-snapshot" type="button">Sao chép snapshot tiến độ</button>
      </section>
    </div>
  `;
}

function tasksView() {
  const columns = [
    ["Cần làm", [
      ["Chốt acceptance criteria Dashboard", "MRERP", "Hôm nay", "tag--coral", "Ưu tiên"],
      ["Review cấu trúc dữ liệu Employee", "People", "29/08", "tag--blue", "Nền tảng"],
    ]],
    ["Đang thực hiện", [
      ["Xây visual prototype MRERP", "Design", "Hôm nay", "tag--green", "Đang làm"],
      ["Chuẩn hóa contract Identity giả lập", "Platform", "30/08", "tag--violet", "Contract"],
    ]],
    ["Chờ phản hồi", [
      ["Duyệt ma trận quyền vertical slice", "Security", "Chờ PO", "tag--gold", "Cần duyệt"],
    ]],
    ["Hoàn thành", [
      ["Tạo source of truth Phase 0", "Docs", "27/08", "tag--green", "Đã xong"],
      ["Thiết lập repository quality CI", "Platform", "27/08", "tag--blue", "Đã xong"],
    ]],
  ];

  return `
    <div class="page-wrap">
      ${pageHeading("Task module", "Công việc của tôi", "Task thuộc MRERP; Kanban ở đây là một cách nhìn trên cùng nguồn dữ liệu minh họa.")}
      <div class="section-toolbar">
        <div class="segmented-control" aria-label="Kiểu hiển thị">
          <button type="button" data-action="List view sẽ dùng cùng nguồn Task.">Danh sách</button>
          <button class="is-active" type="button">Kanban</button>
          <button type="button" data-action="Calendar view sẽ dùng cùng nguồn Task.">Lịch</button>
        </div>
        <button class="button button--primary" type="button" data-create-shortcut="Công việc">＋ Công việc mới</button>
      </div>
      <div class="kanban-board">
        ${columns.map(([title, cards]) => `
          <section class="kanban-column">
            <div class="kanban-column__head"><strong>${title}</strong><span>${cards.length}</span></div>
            <div class="kanban-cards">
              ${cards.map(([name, module, due, tagClass, tag]) => `
                <article class="kanban-card">
                  <div class="kanban-card__tags"><span class="tag ${tagClass}">${tag}</span><span class="tag">${module}</span></div>
                  <h3>${name}</h3>
                  <p>Task UUID sẽ do MRERP backend sở hữu khi slice production được triển khai.</p>
                  <div class="kanban-card__foot"><div class="avatar-stack"><span class="avatar avatar--ha">LH</span><span class="avatar avatar--blue">PM</span></div><span>⌁ ${due}</span></div>
                </article>
              `).join("")}
            </div>
          </section>
        `).join("")}
      </div>
    </div>
  `;
}

function calendarView() {
  return `
    <div class="page-wrap">
      ${pageHeading("Lịch & Phê duyệt", "Những việc cần quyết định", "Lịch cá nhân và các yêu cầu trong đúng phạm vi được giao sẽ hội tụ tại đây.")}
      <div class="content-pair">
        <section class="panel">
          <div class="panel__head"><div><h2>Tuần 31/08 — 06/09</h2><p>Lịch minh họa theo múi giờ Asia/Bangkok</p></div><div class="segmented-control"><button type="button">Ngày</button><button class="is-active" type="button">Tuần</button></div></div>
          <div class="panel__body">
            <div class="agenda-list">
              <div class="agenda-item"><span class="agenda-item__time">Thứ hai</span><span class="agenda-item__copy"><strong>09:30 · Product weekly</strong><span>Review roadmap và các open decision chặn Phase 1</span></span></div>
              <div class="agenda-item"><span class="agenda-item__time">Thứ ba</span><span class="agenda-item__copy"><strong>14:00 · People sync</strong><span>Rà soát cơ cấu nhân sự và capability</span></span></div>
              <div class="agenda-item"><span class="agenda-item__time">Thứ tư</span><span class="agenda-item__copy"><strong>10:00 · CRM operations</strong><span>Snapshot freshness và backlog tích hợp</span></span></div>
              <div class="agenda-item"><span class="agenda-item__time">Thứ sáu</span><span class="agenda-item__copy"><strong>16:30 · Weekly wrap-up</strong><span>Tổng kết Task và ghi nhận đồng đội</span></span></div>
            </div>
          </div>
        </section>
        <section class="panel">
          <div class="panel__head"><div><h2>Hàng chờ phê duyệt</h2><p>Policy và scope chỉ là minh họa UI</p></div><span class="tag tag--coral">3 đang chờ</span></div>
          <div class="panel__body">
            <ul class="approval-list">
              <li class="approval-item"><span class="avatar avatar--coral">NT</span><span><strong>Đơn nghỉ phép</strong><small>Nguyễn Thảo · 1 ngày</small></span><button class="button button--quiet" data-action="Prototype chưa thực hiện quyết định phê duyệt thật.">Mở</button></li>
              <li class="approval-item"><span class="avatar avatar--blue">PM</span><span><strong>Ngân sách chiến dịch</strong><small>Phạm Minh · 24 triệu</small></span><button class="button button--quiet" data-action="Prototype chưa thực hiện quyết định phê duyệt thật.">Mở</button></li>
              <li class="approval-item"><span class="avatar avatar--violet">AL</span><span><strong>Yêu cầu thiết bị</strong><small>Anh Lê · Màn hình</small></span><button class="button button--quiet" data-action="Prototype chưa thực hiện quyết định phê duyệt thật.">Mở</button></li>
            </ul>
            <div class="restricted-strip"><strong>!</strong><span>Backend production phải kiểm tra account, capability, scope, object rule và field policy trước khi trả dữ liệu hoặc nhận quyết định.</span></div>
          </div>
        </section>
      </div>
    </div>
  `;
}

function peopleView() {
  return `
    <div class="page-wrap">
      ${pageHeading("People / HR", "Nhân sự MRE", "MRERP là nguồn dữ liệu chuẩn về hồ sơ làm việc, team và trạng thái nhân sự.")}
      <div class="section-toolbar">
        <div class="segmented-control"><button class="is-active" type="button">Danh bạ</button><button type="button" data-action="Organization view đang là màn hình minh họa tiếp theo.">Sơ đồ tổ chức</button><button type="button" data-action="Team view đang là màn hình minh họa tiếp theo.">Team</button></div>
        <button class="button button--primary" type="button" data-action="Tạo nhân sự cần contract và quyền Admin đã được duyệt.">＋ Thêm nhân sự</button>
      </div>
      <section class="panel table-panel">
        <table class="data-table">
          <thead><tr><th>Nhân sự</th><th>Phòng ban</th><th>Cấp bậc</th><th>Trạng thái</th><th></th></tr></thead>
          <tbody>
            ${mockPeople.map(([initials, name, title, department, level, status, avatarClass]) => `
              <tr>
                <td><span class="person-cell"><span class="avatar ${avatarClass}">${initials}</span><span><strong>${name}</strong><small>${title}</small></span></span></td>
                <td>${department}</td><td>${level}</td>
                <td><span class="tag ${status === "Đang làm việc" ? "tag--green" : status === "Thử việc" ? "tag--gold" : "tag--blue"}">${status}</span></td>
                <td><button class="text-link" type="button" data-action="Hồ sơ ${name} đang dùng dữ liệu mô phỏng.">Xem →</button></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </section>
      <div class="restricted-strip"><strong>i</strong><span>Tên, cơ cấu và cấp bậc trong bảng chỉ là dữ liệu thiết kế. Danh sách chính thức vẫn thuộc OD-16 và không được suy ra từ prototype.</span></div>
    </div>
  `;
}

function recruitmentView() {
  const stages = [
    ["Ứng viên mới", [["Hà My", "Product Designer", "Hôm nay"], ["Minh Tú", "Backend Engineer", "Hôm qua"]]],
    ["Sàng lọc", [["Quỳnh Anh", "HR Executive", "CV đạt"], ["Tuấn Kiệt", "Performance Ads", "Chờ bài test"]]],
    ["Phỏng vấn", [["Bảo Trân", "Content Lead", "02/09 · 10:00"]]],
    ["Đề nghị", [["Hữu Phước", "Sales Executive", "Chờ phản hồi"]]],
  ];

  return `
    <div class="page-wrap">
      ${pageHeading("Recruitment", "Tuyển đúng người, theo đúng nhịp", "Tuyển dụng nằm gần miền Nhân sự trên điều hướng nhưng có workflow và dữ liệu riêng.")}
      <div class="section-toolbar"><div class="segmented-control"><button class="is-active">Pipeline</button><button data-action="Danh sách vị trí sẽ được triển khai theo contract riêng.">Vị trí tuyển</button></div><button class="button button--primary" data-action="Tạo yêu cầu tuyển là luồng backend tương lai.">＋ Yêu cầu tuyển</button></div>
      <div class="pipeline">
        ${stages.map(([stage, candidates]) => `
          <section class="pipeline-stage">
            <div class="pipeline-stage__head"><strong>${stage}</strong><span class="tag">${candidates.length}</span></div>
            ${candidates.map(([name, role, note], index) => `
              <article class="candidate-card">
                <span class="person-cell"><span class="avatar ${index % 2 ? "avatar--blue" : "avatar--coral"}">${name.split(" ").map((part) => part[0]).slice(-2).join("")}</span><span><strong>${name}</strong><small>${role}</small></span></span>
                <div class="candidate-card__foot"><span class="tag tag--violet">${note}</span><button class="text-link" data-action="Hồ sơ ứng viên đang là dữ liệu mô phỏng.">Mở</button></div>
              </article>
            `).join("")}
          </section>
        `).join("")}
      </div>
    </div>
  `;
}

function rewardsView() {
  return `
    <div class="page-wrap">
      ${pageHeading("Recognition & Rewards", "Điều tốt cần được nhìn thấy", "Ghi nhận đóng góp kịp thời và nuôi dưỡng những giá trị MRE muốn giữ lâu dài.")}
      <section class="reward-hero">
        <div><span class="eyebrow" style="color:#f2cf7b">Số dư của bạn</span><h2>248 sao ghi nhận</h2><p>Bạn nhận thêm 32 sao trong tháng này. Công thức và catalog đổi thưởng vẫn cần policy được duyệt trước khi triển khai production.</p><button class="button button--light" data-action="Catalog phần thưởng chưa được chốt.">Khám phá phần thưởng</button></div>
        <div class="star-balance"><span>◇</span><strong>248</strong><small>MRE Stars</small></div>
      </section>
      <div class="content-pair" style="margin-top:20px">
        <section class="panel"><div class="panel__head"><div><h2>Ghi nhận gần đây</h2><p>Dòng chảy tích cực trong công ty</p></div><button class="text-link" data-create-shortcut="Ghi nhận">Gửi ghi nhận ＋</button></div><div class="panel__body"><ul class="approval-list"><li class="approval-item"><span class="avatar avatar--blue">PM</span><span><strong>Phạm Minh ghi nhận Nguyễn Thảo</strong><small>“Luôn chủ động tháo gỡ vướng mắc cho team.”</small></span><span class="tag tag--gold">+12 ◇</span></li><li class="approval-item"><span class="avatar avatar--coral">NT</span><span><strong>Nguyễn Thảo ghi nhận Anh Lê</strong><small>“Chuyển insight thành thiết kế rất rõ ràng.”</small></span><span class="tag tag--gold">+8 ◇</span></li></ul></div></section>
        <section class="panel"><div class="panel__head"><div><h2>Giá trị nổi bật</h2><p>Dữ liệu văn hóa minh họa</p></div></div><div class="panel__body"><div class="quick-actions"><div class="quick-action"><span>↗</span><strong>Chủ động</strong></div><div class="quick-action"><span>◎</span><strong>Đồng đội</strong></div><div class="quick-action"><span>◇</span><strong>Tử tế</strong></div><div class="quick-action"><span>≈</span><strong>Hiệu quả</strong></div></div></div></section>
      </div>
    </div>
  `;
}

function documentsView() {
  const docs = [
    ["Quy trình onboarding", "People", "Cập nhật 2 ngày trước", "▤"],
    ["Brand guideline MRE", "Marketing", "Cập nhật 12/08", "Aa"],
    ["Chính sách nội bộ", "Company", "Cập nhật 05/08", "§"],
    ["Playbook vận hành CRM", "Operations", "Cập nhật 01/08", "⌁"],
    ["Mẫu đề xuất dự án", "Product", "Cập nhật 28/07", "□"],
    ["Hướng dẫn bảo mật", "Security", "Cập nhật 20/07", "◇"],
  ];
  return `
    <div class="page-wrap">
      ${pageHeading("Knowledge base", "Tài liệu nội bộ", "Tìm đúng tài liệu, hiểu đúng phiên bản và chỉ truy cập nội dung bạn được phép xem.")}
      <div class="section-toolbar"><div class="segmented-control"><button class="is-active">Tất cả</button><button data-action="Bộ lọc của tôi đang là tương tác minh họa.">Của tôi</button><button data-action="Bộ lọc đã lưu đang là tương tác minh họa.">Đã lưu</button></div><button class="button button--primary" data-create-shortcut="Tài liệu">＋ Tài liệu mới</button></div>
      <div class="document-grid">
        ${docs.map(([name, category, updated, icon]) => `<article class="document-card"><span class="document-card__icon">${icon}</span><strong>${name}</strong><small>${category}</small><div class="document-card__foot"><span>${updated}</span><button class="text-link" data-action="Đã mở bản xem trước ${name}.">Mở</button></div></article>`).join("")}
      </div>
    </div>
  `;
}

function productBoundaryView(product) {
  const isAsset = product === "asset";
  const name = isAsset ? "ASSETCONTROL" : "MRECRM";
  const description = isAsset
    ? "Quản lý Resource, Grant, Vault và audit tài nguyên trong product có ranh giới riêng."
    : "Vận hành Customer, Product, Order, Channel, đối soát và báo cáo trong deployable riêng.";
  const access = isAsset
    ? "Hiện chỉ CEO và Leader được cấp quyền; đối tượng khác chưa quyết định."
    : "Quyền và field payload sẽ do server CRM kiểm tra theo capability, scope và field policy.";
  return `
    <div class="page-wrap">
      ${pageHeading("Sản phẩm kết nối", name, "MRERP là điểm vào chung, không phải nơi sao chép toàn bộ dữ liệu và code của product đích.")}
      <section class="product-boundary ${isAsset ? "product-boundary--asset" : ""}">
        <div><div class="product-boundary__mark">${isAsset ? "A" : "C"}</div><h2>${name}</h2><p>${description}</p><button class="button button--primary" data-action="SSO và deep link production chưa được nối trong prototype.">Mở ${name} ↗</button></div>
        <div class="boundary-list">
          <div class="boundary-item"><span>✓</span><div><strong>SSO dùng chung</strong><br />Không nhập lại mật khẩu khi đã có quyền.</div></div>
          <div class="boundary-item"><span>✓</span><div><strong>Data ownership riêng</strong><br />Không đọc trực tiếp database của nhau.</div></div>
          <div class="boundary-item"><span>✓</span><div><strong>Server tự kiểm quyền</strong><br />${access}</div></div>
          <div class="boundary-item"><span>i</span><div><strong>Trạng thái prototype</strong><br />Nút mở product chưa phải tích hợp production.</div></div>
        </div>
      </section>
    </div>
  `;
}

function adminView() {
  const cards = [
    ["◎", "Tài khoản & nhân sự", "Provisioning, trạng thái làm việc và liên kết Identity."],
    ["⌘", "Cơ cấu tổ chức", "Phòng ban, team và quan hệ quản lý theo dữ liệu cấu hình."],
    ["◇", "Capability & scope", "Quyền thao tác và phạm vi dữ liệu được kiểm tra ở server."],
    ["⚑", "Feature flags", "Mở module có kiểm soát theo môi trường và nhóm người dùng."],
    ["▤", "Audit trail", "Theo dõi hành động nhạy cảm và thay đổi cấu hình."],
    ["⌁", "Integration health", "Freshness, queue và trạng thái kết nối các product."],
  ];
  return `
    <div class="page-wrap">
      ${pageHeading("Quản trị trung tâm", "Admin Panel", "Bề mặt quản trị account, employee và access cấp cao; không thay thế giao diện vận hành riêng của từng product.")}
      <div class="admin-grid">${cards.map(([icon, title, copy]) => `<article class="admin-card"><div class="admin-card__top"><span class="admin-card__icon">${icon}</span><span class="tag tag--green">Preview</span></div><h3>${title}</h3><p>${copy}</p></article>`).join("")}</div>
      <div class="restricted-strip"><strong>!</strong><span>Ai được vào Admin Panel, ranh giới thao tác với Identity Provider và capability chính thức vẫn là quyết định cần duyệt. Prototype không cấp quyền thật.</span></div>
    </div>
  `;
}

function simpleStateView(view) {
  const map = {
    profile: ["Hồ sơ cá nhân", "Thông tin của bạn sẽ nằm ở đây", "Backend chỉ trả các field hồ sơ phù hợp với chủ thể và capability."],
    settings: ["Cài đặt", "Tùy chỉnh trải nghiệm làm việc", "Theme có thể lưu cục bộ; notification và security preference sẽ cần backend contract."],
  };
  const [eyebrow, title, copy] = map[view] || ["Prototype", "Màn hình đang được định hình", "Nội dung sẽ được bổ sung theo vertical slice đã duyệt."];
  return `<div class="page-wrap">${pageHeading(eyebrow, title, copy)}<section class="state-card"><div><div class="state-card__visual">◎</div><h2>Khung trải nghiệm đã sẵn sàng</h2><p>${copy} Màn hình này chưa kết nối dữ liệu production.</p><button class="button button--primary" data-view="dashboard">Về Tổng quan</button></div></section></div>`;
}

function searchView(query) {
  const safeQuery = escapeHtml(query);
  return `
    <div class="page-wrap">
      ${pageHeading("Tìm kiếm toàn hệ thống", `Kết quả cho “${safeQuery}”`, "Kết quả hiện tại là dữ liệu mô phỏng; production phải lọc kết quả theo quyền ở server.")}
      <section class="state-card"><div><div class="state-card__visual">⌕</div><h2>Đã tìm thấy 3 kết quả minh họa</h2><p>Một công việc, một nhân sự và một tài liệu có chứa từ khóa “${safeQuery}”. API tìm kiếm thật chưa được triển khai.</p><button class="button button--primary" data-view="dashboard">Quay lại Tổng quan</button></div></section>
    </div>
  `;
}

const viewFactories = {
  dashboard: dashboardView,
  progress: progressView,
  tasks: tasksView,
  calendar: calendarView,
  people: peopleView,
  recruitment: recruitmentView,
  rewards: rewardsView,
  documents: documentsView,
  crm: () => productBoundaryView("crm"),
  asset: () => productBoundaryView("asset"),
  admin: adminView,
  profile: () => simpleStateView("profile"),
  settings: () => simpleStateView("settings"),
};

function renderView(view, options = {}) {
  const factory = viewFactories[view] || (() => simpleStateView(view));
  currentView = view;
  pageContent.innerHTML = factory();
  navItems.forEach((item) => item.classList.toggle("is-active", item.dataset.view === view));
  closeSidebar();
  profilePopover.hidden = true;
  pageContent.scrollTop = 0;
  if (options.focus) pageContent.focus({ preventScroll: true });
}

function closeSidebar() {
  sidebar.classList.remove("is-open");
  sidebarBackdrop.classList.remove("is-visible");
}

function updateTaskProgress() {
  const tasks = [...pageContent.querySelectorAll(".task-item")];
  if (!tasks.length) return;
  const completed = tasks.filter((task) => task.classList.contains("is-done")).length;
  const percentage = Math.round((completed / tasks.length) * 100);
  const ring = pageContent.querySelector("#progress-ring");
  const value = pageContent.querySelector("#progress-value");
  if (ring && value) {
    const weeklyPercentage = Math.min(100, 60 + percentage / 2);
    ring.style.setProperty("--progress", weeklyPercentage);
    value.textContent = `${Math.round(weeklyPercentage)}%`;
  }
}

document.addEventListener("click", (event) => {
  const moduleFilter = event.target.closest("[data-module-filter]");
  if (moduleFilter) {
    const filter = moduleFilter.dataset.moduleFilter;
    document.querySelectorAll("[data-module-filter]").forEach((button) => button.classList.toggle("is-active", button === moduleFilter));
    document.querySelectorAll("[data-module-group]").forEach((card) => {
      card.hidden = filter !== "all" && card.dataset.moduleGroup !== filter;
    });
    return;
  }

  const copyProgressButton = event.target.closest("#copy-progress-snapshot");
  if (copyProgressButton) {
    const snapshot = [
      `MRERP — ${projectStatus.overallPercent}% toàn kế hoạch`,
      `${projectStatus.currentPhase}: ${projectStatus.phase0Gates.filter((gate) => gate.done).length}/${projectStatus.phase0Gates.length} cổng đạt`,
      `${projectStatus.modules.length} module lõi · ${projectStatus.decisionSummary.open} quyết định đang mở`,
      `Đối chiếu: ${projectStatus.updatedAt}`,
    ].join("\n");
    if (!navigator.clipboard) {
      showToast("Không thể sao chép tự động; trình duyệt đang chặn clipboard.");
      return;
    }
    navigator.clipboard.writeText(snapshot)
      .then(() => showToast("Đã sao chép snapshot tiến độ."))
      .catch(() => showToast("Không thể sao chép tự động; trình duyệt đang chặn clipboard."));
    return;
  }

  const viewButton = event.target.closest("[data-view]");
  if (viewButton) {
    event.preventDefault();
    renderView(viewButton.dataset.view, { focus: true });
    return;
  }

  const actionButton = event.target.closest("[data-action]");
  if (actionButton) {
    showToast(actionButton.dataset.action);
    return;
  }

  const shortcut = event.target.closest("[data-create-shortcut]");
  if (shortcut) {
    showToast(`${shortcut.dataset.createShortcut}: luồng tạo mới đang ở chế độ prototype.`);
    return;
  }

  const taskCheck = event.target.closest(".task-check");
  if (taskCheck) {
    const task = taskCheck.closest(".task-item");
    task.classList.toggle("is-done");
    taskCheck.setAttribute("aria-label", task.classList.contains("is-done") ? "Bỏ đánh dấu hoàn thành" : "Đánh dấu hoàn thành");
    updateTaskProgress();
    showToast(task.classList.contains("is-done") ? "Đã đánh dấu hoàn thành trong prototype." : "Đã mở lại công việc trong prototype.");
  }
});

themeToggle.addEventListener("click", () => {
  const isDark = document.documentElement.dataset.theme === "dark";
  const nextTheme = isDark ? "light" : "dark";
  document.documentElement.dataset.theme = nextTheme;
  preferenceStorage.set("mrerp-prototype-theme", nextTheme);
  document.querySelector('meta[name="theme-color"]').setAttribute("content", nextTheme === "dark" ? "#0d1714" : "#153c31");
  showToast(nextTheme === "dark" ? "Đã chuyển sang giao diện tối." : "Đã chuyển sang giao diện sáng.");
});

createButton.addEventListener("click", () => createDialog.showModal());

createDialog.addEventListener("click", (event) => {
  const createOption = event.target.closest("[data-create]");
  if (createOption) showToast(`${createOption.dataset.create}: đây là tương tác minh họa, chưa gửi backend.`);
});

profileButton.addEventListener("click", (event) => {
  event.stopPropagation();
  profilePopover.hidden = !profilePopover.hidden;
});

document.querySelector("#notification-button").addEventListener("click", () => {
  showToast("Bạn có 3 thông báo minh họa chưa đọc.");
});

document.querySelector("#signout-demo").addEventListener("click", () => {
  profilePopover.hidden = true;
  showToast("Đăng xuất production sẽ do Identity Provider xử lý.");
});

document.addEventListener("click", (event) => {
  if (!profilePopover.contains(event.target) && !profileButton.contains(event.target)) profilePopover.hidden = true;
});

mobileMenu.addEventListener("click", () => {
  sidebar.classList.add("is-open");
  sidebarBackdrop.classList.add("is-visible");
});

sidebarBackdrop.addEventListener("click", closeSidebar);

globalSearch.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && globalSearch.value.trim()) {
    const query = globalSearch.value.trim();
    currentView = "search";
    pageContent.innerHTML = searchView(query);
    navItems.forEach((item) => item.classList.remove("is-active"));
    pageContent.focus({ preventScroll: true });
  }
});

document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    globalSearch.focus();
  }
  if (event.key === "Escape") {
    closeSidebar();
    profilePopover.hidden = true;
  }
});

const savedTheme = preferenceStorage.get("mrerp-prototype-theme");
if (savedTheme === "dark" || savedTheme === "light") document.documentElement.dataset.theme = savedTheme;

const progressNavBadge = document.querySelector("#progress-nav-badge");
if (progressNavBadge) progressNavBadge.textContent = `${projectStatus.overallPercent}%`;

renderView(currentView);
