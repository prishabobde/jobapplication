/**
 * Uses Vite dev proxy: requests to /api/* → backend (see vite.config.js).
 * Set VITE_API_URL (e.g. http://127.0.0.1:3001) if you serve the SPA without the proxy.
 */
const base = import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";

async function parseError(res) {
  try {
    const j = await res.json();
    if (j && typeof j.error === "string") return j.error;
    if (j && typeof j.detail === "string") return j.detail;
  } catch {
    /* ignore */
  }
  return res.statusText || "Request failed";
}

export async function apiPost(path, body, token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

/** POST with no JSON body (e.g. trigger actions). */
export async function apiPostTrigger(path, token) {
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function apiGet(path, token) {
  const res = await fetch(`${base}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

/** GET that returns null on 404 instead of throwing (for optional resources). */
export async function apiGetMaybe(path, token) {
  const res = await fetch(`${base}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function apiUploadResume(jobId, file, token) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${base}/api/jobs/${jobId}/resume`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function apiDownloadResume(applicationId, token, downloadName) {
  const res = await fetch(`${base}/api/applications/${applicationId}/resume`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await parseError(res));
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = downloadName || "resume";
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
