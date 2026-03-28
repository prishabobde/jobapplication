import { useEffect, useMemo, useState } from "react";
import { apiDownloadResume, apiGet, apiGetMaybe, apiPostTrigger, apiUploadResume } from "../api.js";

export default function JobBoard({ jobs, role, token }) {
  const [selectedId, setSelectedId] = useState(jobs[0]?.id ?? null);

  useEffect(() => {
    if (jobs.length === 0) return;
    if (selectedId == null || !jobs.some((j) => j.id === selectedId)) {
      setSelectedId(jobs[0].id);
    }
  }, [jobs, selectedId]);

  const selected = useMemo(
    () => jobs.find((j) => j.id === selectedId) ?? null,
    [jobs, selectedId]
  );

  const isHr = role === "hr";

  const [applicants, setApplicants] = useState([]);
  const [applicantsError, setApplicantsError] = useState("");
  const [applicantsLoading, setApplicantsLoading] = useState(false);

  const [myApp, setMyApp] = useState(null);
  const [myAppLoading, setMyAppLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploading, setUploading] = useState(false);

  const [summaries, setSummaries] = useState([]);
  const [topPick, setTopPick] = useState(null);
  const [summaryModel, setSummaryModel] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  useEffect(() => {
    setSummaries([]);
    setTopPick(null);
    setSummaryModel("");
    setSummaryError("");
  }, [selectedId]);

  useEffect(() => {
    if (!token || !selectedId || role !== "hr") {
      setApplicants([]);
      setApplicantsError("");
      return;
    }
    let cancelled = false;
    setApplicantsLoading(true);
    setApplicantsError("");
    apiGet(`/api/jobs/${selectedId}/applicants`, token)
      .then((d) => {
        if (!cancelled) setApplicants(d.applicants ?? []);
      })
      .catch((e) => {
        if (!cancelled) {
          setApplicants([]);
          setApplicantsError(e.message || "Could not load applicants");
        }
      })
      .finally(() => {
        if (!cancelled) setApplicantsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token, selectedId, role]);

  useEffect(() => {
    if (!token || !selectedId || role !== "applicant") {
      setMyApp(null);
      return;
    }
    let cancelled = false;
    setMyAppLoading(true);
    apiGetMaybe(`/api/jobs/${selectedId}/my-application`, token)
      .then((d) => {
        if (!cancelled) setMyApp(d);
      })
      .catch(() => {
        if (!cancelled) setMyApp(null);
      })
      .finally(() => {
        if (!cancelled) setMyAppLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token, selectedId, role]);

  async function onUploadChange(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !selectedId || !token) return;
    setUploadError("");
    setUploading(true);
    try {
      const r = await apiUploadResume(selectedId, file, token);
      setMyApp({
        application_id: r.application_id,
        original_filename: r.original_filename,
        applied_at: r.applied_at,
      });
    } catch (err) {
      setUploadError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function onDownloadApp(applicationId, filename) {
    apiDownloadResume(applicationId, token, filename).catch((err) => {
      alert(err.message || "Download failed");
    });
  }

  async function onSummarizeResumes() {
    if (!token || !selectedId) return;
    setSummaryError("");
    setSummaryLoading(true);
    setSummaries([]);
    setTopPick(null);
    try {
      const data = await apiPostTrigger(`/api/jobs/${selectedId}/summarize-resumes`, token);
      setSummaries(data.summaries ?? []);
      setTopPick(data.top_pick ?? null);
      setSummaryModel(data.model ?? "");
    } catch (err) {
      setSummaryError(err.message || "Summarization failed");
    } finally {
      setSummaryLoading(false);
    }
  }

  return (
    <div className="job-board">
      <div className="job-board-intro">
        <h2 className="job-board-title">
          {isHr ? "Open roles — HR workspace" : "Open positions"}
        </h2>
        <p className="job-board-sub">
          {isHr
            ? "Select a role to view the five most recent applicants, download resumes, or generate AI summaries (OpenAI)."
            : "Select a role to read the description and upload your resume for that opening."}
        </p>
      </div>

      <div className="job-board-shell">
        <aside className="job-list" aria-label="Job openings">
          {jobs.length === 0 ? (
            <p className="job-list-empty">No open positions right now.</p>
          ) : (
            <ul>
              {jobs.map((j) => (
                <li key={j.id}>
                  <button
                    type="button"
                    className={`job-list-item${selectedId === j.id ? " job-list-item--active" : ""}`}
                    onClick={() => setSelectedId(j.id)}
                  >
                    <span className="job-list-item-title">{j.title}</span>
                    {j.department ? (
                      <span className="job-list-item-meta">{j.department}</span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <section className="job-detail-panel" aria-live="polite">
          {selected ? (
            <>
              <header className="job-detail-header">
                <h3>{selected.title}</h3>
                <div className="job-detail-tags">
                  {selected.department ? (
                    <span className="job-tag">{selected.department}</span>
                  ) : null}
                  {selected.location ? (
                    <span className="job-tag job-tag--muted">{selected.location}</span>
                  ) : null}
                  {selected.employment_type ? (
                    <span className="job-tag job-tag--muted">{selected.employment_type}</span>
                  ) : null}
                </div>
              </header>
              <div className="job-detail-body">
                {selected.description.split("\n\n").map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
              <p className="job-detail-foot">Posted {selected.created_at?.slice(0, 10) ?? "—"}</p>

              {isHr ? (
                <div className="job-side-section">
                  <h4 className="job-side-title">Top applicants (up to 5)</h4>
                  {applicantsLoading ? (
                    <p className="job-side-muted">Loading applicants…</p>
                  ) : applicantsError ? (
                    <p className="job-side-error">{applicantsError}</p>
                  ) : applicants.length === 0 ? (
                    <p className="job-side-muted">No applicants yet for this role.</p>
                  ) : (
                    <ul className="applicant-list">
                      {applicants.map((a) => (
                        <li key={a.application_id} className="applicant-row">
                          <div className="applicant-row-main">
                            <span className="applicant-name">{a.username}</span>
                            <span className="applicant-meta">
                              Applied {a.applied_at?.slice(0, 10) ?? "—"}
                            </span>
                          </div>
                          <div className="applicant-row-file">{a.original_filename}</div>
                          <button
                            type="button"
                            className="btn-download"
                            onClick={() => onDownloadApp(a.application_id, a.original_filename)}
                          >
                            Download resume
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                  {applicants.length > 0 ? (
                    <div className="hr-ai-summarize">
                      <button
                        type="button"
                        className="btn btn-primary btn-summarize"
                        disabled={summaryLoading}
                        onClick={onSummarizeResumes}
                      >
                        {summaryLoading ? "Working…" : "Summarize & recommend top match"}
                      </button>
                      {summaryError ? <p className="job-side-error">{summaryError}</p> : null}
                      {summaries.length > 0 ? (
                        <div className="ai-summary-panel">
                          {topPick ? (
                            <div className="ai-top-pick">
                              <h5 className="ai-top-pick-heading">Top pick for this role</h5>
                              <div className="ai-top-pick-user">{topPick.username}</div>
                              <div className="ai-top-pick-reason">{topPick.reason}</div>
                            </div>
                          ) : null}
                          <h5 className="ai-summary-heading">
                            All summaries{summaryModel ? ` · ${summaryModel}` : ""}
                          </h5>
                          <ul className="ai-summary-list">
                            {summaries.map((s) => (
                              <li key={s.application_id} className="ai-summary-card">
                                <div className="ai-summary-user">{s.username}</div>
                                <div className="ai-summary-body">{s.summary}</div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              ) : (
                <div className="job-side-section">
                  <h4 className="job-side-title">Your application</h4>
                  {myAppLoading ? (
                    <p className="job-side-muted">Checking for a saved resume…</p>
                  ) : myApp ? (
                    <div className="applicant-upload-status">
                      <p>
                        Resume on file: <strong>{myApp.original_filename}</strong>
                        <span className="job-side-muted"> · Submitted {myApp.applied_at?.slice(0, 10)}</span>
                      </p>
                      <button
                        type="button"
                        className="btn-download"
                        onClick={() => onDownloadApp(myApp.application_id, myApp.original_filename)}
                      >
                        Download my resume
                      </button>
                      <p className="job-side-muted job-side-muted--tight">
                        Upload again to replace the file for this role (.pdf, .doc, .docx, .txt — max 5MB).
                      </p>
                    </div>
                  ) : (
                    <p className="job-side-muted">You have not applied to this role yet. Upload a resume below.</p>
                  )}
                  {uploadError ? <p className="job-side-error">{uploadError}</p> : null}
                  <label className="btn-upload-label">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx,.txt,application/pdf"
                      className="btn-upload-input"
                      disabled={uploading}
                      onChange={onUploadChange}
                    />
                    <span className="btn btn-primary btn-upload-pseudo">
                      {uploading ? "Uploading…" : myApp ? "Replace resume" : "Upload resume"}
                    </span>
                  </label>
                </div>
              )}
            </>
          ) : (
            <p className="job-list-empty">Select a position to view details.</p>
          )}
        </section>
      </div>
    </div>
  );
}
