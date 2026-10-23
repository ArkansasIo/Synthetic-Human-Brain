CREATE DATABASE IF NOT EXISTS synthetic_brain;
USE synthetic_brain;

CREATE TABLE IF NOT EXISTS backend_jobs (
    id VARCHAR(64) PRIMARY KEY,
    job_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    payload_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS hardware_devices (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    kind VARCHAR(64) NOT NULL,
    driver VARCHAR(255) NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    metadata_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiments (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL,
    backend VARCHAR(32) NOT NULL,
    simulation_time_ms DOUBLE NOT NULL DEFAULT 0,
    spike_count BIGINT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS neural_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    experiment_id VARCHAR(64) NOT NULL,
    timestamp_ms DOUBLE NOT NULL,
    channel INT UNSIGNED NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    value DOUBLE NULL,
    INDEX idx_events_experiment_time (experiment_id, timestamp_ms),
    CONSTRAINT fk_events_experiment FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metrics (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    experiment_id VARCHAR(64) NOT NULL,
    metric_name VARCHAR(128) NOT NULL,
    metric_value DOUBLE NOT NULL,
    timestamp_ms DOUBLE NOT NULL,
    INDEX idx_metrics_experiment_time (experiment_id, timestamp_ms),
    CONSTRAINT fk_metrics_experiment FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    actor_id VARCHAR(64) NULL,
    action VARCHAR(128) NOT NULL,
    resource_type VARCHAR(64) NULL,
    resource_id VARCHAR(64) NULL,
    details_json JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
