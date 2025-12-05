import type { Coordinates } from './pipeline';
import type { Severity } from './analysis';

export type AlertType = 'leak' | 'change' | 'encroachment' | 'emission' | 'facility' | 'system';

export interface Alert {
  id: number;
  alert_type: AlertType;
  alert_type_display: string;
  severity: Severity;
  severity_display: string;
  title: string;
  description: string;
  location: Coordinates | null;
  location_name: string;
  is_acknowledged: boolean;
  acknowledged_at: string | null;
  acknowledged_by: number | null;
  acknowledged_by_email: string | null;
  satellite_image: number | null;
  satellite_image_name: string | null;
  pipeline: number | null;
  pipeline_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertSeverityCounts {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface AlertsResponse {
  success: boolean;
  count: number;
  unacknowledged_count: number;
  severity_counts: AlertSeverityCounts;
  data: Alert[];
}

