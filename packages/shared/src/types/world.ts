export interface CoordinatesDto {
  lat: number;
  lng: number;
}

export interface WorldClockDto {
  world_id: number;
  game_minutes: number;
  is_paused: boolean;
  speed: number;
  ticks_elapsed: number;
  crisis_start_label: string;
  tick_game_minutes: number;
}

export interface EventDto {
  id: string;
  game_minutes: number;
  title: string;
  summary: string;
  severity: string;
  event_type: string;
  region: string;
  country: string;
  coordinates: CoordinatesDto;
}

export interface IntelReportDto {
  id: string;
  title: string;
  description: string;
  source: string;
  confidence: number;
  timestamp: number;
  region: string;
  coordinates: CoordinatesDto;
  analyst_assessments?: AnalystAssessmentDto[];
  /** @deprecated Use description — kept for backward compatibility */
  summary?: string;
  /** @deprecated Use timestamp */
  game_minutes?: number;
}

import type { AnalystAssessmentDto } from "./analysts";
import type { AssetDto, OperationDto } from "./operations";

export interface WorldStateDto {
  clock: WorldClockDto;
  events: EventDto[];
  intel_reports: IntelReportDto[];
  assets?: AssetDto[];
  operations?: OperationDto[];
}

export interface AdvanceResultDto {
  clock: WorldClockDto;
  ticks_run: number;
  new_events: EventDto[];
  new_intel_reports: IntelReportDto[];
  events: EventDto[];
  intel_reports: IntelReportDto[];
  assets?: AssetDto[];
  operations?: OperationDto[];
  resolved_operations?: OperationDto[];
}
