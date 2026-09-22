import type {
  AdvanceResultDto,
  AnalystAssessmentDto,
  AssetDto,
  EventDto,
  IntelReportDto,
  OperationDto,
  WorldStateDto,
} from "@prisma/shared";

import type {
  AnalystAssessment,
  Asset,
  AssetStatus,
  EventSeverity,
  IntelReport,
  IntelSource,
  Operation,
  OperationStatus,
  OperationType,
  WorldEvent,
} from "@/features/command-center/types";

function formatSpecialty(specialty: string): string {
  return specialty
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function mapAssessmentDto(dto: AnalystAssessmentDto): AnalystAssessment {
  return {
    id: dto.id,
    analystId: dto.analyst_id,
    analystName: dto.analyst_name,
    specialty: formatSpecialty(dto.specialty),
    bias: dto.bias.replace(/_/g, " "),
    reliability: dto.reliability,
    assessment: dto.assessment,
    assessedConfidence: dto.assessed_confidence,
    timestamp: dto.timestamp,
  };
}

export function mapEventDto(dto: EventDto): WorldEvent {
  return {
    id: dto.id,
    gameMinutes: dto.game_minutes,
    title: dto.title,
    summary: dto.summary,
    severity: dto.severity as EventSeverity,
    region: dto.region,
    coordinates: dto.coordinates,
  };
}

export function mapIntelDto(dto: IntelReportDto): IntelReport {
  const timestamp = dto.timestamp ?? dto.game_minutes ?? 0;
  const description = dto.description ?? dto.summary ?? "";
  return {
    id: dto.id,
    gameMinutes: timestamp,
    source: dto.source as IntelSource,
    confidence: dto.confidence,
    title: dto.title,
    summary: description,
    region: dto.region,
    coordinates: dto.coordinates,
    analystAssessments: (dto.analyst_assessments ?? []).map(mapAssessmentDto),
  };
}

export function mapAssetDto(dto: AssetDto): Asset {
  return {
    id: dto.id,
    name: dto.name,
    assetType: dto.asset_type,
    status: dto.status as AssetStatus,
    supportsRecon: dto.supports_recon,
    supportsStrike: dto.supports_strike,
  };
}

export function mapOperationDto(dto: OperationDto): Operation {
  return {
    id: dto.id,
    operationType: dto.operation_type as OperationType,
    status: dto.status as OperationStatus,
    regionName: dto.region_name,
    intelConfidence: dto.intel_confidence,
    startedAt: dto.started_at,
    completesAt: dto.completes_at,
    durationMinutes: dto.duration_minutes,
    assetId: dto.asset_id,
    assetName: dto.asset_name,
    intelReportId: dto.intel_report_id,
    result: dto.result
      ? {
          success: dto.result.success,
          outcomeSummary: dto.result.outcome_summary,
          confidenceAtPlanning: dto.result.confidence_at_planning,
          completedAt: dto.result.completed_at,
        }
      : null,
  };
}

export function mapWorldState(dto: WorldStateDto | AdvanceResultDto) {
  return {
    gameMinutes: dto.clock.game_minutes,
    isPaused: dto.clock.is_paused,
    speed: dto.clock.speed as 1 | 2 | 4,
    crisisStartLabel: dto.clock.crisis_start_label,
    events: dto.events.map(mapEventDto),
    intelReports: dto.intel_reports.map(mapIntelDto),
    assets: (dto.assets ?? []).map(mapAssetDto),
    operations: (dto.operations ?? []).map(mapOperationDto),
  };
}
