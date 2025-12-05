import apiClient, { withRetry } from "./client";
import type {
  AnalysisResult,
  AnalysisResultListItem,
  AnalysisSummary,
} from "@/types";

interface AnalysisListResponse {
  success: boolean;
  count: number;
  data: AnalysisResultListItem[];
}

interface AnalysisResponse {
  success: boolean;
  data: AnalysisResult;
}

interface AnalysisByImageResponse {
  success: boolean;
  image_id: number;
  count: number;
  total_detections: number;
  severity_summary: Record<string, number>;
  data: AnalysisResult[];
}

interface AnalysisSummaryResponse {
  success: boolean;
  count: number;
  data: AnalysisSummary[];
}

interface RunAnalysisResponse {
  success: boolean;
  message: string;
  image_id: number;
}

export const analysisApi = {
  getResults: async (
    params: {
      imageId?: number;
      type?: string;
      status?: string;
    } = {}
  ): Promise<{ data: AnalysisResultListItem[] }> => {
    const queryParams = new URLSearchParams();
    if (params.imageId) queryParams.append("image", String(params.imageId));
    if (params.type) queryParams.append("type", params.type);
    if (params.status) queryParams.append("status", params.status);

    const response = await withRetry(() =>
      apiClient.get<AnalysisListResponse>(`/analysis/results/?${queryParams}`)
    );
    return { data: response.data.data };
  },

  getResult: async (id: number): Promise<{ data: AnalysisResult }> => {
    const response = await withRetry(() =>
      apiClient.get<AnalysisResponse>(`/analysis/results/${id}/`)
    );
    return { data: response.data.data };
  },

  getResultsByImage: async (
    imageId: number
  ): Promise<AnalysisByImageResponse> => {
    const response = await withRetry(() =>
      apiClient.get<AnalysisByImageResponse>(
        `/analysis/results/by-image/${imageId}/`
      )
    );
    return response.data;
  },

  getResultGeoJSON: async (id: number): Promise<{ data: unknown }> => {
    const response = await withRetry(() =>
      apiClient.get(`/analysis/results/${id}/geojson/`)
    );
    return { data: response.data.data };
  },

  getSummary: async (): Promise<{ data: AnalysisSummary[] }> => {
    const response = await withRetry(() =>
      apiClient.get<AnalysisSummaryResponse>("/analysis/results/summary/")
    );
    return { data: response.data.data };
  },

  runAnalysis: async (
    imageId: number,
    analysisTypes?: string[]
  ): Promise<RunAnalysisResponse> => {
    const response = await apiClient.post<RunAnalysisResponse>(
      "/analysis/results/run/",
      {
        image_id: imageId,
        analysis_types: analysisTypes || ["all"],
      }
    );
    return response.data;
  },
};
