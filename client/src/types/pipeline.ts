export interface Coordinates {
  lng: number;
  lat: number;
}

export interface Bounds {
  0: number; // minLng
  1: number; // minLat
  2: number; // maxLng
  3: number; // maxLat
}

export interface PipelineRoute {
  id: number;
  name: string;
  description: string;
  geojson_file: string;
  geojson_data: GeoJSONData | null;
  total_length_km: number | null;
  start_point: Coordinates | null;
  end_point: Coordinates | null;
  bounds: Bounds | null;
  color: string;
  is_active: boolean;
  organization_name: string;
  created_at: string;
  updated_at: string;
}

export interface PipelineRouteListItem {
  id: number;
  name: string;
  bounds: Bounds | null;
  color: string;
  is_active: boolean;
  created_at: string;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: number[] | number[][] | number[][][];
  };
  properties: Record<string, unknown>;
}

export interface GeoJSONData {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

