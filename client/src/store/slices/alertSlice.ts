import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from "@reduxjs/toolkit";
import { alertApi } from "@/services/api/alert";
import type { Alert, AlertSeverityCounts } from "@/types/alert";

interface AlertState {
  alerts: Alert[];
  unacknowledgedAlerts: Alert[];
  criticalAlerts: Alert[];
  severityCounts: AlertSeverityCounts;
  isLoading: boolean;
  error: string | null;
  hasNewCriticalAlert: boolean;
  soundEnabled: boolean;
}

const initialState: AlertState = {
  alerts: [],
  unacknowledgedAlerts: [],
  criticalAlerts: [],
  severityCounts: {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  },
  isLoading: false,
  error: null,
  hasNewCriticalAlert: false,
  soundEnabled: true,
};

export const fetchAlerts = createAsyncThunk(
  "alerts/fetchAlerts",
  async (
    params: { acknowledged?: boolean; severity?: string } = {},
    { rejectWithValue }
  ) => {
    try {
      const response = await alertApi.getAlerts(params);
      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch alerts";
      return rejectWithValue(message);
    }
  }
);

export const fetchUnacknowledgedAlerts = createAsyncThunk(
  "alerts/fetchUnacknowledged",
  async (_, { rejectWithValue }) => {
    try {
      const response = await alertApi.getUnacknowledgedAlerts();
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch alerts";
      return rejectWithValue(message);
    }
  }
);

export const fetchCriticalAlerts = createAsyncThunk(
  "alerts/fetchCritical",
  async (_, { rejectWithValue }) => {
    try {
      const response = await alertApi.getCriticalAlerts();
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch alerts";
      return rejectWithValue(message);
    }
  }
);

export const acknowledgeAlert = createAsyncThunk(
  "alerts/acknowledge",
  async (alertId: number, { rejectWithValue }) => {
    try {
      const response = await alertApi.acknowledgeAlert(alertId);
      return { alertId, data: response.data };
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to acknowledge alert";
      return rejectWithValue(message);
    }
  }
);

export const acknowledgeMultipleAlerts = createAsyncThunk(
  "alerts/acknowledgeMultiple",
  async (alertIds: number[], { rejectWithValue }) => {
    try {
      await alertApi.acknowledgeMultipleAlerts(alertIds);
      return alertIds;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to acknowledge alerts";
      return rejectWithValue(message);
    }
  }
);

const alertSlice = createSlice({
  name: "alerts",
  initialState,
  reducers: {
    addNewAlert: (state, action: PayloadAction<Alert>) => {
      state.alerts.unshift(action.payload);
      if (!action.payload.is_acknowledged) {
        state.unacknowledgedAlerts.unshift(action.payload);
        if (
          action.payload.severity === "critical" ||
          action.payload.severity === "high"
        ) {
          state.criticalAlerts.unshift(action.payload);
          state.hasNewCriticalAlert = true;
        }
        // Update severity counts
        const severity = action.payload.severity as keyof AlertSeverityCounts;
        state.severityCounts[severity] =
          (state.severityCounts[severity] || 0) + 1;
      }
    },
    dismissCriticalAlert: (state) => {
      state.hasNewCriticalAlert = false;
    },
    toggleSound: (state) => {
      state.soundEnabled = !state.soundEnabled;
    },
    setSoundEnabled: (state, action: PayloadAction<boolean>) => {
      state.soundEnabled = action.payload;
    },
    clearAlertError: (state) => {
      state.error = null;
    },
    resetAlertState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Fetch Alerts
      .addCase(fetchAlerts.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.isLoading = false;
        state.alerts = action.payload.data;
        state.severityCounts = action.payload.severity_counts;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Unacknowledged
      .addCase(fetchUnacknowledgedAlerts.fulfilled, (state, action) => {
        state.unacknowledgedAlerts = action.payload;
      })
      // Fetch Critical
      .addCase(fetchCriticalAlerts.fulfilled, (state, action) => {
        state.criticalAlerts = action.payload;
        if (action.payload.length > 0) {
          state.hasNewCriticalAlert = true;
        }
      })
      // Acknowledge Alert
      .addCase(acknowledgeAlert.fulfilled, (state, action) => {
        const { alertId } = action.payload;
        // Update alerts array
        const alertIndex = state.alerts.findIndex((a) => a.id === alertId);
        if (alertIndex !== -1) {
          state.alerts[alertIndex].is_acknowledged = true;
        }
        // Remove from unacknowledged
        state.unacknowledgedAlerts = state.unacknowledgedAlerts.filter(
          (a) => a.id !== alertId
        );
        // Remove from critical if present
        state.criticalAlerts = state.criticalAlerts.filter(
          (a) => a.id !== alertId
        );
        // Check if we should dismiss critical alert status
        if (state.criticalAlerts.length === 0) {
          state.hasNewCriticalAlert = false;
        }
      })
      // Acknowledge Multiple
      .addCase(acknowledgeMultipleAlerts.fulfilled, (state, action) => {
        const alertIds = action.payload;
        state.alerts.forEach((alert) => {
          if (alertIds.includes(alert.id)) {
            alert.is_acknowledged = true;
          }
        });
        state.unacknowledgedAlerts = state.unacknowledgedAlerts.filter(
          (a) => !alertIds.includes(a.id)
        );
        state.criticalAlerts = state.criticalAlerts.filter(
          (a) => !alertIds.includes(a.id)
        );
        if (state.criticalAlerts.length === 0) {
          state.hasNewCriticalAlert = false;
        }
      });
  },
});

export const {
  addNewAlert,
  dismissCriticalAlert,
  toggleSound,
  setSoundEnabled,
  clearAlertError,
  resetAlertState,
} = alertSlice.actions;
export default alertSlice.reducer;
