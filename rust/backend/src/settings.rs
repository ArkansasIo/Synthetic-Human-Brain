//! Settings / options for the Synthetic Human Brain Rust backend.
//!
//! Values load from `config/rust-backend.toml` (see `config/rust-backend.example.toml`)
//! with environment-variable overrides (`SYNTHETIC_BRAIN_*`).

use std::env;

/// Full runtime configuration for the backend process.
#[derive(Debug, Clone)]
pub struct Settings {
    /// Listening address for the HTTP API.
    pub host: String,
    /// Listening port (default 7800; Python server expects this value).
    pub port: u16,
    /// MySQL connection settings (see `store::MySqlConfig`).
    pub database: MySqlSettings,
    /// Worker pool sizing.
    pub workers: WorkerSettings,
    /// Operational toggles.
    pub options: OptionSettings,
}

/// MySQL connection settings — mirrors `server/config/mysql/my.ini` defaults.
#[derive(Debug, Clone)]
pub struct MySqlSettings {
    pub host: String,
    pub port: u16,
    pub database: String,
    pub username: String,
    /// Read from `SYNTHETIC_BRAIN_DB_PASSWORD`; never stored in config files.
    pub password_env: String,
    /// Pool sizing for the connection pool.
    pub max_connections: u32,
}

/// Worker pool settings — mirrors `server/config/server.example.toml`.
#[derive(Debug, Clone)]
pub struct WorkerSettings {
    pub max_concurrent_jobs: usize,
    pub backend: String,
}

/// Operational options and feature toggles.
#[derive(Debug, Clone)]
pub struct OptionSettings {
    /// Emit structured request logs.
    pub log_requests: bool,
    /// Refuse to start with the placeholder JWT/database credentials.
    pub refuse_placeholder_secrets: bool,
    /// Telemetry retention hint (days) surfaced to the Python server.
    pub telemetry_retention_days: u32,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".into(),
            port: 7800,
            database: MySqlSettings {
                host: "127.0.0.1".into(),
                port: 3306,
                database: "synthetic_brain".into(),
                username: "synthetic_brain".into(),
                password_env: "SYNTHETIC_BRAIN_DB_PASSWORD".into(),
                max_connections: 16,
            },
            workers: WorkerSettings {
                max_concurrent_jobs: 4,
                backend: "auto".into(),
            },
            options: OptionSettings {
                log_requests: true,
                refuse_placeholder_secrets: true,
                telemetry_retention_days: 90,
            },
        }
    }
}

impl Settings {
    /// Load settings from the environment over the compiled defaults.
    ///
    /// Supported variables:
    /// `SYNTHETIC_BRAIN_HOST`, `SYNTHETIC_BRAIN_PORT`,
    /// `SYNTHETIC_BRAIN_DB_HOST`, `SYNTHETIC_BRAIN_DB_PORT`,
    /// `SYNTHETIC_BRAIN_DB_NAME`, `SYNTHETIC_BRAIN_DB_USER`,
    /// `SYNTHETIC_BRAIN_DB_PASSWORD`, `SYNTHETIC_BRAIN_MAX_JOBS`,
    /// `SYNTHETIC_BRAIN_TELEMETRY_RETENTION_DAYS`.
    pub fn from_env() -> Self {
        let mut settings = Self::default();

        if let Ok(host) = env::var("SYNTHETIC_BRAIN_HOST") {
            settings.host = host;
        }
        if let Ok(port) = env::var("SYNTHETIC_BRAIN_PORT") {
            if let Ok(port) = port.parse() {
                settings.port = port;
            }
        }
        if let Ok(host) = env::var("SYNTHETIC_BRAIN_DB_HOST") {
            settings.database.host = host;
        }
        if let Ok(port) = env::var("SYNTHETIC_BRAIN_DB_PORT") {
            if let Ok(port) = port.parse() {
                settings.database.port = port;
            }
        }
        if let Ok(name) = env::var("SYNTHETIC_BRAIN_DB_NAME") {
            settings.database.database = name;
        }
        if let Ok(user) = env::var("SYNTHETIC_BRAIN_DB_USER") {
            settings.database.username = user;
        }
        if let Ok(jobs) = env::var("SYNTHETIC_BRAIN_MAX_JOBS") {
            if let Ok(jobs) = jobs.parse() {
                settings.workers.max_concurrent_jobs = jobs;
            }
        }
        if let Ok(days) = env::var("SYNTHETIC_BRAIN_TELEMETRY_RETENTION_DAYS") {
            if let Ok(days) = days.parse() {
                settings.options.telemetry_retention_days = days;
            }
        }
        settings
    }

    /// MySQL DSN without the password (password comes from the environment).
    pub fn database_url(&self) -> String {
        format!(
            "mysql://{}@{}:{}/{}",
            self.database.username, self.database.host, self.database.port, self.database.database
        )
    }

    /// True when the placeholder password is still configured.
    pub fn using_placeholder_secret(&self) -> bool {
        matches!(env::var(&self.database.password_env), Ok(value) if value.contains("CHANGE_ME"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn defaults_match_server_config() {
        let settings = Settings::default();
        assert_eq!(settings.port, 7800);
        assert_eq!(settings.database.database, "synthetic_brain");
        assert_eq!(settings.workers.max_concurrent_jobs, 4);
    }

    #[test]
    fn database_url_contains_host_and_db() {
        let settings = Settings::default();
        let url = settings.database_url();
        assert!(url.contains("127.0.0.1:3306"));
        assert!(url.ends_with("/synthetic_brain"));
    }
}
