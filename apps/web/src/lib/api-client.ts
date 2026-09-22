import type {
  AdvanceResultDto,
  HealthResponse,
  IntelligenceActionDto,
  OperationDto,
  PlanOperationDto,
  WorldStateDto,
} from "@prisma/shared";
import { API_ROUTES } from "@prisma/shared";

import { getApiUrl } from "@/lib/env";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getApiUrl()}${path}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(`Request failed: ${response.statusText}`, response.status);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  health: () => request<HealthResponse>(API_ROUTES.health),

  getWorldState: () => request<WorldStateDto>(API_ROUTES.worldState),

  advanceWorld: (minutes: number) =>
    request<AdvanceResultDto>(API_ROUTES.worldAdvance, {
      method: "POST",
      body: JSON.stringify({ minutes }),
    }),

  updateWorldClock: (payload: { is_paused?: boolean; speed?: number }) =>
    request<WorldStateDto>(API_ROUTES.worldClock, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  resetWorld: () =>
    request<WorldStateDto>(API_ROUTES.worldReset, {
      method: "POST",
    }),

  planOperation: (payload: PlanOperationDto) =>
    request<OperationDto>(API_ROUTES.operationsPlan, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  takeIntelligenceAction: (
    reportId: string,
    payload: { action_type: string; reason?: string },
  ) =>
    request<IntelligenceActionDto>(API_ROUTES.intelligenceReportAction(reportId), {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
