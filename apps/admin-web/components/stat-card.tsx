import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function StatCard({
  label,
  value,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: number | string;
  icon: LucideIcon;
  tone?: "default" | "new" | "progress" | "done" | "critical";
}) {
  const toneClasses: Record<string, string> = {
    default: "bg-primary/10 text-primary",
    new: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
    progress: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    done: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    critical: "bg-critical/10 text-critical",
  };

  return (
    <Card className={cn(tone === "critical" && value !== 0 && "border-critical/50")}>
      <CardContent className="flex items-center gap-4 p-4">
        <div className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-lg", toneClasses[tone])}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-2xl font-bold leading-none">{value}</p>
          <p className="mt-1 text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
