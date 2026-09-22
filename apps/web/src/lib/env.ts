function localServiceUrl(port: number, protocol: "http" | "ws"): string {
  const host = typeof window === "undefined" ? "127.0.0.1" : window.location.hostname;
  return `${protocol}://${host}:${port}`;
}

export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? localServiceUrl(8000, "http");
}

export function getWsUrl(): string {
  return process.env.NEXT_PUBLIC_WS_URL ?? localServiceUrl(8000, "ws");
}
