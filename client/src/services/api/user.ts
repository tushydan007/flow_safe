import apiClient, { withRetry } from "./client";
import type { Organization, UserSettings, ApiResponse } from "@/types";

export const userApi = {
  getOrganization: async (): Promise<ApiResponse<Organization>> => {
    const response = await withRetry(() =>
      apiClient.get<ApiResponse<Organization>>("/auth/organization/")
    );
    return response.data;
  },

  updateOrganization: async (
    data: Partial<Organization>
  ): Promise<ApiResponse<Organization>> => {
    const response = await apiClient.patch<ApiResponse<Organization>>(
      "/auth/organization/",
      data
    );
    return response.data;
  },

  updateOrganizationLogo: async (
    file: File
  ): Promise<ApiResponse<Organization>> => {
    const formData = new FormData();
    formData.append("logo", file);

    const response = await apiClient.patch<ApiResponse<Organization>>(
      "/auth/organization/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  getSettings: async (): Promise<ApiResponse<UserSettings>> => {
    const response = await withRetry(() =>
      apiClient.get<ApiResponse<UserSettings>>("/auth/settings/")
    );
    return response.data;
  },

  updateSettings: async (
    data: Partial<UserSettings>
  ): Promise<ApiResponse<UserSettings>> => {
    const response = await apiClient.patch<ApiResponse<UserSettings>>(
      "/auth/settings/",
      data
    );
    return response.data;
  },
};
