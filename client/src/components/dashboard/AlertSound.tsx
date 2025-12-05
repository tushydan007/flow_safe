import { useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Volume2, VolumeX, AlertTriangle, X } from "lucide-react";

import { useAppSelector, useAppDispatch } from "@/store/hooks";
import { dismissCriticalAlert, toggleSound } from "@/store/slices/alertSlice";
import { Button } from "@/components/ui/button";

export function AlertSound() {
  const dispatch = useAppDispatch();
  const { hasNewCriticalAlert, soundEnabled, criticalAlerts } = useAppSelector(
    (state) => state.alerts
  );
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const intervalRef = useRef<number | null>(null);

  const playAlertSound = useCallback(() => {
    if (!soundEnabled || !audioRef.current) return;

    audioRef.current.currentTime = 0;
    audioRef.current.play().catch(() => {
      // Browser may block autoplay
    });
  }, [soundEnabled]);

  useEffect(() => {
    // Create audio element
    audioRef.current = new Audio(
      "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAB/f39/"
    );
    audioRef.current.volume = 0.5;

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (hasNewCriticalAlert && soundEnabled) {
      // Play immediately
      playAlertSound();

      // Then play every 5 seconds
      intervalRef.current = window.setInterval(() => {
        playAlertSound();
      }, 5000);
    } else {
      // Stop the interval when alert is dismissed
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [hasNewCriticalAlert, soundEnabled, playAlertSound]);

  const handleDismiss = () => {
    dispatch(dismissCriticalAlert());
  };

  const handleToggleSound = () => {
    dispatch(toggleSound());
  };

  return (
    <AnimatePresence>
      {hasNewCriticalAlert && (
        <motion.div
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-100 bg-destructive text-destructive-foreground"
        >
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <AlertTriangle className="h-5 w-5" />
                </motion.div>
                <div>
                  <p className="font-semibold">Critical Alert Detected</p>
                  <p className="text-sm opacity-90">
                    {criticalAlerts.length} critical issue(s) require immediate
                    attention
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleToggleSound}
                  className="hover:bg-destructive-foreground/20"
                >
                  {soundEnabled ? (
                    <Volume2 className="h-5 w-5" />
                  ) : (
                    <VolumeX className="h-5 w-5" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleDismiss}
                  className="hover:bg-destructive-foreground/20"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
