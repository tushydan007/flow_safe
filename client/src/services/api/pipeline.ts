import apiClient, { withRetry } from "./client";
import type {
  PipelineRoute,
  PipelineRouteListItem,
  GeoJSONData,
} from "@/types";

interface PipelineListResponse {
  success: boolean;
  count: number;
  data: PipelineRouteListItem[];
}

interface PipelineResponse {
  success: boolean;
  data: PipelineRoute;
}

interface GeoJSONResponse {
  success: boolean;
  data: GeoJSONData;
}

export const pipelineApi = {
  getRoutes: async (): Promise<{ data: PipelineRouteListItem[] }> => {
    const response = await withRetry(() =>
      apiClient.get<PipelineListResponse>("/pipeline/routes/")
    );
    return { data: response.data.data };
  },

  getRoute: async (id: number): Promise<{ data: PipelineRoute }> => {
    const response = await withRetry(() =>
      apiClient.get<PipelineResponse>(`/pipeline/routes/${id}/`)
    );
    return { data: response.data.data };
  },

  getRouteGeoJSON: async (id: number): Promise<{ data: GeoJSONData }> => {
    const response = await withRetry(() =>
      apiClient.get<GeoJSONResponse>(`/pipeline/routes/${id}/geojson/`)
    );
    return { data: response.data.data };
  },

  getAllGeoJSON: async (): Promise<{ data: GeoJSONData }> => {
    const response = await withRetry(() =>
      apiClient.get<GeoJSONResponse>("/pipeline/routes/all-geojson/")
    );
    return { data: response.data.data };
  },
};
