use axum::{
    extract::ws::{Message, WebSocket, WebSocketUpgrade},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::info;

#[derive(Debug, Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
    version: &'static str,
}

#[derive(Debug, Serialize)]
struct AboutResponse {
    name: &'static str,
    version: &'static str,
    developer: &'static str,
    role: &'static str,
    platforms: [&'static str; 3],
}

#[derive(Debug, Deserialize)]
struct JobRequest {
    operation: String,
    payload: Option<serde_json::Value>,
}

#[derive(Debug, Serialize)]
struct JobResponse {
    accepted: bool,
    operation: String,
    payload: Option<serde_json::Value>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let app = Router::new()
        .route("/api/v1/health", get(health))
        .route("/api/v1/about", get(about))
        .route("/api/v1/jobs", post(submit_job))
        .route("/ws", get(websocket))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http());

    let address = std::env::var("SYNTHETIC_BRAIN_RUST_ADDR")
        .unwrap_or_else(|_| "0.0.0.0:7800".to_string());
    let listener = tokio::net::TcpListener::bind(&address)
        .await
        .expect("failed to bind Rust server");

    info!(%address, "Synthetic Brain Rust server started");
    axum::serve(listener, app).await.expect("Rust server stopped");
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok",
        service: "synthetic-brain-rust-server",
        version: "0.1.0",
    })
}

async fn about() -> Json<AboutResponse> {
    Json(AboutResponse {
        name: "Synthetic Human Brain",
        version: "0.1.0-alpha",
        developer: "ArkansasIo",
        role: "Rust simulation and worker backend",
        platforms: ["windows", "macos", "linux"],
    })
}

async fn submit_job(Json(request): Json<JobRequest>) -> Json<JobResponse> {
    Json(JobResponse {
        accepted: true,
        operation: request.operation,
        payload: request.payload,
    })
}

async fn websocket(upgrade: WebSocketUpgrade) -> impl IntoResponse {
    upgrade.on_upgrade(handle_socket)
}

async fn handle_socket(mut socket: WebSocket) {
    while let Some(Ok(message)) = socket.recv().await {
        match message {
            Message::Text(text) => {
                let response = format!("{{\"type\":\"ack\",\"message\":{text}}}");
                if socket.send(Message::Text(response.into())).await.is_err() {
                    break;
                }
            }
            Message::Ping(payload) => {
                if socket.send(Message::Pong(payload)).await.is_err() {
                    break;
                }
            }
            Message::Close(_) => break,
            _ => {}
        }
    }
}
