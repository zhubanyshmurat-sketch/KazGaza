"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BarChart3,
  Bell,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Search,
  Settings,
  Users,
  X,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { dashboardApi } from "@/lib/api";
import { useRealtime } from "@/hooks/useRealtime";
import { useToast } from "@/lib/toast-context";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: null },
  { href: "/applications", label: "Өтінімдер", icon: FileText, roles: null },
  { href: "/emergency", label: "Авариялық өтінімдер", icon: AlertTriangle, roles: null },
  { href: "/employees", label: "Қызметкерлер", icon: Users, roles: ["SUPER_ADMIN"] },
  { href: "/reports", label: "Есептер", icon: BarChart3, roles: null },
  { href: "/settings", label: "Баптаулар", icon: Settings, roles: null },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { admin, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [search, setSearch] = useState("");
  const { toast } = useToast();

  const { data: stats } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardApi.stats,
    refetchInterval: 60_000,
  });

  useRealtime((event) => {
    if (event.event === "application_created" && event.payload.priority === "CRITICAL") {
      toast(`🚨 Жаңа авариялық өтінім: ${event.payload.application_number}`, "error");
    } else if (event.event === "application_created") {
      toast(`🆕 Жаңа өтінім: ${event.payload.application_number}`, "info");
    }
  });

  const visibleNav = NAV.filter(
    (item) => !item.roles || (admin && (item.roles as readonly string[]).includes(admin.role))
  );

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (search.trim()) router.push(`/applications?q=${encodeURIComponent(search.trim())}`);
  }

  return (
    <div className="flex min-h-screen bg-background">
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 shrink-0 border-r bg-card transition-transform lg:static lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-14 items-center justify-between border-b px-4">
          <span className="text-lg font-bold text-primary">KazGaza</span>
          <button className="lg:hidden" onClick={() => setMobileOpen(false)}>
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="space-y-1 p-3">
          {visibleNav.map((item) => {
            const active = pathname?.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-accent"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
                {item.href === "/emergency" && !!stats?.critical && (
                  <span className="ml-auto rounded-full bg-critical px-1.5 py-0.5 text-[10px] font-bold text-critical-foreground">
                    {stats.critical}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b bg-card px-4">
          <button className="lg:hidden" onClick={() => setMobileOpen(true)}>
            <Menu className="h-5 w-5" />
          </button>

          <form onSubmit={handleSearchSubmit} className="flex max-w-sm flex-1 items-center gap-2">
            <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Өтінім нөмірі немесе дербес шот..."
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
          </form>

          <div className="ml-auto flex items-center gap-3">
            <Link href="/emergency" className="relative rounded-md p-2 hover:bg-accent">
              <Bell className="h-5 w-5" />
              {!!stats?.critical && (
                <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-critical text-[10px] font-bold text-critical-foreground">
                  {stats.critical}
                </span>
              )}
            </Link>
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium leading-none">{admin?.name}</p>
              <p className="text-xs text-muted-foreground">{admin?.role}</p>
            </div>
            <button
              onClick={() => logout()}
              className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-foreground"
              title="Шығу"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
