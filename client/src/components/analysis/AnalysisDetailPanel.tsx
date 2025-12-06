import { motion } from "framer-motion";
import { X, MapPin, Clock, AlertTriangle, CheckCircle } from "lucide-react";
import type { AnalysisResult } from "@/types/analysis";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AnalysisDetailPanelProps {
  result: AnalysisResult;
  onClose: () => void;
}

const severityColors = {
  critical: "text-red-500",
  high: "text-orange-500",
  medium: "text-yellow-500",
  low: "text-emerald-500",
};

export function AnalysisDetailPanel({
  result,
  onClose,
}: AnalysisDetailPanelProps) {
  const detections = result.result_data?.detections || [];
  const severityCounts = result.result_data?.severity_counts || {};

  return (
    <motion.div
      initial={{ x: 20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="h-full overflow-auto"
    >
      {/* Header */}
      <div className="sticky top-0 bg-background border-b p-4 flex items-center justify-between">
        <h2 className="font-semibold">{result.analysis_type_display}</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="p-4 space-y-6">
        {/* Summary */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-muted-foreground">Summary</h3>
          <p className="text-sm">{result.summary || "No summary available"}</p>
        </div>

        {/* Severity Counts */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-muted-foreground">
            Severity Breakdown
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(severityCounts).map(([severity, count]) => (
              <div
                key={severity}
                className={cn(
                  "flex items-center justify-between p-3 rounded-lg border",
                  severity === "critical" &&
                    "border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-900/10",
                  severity === "high" &&
                    "border-orange-200 bg-orange-50 dark:border-orange-900/50 dark:bg-orange-900/10",
                  severity === "medium" &&
                    "border-yellow-200 bg-yellow-50 dark:border-yellow-900/50 dark:bg-yellow-900/10",
                  severity === "low" &&
                    "border-emerald-200 bg-emerald-50 dark:border-emerald-900/50 dark:bg-emerald-900/10"
                )}
              >
                <span className="text-sm capitalize">{severity}</span>
                <span
                  className={cn(
                    "font-bold",
                    severityColors[severity as keyof typeof severityColors]
                  )}
                >
                  {count as number}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Detections List */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-muted-foreground">
            Detected Issues ({detections.length})
          </h3>
          <div className="space-y-2 max-h-[400px] overflow-auto">
            {detections.map((detection, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-3 rounded-lg border bg-card"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle
                      className={cn(
                        "h-4 w-4",
                        severityColors[
                          detection.severity as keyof typeof severityColors
                        ]
                      )}
                    />
                    <span className="font-medium text-sm capitalize">
                      {detection.severity} Severity
                    </span>
                  </div>
                  {detection.confidence && (
                    <span className="text-xs text-muted-foreground">
                      {(detection.confidence * 100).toFixed(0)}% confidence
                    </span>
                  )}
                </div>

                {detection.location && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    <span>
                      {detection.location.lat.toFixed(6)},{" "}
                      {detection.location.lng.toFixed(6)}
                    </span>
                  </div>
                )}

                {detection.description && (
                  <p className="text-sm mt-2 text-muted-foreground">
                    {detection.description}
                  </p>
                )}
              </motion.div>
            ))}

            {detections.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No issues detected</p>
              </div>
            )}
          </div>
        </div>

        {/* Processing Info */}
        {result.processing_time_seconds && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>
              Processed in {result.processing_time_seconds.toFixed(1)} seconds
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
