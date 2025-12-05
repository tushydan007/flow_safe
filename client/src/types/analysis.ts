import type { Coordinates, GeoJSONData } from "./pipeline";

export type AnalysisType =
  | "ndvi"
  | "change"
  | "encroachment"
  | "emission"
  | "facility";
export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";
export type Severity = "low" | "medium" | "high" | "critical";

export interface AnalysisResult {
  id: number;
  satellite_image: number;
  satellite_image_name: string;
  analysis_type: AnalysisType;
  analysis_type_display: string;
  status: AnalysisStatus;
  status_display: string;
  progress: number;
  error_message: string;
  chunks_total: number;
  chunks_processed: number;
  processing_time_seconds: number | null;
  summary: string;
  severity: Severity | null;
  result_data: AnalysisResultData | null;
  result_geojson: GeoJSONData | null;
  result_image: string | null;
  started_at: string | null;
  completed_at: string | null;
  detections_count: number;
  created_at: string;
  updated_at: string;
  // Detailed detections
  leak_detections?: LeakDetection[];
  change_detections?: ChangeDetection[];
  encroachment_detections?: EncroachmentDetection[];
  emission_detections?: EmissionDetection[];
  facility_monitoring?: FacilityMonitoring[];
}

export interface AnalysisResultData {
  analysis_type: string;
  detections: Detection[];
  statistics?: Record<string, number>;
  summary: string;
  total_anomalies?: number;
  total_changes?: number;
  total_objects?: number;
  total_facilities?: number;
  severity_counts: SeverityCounts;
  by_type?: Record<string, Detection[]>;
}

export interface SeverityCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface Detection {
  location: Coordinates;
  pixel_location?: { col: number; row: number };
  severity: Severity;
  confidence?: number;
  description?: string;
}

export interface LeakDetection {
  id: number;
  location: Coordinates;
  location_name: string;
  ndvi_value: number;
  confidence: number;
  extent_sqm: number | null;
  severity: Severity;
  description: string;
  detected_at: string;
}

export interface ChangeDetection {
  id: number;
  location: Coordinates;
  location_name: string;
  change_type: string;
  change_type_display: string;
  change_percentage: number;
  confidence: number;
  area_sqm: number | null;
  severity: Severity;
  description: string;
  detected_at: string;
}

export interface EncroachmentDetection {
  id: number;
  location: Coordinates;
  location_name: string;
  object_type: string;
  object_type_display: string;
  object_label: string;
  confidence: number;
  bounding_box: number[];
  distance_to_pipeline_m: number | null;
  severity: Severity;
  description: string;
  detected_at: string;
}

export interface EmissionDetection {
  id: number;
  location: Coordinates;
  location_name: string;
  emission_type: string;
  emission_type_display: string;
  intensity: number;
  confidence: number;
  estimated_volume: number | null;
  severity: Severity;
  description: string;
  detected_at: string;
}

export interface FacilityMonitoring {
  id: number;
  location: Coordinates;
  location_name: string;
  facility_type: string;
  facility_type_display: string;
  condition: string;
  condition_display: string;
  confidence: number;
  segmentation_mask: number[][] | null;
  area_sqm: number | null;
  severity: Severity;
  description: string;
  detected_at: string;
}

export interface AnalysisSummary {
  image_id: number;
  image_name: string;
  acquisition_date: string | null;
  is_analyzed: boolean;
  analysis_results: AnalysisResultListItem[];
  total_alerts: number;
  critical_alerts: number;
  overall_status: string;
}

export interface AnalysisResultListItem {
  id: number;
  analysis_type: AnalysisType;
  analysis_type_display: string;
  status: AnalysisStatus;
  status_display: string;
  progress: number;
  severity: Severity | null;
  summary: string;
  completed_at: string | null;
  created_at: string;
}
