export type IntelSource = "SATINT" | "SIGINT" | "HUMINT" | "CYBER";

export type EventSeverity = "low" | "medium" | "high" | "critical";

export type OperationType = "recon" | "strike";

export type AssetStatus = "available" | "in_use" | "damaged" | "destroyed";

export type OperationStatus = "planned" | "active" | "completed" | "failed";

export interface MapCoordinates {
  lat: number;
  lng: number;
}

export interface WorldEvent {
  id: string;
  gameMinutes: number;
  title: string;
  summary: string;
  severity: EventSeverity;
  region: string;
  coordinates: MapCoordinates;
}

export interface AnalystAssessment {
  id: string;
  analystId: string;
  analystName: string;
  specialty: string;
  bias: string;
  reliability: number;
  assessment: string;
  assessedConfidence: number;
  timestamp: number;
}

export interface IntelReport {
  id: string;
  gameMinutes: number;
  source: IntelSource;
  confidence: number;
  title: string;
  summary: string;
  region: string;
  coordinates: MapCoordinates;
  analystAssessments?: AnalystAssessment[];
}

export interface Asset {
  id: string;
  name: string;
  assetType: string;
  status: AssetStatus;
  supportsRecon: boolean;
  supportsStrike: boolean;
}

export interface OperationResult {
  success: boolean;
  outcomeSummary: string;
  confidenceAtPlanning: number;
  completedAt: number;
}

export interface Operation {
  id: string;
  operationType: OperationType;
  status: OperationStatus;
  regionName: string;
  intelConfidence: number;
  startedAt: number;
  completesAt: number;
  durationMinutes: number;
  assetId: string;
  assetName: string;
  intelReportId: string;
  result: OperationResult | null;
}

export type SimulationSpeed = 1 | 2 | 4;
