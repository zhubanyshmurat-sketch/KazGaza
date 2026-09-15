"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/stat-card";
import { dashboardApi, applicationsApi, adminsApi } from "@/lib/api";
import { APPLICATION_TYPE_LABELS, type ApplicationStatus, type ApplicationType } from "@/lib/types";
import { AlertTriangle, CheckCircle2, Clock, ListChecks, Timer, XCircle } from "lucide-react";

export default function ReportsPage() {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [applicationType, setApplicationType] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [assignedTo, setAssignedTo] = useState<string>("all");

  const { data: admins } = useQuery({ queryKey: ["admins-roster"], queryFn: adminsApi.list, retry: 0 });

  const filters = {
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    application_type: applicationType !== "all" ? (applicationType as ApplicationType) : undefined,
    status: status !== "all" ? (status as ApplicationStatus) : undefined,
    assigned_to: assignedTo !== "all" ? Number(assignedTo) : undefined,
  };

  const { data: report, isLoading } = useQuery({
    queryKey: ["report", filters],
    queryFn: () => dashboardApi.report(filters),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Есептер</h1>

      <Card>
        <CardHeader>
          <CardTitle>Сүзгілер</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-3">
          <div className="space-y-1">
            <Label className="text-xs">Күні бастап</Label>
            <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Күні дейін</Label>
            <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Өтінім түрі</Label>
            <Select value={applicationType} onValueChange={setApplicationType}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Барлығы</SelectItem>
                {Object.entries(APPLICATION_TYPE_LABELS).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Статус</Label>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[160px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Барлығы</SelectItem>
                <SelectItem value="NEW">NEW</SelectItem>
                <SelectItem value="IN_PROGRESS">IN_PROGRESS</SelectItem>
                <SelectItem value="COMPLETED">COMPLETED</SelectItem>
                <SelectItem value="REJECTED">REJECTED</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {admins && (
            <div className="space-y-1">
              <Label className="text-xs">Орындаушы</Label>
              <Select value={assignedTo} onValueChange={setAssignedTo}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Барлығы</SelectItem>
                  {admins.map((a) => (
                    <SelectItem key={a.id} value={String(a.id)}>
                      {a.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="ml-auto flex gap-2">
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
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {isLoading || !report ? (
          Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-[76px]" />)
        ) : (
          <>
            <StatCard label="Барлығы" value={report.total} icon={ListChecks} />
            <StatCard label="Жаңа" value={report.new} icon={Clock} tone="new" />
            <StatCard label="Өңделуде" value={report.in_progress} icon={AlertTriangle} tone="progress" />
            <StatCard label="Аяқталды" value={report.completed} icon={CheckCircle2} tone="done" />
            <StatCard label="Қабылданбады" value={report.rejected} icon={XCircle} />
            <StatCard label="Авариялық" value={report.critical} icon={AlertTriangle} tone="critical" />
            <StatCard
              label="Орташа өңдеу уақыты"
              value={report.avg_processing_hours != null ? `${report.avg_processing_hours} сағ.` : "—"}
              icon={Timer}
            />
          </>
        )}
      </div>
    </div>
  );
}
