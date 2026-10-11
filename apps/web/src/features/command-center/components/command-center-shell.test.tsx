import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { CommandCenterShell } from "./command-center-shell";

// The strategic map mounts a real Leaflet instance via next/dynamic, which needs a
// real browser layout engine — irrelevant to what this test verifies, so it's stubbed.
vi.mock("@/features/command-center/components/strategic-map", () => ({
  StrategicMap: () => <div data-testid="strategic-map-stub" />,
}));

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

describe("CommandCenterShell", () => {
  const initialState = useSimulationStore.getState();

  beforeEach(() => {
    // isHydrated: true stops SimulationHydrator from firing its async hydrate()
    // on mount, which would otherwise resolve after each test's assertions run.
    useSimulationStore.setState({ ...initialState, isHydrated: true }, true);
    mockedApiClient.getWorldState.mockResolvedValue({
      clock: {
        world_id: 1,
        game_minutes: 90,
        is_paused: true,
        speed: 1,
        ticks_elapsed: 1,
        crisis_start_label: "2026-06-01 00:00Z",
        tick_game_minutes: 10,
      },
      events: [],
      intel_reports: [],
      assets: [],
      operations: [],
    });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders the header, the formatted clock, and every main panel", () => {
    render(<CommandCenterShell>{null}</CommandCenterShell>);

    expect(screen.getByText("PRISMA")).toBeInTheDocument();
    // Rendered in both the header clock and the TimeControls panel below it.
    expect(screen.getAllByText("D+001 00:00Z")).toHaveLength(2);
    expect(screen.getByTestId("strategic-map-stub")).toBeInTheDocument();
    expect(screen.getByText("Стрічка подій")).toBeInTheDocument();
    expect(screen.getByText("Керування часом")).toBeInTheDocument();
  });

  it("shows the paused badge and offers a start action when the clock is paused", () => {
    useSimulationStore.setState({ isPaused: true });
    render(<CommandCenterShell>{null}</CommandCenterShell>);

    expect(screen.getByText("Пауза")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ЗАПУСТИТИ" })).toBeInTheDocument();
  });

  it("shows the live badge and offers a pause action when the clock is running", () => {
    useSimulationStore.setState({ isPaused: false });
    render(<CommandCenterShell>{null}</CommandCenterShell>);

    expect(screen.getByText("Наживо")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ПАУЗА" })).toBeInTheDocument();
  });

  it("surfaces a sync error indicator when the store reports one", () => {
    useSimulationStore.setState({ syncError: "Не вдалося завантажити симуляцію" });
    render(<CommandCenterShell>{null}</CommandCenterShell>);

    expect(screen.getByTitle("Не вдалося завантажити симуляцію")).toBeInTheDocument();
  });

  describe("world reset", () => {
    const originalLocation = window.location;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- vi.spyOn's overload return type can't be named ahead of the call it types.
    let confirmSpy: any;
    let reloadSpy: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      confirmSpy = vi.spyOn(window, "confirm");
      reloadSpy = vi.fn();
      Object.defineProperty(window, "location", {
        configurable: true,
        value: { ...originalLocation, reload: reloadSpy },
      });
    });

    afterEach(() => {
      confirmSpy.mockRestore();
      Object.defineProperty(window, "location", {
        configurable: true,
        value: originalLocation,
      });
    });

    it("does nothing when the reset confirmation is declined", async () => {
      const user = userEvent.setup();
      confirmSpy.mockReturnValue(false);
      render(<CommandCenterShell>{null}</CommandCenterShell>);

      await user.click(screen.getByRole("button", { name: "НОВА ГРА" }));

      expect(confirmSpy).toHaveBeenCalledWith("Почати нову гру? Поточний прогрес буде скинуто.");
      expect(mockedApiClient.resetWorld).not.toHaveBeenCalled();
      expect(reloadSpy).not.toHaveBeenCalled();
    });

    it("resets the world, clears onboarding state, and reloads once confirmed", async () => {
      const user = userEvent.setup();
      confirmSpy.mockReturnValue(true);
      window.localStorage.setItem("prisma-onboarding-complete", "true");
      mockedApiClient.resetWorld.mockResolvedValue({
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
      render(<CommandCenterShell>{null}</CommandCenterShell>);

      await user.click(screen.getByRole("button", { name: "НОВА ГРА" }));

      expect(mockedApiClient.resetWorld).toHaveBeenCalledTimes(1);
      await vi.waitFor(() => expect(reloadSpy).toHaveBeenCalledTimes(1));
      expect(window.localStorage.getItem("prisma-onboarding-complete")).toBeNull();
    });

    it("keeps onboarding state and does not reload when the reset request fails", async () => {
      const user = userEvent.setup();
      confirmSpy.mockReturnValue(true);
      window.localStorage.setItem("prisma-onboarding-complete", "true");
      mockedApiClient.resetWorld.mockRejectedValue(new Error("reset failed"));
      render(<CommandCenterShell>{null}</CommandCenterShell>);

      await user.click(screen.getByRole("button", { name: "НОВА ГРА" }));

      await vi.waitFor(() => expect(mockedApiClient.resetWorld).toHaveBeenCalledTimes(1));
      expect(reloadSpy).not.toHaveBeenCalled();
      expect(window.localStorage.getItem("prisma-onboarding-complete")).toBe("true");
    });
  });
});
