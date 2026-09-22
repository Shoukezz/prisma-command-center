export interface HealthResponse {
  status: string;
  environment: string;
}

export interface IntelligenceActionDto {
  id: string;
  intel_report_id: string;
  action_type: string;
  status: string;
  taken_at: number;
  reason: string | null;
}
