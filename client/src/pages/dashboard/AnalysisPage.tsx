import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader2,
  ChevronRight,
} from 'lucide-react';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { fetchDropdownList } from '@/store/slices/satelliteSlice';
import { fetchResultsByImage, selectResult } from '@/store/slices/analysisSlice';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CardSkeleton } from '@/components/common/LoadingSkeleton';
import { AnalysisResultCard } from '@/components/analysis/AnalysisResultCard';
import { AnalysisDetailPanel } from '@/components/analysis/AnalysisDetailPanel';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function AnalysisPage() {
  const dispatch = useAppDispatch();
  const { dropdownList } = useAppSelector((state) => state.satellite);
  const { currentImageResults, selectedResult, isLoading } = useAppSelector(
    (state) => state.analysis
  );
  const [selectedImageId, setSelectedImageId] = useState<string>('');

  useEffect(() => {
    dispatch(fetchDropdownList());
  }, [dispatch]);

  const handleImageSelect = (imageId: string) => {
    setSelectedImageId(imageId);
    dispatch(fetchResultsByImage(Number(imageId)));
  };

  const getSeverityIcon = (severity: string | null) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-destructive" />;
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-emerald-500" />;
    }
  };

  return (
    <div className="flex h-full">
      {/* Main Content */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="flex-1 p-6 space-y-6 overflow-auto"
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Analysis Results</h1>
          <p className="text-muted-foreground">
            View satellite image analysis results and detected anomalies
          </p>
        </motion.div>

        {/* Image Selector */}
        <motion.div variants={itemVariants}>
          <Select value={selectedImageId} onValueChange={handleImageSelect}>
            <SelectTrigger className="w-full max-w-md">
              <SelectValue placeholder="Select a satellite image to view analysis" />
            </SelectTrigger>
            <SelectContent>
              {dropdownList
                .filter((img) => img.is_analyzed)
                .map((image) => (
                  <SelectItem key={image.id} value={image.id.toString()}>
                    <div className="flex items-center gap-2">
                      <BarChart3 className="h-4 w-4 text-muted-foreground" />
                      <span>{image.display_name}</span>
                    </div>
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </motion.div>

        {/* Results Grid */}
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : selectedImageId ? (
          currentImageResults.length > 0 ? (
            <motion.div
              variants={containerVariants}
              className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            >
              {currentImageResults.map((result) => (
                <motion.div key={result.id} variants={itemVariants}>
                  <AnalysisResultCard
                    result={result}
                    isSelected={selectedResult?.id === result.id}
                    onClick={() => dispatch(selectResult(result))}
                  />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <motion.div
              variants={itemVariants}
              className="text-center py-12 text-muted-foreground"
            >
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No analysis results available for this image</p>
            </motion.div>
          )
        ) : (
          <motion.div
            variants={itemVariants}
            className="text-center py-12 text-muted-foreground"
          >
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Select a satellite image to view analysis results</p>
          </motion.div>
        )}
      </motion.div>

      {/* Detail Panel */}
      {selectedResult && (
        <motion.div
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 400, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          className="border-l bg-background"
        >
          <AnalysisDetailPanel
            result={selectedResult}
            onClose={() => dispatch(selectResult(null))}
          />
        </motion.div>
      )}
    </div>
  );
}

