"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Download } from "lucide-react";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge, PriorityBadge } from "@/components/status-badge";
import { applicationsApi, type ApplicationFilters } from "@/lib/api";
import { APPLICATION_TYPE_LABELS, type ApplicationStatus, type ApplicationType } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";

const TYPE_OPTIONS: ApplicationType[] = ["METER_NOT_WORKING", "MPI_REMOVAL", "GAS_LEAK"];
const STATUS_OPTIONS: ApplicationStatus[] = ["NEW", "IN_PROGRESS", "COMPLETED", "REJECTED"];

export function ApplicationsTable({
  fixedFilters,
  hidePriorityFilter,
  title,
}: {
  fixedFilters?: Partial<ApplicationFilters>;
  hidePriorityFilter?: boolean;
  title?: string;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [q, setQ] = useState(searchParams.get("q") || "");
  const [applicationType, setApplicationType] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [priority, setPriority] = useState<string>("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sort, setSort] = useState<"desc" | "asc">("desc");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const filters: ApplicationFilters = {
    q: q || undefined,
    application_type: applicationType !== "all" ? (applicationType as ApplicationType) : undefined,
    status: status !== "all" ? (status as ApplicationStatus) : undefined,
    priority: priority !== "all" ? (priority as ApplicationFilters["priority"]) : undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    sort,
    page,
    page_size: pageSize,
    ...fixedFilters,
  };

  const { data, isLoading } = useQuery({
    queryKey: ["applications", filters],
    queryFn: () => applicationsApi.list(filters),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <div className="space-y-4">
      {title && <h1 className="text-xl font-semibold">{title}</h1>}

      <div className="flex flex-wrap items-end gap-2 rounded-lg border bg-card p-3">
        <div className="min-w-[180px] flex-1">
          <Input
            placeholder="Өтінім №, дербес шот..."
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <Select
          value={applicationType}
          onValueChange={(v) => {
            setApplicationType(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Барлық түрлер" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Барлық түрлер</SelectItem>
            {TYPE_OPTIONS.map((t) => (
              <SelectItem key={t} value={t}>
                {APPLICATION_TYPE_LABELS[t]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={status}
          onValueChange={(v) => {
            setStatus(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Барлық статустар" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Барлық статустар</SelectItem>
            {STATUS_OPTIONS.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {!hidePriorityFilter && (
          <Select
            value={priority}
            onValueChange={(v) => {
              setPriority(v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Барлық приоритет" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Барлық приоритет</SelectItem>
              <SelectItem value="NORMAL">Қалыпты</SelectItem>
              <SelectItem value="HIGH">Жоғары</SelectItem>
              <SelectItem value="CRITICAL">Авариялық</SelectItem>
            </SelectContent>
          </Select>
        )}

        <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="w-[150px]" />
        <span className="text-muted-foreground">—</span>
        <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="w-[150px]" />

        <Select value={sort} onValueChange={(v) => setSort(v as "asc" | "desc")}>
          <SelectTrigger className="w-[170px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Жаңадан ескіге</SelectItem>
            <SelectItem value="asc">Ескіден жаңаға</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          size="sm"
          onClick={() => window.open(applicationsApi.exportUrl(filters, "xlsx"), "_blank")}
        >
          <Download className="mr-1 h-3.5 w-3.5" /> Excel
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.open(applicationsApi.exportUrl(filters, "csv"), "_blank")}
        >
          <Download className="mr-1 h-3.5 w-3.5" /> CSV
        </Button>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>№ Өтінім</TableHead>
              <TableHead>Күні</TableHead>
              <TableHead>Дербес шот</TableHead>
              <TableHead>Түрі</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead>Приоритет</TableHead>
              <TableHead>Пайдаланушы</TableHead>
              <TableHead>Орындаушы</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading &&
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 9 }).map((__, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-16" />
                    </TableCell>
                  ))}
                </TableRow>
              ))}

            {!isLoading && data?.items.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} className="py-8 text-center text-muted-foreground">
                  Өтінімдер табылмады.
                </TableCell>
              </TableRow>
            )}

            {data?.items.map((app) => (
              <TableRow
                key={app.id}
                className={`cursor-pointer ${app.priority === "CRITICAL" ? "bg-critical/5" : ""}`}
                onClick={() => router.push(`/applications/${app.id}`)}
              >
                <TableCell className="font-medium">{app.application_number}</TableCell>
                <TableCell>{formatDateTime(app.created_at)}</TableCell>
                <TableCell>{app.personal_account}</TableCell>
                <TableCell>{APPLICATION_TYPE_LABELS[app.application_type]}</TableCell>
                <TableCell>
                  <StatusBadge status={app.status} />
                </TableCell>
                <TableCell>
                  <PriorityBadge priority={app.priority} />
                </TableCell>
                <TableCell>{app.user.telegram_username ? `@${app.user.telegram_username}` : app.user.first_name || `id${app.user.telegram_user_id}`}</TableCell>
                <TableCell>{app.assigned_admin?.name || "—"}</TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm">
                    Ашу
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {data && data.total > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Барлығы: {data.total} · Бет {page} / {totalPages}
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
