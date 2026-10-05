import { act, cleanup, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "@/lib/api-client";

import { useSimulationStore } from "@/features/command-center/stores/simulation-store";
import { SimulationHydrator } from "./simulation-hydrator";

vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getWorldState: vi.fn(),
  },
}));

const mockedApiClient = vi.mocked(apiClient, { deep: true });

class RecordingWebSocket {
  static instances: RecordingWebSocket[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(public url: string) {
    RecordingWebSocket.instances.push(this);
  }

  close() {
    this.onclose?.();
  }

  send() {}
}

describe("SimulationHydrator", () => {
  const initialState = useSimulationStore.getState();

  beforeEach(() => {
    vi.useFakeTimers();
    RecordingWebSocket.instances = [];
    vi.stubGlobal("WebSocket", RecordingWebSocket);
    // isHydrated: true skips the mount-time hydrate() so only the
    // websocket/poll lifecycle under test drives getWorldState calls.
    useSimulationStore.setState({ ...initialState, isHydrated: true }, true);
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
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it("polls world state on an interval while the websocket is still connecting", async () => {
    render(<SimulationHydrator />);
    const callsBefore = mockedApiClient.getWorldState.mock.calls.length;

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });

    expect(mockedApiClient.getWorldState.mock.calls.length).toBeGreaterThan(callsBefore);
  });

  it("stops polling once the websocket opens, and resumes polling after it drops", async () => {
    render(<SimulationHydrator />);
    const socket = RecordingWebSocket.instances[0];

    act(() => socket.onopen?.());
    const callsAfterOpen = mockedApiClient.getWorldState.mock.calls.length;

    await act(async () => {
      await vi.advanceTimersByTimeAsync(10_000);
    });
    expect(mockedApiClient.getWorldState.mock.calls.length).toBe(callsAfterOpen);

    act(() => socket.onclose?.());
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });
    expect(mockedApiClient.getWorldState.mock.calls.length).toBeGreaterThan(callsAfterOpen);
  });

  it("re-hydrates when a world.tick message is pushed over the websocket", async () => {
    render(<SimulationHydrator />);
    const socket = RecordingWebSocket.instances[0];
    act(() => socket.onopen?.());

    const callsBefore = mockedApiClient.getWorldState.mock.calls.length;
    await act(async () => {
      socket.onmessage?.({ data: JSON.stringify({ type: "world.tick", payload: {} }) } as MessageEvent);
    });

    expect(mockedApiClient.getWorldState.mock.calls.length).toBe(callsBefore + 1);
  });
});
