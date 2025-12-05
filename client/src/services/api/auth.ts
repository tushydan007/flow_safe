import apiClient, { withRetry } from "./client";
import type {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  User,
  ApiResponse,
} from "@/types/auth";

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>(
      "/auth/jwt/create/",
      credentials
    );
    return response.data;
  },

  register: async (data: RegisterData): Promise<void> => {
    await apiClient.post("/auth/users/", data);
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post("/auth/jwt/blacklist/", { refresh: refreshToken });
  },

  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>("/auth/jwt/refresh/", {
      refresh: refreshToken,
    });
    return {
      access: response.data.access,
      refresh: refreshToken,
    };
  },

  verifyToken: async (token: string): Promise<boolean> => {
    try {
      await apiClient.post("/auth/jwt/verify/", { token });
      return true;
    } catch {
      return false;
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await withRetry(() =>
      apiClient.get<ApiResponse<User>>("/auth/users/me/")
    );
    return response.data.data as User;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch<ApiResponse<User>>(
      "/auth/users/me/",
      data
    );
    return response.data.data as User;
  },

  updateAvatar: async (file: File): Promise<User> => {
    const formData = new FormData();
    formData.append("avatar", file);

    const response = await apiClient.patch<ApiResponse<User>>(
      "/auth/users/me/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data.data as User;
  },

  changePassword: async (data: {
    current_password: string;
    new_password: string;
    re_new_password: string;
  }): Promise<void> => {
    await apiClient.post("/auth/users/change-password/", data);
  },

  deleteAccount: async (): Promise<void> => {
    await apiClient.delete("/auth/users/delete-account/");
  },
};
