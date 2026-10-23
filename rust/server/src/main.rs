use std::sync::{Arc, Mutex};

use axum::{
    extract::{ws::{Message, WebSocket, WebSocketUpgrade}, State},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use synthetic_brain_backend::BackendService;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::info;

#[derive(Clone)]
struct AppState {
    service: Arc<Mutex<BackendService>>,
}

#[derive(Debug, Serialize)]
struct HealthResponse { status: &'static str, service: &'static str, version: &'static str }

#[derive(Debug, Serialize)]
struct AboutResponse {
    name: &'static str,
    version: &'static str,
    developer: &'static str,
    role: &'static str,
    platforms: [&'static str; 3],
}

#[derive(Debug, Deserialize)]
struct StepRequest { input_current: f64, dt_ms: f64 }

#[derive(Debug, Serialize)]
struct StepResponse { spike: bool, simulation_time_ms: f64, spikes_emitted: u64 }

#[derive(Debug, Deserialize)]
struct JobRequest { job_id: String, operation: String, payload: Option<serde_json::Value> }

#[derive(Debug, Serialize)]
struct JobResponse { accepted: bool, job_id: String, operation: String, status: &'static str, payload: serde_json::Value }

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_env_filter("info").init();
    let state = AppState { service: Arc::new(Mutex::new(BackendService::new())) };
    let app = Router::new()
        .route("/health", get(health))
        .route("/api/v1/health", get(health))
        .route("/api/v1/about", get(about))
        .route("/api/v1/simulation/step", post(step))
        .route("/api/v1/jobs", post(run_job))
        .route("/ws", get(websocket))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);
    let address = std::env::var("SYNTHETIC_BRAIN_RUST_ADDR").unwrap_or_else(|_| "0.0.0.0:7800".to_string());
    let listener = tokio::net::TcpListener::bind(&address).await.expect("failed to bind Rust server");
    info!(%address, "Synthetic Brain Rust server started");
    axum::serve(listener, app).await.expect("Rust server stopped");
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse { status: "ok", service: "synthetic-brain-rust-server", version: "0.1.0-alpha" })
}

async fn about() -> Json<AboutResponse> {
    Json(AboutResponse { name: "Synthetic Human Brain", version: "0.1.0-alpha", developer: "ArkansasIo", role: "Rust simulation and worker backend", platforms: ["windows", "macos", "linux"] })
}

async fn step(State(state): State<AppState>, Json(request): Json<StepRequest>) -> Json<StepResponse> {
    let mut service = state.service.lock().expect("backend service lock poisoned");
    let spike = service.step(request.input_current, request.dt_ms);
    Json(StepResponse { spike, simulation_time_ms: service.simulation_time_ms, spikes_emitted: service.spikes_emitted })
}

async fn run_job(State(state): State<AppState>, Json(request): Json<JobRequest>) -> Json<JobResponse> {
    let payload = request.payload.unwrap_or_else(|| serde_json::json!({}));
    match request.operation.as_str() {
        "simulation.step" => {
            let input_current = payload.get("input_current").and_then(serde_json::Value::as_f64).unwrap_or(0.0);
            let dt_ms = payload.get("dt_ms").and_then(serde_json::Value::as_f64).unwrap_or(1.0);
            let mut service = state.service.lock().expect("backend service lock poisoned");
            let spike = service.step(input_current, dt_ms);
            let result = serde_json::json!({
                "spike": spike,
                "simulation_time_ms": service.simulation_time_ms,
                "spikes_emitted": service.spikes_emitted
            });
            Json(JobResponse { accepted: true, job_id: request.job_id, operation: request.operation, status: "completed", payload: result })
        }
        "simulation.run" => {
            let steps = payload.get("steps").and_then(serde_json::Value::as_u64).unwrap_or(1).min(100_000);
            let input_current = payload.get("input_current").and_then(serde_json::Value::as_f64).unwrap_or(0.0);
            let dt_ms = payload.get("dt_ms").and_then(serde_json::Value::as_f64).unwrap_or(1.0);
            let mut service = state.service.lock().expect("backend service lock poisoned");
            let mut spikes = 0_u64;
            for _ in 0..steps {
                if service.step(input_current, dt_ms) { spikes += 1; }
            }
            let result = serde_json::json!({
                "steps": steps,
                "spikes_in_run": spikes,
                "simulation_time_ms": service.simulation_time_ms,
                "spikes_emitted": service.spikes_emitted
            });
            Json(JobResponse { accepted: true, job_id: request.job_id, operation: request.operation, status: "completed", payload: result })
        }
        _ => {
            let result = serde_json::json!({"error": "unsupported_operation", "operation": request.operation});
            Json(JobResponse { accepted: false, job_id: request.job_id, operation: request.operation, status: "rejected", payload: result })
        }
    }
}

async fn websocket(upgrade: WebSocketUpgrade) -> impl IntoResponse { upgrade.on_upgrade(handle_socket) }

async fn handle_socket(mut socket: WebSocket) {
    while let Some(Ok(message)) = socket.recv().await {
        match message {
            Message::Text(text) => {
                let response = format!("{{\"type\":\"ack\",\"message\":{text}}}");
                if socket.send(Message::Text(response.into())).await.is_err() { break; }
            }
            Message::Ping(payload) => { if socket.send(Message::Pong(payload)).await.is_err() { break; } }
            Message::Close(_) => break,
            _ => {}
        }
    }
}
