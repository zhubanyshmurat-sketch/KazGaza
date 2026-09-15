"use client";

import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { settingsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import type { SystemSettingsOut } from "@/lib/types";

export default function SettingsPage() {
  const { admin } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const canEdit = admin?.role === "SUPER_ADMIN";

  const { data, isLoading } = useQuery({ queryKey: ["settings"], queryFn: settingsApi.get });
  const [form, setForm] = useState<SystemSettingsOut | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (data) setForm(data);
  }, [data]);

  async function handleSave() {
    if (!form) return;
    setSaving(true);
    try {
      const updated = await settingsApi.update(form);
      setForm(updated);
      queryClient.setQueryData(["settings"], updated);
      toast("Баптаулар сақталды.", "success");
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    } finally {
      setSaving(false);
    }
  }

  if (isLoading || !form) {
    return <Skeleton className="h-96 w-full" />;
  }

  function field(key: keyof SystemSettingsOut, label: string, multiline = false) {
    const Comp = multiline ? Textarea : Input;
    return (
      <div className="space-y-1.5">
        <Label>{label}</Label>
        <Comp
          disabled={!canEdit}
          value={String(form![key] ?? "")}
          onChange={(e) => setForm({ ...form!, [key]: e.target.value })}
        />
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold">Баптаулар</h1>
      {!canEdit && (
        <p className="text-sm text-muted-foreground">
          Тек SUPER_ADMIN рөліндегі қолданушылар баптауларды өзгерте алады.
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Ұйым туралы</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {field("organization_name", "Ұйым атауы")}
          {field("contact_phone", "Байланыс телефоны")}
          {field("emergency_phone", "🚨 Авариялық қызмет телефоны")}
          <div className="space-y-1.5">
            <Label>Фотосурет максимал өлшемі (МБ)</Label>
            <Input
              type="number"
              disabled={!canEdit}
              value={form.max_photo_size_mb}
              onChange={(e) => setForm({ ...form, max_photo_size_mb: Number(e.target.value) })}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Telegram bot хабарлама мәтіндері</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {field("welcome_text", "Қош келдіңіз хабарламасы", true)}
          {field("status_new_text", "🆕 Жаңа статус хабарламасы", true)}
          {field("status_in_progress_text", "🟡 Өңделуде статус хабарламасы", true)}
          {field("status_completed_text", "🟢 Аяқталды статус хабарламасы", true)}
          {field("status_rejected_text", "🔴 Қабылданбады статус хабарламасы", true)}
        </CardContent>
      </Card>

      {canEdit && (
        <Button onClick={handleSave} disabled={saving}>
          Сақтау
        </Button>
      )}
    </div>
  );
}
