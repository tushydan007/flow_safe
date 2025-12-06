import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, Layers, ZoomIn, ZoomOut, Locate, X } from "lucide-react";

import { useAppDispatch, useAppSelector } from "@/store/hooks";
import {
  fetchPipelineRoutes,
  fetchAllGeoJSON,
} from "@/store/slices/pipelineSlice";
import { fetchDropdownList, selectImage } from "@/store/slices/satelliteSlice";
import { fetchResultsByImage } from "@/store/slices/analysisSlice";
import {
  toggleLegend,
  setSearchQuery,
  setSearching,
} from "@/store/slices/uiSlice";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MapContainer } from "@/components/map/MapContainer";
import { MapLegend } from "@/components/map/MapLegend";
import { MapSkeleton } from "@/components/common/LoadingSkeleton";

interface SearchResult {
  display_name: string;
  lat: string;
  lon: string;
}

export function MapPage() {
  const dispatch = useAppDispatch();
  const {
    routes,
    allGeoJSON,
    isLoading: pipelineLoading,
  } = useAppSelector((state) => state.pipeline);
  const { dropdownList, selectedImage } = useAppSelector(
    (state) => state.satellite
  );
  const { currentImageResults } = useAppSelector((state) => state.analysis);
  const { showLegend, searchQuery } = useAppSelector((state) => state.ui);

  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [, setIsSearchingLocation] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([0, 0]);
  const [mapZoom, setMapZoom] = useState(3);

  useEffect(() => {
    dispatch(fetchPipelineRoutes());
    dispatch(fetchAllGeoJSON());
    dispatch(fetchDropdownList());
  }, [dispatch]);

  useEffect(() => {
    if (selectedImage) {
      dispatch(fetchResultsByImage(selectedImage.id));
    }
  }, [dispatch, selectedImage]);

  const handleImageSelect = async (imageId: string) => {
    if (imageId === "none") {
      dispatch(selectImage(null));
      return;
    }

    const image = dropdownList.find((img) => img.id === Number(imageId));
    if (image) {
      // Fetch full image data
      const { satelliteApi } = await import("@/services/api/satellite");
      const response = await satelliteApi.getImage(image.id);
      dispatch(selectImage(response.data));

      // Center map on image
      if (response.data.center) {
        setMapCenter([response.data.center.lat, response.data.center.lng]);
        setMapZoom(12);
      }
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearchingLocation(true);
    dispatch(setSearching(true));

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery
        )}`
      );
      const data = await response.json();
      setSearchResults(data.slice(0, 5));
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsSearchingLocation(false);
      dispatch(setSearching(false));
    }
  };

  const handleSelectLocation = (result: SearchResult) => {
    setMapCenter([parseFloat(result.lat), parseFloat(result.lon)]);
    setMapZoom(14);
    setSearchResults([]);
    dispatch(setSearchQuery(""));
  };

  const handleZoomIn = () => setMapZoom((z) => Math.min(z + 1, 18));
  const handleZoomOut = () => setMapZoom((z) => Math.max(z - 1, 1));

  if (pipelineLoading && routes.length === 0) {
    return (
      <div className="h-full p-4">
        <MapSkeleton />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Controls Bar */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 p-4 border-b bg-background/95 backdrop-blur"
      >
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search location..."
            value={searchQuery}
            onChange={(e) => dispatch(setSearchQuery(e.target.value))}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="pl-9"
          />
          {searchQuery && (
            <button
              onClick={() => {
                dispatch(setSearchQuery(""));
                setSearchResults([]);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          )}

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-popover border rounded-md shadow-lg z-50 overflow-hidden">
              {searchResults.map((result, index) => (
                <button
                  key={index}
                  onClick={() => handleSelectLocation(result)}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-accent transition-colors"
                >
                  {result.display_name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Image Selector */}
        <Select
          value={selectedImage?.id.toString() || "none"}
          onValueChange={handleImageSelect}
        >
          <SelectTrigger className="w-[280px]">
            <SelectValue placeholder="Select satellite image" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">No image selected</SelectItem>
            {dropdownList.map((image) => (
              <SelectItem key={image.id} value={image.id.toString()}>
                {image.display_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Legend Toggle */}
        <Button
          variant={showLegend ? "default" : "outline"}
          size="icon"
          onClick={() => dispatch(toggleLegend())}
        >
          <Layers className="h-4 w-4" />
        </Button>
      </motion.div>

      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          pipelineGeoJSON={allGeoJSON}
          selectedImage={selectedImage}
          analysisResults={currentImageResults}
          onZoomChange={setMapZoom}
          onCenterChange={setMapCenter}
        />

        {/* Map Controls */}
        <div className="absolute right-4 top-4 flex flex-col gap-2 z-10">
          <Button variant="secondary" size="icon" onClick={handleZoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="secondary" size="icon" onClick={handleZoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            onClick={() => {
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                  setMapCenter([
                    position.coords.latitude,
                    position.coords.longitude,
                  ]);
                  setMapZoom(14);
                });
              }
            }}
          >
            <Locate className="h-4 w-4" />
          </Button>
        </div>

        {/* Legend */}
        {showLegend && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute left-4 bottom-4 z-10"
          >
            <MapLegend analysisResults={currentImageResults} />
          </motion.div>
        )}
      </div>
    </div>
  );
}
