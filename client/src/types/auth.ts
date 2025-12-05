export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string | null;
  is_active: boolean;
  date_joined: string;
  updated_at: string;
  organization?: OrganizationBasic;
  settings?: UserSettingsBasic;
}

export interface OrganizationBasic {
  name: string;
  logo: string | null;
}

export interface UserSettingsBasic {
  theme: "light" | "dark" | "system";
  notifications_enabled: boolean;
  sound_alerts_enabled: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  re_password: string;
}

export interface PasswordChangeData {
  current_password: string;
  new_password: string;
  re_new_password: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: number;
    message: string;
    details: Record<string, string[]>;
  };
}
