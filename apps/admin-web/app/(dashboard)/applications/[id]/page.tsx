"use client";

import { use, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, MapPin } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge, PriorityBadge } from "@/components/status-badge";
import { PhotoGallery } from "@/components/photo-lightbox";
import { applicationsApi, adminsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { useRealtime } from "@/hooks/useRealtime";
import { APPLICATION_TYPE_LABELS, type ApplicationStatus } from "@/lib/types";
import { formatDate, formatDateTime } from "@/lib/utils";

const ApplicationMap = dynamic(() => import("@/components/application-map").then((m) => m.ApplicationMap), {
  ssr: false,
  loading: () => <Skeleton className="h-64 w-full" />,
});

const STATUS_OPTIONS: ApplicationStatus[] = ["NEW", "IN_PROGRESS", "COMPLETED", "REJECTED"];

export default function ApplicationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const applicationId = Number(id);
  const { admin } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  useRealtime();

  const { data: app, isLoading } = useQuery({
    queryKey: ["application", applicationId],
    queryFn: () => applicationsApi.get(applicationId),
  });

  const { data: admins } = useQuery({
    queryKey: ["admins-roster"],
    queryFn: adminsApi.list,
    enabled: admin?.role === "SUPER_ADMIN" || admin?.role === "DISPATCHER",
  });

  const [newStatus, setNewStatus] = useState<ApplicationStatus | "">("");
  const [statusComment, setStatusComment] = useState("");
  const [comment, setComment] = useState("");
  const [assignee, setAssignee] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ["application", applicationId] });
    queryClient.invalidateQueries({ queryKey: ["applications"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
  }

  async function handleStatusSubmit() {
    if (!newStatus) return;
    setSubmitting(true);
    try {
      await applicationsApi.updateStatus(applicationId, newStatus, statusComment || undefined);
      toast("Статус жаңартылды.", "success");
      setStatusComment("");
      setNewStatus("");
      invalidate();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAssign() {
    setSubmitting(true);
    try {
      await applicationsApi.assign(applicationId, assignee && assignee !== "none" ? Number(assignee) : null);
      toast("Орындаушы тағайындалды.", "success");
      invalidate();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleComment() {
    if (!comment.trim()) return;
    setSubmitting(true);
    try {
      await applicationsApi.addComment(applicationId, comment.trim());
      toast("Пікір қосылды.", "success");
      setComment("");
      invalidate();
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    } finally {
      setSubmitting(false);
    }
  }

  if (isLoading || !app) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const canAssign = admin?.role === "SUPER_ADMIN" || admin?.role === "DISPATCHER";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/applications">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-xl font-semibold">{app.application_number}</h1>
        <StatusBadge status={app.status} />
        <PriorityBadge priority={app.priority} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Өтінім ақпараты</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3 text-sm">
              <Info label="Құрылған күні" value={formatDateTime(app.created_at)} />
              <Info label="Дербес шот" value={app.personal_account} />
              <Info label="Өтінім түрі" value={APPLICATION_TYPE_LABELS[app.application_type]} />
              <Info
                label="Telegram пайдаланушы"
                value={
                  app.user.telegram_username
                    ? `@${app.user.telegram_username}`
                    : `${app.user.first_name || ""} ${app.user.last_name || ""}`.trim() ||
                      `id${app.user.telegram_user_id}`
                }
              />
              {app.requested_date && <Info label="Дата МПИ" value={formatDate(app.requested_date)} />}
              {app.admin_comment && <Info label="Әкімші пікірі" value={app.admin_comment} full />}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Фотосуреттер</CardTitle>
            </CardHeader>
            <CardContent>
              <PhotoGallery files={app.files} />
            </CardContent>
          </Card>

          {app.latitude != null && app.longitude != null && (
            <Card>
              <CardHeader className="flex-row items-center justify-between space-y-0">
                <CardTitle>Геолокация</CardTitle>
                <a
                  href={`https://www.openstreetmap.org/?mlat=${app.latitude}&mlon=${app.longitude}#map=17/${app.latitude}/${app.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Button variant="outline" size="sm">
                    <MapPin className="mr-1 h-3.5 w-3.5" /> Картадан ашу
                  </Button>
                </a>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-xs text-muted-foreground">
                  Latitude: {app.latitude} · Longitude: {app.longitude}
                </p>
                <ApplicationMap
                  latitude={app.latitude}
                  longitude={app.longitude}
                  label={app.application_number}
                />
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Өзгерістер тарихы</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {app.history.length === 0 && <p className="text-sm text-muted-foreground">Тарих бос.</p>}
              {app.history.map((h) => (
                <div key={h.id} className="border-l-2 border-primary/40 pl-3 text-sm">
                  <p className="text-xs text-muted-foreground">
                    {formatDateTime(h.created_at)} · {h.admin?.name || "Жүйе"}
                  </p>
                  {h.old_status !== h.new_status && (
                    <p>
                      Статус: <StatusBadge status={h.old_status ?? h.new_status} /> →{" "}
                      <StatusBadge status={h.new_status} />
                    </p>
                  )}
                  {h.comment && <p className="mt-1">{h.comment}</p>}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Статусты өзгерту</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Select value={newStatus} onValueChange={(v) => setNewStatus(v as ApplicationStatus)}>
                <SelectTrigger>
                  <SelectValue placeholder="Жаңа статус таңдаңыз" />
                </SelectTrigger>
                <SelectContent>
                  {STATUS_OPTIONS.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Textarea
                placeholder="Пайдаланушыға көрінетін түсініктеме (міндетті емес)"
                value={statusComment}
                onChange={(e) => setStatusComment(e.target.value)}
              />
              <Button className="w-full" disabled={!newStatus || submitting} onClick={handleStatusSubmit}>
                Статусты сақтау
              </Button>
            </CardContent>
          </Card>

          {canAssign && (
            <Card>
              <CardHeader>
                <CardTitle>Орындаушыны тағайындау</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Select value={assignee} onValueChange={setAssignee}>
                  <SelectTrigger>
                    <SelectValue placeholder={app.assigned_admin?.name || "Тағайындалмаған"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Тағайындалмаған</SelectItem>
                    {admins?.map((a) => (
                      <SelectItem key={a.id} value={String(a.id)}>
                        {a.name} ({a.role})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button variant="secondary" className="w-full" disabled={submitting} onClick={handleAssign}>
                  Тағайындау
                </Button>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Пікір қосу</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                placeholder="Ішкі пікір / ескертпе"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
              <Button variant="outline" className="w-full" disabled={!comment.trim() || submitting} onClick={handleComment}>
                Қосу
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Info({ label, value, full }: { label: string; value: string; full?: boolean }) {
  return (
    <div className={full ? "col-span-2" : undefined}>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  );
}
