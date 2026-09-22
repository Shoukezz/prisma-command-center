export const API_PREFIX = "/api/v1" as const;

export const API_ROUTES = {
  health: `${API_PREFIX}/health`,
  auth: `${API_PREFIX}/auth`,
  world: `${API_PREFIX}/world`,
  worldState: `${API_PREFIX}/world/state`,
  worldAdvance: `${API_PREFIX}/world/advance`,
  worldClock: `${API_PREFIX}/world/clock`,
  worldReset: `${API_PREFIX}/world/reset`,
  worldGeography: `${API_PREFIX}/world/geography`,
  events: `${API_PREFIX}/events`,
  intelligenceReports: `${API_PREFIX}/intelligence/reports`,
  intelligenceReportAction: (reportId: string) =>
    `${API_PREFIX}/intelligence/reports/${reportId}/action`,
  operations: `${API_PREFIX}/operations`,
  operationsPlan: `${API_PREFIX}/operations/plan`,
  assets: `${API_PREFIX}/operations/assets`,
  analysts: `${API_PREFIX}/analysts`,
  sessions: `${API_PREFIX}/sessions`,
} as const;
