import { Badge } from "@/components/ui/badge";
import type { ApplicationPriority, ApplicationStatus } from "@/lib/types";
import { PRIORITY_LABELS, STATUS_LABELS } from "@/lib/types";

const STATUS_VARIANT: Record<ApplicationStatus, "default" | "warning" | "success" | "destructive"> = {
  NEW: "default",
  IN_PROGRESS: "warning",
  COMPLETED: "success",
  REJECTED: "destructive",
};

const STATUS_ICON: Record<ApplicationStatus, string> = {
  NEW: "🆕",
  IN_PROGRESS: "🟡",
  COMPLETED: "🟢",
  REJECTED: "🔴",
};

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return (
    <Badge variant={STATUS_VARIANT[status]}>
      {STATUS_ICON[status]} {STATUS_LABELS[status]}
    </Badge>
  );
}

export function PriorityBadge({ priority }: { priority: ApplicationPriority }) {
  if (priority === "CRITICAL") {
    return <Badge variant="critical">🚨 АВАРИЯ</Badge>;
  }
  if (priority === "HIGH") {
    return <Badge variant="warning">{PRIORITY_LABELS[priority]}</Badge>;
  }
  return <Badge variant="secondary">{PRIORITY_LABELS[priority]}</Badge>;
}
