"use client";

import { useEffect } from "react";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { getWebSocketUrl } from "@/lib/ws-client";

/** Loads world simulation state from the API on mount. */
export function SimulationHydrator() {
  const hydrate = useSimulationStore((s) => s.hydrate);
  const isHydrated = useSimulationStore((s) => s.isHydrated);

  useEffect(() => {
    if (!isHydrated) {
      void hydrate();
    }
  }, [hydrate, isHydrated]);

  useEffect(() => {
    let disposed = false;
    let reconnectTimer: number | undefined;
    let socket: WebSocket | undefined;

    const connect = () => {
      socket = new WebSocket(getWebSocketUrl());
      socket.onmessage = (event) => {
        try {
          const message: unknown = JSON.parse(event.data);
          if (
            typeof message === "object" &&
            message !== null &&
            "type" in message &&
            ((message as { type: string }).type === "world.updated" ||
              (message as { type: string }).type === "world.tick" ||
              (message as { type: string }).type === "intel.action" ||
              (message as { type: string }).type === "operation.planned")
          ) {
            void hydrate();
          }
        } catch {
          // Ignore malformed realtime messages; the REST state remains authoritative.
        }
      };
      socket.onclose = () => {
        if (!disposed) {
          reconnectTimer = window.setTimeout(connect, 2_000);
        }
      };
    };

    connect();
    return () => {
      disposed = true;
      if (reconnectTimer !== undefined) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [hydrate]);

  return null;
}
