import { Suspense } from "react";

import { ApplicationsTable } from "@/components/applications-table";

export default function ApplicationsPage() {
  return (
    <Suspense>
      <ApplicationsTable title="Өтінімдер" />
    </Suspense>
  );
}
