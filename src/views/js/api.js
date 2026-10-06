/* Cliente HTTP para la API: tokens en localStorage, refresh automático en 401. */
const API_BASE = ""; // mismo origen: el backend sirve estas vistas (StaticFiles)

const TokenStore = {
  get access() { return localStorage.getItem("access_token"); },
  get refresh() { return localStorage.getItem("refresh_token"); },
  save(access, refresh) {
    localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

function decodeJwt(token) {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch { return null; }
}

function currentUser() {
  const t = TokenStore.access;
  if (!t) return null;
  const p = decodeJwt(t);
  if (!p) return null;
  return { id: p.sub, role: p.role, exp: p.exp };
}

async function refreshTokens() {
  const rt = TokenStore.refresh;
  if (!rt) throw new Error("sin refresh token");
  const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: rt }),
  });
  if (!res.ok) throw new Error("refresh falló");
  const data = await res.json();
  TokenStore.save(data.access_token, data.refresh_token);
  return data.access_token;
}

let refreshing = null;

async function apiFetch(path, options = {}, retry = true) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  if (TokenStore.access) headers["Authorization"] = `Bearer ${TokenStore.access}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 && retry && TokenStore.refresh) {
    try {
      refreshing = refreshing || refreshTokens();
      await refreshing;
      refreshing = null;
      return apiFetch(path, options, false);
    } catch {
      refreshing = null;
      TokenStore.clear();
      if (!location.pathname.endsWith("login.html")) location.href = "login.html";
      throw new Error("Sesión expirada");
    }
  }
  return res;
}

async function apiJson(path, options = {}, retry = true) {
  const res = await apiFetch(path, options, retry);
  if (res.status === 204) return null;
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = null; }
  if (!res.ok) {
    let msg = `Error ${res.status}`;
    if (data) {
      if (typeof data.detail === "string") msg = data.detail;
      else if (data.detail?.message) msg = data.detail.message;
      else if (Array.isArray(data.detail)) msg = data.detail.map(d => d.msg).join(", ");
    }
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

async function logout() {
  try {
    await apiFetch("/api/v1/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: TokenStore.refresh || "" }),
    }, false);
  } catch { /* ignorar */ }
  TokenStore.clear();
  location.href = "login.html";
}

function requireAuth(roles) {
  const u = currentUser();
  if (!u) { location.href = "login.html"; return null; }
  if (roles && !roles.includes(u.role)) { location.href = "catalog.html"; return null; }
  return u;
}

function formatMoney(n) { return `$${Number(n).toFixed(2)}`; }

function showMessage(el, type, msg) {
  el.className = `mt-4 p-3 rounded text-sm ${type === "error" ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`;
  el.textContent = msg;
  el.classList.remove("hidden");
}
