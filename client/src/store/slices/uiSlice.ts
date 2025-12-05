import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

interface MapView {
  center: [number, number];
  zoom: number;
}

interface UIState {
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  mapView: MapView;
  showLegend: boolean;
  activeAnalysisType: string | null;
  isSearching: boolean;
  searchQuery: string;
  globalLoading: boolean;
  globalError: string | null;
}

const initialState: UIState = {
  sidebarCollapsed: false,
  sidebarWidth: 320,
  mapView: {
    center: [0, 0],
    zoom: 3,
  },
  showLegend: true,
  activeAnalysisType: null,
  isSearching: false,
  searchQuery: "",
  globalLoading: false,
  globalError: null,
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    setSidebarWidth: (state, action: PayloadAction<number>) => {
      state.sidebarWidth = action.payload;
    },
    setMapView: (state, action: PayloadAction<Partial<MapView>>) => {
      state.mapView = { ...state.mapView, ...action.payload };
    },
    toggleLegend: (state) => {
      state.showLegend = !state.showLegend;
    },
    setActiveAnalysisType: (state, action: PayloadAction<string | null>) => {
      state.activeAnalysisType = action.payload;
    },
    setSearching: (state, action: PayloadAction<boolean>) => {
      state.isSearching = action.payload;
    },
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
    },
    setGlobalError: (state, action: PayloadAction<string | null>) => {
      state.globalError = action.payload;
    },
    clearGlobalError: (state) => {
      state.globalError = null;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarCollapsed,
  setSidebarWidth,
  setMapView,
  toggleLegend,
  setActiveAnalysisType,
  setSearching,
  setSearchQuery,
  setGlobalLoading,
  setGlobalError,
  clearGlobalError,
} = uiSlice.actions;
export default uiSlice.reducer;
