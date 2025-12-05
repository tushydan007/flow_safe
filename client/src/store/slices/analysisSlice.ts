import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { analysisApi } from '@/services/api/analysis';
import type { AnalysisResult, AnalysisSummary } from '@/types/analysis';

interface AnalysisState {
  results: AnalysisResult[];
  selectedResult: AnalysisResult | null;
  summaries: AnalysisSummary[];
  currentImageResults: AnalysisResult[];
  isLoading: boolean;
  isRunningAnalysis: boolean;
  error: string | null;
}

const initialState: AnalysisState = {
  results: [],
  selectedResult: null,
  summaries: [],
  currentImageResults: [],
  isLoading: false,
  isRunningAnalysis: false,
  error: null,
};

export const fetchAnalysisResults = createAsyncThunk(
  'analysis/fetchResults',
  async (params: { imageId?: number; type?: string } = {}, { rejectWithValue }) => {
    try {
      const response = await analysisApi.getResults(params);
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch results';
      return rejectWithValue(message);
    }
  }
);

export const fetchAnalysisResult = createAsyncThunk(
  'analysis/fetchResult',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await analysisApi.getResult(id);
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch result';
      return rejectWithValue(message);
    }
  }
);

export const fetchResultsByImage = createAsyncThunk(
  'analysis/fetchResultsByImage',
  async (imageId: number, { rejectWithValue }) => {
    try {
      const response = await analysisApi.getResultsByImage(imageId);
      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch results';
      return rejectWithValue(message);
    }
  }
);

export const fetchAnalysisSummary = createAsyncThunk(
  'analysis/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analysisApi.getSummary();
      return response.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch summary';
      return rejectWithValue(message);
    }
  }
);

export const runAnalysis = createAsyncThunk(
  'analysis/run',
  async (
    params: { imageId: number; analysisTypes?: string[] },
    { rejectWithValue }
  ) => {
    try {
      const response = await analysisApi.runAnalysis(params.imageId, params.analysisTypes);
      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to run analysis';
      return rejectWithValue(message);
    }
  }
);

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    selectResult: (state, action: PayloadAction<AnalysisResult | null>) => {
      state.selectedResult = action.payload;
    },
    updateAnalysisProgress: (state, action: PayloadAction<{ id: number; progress: number; status: string }>) => {
      const result = state.results.find(r => r.id === action.payload.id);
      if (result) {
        result.progress = action.payload.progress;
        result.status = action.payload.status;
      }
      const currentResult = state.currentImageResults.find(r => r.id === action.payload.id);
      if (currentResult) {
        currentResult.progress = action.payload.progress;
        currentResult.status = action.payload.status;
      }
    },
    clearAnalysisError: (state) => {
      state.error = null;
    },
    resetAnalysisState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Fetch Results
      .addCase(fetchAnalysisResults.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAnalysisResults.fulfilled, (state, action) => {
        state.isLoading = false;
        state.results = action.payload;
      })
      .addCase(fetchAnalysisResults.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Single Result
      .addCase(fetchAnalysisResult.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAnalysisResult.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedResult = action.payload;
      })
      .addCase(fetchAnalysisResult.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Results by Image
      .addCase(fetchResultsByImage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchResultsByImage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentImageResults = action.payload.data;
      })
      .addCase(fetchResultsByImage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Summary
      .addCase(fetchAnalysisSummary.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchAnalysisSummary.fulfilled, (state, action) => {
        state.isLoading = false;
        state.summaries = action.payload;
      })
      .addCase(fetchAnalysisSummary.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Run Analysis
      .addCase(runAnalysis.pending, (state) => {
        state.isRunningAnalysis = true;
        state.error = null;
      })
      .addCase(runAnalysis.fulfilled, (state) => {
        state.isRunningAnalysis = false;
      })
      .addCase(runAnalysis.rejected, (state, action) => {
        state.isRunningAnalysis = false;
        state.error = action.payload as string;
      });
  },
});

export const { selectResult, updateAnalysisProgress, clearAnalysisError, resetAnalysisState } = analysisSlice.actions;
export default analysisSlice.reducer;

