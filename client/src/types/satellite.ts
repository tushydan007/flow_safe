import type { Bounds, Coordinates } from "./pipeline";

export interface SatelliteImage {
  id: number;
  name: string;
  display_name: string;
  description: string;
  original_file: string;
  cog_file: string | null;
  acquisition_date: string | null;
  satellite_name: string;
  resolution: number | null;
  bounds: Bounds | null;
  center: Coordinates | null;
  width: number | null;
  height: number | null;
  bands: number | null;
  file_size: number | null;
  crs: string;
  status: "uploading" | "processing" | "ready" | "error";
  error_message: string;
  is_analyzed: boolean;
  analysis_completed_at: string | null;
  pipeline: number | null;
  pipeline_name: string | null;
  organization_name: string;
  has_alerts: boolean;
  created_at: string;
  updated_at: string;
}

export interface SatelliteImageListItem {
  id: number;
  name: string;
  display_name: string;
  acquisition_date: string | null;
  status: string;
  is_analyzed: boolean;
  has_unacknowledged_alerts: boolean;
  created_at: string;
}

export interface SatelliteImageDropdown {
  id: number;
  name: string;
  display_name: string;
  acquisition_date: string | null;
  is_analyzed: boolean;
}
