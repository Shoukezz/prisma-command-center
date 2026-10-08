import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { OperationsQueuePanel } from "./operations-queue-panel";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getWorldState: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient, { deep: true });

const baseOperation = {
  id: "op-1",
  operationType: "recon" as const,
  status: "active" as const,
  regionName: "Northern strait",
  intelConfidence: 70,
  startedAt: 0,
  completesAt: 60,
  durationMinutes: 60,
  assetId: "asset-1",
  assetName: "Drone 1",
  intelReportId: "intel-1",
  result: null,
};

describe("OperationsQueuePanel", () => {
  const initialState = useSimulationStore.getState();

  beforeEach(() => {
    useSimulationStore.setState(initialState, true);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows a loading skeleton before the store has hydrated", () => {
    useSimulationStore.setState({ isHydrated: false });
    render(<OperationsQueuePanel />);

    expect(screen.getByRole("status", { name: "Завантаження" })).toBeInTheDocument();
  });

  it("hydrates itself on mount when rendered standalone and not yet hydrated", () => {
    mockedApiClient.getWorldState.mockResolvedValue({
      clock: {
        world_id: 1,
        game_minutes: 0,
        is_paused: true,
        speed: 1,
        ticks_elapsed: 0,
        crisis_start_label: "2026-06-01 00:00Z",
        tick_game_minutes: 10,
      },
      events: [],
      intel_reports: [],
      assets: [],
      operations: [],
    });
    useSimulationStore.setState({ isHydrated: false, isSyncing: false });

    render(<OperationsQueuePanel />);

    expect(mockedApiClient.getWorldState).toHaveBeenCalledTimes(1);
  });

  it("shows the empty state once hydrated with no operations", () => {
    useSimulationStore.setState({ isHydrated: true, operations: [] });
    render(<OperationsQueuePanel />);

    expect(screen.getByText("У черзі немає операцій.")).toBeInTheDocument();
  });

  it("shows an error state with a retry action when hydration failed and there is no cached data", () => {
    useSimulationStore.setState({
      isHydrated: true,
      operations: [],
      syncError: "Не вдалося завантажити симуляцію",
    });
    render(<OperationsQueuePanel />);

    expect(screen.getByText("Не вдалося завантажити симуляцію")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Спробувати знову" })).toBeInTheDocument();
  });

  it("keeps showing cached operations instead of the error state when a later sync fails", () => {
    useSimulationStore.setState({
      isHydrated: true,
      operations: [baseOperation],
      syncError: "Не вдалося спланувати операцію",
    });
    render(<OperationsQueuePanel />);

    expect(screen.getByText("Drone 1 → Northern strait")).toBeInTheDocument();
    expect(screen.queryByText("Не вдалося спланувати операцію")).not.toBeInTheDocument();
  });

  it("renders the operation list once hydrated with data", () => {
    useSimulationStore.setState({ isHydrated: true, operations: [baseOperation], syncError: null });
    render(<OperationsQueuePanel />);

    expect(screen.getByText("Drone 1 → Northern strait")).toBeInTheDocument();
  });
});
