export type ServerConfig = {
  baseUrl: string;
  websocketUrl: string;
};

export type User = {
  id: string;
  username: string;
  display_name: string;
  roles: string[];
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  session_id: string;
  user: User;
};

export type ApiEnvelope<T> = {
  protocol_version: string;
  request_id: string;
  session_id?: string;
  message_type: string;
  timestamp: string;
  payload: T;
};

export class ResearchApi {
  private token: string | null = localStorage.getItem("synthetic_brain_access_token");

  constructor(private readonly config: ServerConfig) {}

  setToken(token: string | null): void {
    this.token = token;
    if (token) localStorage.setItem("synthetic_brain_access_token", token);
    else localStorage.removeItem("synthetic_brain_access_token");
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set("Content-Type", "application/json");
    if (this.token) headers.set("Authorization", `Bearer ${this.token}`);
    const response = await fetch(`${this.config.baseUrl}${path}`, { ...init, headers });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`${response.status}: ${detail || response.statusText}`);
    }
    return response.json() as Promise<T>;
  }

  async health(): Promise<unknown> {
    return this.request("/api/v1/health");
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    const result = await this.request<AuthResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password, client_id: "researcher-browser", platform: "browser" })
    });
    this.setToken(result.access_token);
    return result;
  }

  async me(): Promise<User> {
    return this.request<User>("/api/v1/me");
  }

  async projects(): Promise<{ items: unknown[] }> {
    return this.request("/api/v1/projects");
  }

  async createProject(name: string, description = ""): Promise<unknown> {
    return this.request("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify({ name, description, visibility: "private" })
    });
  }

  async experiments(projectId: string): Promise<{ items: unknown[] }> {
    return this.request(`/api/v1/projects/${projectId}/experiments`);
  }

  async jobs(): Promise<{ items: unknown[] }> {
    return this.request("/api/v1/jobs");
  }

  async telemetry(experimentId: string): Promise<{ items: unknown[] }> {
    return this.request(`/api/v1/experiments/${experimentId}/telemetry`);
  }

  connectTelemetry(onMessage: (event: MessageEvent) => void): WebSocket {
    const url = new URL(this.config.websocketUrl);
    if (this.token) url.searchParams.set("token", this.token);
    const socket = new WebSocket(url.toString());
    socket.addEventListener("message", onMessage);
    return socket;
  }
}
