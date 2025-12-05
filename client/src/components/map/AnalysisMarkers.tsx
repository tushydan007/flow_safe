import { Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import type { AnalysisResult } from '@/types/analysis';

interface AnalysisMarkersProps {
  results: AnalysisResult[];
}

const severityColors = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

const analysisTypeIcons = {
  ndvi: '🛢️',
  change: '📊',
  encroachment: '🚧',
  emission: '💨',
  facility: '🏭',
};

export function AnalysisMarkers({ results }: AnalysisMarkersProps) {
  if (!results || results.length === 0) return null;

  return (
    <>
      {results.map((result) => {
        if (!result.result_geojson?.features) return null;

        return result.result_geojson.features.map((feature, index) => {
          const { geometry, properties } = feature;
          
          if (geometry.type !== 'Point') return null;

          const [lng, lat] = geometry.coordinates as [number, number];
          const severity = (properties?.severity as keyof typeof severityColors) || 'low';
          const color = severityColors[severity];

          return (
            <CircleMarker
              key={`${result.id}-${index}`}
              center={[lat, lng]}
              radius={10}
              fillColor={color}
              fillOpacity={0.7}
              color={color}
              weight={2}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">
                      {analysisTypeIcons[result.analysis_type as keyof typeof analysisTypeIcons]}
                    </span>
                    <h3 className="font-semibold">{result.analysis_type_display}</h3>
                  </div>
                  
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className="inline-block w-3 h-3 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      <span className="capitalize">{severity} Severity</span>
                    </div>
                    
                    {properties?.confidence && (
                      <p>
                        <strong>Confidence:</strong> {(properties.confidence * 100).toFixed(1)}%
                      </p>
                    )}
                    
                    {properties?.ndvi_value !== undefined && (
                      <p>
                        <strong>NDVI:</strong> {properties.ndvi_value.toFixed(3)}
                      </p>
                    )}
                    
                    {properties?.object_label && (
                      <p>
                        <strong>Detected:</strong> {properties.object_label}
                      </p>
                    )}
                    
                    {properties?.distance_to_pipeline_m && (
                      <p>
                        <strong>Distance:</strong> {properties.distance_to_pipeline_m.toFixed(1)}m
                      </p>
                    )}
                    
                    {properties?.emission_type && (
                      <p>
                        <strong>Type:</strong> {properties.emission_type}
                      </p>
                    )}
                    
                    {properties?.condition && (
                      <p>
                        <strong>Condition:</strong> {properties.condition}
                      </p>
                    )}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        });
      })}
    </>
  );
}

