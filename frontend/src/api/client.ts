import { useAuth } from "../state/AuthContext";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!res.ok) {
    if (res.status === 401) {
      throw new Error("UNAUTHORIZED");
    }

    let message = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data) {
        if (typeof data?.detail === "string") {
          message = data.detail;
        } else if (typeof data?.message === "string") {
          message = data.message;
        } else if (typeof data === "string") {
          message = data;
        } else {
          // fallback: stringify the body object for visibility
          message = JSON.stringify(data);
        }
      }
    } catch {
      // ignore JSON parse errors
    }

    throw new Error(message);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const contentType = res.headers.get("content-type") || "";
  const hasBody =
    (res.headers.has("content-length") && res.headers.get("content-length") !== "0") ||
    contentType.includes("application/json");

  if (!hasBody) {
    return undefined as T;
  }

  return (await res.json()) as T;
}

export async function login(body: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(body)
  });
}


export function useApi() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  const handleUnauthorized = () => {
    try {
      logout();
    } catch {}
    navigate("/login", { replace: true });
  };

  const get = useCallback(
    async <T,>(path: string) => {
      try {
        return await request<T>(path, { method: "GET" }, token);
      } catch (err: any) {
        if (err?.message === "UNAUTHORIZED") {
          handleUnauthorized();
        }
        throw err;
      }
    },
    [token, logout, navigate]
  );

  const post = useCallback(
    async <T,>(path: string, body: unknown) => {
      try {
        return await request<T>(path, { method: "POST", body: JSON.stringify(body) }, token);
      } catch (err: any) {
        if (err?.message === "UNAUTHORIZED") {
          handleUnauthorized();
        }
        throw err;
      }
    },
    [token, logout, navigate]
  );

  const patch = useCallback(
    async <T,>(path: string, body: unknown) => {
      try {
        return await request<T>(path, { method: "PATCH", body: JSON.stringify(body) }, token);
      } catch (err: any) {
        if (err?.message === "UNAUTHORIZED") {
          handleUnauthorized();
        }
        throw err;
      }
    },
    [token, logout, navigate]
  );

  const del = useCallback(
    async <T,>(path: string) => {
      try {
        return await request<T>(path, { method: "DELETE" }, token);
      } catch (err: any) {
        if (err?.message === "UNAUTHORIZED") {
          handleUnauthorized();
        }
        throw err;
      }
    },
    [token, logout, navigate]
  );

  return { get, post, patch, del };
}

