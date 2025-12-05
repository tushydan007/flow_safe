import { useEffect, useRef } from "react";
import {
  MapContainer as LeafletMap,
  TileLayer,
  GeoJSON,
  useMap,
} from "react-leaflet";
import { LatLngBoundsExpression } from "leaflet";
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

  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);

  useEffect(() => {
    const handleZoomEnd = () => {
      onZoomChange(map.getZoom());
    };

    const handleMoveEnd = () => {
      const mapCenter = map.getCenter();
      onCenterChange([mapCenter.lat, mapCenter.lng]);
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
