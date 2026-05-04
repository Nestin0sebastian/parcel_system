import { apiRequest, setToken, clearToken, getToken } from "./api.js";

// 🔐 LOGIN
export async function login(username, password) {
  try {
    const data = await apiRequest("/api/auth/login/", "POST", {
      username,
      password,
    });

    if (data && data.access) {
      setToken(data.access);
      localStorage.setItem("username", username);

      if (data.user_id) {
        localStorage.setItem("user_id", data.user_id);
      }
    }

    return data;
  } catch (error) {
    console.log("LOGIN ERROR:", error.data);
    throw new Error(JSON.stringify(error.data));
  }
}

// 📝 SIGNUP
export async function signup(data) {
  try {
    const response = await apiRequest("/api/auth/signup/", "POST", data);
    return response;
  } catch (error) {
    console.log("SIGNUP ERROR:", error.data); // 🔥 IMPORTANT
    throw new Error(JSON.stringify(error.data));
  }
}

// 🚪 LOGOUT
export function logout() {
  clearToken();
  window.location.href = "login.html";
}

// 🔍 CHECK LOGIN
export function isLoggedIn() {
  const token = getToken();
  return token && token !== "undefined" && token !== "null";
}

// 👤 CURRENT USER
export function getCurrentUser() {
  return {
    id: localStorage.getItem("user_id"),
    username: localStorage.getItem("username"),
  };
}