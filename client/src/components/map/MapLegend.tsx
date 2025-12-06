import { motion } from "framer-motion";
import type { AnalysisResult, AnalysisType } from "@/types/analysis";

interface MapLegendProps {
  analysisResults: AnalysisResult[];
}

const severityColors = {
  critical: { color: "#ef4444", label: "Critical" },
  high: { color: "#f97316", label: "High" },
  medium: { color: "#eab308", label: "Medium" },
  low: { color: "#22c55e", label: "Low" },
};

const analysisTypes = {
  ndvi: {
    icon: "🛢️",
    label: "Leak Detection",
    description: "NDVI-based oil spill detection",
  },
  change: {
    icon: "📊",
    label: "Change Detection",
    description: "Land use changes",
  },
  encroachment: {
    icon: "🚧",
    label: "Encroachment",
    description: "Objects near pipeline",
  },
  emission: {
    icon: "💨",
    label: "Emissions",
    description: "Gas leaks and thermal anomalies",
  },
  facility: {
    icon: "🏭",
    label: "Facility",
    description: "Infrastructure monitoring",
  },
};

export function MapLegend({ analysisResults }: MapLegendProps) {
  const activeTypes = new Set(analysisResults.map((r) => r.analysis_type));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-background/95 backdrop-blur border rounded-lg shadow-lg p-4 max-w-xs"
    >
      <h3 className="font-semibold text-sm mb-3">Map Legend</h3>

      {/* Severity Levels */}
      <div className="mb-4">
        <h4 className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">
          Severity Levels
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(severityColors).map(([key, { color, label }]) => (
            <div key={key} className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis Types */}
      <div>
        <h4 className="text-xs text-muted-foreground mb-2 uppercase tracking-wide">
          Analysis Types
        </h4>
        <div className="space-y-2">
          {Object.entries(analysisTypes).map(
            ([key, { icon, label, description }]) => (
              <div
                key={key}
                className={`flex items-start gap-2 ${
                  activeTypes.has(key as AnalysisType)
                    ? "opacity-100"
                    : "opacity-50"
                }`}
              >
                <span className="text-base">{icon}</span>
                <div>
                  <p className="text-xs font-medium">{label}</p>
                  <p className="text-xs text-muted-foreground">{description}</p>
                </div>
              </div>
            )
          )}
        </div>
      </div>

      {/* Pipeline */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center gap-2">
          <div className="w-8 h-1 bg-orange-500 rounded" />
          <span className="text-xs">Pipeline Route</span>
        </div>
      </div>
    </motion.div>
  );
}
