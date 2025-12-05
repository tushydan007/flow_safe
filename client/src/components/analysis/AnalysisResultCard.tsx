import { motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader2,
  XCircle,
} from "lucide-react";
import type { AnalysisResult } from "@/types/analysis";
import { cn } from "@/lib/utils";

interface AnalysisResultCardProps {
  result: AnalysisResult;
  isSelected: boolean;
  onClick: () => void;
}

const analysisTypeInfo = {
  ndvi: {
    icon: "🛢️",
    title: "Leak Detection",
    description: "NDVI-based oil spill detection",
  },
  change: {
    icon: "📊",
    title: "Change Detection",
    description: "Land use and terrain changes",
  },
  encroachment: {
    icon: "🚧",
    title: "Encroachment",
    description: "Object detection near pipeline",
  },
  emission: {
    icon: "💨",
    title: "Emission Tracking",
    description: "Gas leaks and thermal anomalies",
  },
  facility: {
    icon: "🏭",
    title: "Facility Monitoring",
    description: "Infrastructure condition assessment",
  },
};

const statusIcons = {
  pending: <Clock className="h-4 w-4 text-muted-foreground" />,
  processing: <Loader2 className="h-4 w-4 animate-spin text-blue-500" />,
  completed: <CheckCircle className="h-4 w-4 text-emerald-500" />,
  failed: <XCircle className="h-4 w-4 text-destructive" />,
};

const severityColors = {
  critical: "border-l-red-500 bg-red-500/5",
  high: "border-l-orange-500 bg-orange-500/5",
  medium: "border-l-yellow-500 bg-yellow-500/5",
  low: "border-l-emerald-500 bg-emerald-500/5",
};

export function AnalysisResultCard({
  result,
  isSelected,
  onClick,
}: AnalysisResultCardProps) {
  const info =
    analysisTypeInfo[result.analysis_type as keyof typeof analysisTypeInfo];
  const severityClass = result.severity
    ? severityColors[result.severity as keyof typeof severityColors]
    : "";

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "rounded-lg border-l-4 border bg-card p-4 cursor-pointer transition-all",
        severityClass,
        isSelected && "ring-2 ring-primary"
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{info?.icon}</span>
          <div>
            <h3 className="font-semibold">
              {info?.title || result.analysis_type_display}
            </h3>
            <p className="text-xs text-muted-foreground">{info?.description}</p>
          </div>
        </div>
        {statusIcons[result.status as keyof typeof statusIcons]}
      </div>

      {/* Progress Bar for Processing */}
      {result.status === "processing" && (
        <div className="mb-3">
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${result.progress}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {result.progress}% complete
          </p>
        </div>
      )}

      {/* Summary */}
      {result.status === "completed" && result.summary && (
        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
          {result.summary}
        </p>
      )}

      {/* Stats */}
      {result.status === "completed" && result.result_data && (
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <AlertTriangle className="h-3.5 w-3.5 text-muted-foreground" />
            <span>{result.detections_count} detected</span>
          </div>
          {result.severity && (
            <span
              className={cn(
                "px-2 py-0.5 rounded-full text-xs font-medium capitalize",
                result.severity === "critical" &&
                  "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                result.severity === "high" &&
                  "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
                result.severity === "medium" &&
                  "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
                result.severity === "low" &&
                  "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
              )}
            >
              {result.severity}
            </span>
          )}
        </div>
      )}

      {/* Error Message */}
      {result.status === "failed" && result.error_message && (
        <p className="text-sm text-destructive">{result.error_message}</p>
      )}
    </motion.div>
  );
}
