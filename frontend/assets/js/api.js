// ============================================
// API Handler: Centralized request management
// ============================================

const BASE_URL = "http://127.0.0.1:8000";

// 🔐 Token helpers
export function getToken() {
  return localStorage.getItem("access");
}

export function setToken(token) {
  localStorage.setItem("access", token);
}

export function clearToken() {
  localStorage.removeItem("access");
  localStorage.removeItem("user_id");
  localStorage.removeItem("username");
}

/**
 * Centralized API request handler
 */
export async function apiRequest(url, method = "GET", body = null) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  const res = await fetch(BASE_URL + url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  let data = {};
  try {
    data = await res.json();
  } catch (e) {
    // ignore non-JSON
  }

  // 🔴 Handle Unauthorized
  if (res.status === 401) {
    clearToken();
    window.location.href = "login.html";
    return;
  }

  // 🔴 Handle Errors (IMPORTANT)
  if (!res.ok) {
    throw {
      status: res.status,
      data: data,
    };
  }

  return data;
}