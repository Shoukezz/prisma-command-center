import type {
  AssetDto,
  EventDto,
  IntelReportDto,
  OperationDto,
  WorldStateDto,
} from "@prisma/shared";
import { describe, expect, it } from "vitest";

import {
  mapAssetDto,
  mapEventDto,
  mapIntelDto,
  mapOperationDto,
  mapWorldState,
} from "./api-mappers";

const coordinates = { lat: 50.45, lng: 30.52 };

function makeEventDto(overrides: Partial<EventDto> = {}): EventDto {
  return {
    id: "evt-1",
    game_minutes: 120,
    title: "Border incursion reported",
    summary: "Unconfirmed movement near the frontier.",
    severity: "high",
    event_type: "military",
    region: "Northern Sector",
    country: "Ruritania",
    coordinates,
    ...overrides,
  };
}

function makeIntelReportDto(overrides: Partial<IntelReportDto> = {}): IntelReportDto {
  return {
    id: "intel-1",
    title: "Satellite pass confirms convoy",
    description: "Thermal imagery shows a column of vehicles.",
    source: "SATINT",
    confidence: 72,
    timestamp: 130,
    region: "Northern Sector",
    coordinates,
    ...overrides,
  };
}

function makeAssetDto(overrides: Partial<AssetDto> = {}): AssetDto {
  return {
    id: "asset-1",
    name: "Recon Drone Alpha",
    asset_type: "drone",
    status: "available",
    supports_recon: true,
    supports_strike: false,
    ...overrides,
  };
}

function makeOperationDto(overrides: Partial<OperationDto> = {}): OperationDto {
  return {
    id: "op-1",
    operation_type: "recon",
    status: "planned",
    region_name: "Northern Sector",
    intel_confidence: 72,
    started_at: 130,
    completes_at: 190,
    duration_minutes: 60,
    asset_id: "asset-1",
    asset_name: "Recon Drone Alpha",
    intel_report_id: "intel-1",
    result: null,
    ...overrides,
  };
}

describe("mapEventDto", () => {
  it("maps snake_case fields to the camelCase view model", () => {
    expect(mapEventDto(makeEventDto())).toEqual({
      id: "evt-1",
      gameMinutes: 120,
      title: "Border incursion reported",
      summary: "Unconfirmed movement near the frontier.",
      severity: "high",
      region: "Northern Sector",
      coordinates,
    });
  });
});

describe("mapIntelDto", () => {
  it("prefers the current description and timestamp fields", () => {
    const mapped = mapIntelDto(makeIntelReportDto());
    expect(mapped.summary).toBe("Thermal imagery shows a column of vehicles.");
    expect(mapped.gameMinutes).toBe(130);
  });

  it("falls back to the deprecated summary and game_minutes fields when present", () => {
    const mapped = mapIntelDto(
      makeIntelReportDto({
        description: undefined,
        summary: "Legacy summary text",
        timestamp: undefined,
        game_minutes: 45,
      }),
    );
    expect(mapped.summary).toBe("Legacy summary text");
    expect(mapped.gameMinutes).toBe(45);
  });

  it("defaults to empty values when neither current nor legacy fields exist", () => {
    const mapped = mapIntelDto(
      makeIntelReportDto({ description: undefined, timestamp: undefined }),
    );
    expect(mapped.summary).toBe("");
    expect(mapped.gameMinutes).toBe(0);
  });

  it("maps analyst assessments and defaults to an empty array when absent", () => {
    expect(mapIntelDto(makeIntelReportDto()).analystAssessments).toEqual([]);

    const mapped = mapIntelDto(
      makeIntelReportDto({
        analyst_assessments: [
          {
            id: "assess-1",
            analyst_id: "analyst-1",
            analyst_name: "J. Okafor",
            specialty: "signals_intelligence",
            bias: "worst_case",
            reliability: 0.8,
            assessment: "Likely a resupply convoy, not an offensive posture.",
            assessed_confidence: 60,
            timestamp: 135,
          },
        ],
      }),
    );
    expect(mapped.analystAssessments).toEqual([
      {
        id: "assess-1",
        analystId: "analyst-1",
        analystName: "J. Okafor",
        specialty: "Signals Intelligence",
        bias: "worst case",
        reliability: 0.8,
        assessment: "Likely a resupply convoy, not an offensive posture.",
        assessedConfidence: 60,
        timestamp: 135,
      },
    ]);
  });
});

describe("mapAssetDto", () => {
  it("maps snake_case fields to the camelCase view model", () => {
    expect(mapAssetDto(makeAssetDto())).toEqual({
      id: "asset-1",
      name: "Recon Drone Alpha",
      assetType: "drone",
      status: "available",
      supportsRecon: true,
      supportsStrike: false,
    });
  });
});

describe("mapOperationDto", () => {
  it("maps a planned operation with no result yet", () => {
    expect(mapOperationDto(makeOperationDto()).result).toBeNull();
  });

  it("maps a completed operation's result", () => {
    const mapped = mapOperationDto(
      makeOperationDto({
        status: "completed",
        result: {
          success: true,
          outcome_summary: "Convoy identified, no engagement.",
          confidence_at_planning: 72,
          completed_at: 190,
        },
      }),
    );
    expect(mapped.result).toEqual({
      success: true,
      outcomeSummary: "Convoy identified, no engagement.",
      confidenceAtPlanning: 72,
      completedAt: 190,
    });
  });
});

describe("mapWorldState", () => {
  function makeWorldStateDto(overrides: Partial<WorldStateDto> = {}): WorldStateDto {
    return {
      clock: {
        world_id: 1,
        game_minutes: 130,
        is_paused: false,
        speed: 2,
        ticks_elapsed: 4,
        crisis_start_label: "2026-06-01 00:00Z",
        tick_game_minutes: 10,
      },
      events: [makeEventDto()],
      intel_reports: [makeIntelReportDto()],
      assets: [makeAssetDto()],
      operations: [makeOperationDto()],
      ...overrides,
    };
  }

  it("maps clock fields and every nested collection", () => {
    const mapped = mapWorldState(makeWorldStateDto());
    expect(mapped.gameMinutes).toBe(130);
    expect(mapped.isPaused).toBe(false);
    expect(mapped.speed).toBe(2);
    expect(mapped.crisisStartLabel).toBe("2026-06-01 00:00Z");
    expect(mapped.events).toHaveLength(1);
    expect(mapped.intelReports).toHaveLength(1);
    expect(mapped.assets).toHaveLength(1);
    expect(mapped.operations).toHaveLength(1);
  });

  it("defaults assets and operations to an empty array when the API omits them", () => {
    const mapped = mapWorldState(
      makeWorldStateDto({ assets: undefined, operations: undefined }),
    );
    expect(mapped.assets).toEqual([]);
    expect(mapped.operations).toEqual([]);
  });
});
