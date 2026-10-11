"use client";

import { useEffect } from "react";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { getWebSocketUrl } from "@/lib/ws-client";

const RECONNECT_DELAY_MS = 2_000;
// Only runs while the websocket is down; once it's open, pushed ticks take over.
const FALLBACK_POLL_MS = 5_000;

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
    let pollTimer: number | undefined;
    let socket: WebSocket | undefined;

    const startPolling = () => {
      if (pollTimer !== undefined) return;
      pollTimer = window.setInterval(() => void hydrate(), FALLBACK_POLL_MS);
    };

    const stopPolling = () => {
      if (pollTimer === undefined) return;
      window.clearInterval(pollTimer);
      pollTimer = undefined;
    };

    const connect = () => {
      socket = new WebSocket(getWebSocketUrl());
      socket.onopen = () => {
        stopPolling();
      };
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
        // The cleanup function below also closes the socket, which fires this handler
        // after `disposed` is already true — without this guard it would restart a
        // polling interval that nothing will ever clear again.
        if (disposed) return;
        startPolling();
        reconnectTimer = window.setTimeout(connect, RECONNECT_DELAY_MS);
      };
    };

    // Poll immediately so the UI stays live while the first connection is pending.
    startPolling();
    connect();
    return () => {
      disposed = true;
      stopPolling();
      if (reconnectTimer !== undefined) window.clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [hydrate]);

  return null;
}
