const API_BASE = 'https://moody-pens-talk.loca.lt';
const WS_BASE = API_BASE.replace(/^http/, 'ws');

export function getApiBase() { return API_BASE; }

export function apiUrl(path) {
  return `${API_BASE}${path}`;
}

export function wsUrl(path, token) {
  const url = `${WS_BASE}${path}`;
  return token ? `${url}?token=${token}` : url;
}

export async function apiGet(path, token) {
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const r = await fetch(apiUrl(path), { headers });
  if (!r.ok) throw new Error(`GET ${path} failed: ${r.status}`);
  return r.json();
}

export async function apiPost(path, body, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const r = await fetch(apiUrl(path), { method: 'POST', headers, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`POST ${path} failed: ${r.status}`);
  return r.json();
}

export async function apiPut(path, body, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const r = await fetch(apiUrl(path), { method: 'PUT', headers, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`PUT ${path} failed: ${r.status}`);
  return r.json();
}

export async function apiDel(path, token) {
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const r = await fetch(apiUrl(path), { method: 'DELETE', headers });
  if (!r.ok) throw new Error(`DELETE ${path} failed: ${r.status}`);
  return r.json();
}
