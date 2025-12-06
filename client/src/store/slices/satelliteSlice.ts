import {
  createSlice,
  createAsyncThunk,
  type PayloadAction,
} from "@reduxjs/toolkit";
import { satelliteApi } from "@/services/api/satellite";
import type {
  SatelliteImage,
  SatelliteImageListItem,
  SatelliteImageDropdown,
} from "@/types/satellite";

interface SatelliteState {
  images: SatelliteImageListItem[];
  selectedImage: SatelliteImage | null;
  dropdownList: SatelliteImageDropdown[];
  isLoading: boolean;
  error: string | null;
}

const initialState: SatelliteState = {
  images: [],
  selectedImage: null,
  dropdownList: [],
  isLoading: false,
  error: null,
};

export const fetchSatelliteImages = createAsyncThunk(
  "satellite/fetchImages",
  async (
    params: { status?: string; isAnalyzed?: boolean } | void,
    { rejectWithValue }
  ) => {
    try {
      const response = await satelliteApi.getImages(params || {});
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch images";
      return rejectWithValue(message);
    }
  }
);

export const fetchSatelliteImage = createAsyncThunk(
  "satellite/fetchImage",
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await satelliteApi.getImage(id);
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch image";
      return rejectWithValue(message);
    }
  }
);

export const fetchDropdownList = createAsyncThunk(
  "satellite/fetchDropdownList",
  async (_, { rejectWithValue }) => {
    try {
      const response = await satelliteApi.getDropdownList();
      return response.data;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to fetch dropdown list";
      return rejectWithValue(message);
    }
  }
);

const satelliteSlice = createSlice({
  name: "satellite",
  initialState,
  reducers: {
    selectImage: (state, action: PayloadAction<SatelliteImage | null>) => {
      state.selectedImage = action.payload;
    },
    updateImageStatus: (
      state,
      action: PayloadAction<{
        id: number;
        status: string;
        progress?: number;
      }>
    ) => {
      const image = state.images.find((img) => img.id === action.payload.id);
      if (image) {
        image.status = action.payload.status;
      }
    },
    clearSatelliteError: (state) => {
      state.error = null;
    },
    resetSatelliteState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      // Fetch Images
      .addCase(fetchSatelliteImages.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSatelliteImages.fulfilled, (state, action) => {
        state.isLoading = false;
        state.images = action.payload;
      })
      .addCase(fetchSatelliteImages.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Single Image
      .addCase(fetchSatelliteImage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSatelliteImage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedImage = action.payload;
      })
      .addCase(fetchSatelliteImage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Dropdown List
      .addCase(fetchDropdownList.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchDropdownList.fulfilled, (state, action) => {
        state.isLoading = false;
        state.dropdownList = action.payload;
      })
      .addCase(fetchDropdownList.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  selectImage,
  updateImageStatus,
  clearSatelliteError,
  resetSatelliteState,
} = satelliteSlice.actions;
export default satelliteSlice.reducer;
