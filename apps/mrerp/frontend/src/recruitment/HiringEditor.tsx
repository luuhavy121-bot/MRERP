import { useState } from "react";
import { api, request } from "../api";
import type { HiringRequest } from "../types";

const empty = {
  title: "",
  headcount: 1,
  justification: "",
  utilization_plan: "",
  location: "",
  employment_type: "",
  description: "",
  requirements: "",
  benefits: "",
  deadline: "",
};
export function HiringEditor({
  teams,
  item,
  done,
  cancel,
}: {
  teams: Array<{ uuid: string; name: string }>;
  item: HiringRequest | null;
  done: () => Promise<void>;
  cancel: () => void;
}) {
  const [form, setForm] = useState(
    item ? { ...empty, ...item, deadline: item.deadline ?? "" } : empty,
  );
  const [team, setTeam] = useState(item?.team ?? teams[0]?.uuid ?? "");
  const [id, setId] = useState(item?.uuid ?? "");
  const [preview, setPreview] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function save(submit: boolean) {
    setBusy(true);
    setError("");
    try {
      const uuid =
        id ||
        (
          await api.createRecruitmentRequest({
            team_uuid: team,
            title: form.title,
            headcount: form.headcount,
            justification: form.justification,
            utilization_plan: form.utilization_plan,
          })
        ).uuid;
      setId(uuid);
      await request(`/api/v1/recruitment/requests/${uuid}/`, {
        method: "PATCH",
        body: JSON.stringify({ ...form, deadline: form.deadline || null }),
      });
      if (submit)
        await request(`/api/v1/recruitment/requests/${uuid}/submit/`, {
          method: "POST",
        });
      await done();
      cancel();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Không lưu được yêu cầu.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      className="phase3-form hiring-editor"
      onSubmit={(e) => {
        e.preventDefault();
        void save(true);
      }}
    >
      <h3>{item ? "Sửa bản nháp" : "Tạo yêu cầu tuyển"}</h3>
      {error && (
        <div className="alert alert--error" role="alert">
          {error}
        </div>
      )}
      <label>
        Team
        <select
          required
          disabled={!!id}
          value={team}
          onChange={(e) => setTeam(e.target.value)}
        >
          {teams.map((t) => (
            <option key={t.uuid} value={t.uuid}>
              {t.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Vị trí
        <input
          required
          maxLength={160}
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />
      </label>
      <label>
        Số lượng
        <input
          type="number"
          min="1"
          max="100"
          required
          value={form.headcount}
          onChange={(e) =>
            setForm({ ...form, headcount: Number(e.target.value) })
          }
        />
      </label>
      <label>
        Lý do nội bộ
        <textarea
          required
          maxLength={3000}
          value={form.justification}
          onChange={(e) => setForm({ ...form, justification: e.target.value })}
        />
      </label>
      <label>
        Kế hoạch sử dụng nhân sự (nội bộ)
        <textarea
          aria-label="Kế hoạch sử dụng nhân sự (nội bộ)"
          maxLength={3000}
          placeholder="Nhân sự sẽ làm việc gì, phụ trách phần nào và mục tiêu dự kiến?"
          value={form.utilization_plan}
          onChange={(e) => setForm({ ...form, utilization_plan: e.target.value })}
        />
      </label>
      <p className="muted">
        Các nội dung bên dưới sẽ xuất hiện trên trang tuyển dụng sau khi HR
        duyệt.
      </p>
      <label>
        Địa điểm
        <input
          value={form.location}
          maxLength={240}
          onChange={(e) => setForm({ ...form, location: e.target.value })}
        />
      </label>
      <label>
        Hình thức làm việc
        <input
          value={form.employment_type}
          maxLength={120}
          placeholder="Ví dụ: Toàn thời gian"
          onChange={(e) =>
            setForm({ ...form, employment_type: e.target.value })
          }
        />
      </label>
      {(["description", "requirements", "benefits"] as const).map((key, i) => (
        <label key={key}>
          {["Mô tả công việc", "Yêu cầu ứng viên", "Quyền lợi"][i]}
          <textarea
            maxLength={10000}
            value={form[key]}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
          />
        </label>
      ))}
      <label>
        Hạn nhận hồ sơ
        <input
          type="date"
          value={form.deadline}
          onChange={(e) => setForm({ ...form, deadline: e.target.value })}
        />
      </label>
      <button type="button" className="secondary-button" aria-expanded={preview} onClick={()=>setPreview(!preview)}>Xem trước tin tuyển</button>
      {preview&&<section className="panel hiring-preview" aria-label="Xem trước tin tuyển"><h3>{form.title||'Chưa nhập vị trí'}</h3><p>{form.location} · {form.employment_type} · {form.headcount} người</p><p>Hạn nhận: {form.deadline||'Chưa đặt'}</p>{(['description','requirements','benefits'] as const).map((key,i)=><div key={key}><h4>{['Mô tả công việc','Yêu cầu ứng viên','Quyền lợi'][i]}</h4><p className="preserve-lines">{form[key]||'Chưa nhập nội dung'}</p></div>)}<p>Đây là bản xem trước; chưa xuất bản. Lý do tuyển nội bộ không hiển thị.</p></section>}
      <div className="row-actions">
        <button
          type="button"
          className="secondary-button"
          disabled={busy}
          onClick={() => void save(false)}
        >
          Lưu nháp
        </button>
        <button className="primary-button" disabled={busy}>
          Gửi duyệt
        </button>
        <button
          type="button"
          className="secondary-button"
          disabled={busy}
          onClick={cancel}
        >
          Đóng
        </button>
      </div>
    </form>
  );
}
