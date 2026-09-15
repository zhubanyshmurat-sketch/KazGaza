"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { WS_BASE_URL } from "@/lib/config";

interface RealtimeEvent {
  event: string;
  payload: Record<string, unknown>;
}

/**
 * Keeps the dashboard/applications table/detail views live: any status
 * change, assignment or new (including GAS_LEAK/critical) application
 * created anywhere invalidates the relevant React Query caches so open
 * screens refetch without a manual page reload.
 */
export function useRealtime(onEvent?: (event: RealtimeEvent) => void) {
  const queryClient = useQueryClient();
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let closedByClient = false;

    function connect() {
      socket = new WebSocket(`${WS_BASE_URL}/ws/dashboard`);

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as RealtimeEvent;
          queryClient.invalidateQueries({ queryKey: ["applications"] });
          queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
          if (data.payload?.id) {
            queryClient.invalidateQueries({ queryKey: ["application", data.payload.id] });
          }
          onEventRef.current?.(data);
        } catch {
          // ignore malformed frames
        }
      };

      socket.onclose = () => {
        if (!closedByClient) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };
    }

    connect();

    return () => {
      closedByClient = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [queryClient]);
}
