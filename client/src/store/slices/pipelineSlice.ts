import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { pipelineApi } from '@/services/api/pipeline';
import type { PipelineRoute, GeoJSONData } from '@/types/pipeline';

interface PipelineState {
  routes: PipelineRoute[];
  selectedRoute: PipelineRoute | null;
  allGeoJSON: GeoJSONData | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: PipelineState = {
  routes: [],
  selectedRoute: null,
  allGeoJSON: null,
  isLoading: false,
  error: null,
};

export const fetchPipelineRoutes = createAsyncThunk(
  'pipeline/fetchRoutes',
  async (_, { rejectWithValue }) => {
    try {
      const response = await pipelineApi.getRoutes();
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch routes';
      return rejectWithValue(message);
    }
  }
);

export const fetchPipelineRoute = createAsyncThunk(
  'pipeline/fetchRoute',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await pipelineApi.getRoute(id);
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch route';
      return rejectWithValue(message);
    }
  }
);

export const fetchAllGeoJSON = createAsyncThunk(
  'pipeline/fetchAllGeoJSON',
  async (_, { rejectWithValue }) => {
    try {
      const response = await pipelineApi.getAllGeoJSON();
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch GeoJSON';
      return rejectWithValue(message);
    }
  }
);

const pipelineSlice = createSlice({
  name: 'pipeline',
  initialState,
  reducers: {
    selectRoute: (state, action: PayloadAction<PipelineRoute | null>) => {
      state.selectedRoute = action.payload;
    },
    clearPipelineError: (state) => {
      state.error = null;
    },
    resetPipelineState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Fetch Routes
      .addCase(fetchPipelineRoutes.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPipelineRoutes.fulfilled, (state, action) => {
        state.isLoading = false;
        state.routes = action.payload;
      })
      .addCase(fetchPipelineRoutes.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Single Route
      .addCase(fetchPipelineRoute.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPipelineRoute.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedRoute = action.payload;
      })
      .addCase(fetchPipelineRoute.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch All GeoJSON
      .addCase(fetchAllGeoJSON.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchAllGeoJSON.fulfilled, (state, action) => {
        state.isLoading = false;
        state.allGeoJSON = action.payload;
      })
      .addCase(fetchAllGeoJSON.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { selectRoute, clearPipelineError, resetPipelineState } = pipelineSlice.actions;
export default pipelineSlice.reducer;

