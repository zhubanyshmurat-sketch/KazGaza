"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { ApiError, authApi } from "@/lib/api";
import type { AdminOut } from "@/lib/types";

interface AuthContextValue {
  admin: AdminOut | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [admin, setAdmin] = useState<AdminOut | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refresh = useCallback(async () => {
    try {
      const me = await authApi.me();
      setAdmin(me);
    } catch (err) {
      setAdmin(null);
      if (err instanceof ApiError && err.status === 401) {
        // handled by caller / route guard
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login(email, password);
      setAdmin(res.admin);
      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    setAdmin(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ admin, loading, login, logout, refresh }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
