"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Clock, ListChecks, XCircle } from "lucide-react";

import { StatCard } from "@/components/stat-card";
import { ApplicationsTrendChart, ApplicationsByTypeChart } from "@/components/dashboard-charts";
import { ApplicationsTable } from "@/components/applications-table";
import { Skeleton } from "@/components/ui/skeleton";
import { dashboardApi } from "@/lib/api";

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardApi.stats,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        {isLoading || !stats ? (
          Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-[76px]" />)
        ) : (
          <>
            <StatCard label="Барлық өтінімдер" value={stats.total} icon={ListChecks} tone="default" />
            <StatCard label="Жаңа" value={stats.new} icon={Clock} tone="new" />
            <StatCard label="Өңделуде" value={stats.in_progress} icon={AlertTriangle} tone="progress" />
            <StatCard label="Аяқталды" value={stats.completed} icon={CheckCircle2} tone="done" />
            <StatCard label="🚨 Авариялық" value={stats.critical} icon={XCircle} tone="critical" />
          </>
        )}
      </div>

      {stats && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <ApplicationsTrendChart data={stats.by_day} />
          <ApplicationsByTypeChart data={stats.by_type} />
        </div>
      )}

      <div>
        <h2 className="mb-3 text-lg font-semibold">Соңғы өтінімдер</h2>
        <ApplicationsTable hidePriorityFilter={false} />
      </div>
    </div>
  );
}
