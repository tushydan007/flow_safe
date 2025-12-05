import { store } from "@/store";
import { addNewAlert } from "@/store/slices/alertSlice";
import { updateImageStatus } from "@/store/slices/satelliteSlice";
import { updateAnalysisProgress } from "@/store/slices/analysisSlice";
import type { Alert } from "@/types/alert";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

type WebSocketMessage = {
  type: string;
  data: Record<string, unknown>;
  sound?: boolean;
};

class WebSocketService {
  private pipelineSocket: WebSocket | null = null;
  private alertSocket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect() {
    const state = store.getState();
    const token = state.auth.tokens?.access;

    if (!token) {
      console.warn("No auth token available for WebSocket connection");
      return;
    }

    this.connectPipelineSocket(token);
    this.connectAlertSocket(token);
  }

  private connectPipelineSocket(token: string) {
    if (this.pipelineSocket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.pipelineSocket = new WebSocket(
      `${WS_URL}/ws/pipeline/?token=${token}`
    );

    this.pipelineSocket.onopen = () => {
      console.log("Pipeline WebSocket connected");
      this.reconnectAttempts = 0;
    };

    this.pipelineSocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handlePipelineMessage(message);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    this.pipelineSocket.onerror = (error) => {
      console.error("Pipeline WebSocket error:", error);
    };

    this.pipelineSocket.onclose = () => {
      console.log("Pipeline WebSocket closed");
      this.attemptReconnect("pipeline");
    };
  }

  private connectAlertSocket(token: string) {
    if (this.alertSocket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.alertSocket = new WebSocket(`${WS_URL}/ws/alerts/?token=${token}`);

    this.alertSocket.onopen = () => {
      console.log("Alert WebSocket connected");
    };

    this.alertSocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleAlertMessage(message);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    this.alertSocket.onerror = (error) => {
      console.error("Alert WebSocket error:", error);
    };

    this.alertSocket.onclose = () => {
      console.log("Alert WebSocket closed");
      this.attemptReconnect("alert");
    };
  }

  private handlePipelineMessage(message: WebSocketMessage) {
    switch (message.type) {
      case "image_update":
        store.dispatch(
          updateImageStatus({
            id: message.data.id as number,
            status: message.data.status as string,
            progress: message.data.progress as number | undefined,
          })
        );
        break;

      case "analysis_progress":
        store.dispatch(
          updateAnalysisProgress({
            id: message.data.id as number,
            progress: message.data.progress as number,
            status: message.data.status as string,
          })
        );
        break;

      case "analysis_complete":
        console.log("Analysis complete:", message.data);
        break;

      case "pipeline_update":
        console.log("Pipeline update:", message.data);
        break;

      default:
        console.log("Unknown pipeline message type:", message.type);
    }
  }

  private handleAlertMessage(message: WebSocketMessage) {
    switch (message.type) {
      case "new_alert":
      case "critical_alert":
        store.dispatch(addNewAlert(message.data as unknown as Alert));
        break;

      case "alert_update":
        console.log("Alert update:", message.data);
        break;

      default:
        console.log("Unknown alert message type:", message.type);
    }
  }

  private attemptReconnect(socketType: "pipeline" | "alert") {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`Max reconnect attempts reached for ${socketType} socket`);
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Attempting to reconnect ${socketType} socket in ${delay}ms...`
    );

    setTimeout(() => {
      const state = store.getState();
      const token = state.auth.tokens?.access;

      if (token) {
        if (socketType === "pipeline") {
          this.connectPipelineSocket(token);
        } else {
          this.connectAlertSocket(token);
        }
      }
    }, delay);
  }

  disconnect() {
    if (this.pipelineSocket) {
      this.pipelineSocket.close();
      this.pipelineSocket = null;
    }

    if (this.alertSocket) {
      this.alertSocket.close();
      this.alertSocket = null;
    }
  }

  sendPipelineMessage(message: Record<string, unknown>) {
    if (this.pipelineSocket?.readyState === WebSocket.OPEN) {
      this.pipelineSocket.send(JSON.stringify(message));
    }
  }

  sendAlertMessage(message: Record<string, unknown>) {
    if (this.alertSocket?.readyState === WebSocket.OPEN) {
      this.alertSocket.send(JSON.stringify(message));
    }
  }

  ping() {
    this.sendPipelineMessage({ type: "ping" });
    this.sendAlertMessage({ type: "ping" });
  }
}

export const wsService = new WebSocketService();
