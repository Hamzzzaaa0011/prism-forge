export class APIError extends Error {
  constructor(message, status, payload = null) {
    super(message);
    this.name = "APIError";
    this.status = status;
    this.payload = payload;
  }
}

function csrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || "";
}

export const API = {
  base: "/api/v1",

  async request(method, path, body = null) {
    const res = await fetch(`${this.base}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken(),
      },
      body: body ? JSON.stringify(body) : null,
      credentials: "include",
    });

    const contentType = res.headers.get("Content-Type") || "";
    const payload = contentType.includes("application/json")
      ? await res.json().catch(() => null)
      : null;

    if (res.status === 401) {
      window.location.href = "/auth/login";
      return null;
    }

    if (!res.ok || payload?.success === false) {
      const message = payload?.error?.message || `Request failed (${res.status}).`;
      throw new APIError(message, res.status, payload);
    }
    return payload?.data || {};
  },

  get(path) {
    return this.request("GET", path);
  },

  post(path, body) {
    return this.request("POST", path, body);
  },
};
