import type { WorldStateDto } from "@prisma/shared";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";

import { useSimulationStore } from "./simulation-store";

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

function makeWorldStateDto(overrides: Partial<WorldStateDto> = {}): WorldStateDto {
  return {
    clock: {
      world_id: 1,
      game_minutes: 90,
      is_paused: true,
      speed: 1,
      ticks_elapsed: 3,
      crisis_start_label: "2026-06-01 00:00Z",
      tick_game_minutes: 10,
    },
    events: [],
    intel_reports: [],
    assets: [],
    operations: [],
    ...overrides,
  } as WorldStateDto;
}

describe("useSimulationStore", () => {
  const initialState = useSimulationStore.getState();

  beforeEach(() => {
    useSimulationStore.setState(initialState, true);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("hydrates from the API and marks the store hydrated", async () => {
    mockedApiClient.getWorldState.mockResolvedValue(
      makeWorldStateDto({ clock: { ...makeWorldStateDto().clock, game_minutes: 90 } }),
    );

    await useSimulationStore.getState().hydrate();

    const state = useSimulationStore.getState();
    expect(state.isHydrated).toBe(true);
    expect(state.isSyncing).toBe(false);
    expect(state.gameMinutes).toBe(90);
    expect(state.syncError).toBeNull();
  });

  it("records a sync error and still marks hydrated when the API call fails", async () => {
    mockedApiClient.getWorldState.mockRejectedValue(new Error("network down"));

    await useSimulationStore.getState().hydrate();

    const state = useSimulationStore.getState();
    expect(state.isHydrated).toBe(true);
    expect(state.isSyncing).toBe(false);
    expect(state.syncError).toBe("network down");
  });

  it("togglePaused flips the current isPaused value through setPaused", async () => {
    useSimulationStore.setState({ isPaused: true });
    mockedApiClient.updateWorldClock.mockResolvedValue(
      makeWorldStateDto({
        clock: { ...makeWorldStateDto().clock, is_paused: false },
      }),
    );

    await useSimulationStore.getState().togglePaused();

    expect(mockedApiClient.updateWorldClock).toHaveBeenCalledWith({ is_paused: false });
    expect(useSimulationStore.getState().isPaused).toBe(false);
  });

  it("selecting an event clears any selected intel report, and vice versa", () => {
    useSimulationStore.getState().selectIntel("intel-1");
    expect(useSimulationStore.getState().selectedIntelId).toBe("intel-1");

    useSimulationStore.getState().selectEvent("evt-1");
    expect(useSimulationStore.getState().selectedEventId).toBe("evt-1");
    expect(useSimulationStore.getState().selectedIntelId).toBeNull();

    useSimulationStore.getState().selectIntel("intel-2");
    expect(useSimulationStore.getState().selectedIntelId).toBe("intel-2");
    expect(useSimulationStore.getState().selectedEventId).toBeNull();
  });

  it("advanceTime is a no-op for zero or negative deltas", async () => {
    await useSimulationStore.getState().advanceTime(0);
    await useSimulationStore.getState().advanceTime(-5);

    expect(mockedApiClient.advanceWorld).not.toHaveBeenCalled();
  });

  it("advanceTime calls the API and applies the returned world state", async () => {
    mockedApiClient.advanceWorld.mockResolvedValue({
      ...makeWorldStateDto({ clock: { ...makeWorldStateDto().clock, game_minutes: 150 } }),
      ticks_run: 6,
      new_events: [],
      new_intel_reports: [],
    });

    await useSimulationStore.getState().advanceTime(60);

    expect(mockedApiClient.advanceWorld).toHaveBeenCalledWith(60);
    expect(useSimulationStore.getState().gameMinutes).toBe(150);
  });

  it("resetWorld clears the current selection and reports success", async () => {
    useSimulationStore.setState({ selectedEventId: "evt-1", selectedIntelId: "intel-1" });
    mockedApiClient.resetWorld.mockResolvedValue(makeWorldStateDto());

    const didReset = await useSimulationStore.getState().resetWorld();

    expect(didReset).toBe(true);
    expect(useSimulationStore.getState().selectedEventId).toBeNull();
    expect(useSimulationStore.getState().selectedIntelId).toBeNull();
  });

  it("resetWorld reports failure and keeps the sync error on API failure", async () => {
    mockedApiClient.resetWorld.mockRejectedValue(new Error("reset failed"));

    const didReset = await useSimulationStore.getState().resetWorld();

    expect(didReset).toBe(false);
    expect(useSimulationStore.getState().syncError).toBe("reset failed");
  });
});
