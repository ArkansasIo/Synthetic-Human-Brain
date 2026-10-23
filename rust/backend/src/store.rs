#[derive(Debug, Clone)]
pub struct MySqlConfig {
    pub host: String,
    pub port: u16,
    pub database: String,
    pub username: String,
}

#[derive(Debug, Clone)]
pub struct ExperimentRecord {
    pub id: String,
    pub name: String,
    pub status: String,
    pub simulation_time_ms: f64,
    pub spike_count: u64,
}

impl ExperimentRecord {
    pub fn new(id: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            name: name.into(),
            status: "created".into(),
            simulation_time_ms: 0.0,
            spike_count: 0,
        }
    }
}
