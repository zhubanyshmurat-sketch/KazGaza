import { Suspense } from "react";

import { ApplicationsTable } from "@/components/applications-table";

export default function EmergencyPage() {
  return (
    <Suspense>
      <ApplicationsTable
        title="🚨 Авариялық өтінімдер"
        fixedFilters={{ priority: "CRITICAL" }}
        hidePriorityFilter
      />
    </Suspense>
  );
}
