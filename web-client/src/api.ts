export type ServerConfig = {
  baseUrl: string;
  websocketUrl: string;
};

export type ApiEnvelope<T> = {
  protocol_version: string;
  request_id: string;
  message_type: string;
  timestamp: string;
  payload: T;
};

export class ResearchApi {
  constructor(private readonly config: ServerConfig) {}

  async health(): Promise<unknown> {
    const response = await fetch(`${this.config.baseUrl}/api/v1/health`);
    if (!response.ok) throw new Error(`Health request failed: ${response.status}`);
    return response.json();
  }

  async login(username: string, password: string): Promise<unknown> {
    const response = await fetch(`${this.config.baseUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!response.ok) throw new Error(`Login failed: ${response.status}`);
    return response.json();
  }

  connectTelemetry(onMessage: (event: MessageEvent) => void): WebSocket {
    const socket = new WebSocket(this.config.websocketUrl);
    socket.addEventListener("message", onMessage);
    return socket;
  }
}
