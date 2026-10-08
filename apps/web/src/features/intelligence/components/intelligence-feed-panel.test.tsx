import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { IntelligenceFeedPanel } from "./intelligence-feed-panel";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getWorldState: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient, { deep: true });

const baseReport = {
  id: "intel-1",
  gameMinutes: 0,
  source: "SATINT" as const,
  confidence: 70,
  title: "Recon pass over the strait",
  summary: "Unusual troop movement spotted.",
  region: "Northern strait",
  coordinates: { lat: 0, lng: 0 },
};

describe("IntelligenceFeedPanel", () => {
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
    render(<IntelligenceFeedPanel />);

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

    render(<IntelligenceFeedPanel />);

    expect(mockedApiClient.getWorldState).toHaveBeenCalledTimes(1);
  });

  it("shows the empty state once hydrated with no reports", () => {
    useSimulationStore.setState({ isHydrated: true, intelReports: [] });
    render(<IntelligenceFeedPanel />);

    expect(screen.getByText("Звітів немає.")).toBeInTheDocument();
  });

  it("shows an error state with a retry action when hydration failed and there is no cached data", () => {
    useSimulationStore.setState({
      isHydrated: true,
      intelReports: [],
      syncError: "Не вдалося завантажити симуляцію",
    });
    render(<IntelligenceFeedPanel />);

    expect(screen.getByText("Не вдалося завантажити симуляцію")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Спробувати знову" })).toBeInTheDocument();
  });

  it("keeps showing cached reports instead of the error state when a later sync fails", () => {
    useSimulationStore.setState({
      isHydrated: true,
      intelReports: [baseReport],
      syncError: "Не вдалося оновити час",
    });
    render(<IntelligenceFeedPanel />);

    expect(screen.getByText("Recon pass over the strait")).toBeInTheDocument();
    expect(screen.queryByText("Не вдалося оновити час")).not.toBeInTheDocument();
  });

  it("renders the report list once hydrated with data", () => {
    useSimulationStore.setState({ isHydrated: true, intelReports: [baseReport], syncError: null });
    render(<IntelligenceFeedPanel />);

    expect(screen.getByText("Recon pass over the strait")).toBeInTheDocument();
  });
});
