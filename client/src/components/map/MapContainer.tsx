import { useEffect, useRef } from "react";
import {
  MapContainer as LeafletMap,
  TileLayer,
  GeoJSON,
  useMap,
} from "react-leaflet";
import { type LatLngBoundsExpression } from "leaflet";
import "leaflet/dist/leaflet.css";

import type { GeoJSONData } from "@/types/pipeline";
import type { SatelliteImage } from "@/types/satellite";
import type { AnalysisResult } from "@/types/analysis";
import { AnalysisMarkers } from "./AnalysisMarkers";

interface MapContainerProps {
  center: [number, number];
  zoom: number;
  pipelineGeoJSON: GeoJSONData | null;
  selectedImage: SatelliteImage | null;
  analysisResults: AnalysisResult[];
  onZoomChange: (zoom: number) => void;
  onCenterChange: (center: [number, number]) => void;
}

function MapController({
  center,
  zoom,
  onZoomChange,
  onCenterChange,
}: {
  center: [number, number];
  zoom: number;
  onZoomChange: (zoom: number) => void;
  onCenterChange: (center: [number, number]) => void;
}) {
  const map = useMap();
  const isProgrammaticChangeRef = useRef(false);
  const prevCenterRef = useRef(center);
  const prevZoomRef = useRef(zoom);

  useEffect(() => {
    // Only update map if center/zoom actually changed from props
    const centerChanged =
      prevCenterRef.current[0] !== center[0] ||
      prevCenterRef.current[1] !== center[1];
    const zoomChanged = prevZoomRef.current !== zoom;

    if (centerChanged || zoomChanged) {
      isProgrammaticChangeRef.current = true;
      map.setView(center, zoom);
      prevCenterRef.current = center;
      prevZoomRef.current = zoom;
      // Reset flag after a short delay to allow event to complete
      setTimeout(() => {
        isProgrammaticChangeRef.current = false;
      }, 100);
    }
  }, [map, center, zoom]);

  useEffect(() => {
    const handleZoomEnd = () => {
      // Skip if this was triggered by programmatic change
      if (isProgrammaticChangeRef.current) return;

      const newZoom = map.getZoom();
      if (newZoom !== prevZoomRef.current) {
        prevZoomRef.current = newZoom;
        onZoomChange(newZoom);
      }
    };

    const handleMoveEnd = () => {
      // Skip if this was triggered by programmatic change
      if (isProgrammaticChangeRef.current) return;

      const mapCenter = map.getCenter();
      const newCenter: [number, number] = [mapCenter.lat, mapCenter.lng];
      if (
        newCenter[0] !== prevCenterRef.current[0] ||
        newCenter[1] !== prevCenterRef.current[1]
      ) {
        prevCenterRef.current = newCenter;
        onCenterChange(newCenter);
      }
    };

    map.on("zoomend", handleZoomEnd);
    map.on("moveend", handleMoveEnd);

    return () => {
      map.off("zoomend", handleZoomEnd);
      map.off("moveend", handleMoveEnd);
    };
  }, [map, onZoomChange, onCenterChange]);

  return null;
}

function ImageOverlay({ selectedImage }: { selectedImage: SatelliteImage }) {
  const map = useMap();

  useEffect(() => {
    if (selectedImage?.bounds) {
      const bounds: LatLngBoundsExpression = [
        [selectedImage.bounds[1], selectedImage.bounds[0]],
        [selectedImage.bounds[3], selectedImage.bounds[2]],
      ];
      map.fitBounds(bounds);
    }
  }, [map, selectedImage]);

  if (!selectedImage?.cog_file || !selectedImage?.bounds) {
    return null;
  }

  // Note: For actual satellite image overlay, you would use a WMS or TileLayer.WMS
  // pointing to your backend serving the COG tiles
  return null;
}

export function MapContainer({
  center,
  zoom,
  pipelineGeoJSON,
  selectedImage,
  analysisResults,
  onZoomChange,
  onCenterChange,
}: MapContainerProps) {
  const mapRef = useRef(null);

  const pipelineStyle = (feature: GeoJSON.Feature | undefined) => {
    const color = feature?.properties?.color || "#FF5722";
    return {
      color,
      weight: 3,
      opacity: 0.8,
      fillOpacity: 0.2,
    };
  };

  const onEachPipelineFeature = (feature: GeoJSON.Feature, layer: L.Layer) => {
    if (feature.properties) {
      const { pipeline_name, pipeline_id } = feature.properties;
      layer.bindPopup(`
        <div class="p-2">
          <h3 class="font-semibold">${pipeline_name || "Pipeline"}</h3>
          <p class="text-sm text-gray-500">ID: ${pipeline_id}</p>
        </div>
      `);
    }
  };

  return (
    <LeafletMap
      ref={mapRef}
      center={center}
      zoom={zoom}
      className="h-full w-full"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapController
        center={center}
        zoom={zoom}
        onZoomChange={onZoomChange}
        onCenterChange={onCenterChange}
      />

      {/* Pipeline Routes */}
      {pipelineGeoJSON && (
        <GeoJSON
          data={pipelineGeoJSON}
          style={pipelineStyle}
          onEachFeature={onEachPipelineFeature}
        />
      )}

      {/* Satellite Image Overlay */}
      {selectedImage && <ImageOverlay selectedImage={selectedImage} />}

      {/* Analysis Result Markers */}
      <AnalysisMarkers results={analysisResults} />
    </LeafletMap>
  );
}
