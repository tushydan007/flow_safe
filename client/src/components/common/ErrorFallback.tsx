import { FallbackProps } from "react-error-boundary";
import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="min-h-screen flex items-center justify-center bg-background p-4"
    >
      <div className="max-w-md w-full text-center space-y-6">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mx-auto w-20 h-20 rounded-full bg-destructive/10 flex items-center justify-center"
        >
          <AlertTriangle className="w-10 h-10 text-destructive" />
        </motion.div>

        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-foreground">
            Something went wrong
          </h1>
          <p className="text-muted-foreground">
            An unexpected error occurred. Please try refreshing the page.
          </p>
        </div>

        <div className="bg-muted/50 rounded-lg p-4 text-left">
          <p className="text-sm font-mono text-muted-foreground break-all">
            {error.message}
          </p>
        </div>

        <Button onClick={resetErrorBoundary} className="gap-2">
          <RefreshCw className="w-4 h-4" />
          Try Again
        </Button>
      </div>
    </motion.div>
  );
}
