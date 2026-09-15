"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { adminsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { ROLE_LABELS, type AdminRole } from "@/lib/types";

export default function EmployeesPage() {
  const { admin: currentAdmin } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { data: admins, isLoading } = useQuery({ queryKey: ["admins-roster"], queryFn: adminsApi.list });

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<AdminRole>("OPERATOR");
  const [submitting, setSubmitting] = useState(false);

  if (currentAdmin?.role !== "SUPER_ADMIN") {
    return <p className="text-sm text-muted-foreground">Бұл бетке қол жеткізу құқығыңыз жоқ.</p>;
  }

  async function handleCreate() {
    setSubmitting(true);
    try {
      await adminsApi.create({ name, email, password, role });
      toast("Қызметкер қосылды.", "success");
      setOpen(false);
      setName("");
      setEmail("");
      setPassword("");
      setRole("OPERATOR");
      queryClient.invalidateQueries({ queryKey: ["admins-roster"] });
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleActive(id: number, active: boolean) {
    try {
      await adminsApi.update(id, { active: !active });
      queryClient.invalidateQueries({ queryKey: ["admins-roster"] });
    } catch (err) {
      toast(err instanceof ApiError ? err.message : "Қате орын алды.", "error");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Қызметкерлер</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-1 h-4 w-4" /> Қызметкер қосу
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Жаңа қызметкер</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <div className="space-y-1.5">
                <Label>Аты-жөні</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Email</Label>
                <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Құпия сөз</Label>
                <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label>Рөлі</Label>
                <Select value={role} onValueChange={(v) => setRole(v as AdminRole)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(ROLE_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                className="w-full"
                disabled={!name || !email || password.length < 8 || submitting}
                onClick={handleCreate}
              >
                Сақтау
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Аты-жөні</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Рөлі</TableHead>
                <TableHead>Күйі</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading &&
                Array.from({ length: 3 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell colSpan={5}>
                      <Skeleton className="h-6 w-full" />
                    </TableCell>
                  </TableRow>
                ))}
              {admins?.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-medium">{a.name}</TableCell>
                  <TableCell>{a.email}</TableCell>
                  <TableCell>{ROLE_LABELS[a.role]}</TableCell>
                  <TableCell>
                    <Badge variant={a.active ? "success" : "destructive"}>{a.active ? "Белсенді" : "Өшірілген"}</Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={() => toggleActive(a.id, a.active)}>
                      {a.active ? "Өшіру" : "Қосу"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
