export interface AssetDto {
  id: string;
  name: string;
  asset_type: string;
  status: string;
  supports_recon: boolean;
  supports_strike: boolean;
}

export interface OperationResultDto {
  success: boolean;
  outcome_summary: string;
  confidence_at_planning: number;
  completed_at: number;
}

export interface OperationDto {
  id: string;
  operation_type: string;
  status: string;
  region_name: string;
  intel_confidence: number;
  started_at: number;
  completes_at: number;
  duration_minutes: number;
  asset_id: string;
  asset_name: string;
  intel_report_id: string;
  result: OperationResultDto | null;
}

export interface PlanOperationDto {
  operation_type: "recon" | "strike";
  intel_report_id: string;
  asset_id: string;
}
