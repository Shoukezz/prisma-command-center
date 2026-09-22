import { getWsUrl } from "@/lib/env";

/** WebSocket URL for realtime feeds — Phase 1.4+ */
export function getWebSocketUrl(path = "/ws"): string {
  const base = getWsUrl().replace(/\/$/, "");
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}
