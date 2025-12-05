import apiClient, { withRetry } from './client';
import type { Alert, AlertsResponse } from '@/types';

interface AlertListResponse {
  success: boolean;
  count: number;
  data: Alert[];
}

interface AcknowledgeResponse {
  success: boolean;
  message: string;
  count?: number;
  data?: Alert;
}

export const alertApi = {
  getAlerts: async (params: {
    acknowledged?: boolean;
    severity?: string;
    type?: string;
    image?: number;
  } = {}): Promise<AlertsResponse> => {
    const queryParams = new URLSearchParams();
    if (params.acknowledged !== undefined) {
      queryParams.append('acknowledged', String(params.acknowledged));
    }
    if (params.severity) queryParams.append('severity', params.severity);
    if (params.type) queryParams.append('type', params.type);
    if (params.image) queryParams.append('image', String(params.image));

    const response = await withRetry(() =>
      apiClient.get<AlertsResponse>(`/pipeline/alerts/?${queryParams}`)
    );
    return response.data;
  },

  getAlert: async (id: number): Promise<{ data: Alert }> => {
    const response = await withRetry(() =>
      apiClient.get<{ success: boolean; data: Alert }>(`/pipeline/alerts/${id}/`)
    );
    return { data: response.data.data };
  },

  getUnacknowledgedAlerts: async (): Promise<{ data: Alert[] }> => {
    const response = await withRetry(() =>
      apiClient.get<AlertListResponse>('/pipeline/alerts/unacknowledged/')
    );
    return { data: response.data.data };
  },

  getCriticalAlerts: async (): Promise<{ data: Alert[] }> => {
    const response = await withRetry(() =>
      apiClient.get<AlertListResponse>('/pipeline/alerts/critical/')
    );
    return { data: response.data.data };
  },

  acknowledgeAlert: async (id: number): Promise<AcknowledgeResponse> => {
    const response = await apiClient.post<AcknowledgeResponse>(
      `/pipeline/alerts/${id}/acknowledge/`
    );
    return response.data;
  },

  acknowledgeMultipleAlerts: async (alertIds: number[]): Promise<AcknowledgeResponse> => {
    const response = await apiClient.post<AcknowledgeResponse>('/pipeline/alerts/acknowledge/', {
      alert_ids: alertIds,
    });
    return response.data;
  },
};

