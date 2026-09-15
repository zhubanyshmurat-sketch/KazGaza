"use client";

import { Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { APPLICATION_TYPE_LABELS, type ApplicationType } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const TYPE_COLORS: Record<string, string> = {
  METER_NOT_WORKING: "#2563eb",
  MPI_REMOVAL: "#0891b2",
  GAS_LEAK: "#dc2626",
};

export function ApplicationsTrendChart({ data }: { data: { date: string; count: number }[] }) {
  return (
    <Card className="col-span-full lg:col-span-2">
      <CardHeader>
        <CardTitle>Соңғы 14 күндегі өтінімдер саны</CardTitle>
      </CardHeader>
      <CardContent className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ left: -20, right: 10, top: 10 }}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(217 91% 45%)" stopOpacity={0.35} />
                <stop offset="95%" stopColor="hsl(217 91% 45%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis
              dataKey="date"
              tickFormatter={(v) => formatDate(v)}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis allowDecimals={false} fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              labelFormatter={(v) => formatDate(String(v))}
              contentStyle={{ fontSize: 12, borderRadius: 8 }}
            />
            <Area type="monotone" dataKey="count" stroke="hsl(217 91% 45%)" fill="url(#colorCount)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function ApplicationsByTypeChart({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data).map(([type, count]) => ({
    type,
    label: APPLICATION_TYPE_LABELS[type as ApplicationType] || type,
    count,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Түрлері бойынша үлестірім</CardTitle>
      </CardHeader>
      <CardContent className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={chartData} dataKey="count" nameKey="label" innerRadius={45} outerRadius={80} paddingAngle={2}>
              {chartData.map((entry) => (
                <Cell key={entry.type} fill={TYPE_COLORS[entry.type] || "#94a3b8"} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-2 space-y-1">
          {chartData.map((entry) => (
            <div key={entry.type} className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: TYPE_COLORS[entry.type] || "#94a3b8" }}
                />
                {entry.label}
              </span>
              <span className="font-medium">{entry.count}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
