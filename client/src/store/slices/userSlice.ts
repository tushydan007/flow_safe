import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from "@reduxjs/toolkit";
import { userApi } from "@/services/api/user";
import type { Organization, UserSettings } from "@/types/user";

interface UserState {
  organization: Organization | null;
  settings: UserSettings | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: UserState = {
  organization: null,
  settings: null,
  isLoading: false,
  error: null,
};

export const fetchOrganization = createAsyncThunk(
  "user/fetchOrganization",
  async (_, { rejectWithValue }) => {
    try {
      const response = await userApi.getOrganization();
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch organization";
      return rejectWithValue(message);
    }
  }
);

export const updateOrganization = createAsyncThunk(
  "user/updateOrganization",
  async (data: Partial<Organization>, { rejectWithValue }) => {
    try {
      const response = await userApi.updateOrganization(data);
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to update organization";
      return rejectWithValue(message);
    }
  }
);

export const fetchSettings = createAsyncThunk(
  "user/fetchSettings",
  async (_, { rejectWithValue }) => {
    try {
      const response = await userApi.getSettings();
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch settings";
      return rejectWithValue(message);
    }
  }
);

export const updateSettings = createAsyncThunk(
  "user/updateSettings",
  async (data: Partial<UserSettings>, { rejectWithValue }) => {
    try {
      const response = await userApi.updateSettings(data);
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to update settings";
      return rejectWithValue(message);
    }
  }
);

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    clearUserError: (state) => {
      state.error = null;
    },
    resetUserState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Fetch Organization
      .addCase(fetchOrganization.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOrganization.fulfilled, (state, action) => {
        state.isLoading = false;
        state.organization = action.payload;
      })
      .addCase(fetchOrganization.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update Organization
      .addCase(updateOrganization.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateOrganization.fulfilled, (state, action) => {
        state.isLoading = false;
        state.organization = action.payload;
      })
      .addCase(updateOrganization.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Settings
      .addCase(fetchSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.settings = action.payload;
      })
      .addCase(fetchSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update Settings
      .addCase(updateSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.settings = action.payload;
      })
      .addCase(updateSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearUserError, resetUserState } = userSlice.actions;
export default userSlice.reducer;
