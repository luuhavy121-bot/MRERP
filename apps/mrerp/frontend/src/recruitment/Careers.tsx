import { useEffect, useState } from "react";
import { request } from "../api";
import type { Page } from "../types";
import "../hr-expansion.css";

type Opening = {
  slug: string;
  title: string;
  team_name: string;
  location: string;
  employment_type: string;
  description: string;
  requirements: string;
  benefits: string;
  deadline: string;
  headcount: number;
};
export function Careers() {
  const slug = window.location.pathname.split("/").filter(Boolean)[1];
  const [jobs, setJobs] = useState<Opening[]>([]);
  const [job, setJob] = useState<Opening | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [next, setNext] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    const go = async () => {
      try {
        if (slug) {
          const j = await request<Opening>(
            `/api/v1/public/recruitment/openings/${encodeURIComponent(slug)}/`,
          );
          if (live) setJob(j);
        } else {
          const p = await request<Page<Opening>>(
            "/api/v1/public/recruitment/openings/",
          );
          if (live) {
            setJobs(p.results);
            setNext(p.next);
          }
        }
      } catch (e) {
        if (live)
          setError(e instanceof Error ? e.message : "Không tải được tin.");
      } finally {
        if (live) setLoading(false);
      }
    };
    void go();
    return () => {
      live = false;
    };
  }, [slug]);
  async function apply(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const cv = form.get("cv") as File;
    if (!form.get("email") && !form.get("phone")) {
      setError("Vui lòng nhập email hoặc số điện thoại.");
      return;
    }
    if (cv.size > 10 * 1024 * 1024) {
      setError("CV tối đa 10 MB.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await request(
        `/api/v1/public/recruitment/openings/${encodeURIComponent(slug)}/applications/`,
        { method: "POST", body: form },
      );
      setSent(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Không gửi được hồ sơ.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="careers">
      <header className="careers-header">
        <a href="/careers">
          <img src="/brand/mr-ecom-logo.png" alt="MR ECOM" />
        </a>
        <a href="/">Đăng nhập nội bộ</a>
      </header>
      {error && (
        <div role="alert" className="alert alert--error">
          {error}
        </div>
      )}
      {loading ? (
        <p role="status">Đang tải tin tuyển dụng…</p>
      ) : !slug ? (
        <>
          <h1>Cơ hội tại MR ECOM</h1>
          <p>
            Tìm vị trí phù hợp và gửi hồ sơ trực tiếp cho đội ngũ tuyển dụng.
          </p>
          <section className="careers-list">
            {jobs.length === 0 && (
              <p>
                Hiện chưa có vị trí đang nhận hồ sơ. Bạn có thể quay lại sau.
              </p>
            )}
            {jobs.map((j) => (
              <a
                key={j.slug}
                className="career-row"
                href={`/careers/${j.slug}`}
              >
                <div>
                  <h2>{j.title}</h2>
                  <p>
                    {j.team_name} · {j.location} · {j.employment_type}
                  </p>
                </div>
                <span>Nhận hồ sơ đến {j.deadline}</span>
              </a>
            ))}
          </section>
          {next && (
            <button
              className="secondary-button"
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                try {
                  const u = new URL(next, location.origin);
                  const p = await request<Page<Opening>>(u.pathname + u.search);
                  setJobs([...jobs, ...p.results]);
                  setNext(p.next);
                } catch {
                  setError("Không tải được trang tiếp theo.");
                } finally {
                  setBusy(false);
                }
              }}
            >
              Xem thêm vị trí
            </button>
          )}
        </>
      ) : job ? (
        <>
          <a href="/careers">Tất cả vị trí</a>
          <h1>{job.title}</h1>
          <p>
            {job.location} · {job.employment_type} · {job.headcount} vị trí ·
            Hạn {job.deadline}
          </p>
          <div className="career-detail">
            <article>
              {(["description", "requirements", "benefits"] as const).map(
                (key, i) => (
                  <section key={key}>
                    <h2>
                      {["Mô tả công việc", "Yêu cầu ứng viên", "Quyền lợi"][i]}
                    </h2>
                    <p className="preserve-lines">{job[key]}</p>
                  </section>
                ),
              )}
            </article>
            <section className="career-apply">
              {sent ? (
                <div role="status">
                  <h2>Đã nhận hồ sơ</h2>
                  <p>
                    Cảm ơn bạn đã ứng tuyển. Công ty sẽ liên hệ qua thông tin
                    bạn cung cấp.
                  </p>
                </div>
              ) : (
                <form className="phase3-form" onSubmit={apply}>
                  <h2>Ứng tuyển vị trí này</h2>
                  <label>
                    Họ tên
                    <input
                      name="full_name"
                      required
                      maxLength={160}
                      autoComplete="name"
                    />
                  </label>
                  <p>Cung cấp ít nhất email hoặc số điện thoại.</p>
                  <label>
                    Email
                    <input name="email" type="email" autoComplete="email" />
                  </label>
                  <label>
                    Số điện thoại
                    <input
                      name="phone"
                      type="tel"
                      maxLength={32}
                      autoComplete="tel"
                    />
                  </label>
                  <label>
                    Giới thiệu ngắn
                    <textarea name="introduction" maxLength={3000} />
                  </label>
                  <label>
                    CV (PDF, DOC, DOCX; tối đa 10 MB)
                    <input
                      name="cv"
                      type="file"
                      accept=".pdf,.doc,.docx"
                      required
                    />
                  </label>
                  <label className="inline-check">
                    <input
                      type="checkbox"
                      name="consent"
                      value="true"
                      required
                    />
                    Tôi đồng ý lưu thông tin và CV để xử lý hồ sơ tuyển dụng. Hồ
                    sơ bị từ chối sẽ được ẩn danh sau sáu tháng.
                  </label>
                  <div aria-live="polite">
                    {error && (
                      <p role="alert" className="alert alert--error">
                        {error}
                      </p>
                    )}
                  </div>
                  <button className="primary-button" disabled={busy}>
                    {busy ? "Đang gửi…" : "Gửi hồ sơ"}
                  </button>
                </form>
              )}
            </section>
          </div>
        </>
      ) : (
        <p>
          Tin không còn nhận hồ sơ. <a href="/careers">Xem vị trí khác</a>
        </p>
      )}
    </main>
  );
}
