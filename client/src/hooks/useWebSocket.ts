import { useEffect } from "react";
import { useAppSelector } from "@/store/hooks";
import { wsService } from "@/services/websocket";

export function useWebSocket() {
  const { isAuthenticated, tokens } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated && tokens?.access) {
      wsService.connect();

      // Set up ping interval to keep connection alive
      const pingInterval = setInterval(() => {
        wsService.ping();
      }, 30000);

      return () => {
        clearInterval(pingInterval);
        wsService.disconnect();
      };
    }
  }, [isAuthenticated, tokens?.access]);

  return wsService;
}
