#[derive(Debug, Clone)]
pub struct ApiRequest { pub request_id: String, pub operation: String, pub payload: String }

#[derive(Debug, Clone)]
pub struct ApiResponse { pub request_id: String, pub ok: bool, pub payload: String }

impl ApiResponse {
    pub fn success(request_id: impl Into<String>, payload: impl Into<String>) -> Self {
        Self { request_id: request_id.into(), ok: true, payload: payload.into() }
    }
}
