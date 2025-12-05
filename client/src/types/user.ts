export interface Organization {
  name: string;
  description: string;
  logo: string | null;
  website: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  created_at: string;
  updated_at: string;
}

export interface UserSettings {
  theme: "light" | "dark" | "system";
  notifications_enabled: boolean;
  sound_alerts_enabled: boolean;
  email_notifications: boolean;
  map_default_zoom: number;
  map_default_lat: number;
  map_default_lng: number;
  sidebar_collapsed: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar: string | null;
  organization: Organization;
  settings: UserSettings;
}
