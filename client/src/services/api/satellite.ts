import apiClient, { withRetry } from './client';
import type { SatelliteImage, SatelliteImageListItem, SatelliteImageDropdown } from '@/types';

interface SatelliteListResponse {
  success: boolean;
  count: number;
  data: SatelliteImageListItem[];
}

interface SatelliteResponse {
  success: boolean;
  data: SatelliteImage;
}

interface DropdownResponse {
  success: boolean;
  data: SatelliteImageDropdown[];
}

interface BoundsResponse {
  success: boolean;
  data: {
    bounds: [number, number, number, number];
    center: { lng: number; lat: number };
  };
}

export const satelliteApi = {
  getImages: async (params: {
    status?: string;
    isAnalyzed?: boolean;
    pipeline?: number;
  } = {}): Promise<{ data: SatelliteImageListItem[] }> => {
    const queryParams = new URLSearchParams();
    if (params.status) queryParams.append('status', params.status);
    if (params.isAnalyzed !== undefined) {
      queryParams.append('is_analyzed', String(params.isAnalyzed));
    }
    if (params.pipeline) queryParams.append('pipeline', String(params.pipeline));

    const response = await withRetry(() =>
      apiClient.get<SatelliteListResponse>(`/pipeline/images/?${queryParams}`)
    );
    return { data: response.data.data };
  },

  getImage: async (id: number): Promise<{ data: SatelliteImage }> => {
    const response = await withRetry(() =>
      apiClient.get<SatelliteResponse>(`/pipeline/images/${id}/`)
    );
    return { data: response.data.data };
  },

  getDropdownList: async (): Promise<{ data: SatelliteImageDropdown[] }> => {
    const response = await withRetry(() =>
      apiClient.get<DropdownResponse>('/pipeline/images/dropdown/')
    );
    return { data: response.data.data };
  },

  getBounds: async (id: number): Promise<BoundsResponse['data']> => {
    const response = await withRetry(() =>
      apiClient.get<BoundsResponse>(`/pipeline/images/${id}/bounds/`)
    );
    return response.data.data;
  },
};

