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

export async function apiGet(path, token) {
  const res = await fetch(`${base}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}
