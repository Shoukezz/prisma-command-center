import { create } from "zustand";

import { CRISIS_START_LABEL } from "@/features/command-center/mock/initial-state";
import { mapWorldState } from "@/features/command-center/lib/api-mappers";
import type {
  Asset,
  IntelReport,
  Operation,
  OperationType,
  SimulationSpeed,
  WorldEvent,
} from "@/features/command-center/types";
import { apiClient } from "@/lib/api-client";

interface SimulationState {
  gameMinutes: number;
  isPaused: boolean;
  speed: SimulationSpeed;
  crisisStartLabel: string;
  events: WorldEvent[];
  intelReports: IntelReport[];
  assets: Asset[];
  operations: Operation[];
  selectedEventId: string | null;
  selectedIntelId: string | null;
  isHydrated: boolean;
  isSyncing: boolean;
  syncError: string | null;

  hydrate: () => Promise<void>;
  setPaused: (paused: boolean) => Promise<void>;
  togglePaused: () => Promise<void>;
  setSpeed: (speed: SimulationSpeed) => Promise<void>;
  selectEvent: (id: string | null) => void;
  selectIntel: (id: string | null) => void;
  advanceTime: (deltaMinutes: number) => Promise<void>;
  resetWorld: () => Promise<boolean>;
  planOperation: (
    operationType: OperationType,
    intelReportId: string,
    assetId: string,
  ) => Promise<void>;
}

function applyWorldState(
  set: (partial: Partial<SimulationState>) => void,
  mapped: ReturnType<typeof mapWorldState>,
) {
  set({
    gameMinutes: mapped.gameMinutes,
    isPaused: mapped.isPaused,
    speed: mapped.speed,
    crisisStartLabel: mapped.crisisStartLabel,
    events: mapped.events,
    intelReports: mapped.intelReports,
    assets: mapped.assets,
    operations: mapped.operations,
    isHydrated: true,
    syncError: null,
  });
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  gameMinutes: 0,
  isPaused: true,
  speed: 1,
  crisisStartLabel: CRISIS_START_LABEL,
  events: [],
  intelReports: [],
  assets: [],
  operations: [],
  selectedEventId: null,
  selectedIntelId: null,
  isHydrated: false,
  isSyncing: false,
  syncError: null,

  hydrate: async () => {
    set({ isSyncing: true, syncError: null });
    try {
      const state = await apiClient.getWorldState();
      applyWorldState(set, mapWorldState(state));
    } catch (err) {
      set({
        syncError: err instanceof Error ? err.message : "Не вдалося завантажити симуляцію",
        isHydrated: true,
      });
    } finally {
      set({ isSyncing: false });
    }
  },

  setPaused: async (paused) => {
    set({ isSyncing: true, syncError: null });
    try {
      const state = await apiClient.updateWorldClock({ is_paused: paused });
      applyWorldState(set, mapWorldState(state));
    } catch (err) {
      set({ syncError: err instanceof Error ? err.message : "Не вдалося оновити час" });
    } finally {
      set({ isSyncing: false });
    }
  },

  togglePaused: async () => {
    await get().setPaused(!get().isPaused);
  },

  setSpeed: async (speed) => {
    set({ isSyncing: true, syncError: null });
    try {
      const state = await apiClient.updateWorldClock({ speed });
      applyWorldState(set, mapWorldState(state));
    } catch (err) {
      set({ syncError: err instanceof Error ? err.message : "Не вдалося оновити швидкість" });
    } finally {
      set({ isSyncing: false });
    }
  },

  selectEvent: (id) =>
    set({
      selectedEventId: id,
      selectedIntelId: id ? null : get().selectedIntelId,
    }),

  selectIntel: (id) =>
    set({
      selectedIntelId: id,
      selectedEventId: id ? null : get().selectedEventId,
    }),

  advanceTime: async (deltaMinutes) => {
    if (deltaMinutes <= 0) return;
    set({ isSyncing: true, syncError: null });
    try {
      const result = await apiClient.advanceWorld(deltaMinutes);
      applyWorldState(set, mapWorldState(result));
    } catch (err) {
      set({ syncError: err instanceof Error ? err.message : "Не вдалося просунути час" });
    } finally {
      set({ isSyncing: false });
    }
  },

  resetWorld: async () => {
    set({ isSyncing: true, syncError: null });
    try {
      const state = await apiClient.resetWorld();
      applyWorldState(set, mapWorldState(state));
      set({ selectedEventId: null, selectedIntelId: null });
      return true;
    } catch (err) {
      set({ syncError: err instanceof Error ? err.message : "Не вдалося почати нову гру" });
      return false;
    } finally {
      set({ isSyncing: false });
    }
  },

  planOperation: async (operationType, intelReportId, assetId) => {
    set({ isSyncing: true, syncError: null });
    try {
      await apiClient.planOperation({
        operation_type: operationType,
        intel_report_id: intelReportId,
        asset_id: assetId,
      });
      const state = await apiClient.getWorldState();
      applyWorldState(set, mapWorldState(state));
    } catch (err) {
      set({ syncError: err instanceof Error ? err.message : "Не вдалося спланувати операцію" });
    } finally {
      set({ isSyncing: false });
    }
  },
}));
