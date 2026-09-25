import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";
import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { TimeControls } from "./time-controls";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getWorldState: vi.fn(),
    updateWorldClock: vi.fn(),
    advanceWorld: vi.fn(),
    resetWorld: vi.fn(),
    planOperation: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient, { deep: true });

describe("TimeControls", () => {
  const initialState = useSimulationStore.getState();

  beforeEach(() => {
    useSimulationStore.setState(initialState, true);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders the current game time, crisis start, and speed options", () => {
    useSimulationStore.setState({ gameMinutes: 65, crisisStartLabel: "2026-06-01 00:00Z" });
    render(<TimeControls />);

    expect(screen.getByText("D+001 01:05Z")).toBeInTheDocument();
    expect(screen.getByText("Початок кризи: 2026-06-01 00:00Z")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "1x" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "2x" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "4x" })).toBeInTheDocument();
  });

  it("shows 'Продовжити' while paused and toggles the clock through the store", async () => {
    useSimulationStore.setState({ isPaused: true });
    mockedApiClient.updateWorldClock.mockResolvedValue({
      clock: {
        world_id: 1,
        game_minutes: 0,
        is_paused: false,
        speed: 1,
        ticks_elapsed: 0,
        crisis_start_label: "",
        tick_game_minutes: 10,
      },
      events: [],
      intel_reports: [],
      assets: [],
      operations: [],
    });

    const user = userEvent.setup();
    render(<TimeControls />);

    await user.click(screen.getByRole("button", { name: "Продовжити" }));

    expect(mockedApiClient.updateWorldClock).toHaveBeenCalledWith({ is_paused: false });
  });

  it("advances time by 60 or 360 minutes through the store", async () => {
    mockedApiClient.advanceWorld.mockResolvedValue({
      clock: {
        world_id: 1,
        game_minutes: 360,
        is_paused: true,
        speed: 1,
        ticks_elapsed: 0,
        crisis_start_label: "",
        tick_game_minutes: 10,
      },
      ticks_run: 6,
      new_events: [],
      new_intel_reports: [],
      events: [],
      intel_reports: [],
      assets: [],
      operations: [],
    });

    const user = userEvent.setup();
    render(<TimeControls />);

    await user.click(screen.getByRole("button", { name: "+6 годин" }));

    expect(mockedApiClient.advanceWorld).toHaveBeenCalledWith(360);
  });

  it("selects a new speed through the store and highlights the active one", async () => {
    useSimulationStore.setState({ speed: 1 });
    mockedApiClient.updateWorldClock.mockResolvedValue({
      clock: {
        world_id: 1,
        game_minutes: 0,
        is_paused: true,
        speed: 4,
        ticks_elapsed: 0,
        crisis_start_label: "",
        tick_game_minutes: 10,
      },
      events: [],
      intel_reports: [],
      assets: [],
      operations: [],
    });

    const user = userEvent.setup();
    render(<TimeControls />);

    await user.click(screen.getByRole("button", { name: "4x" }));

    expect(mockedApiClient.updateWorldClock).toHaveBeenCalledWith({ speed: 4 });
    expect(useSimulationStore.getState().speed).toBe(4);
  });
});
