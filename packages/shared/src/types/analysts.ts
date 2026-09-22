export interface AnalystDto {
  id: string;
  name: string;
  specialty: string;
  reliability: number;
  bias: string;
}

export interface AnalystAssessmentDto {
  id: string;
  analyst_id: string;
  analyst_name: string;
  specialty: string;
  bias: string;
  reliability: number;
  assessment: string;
  assessed_confidence: number;
  timestamp: number;
}
