-- Synthetic Human Brain: research API experiment, job, telemetry, and audit schema.
-- These names intentionally coexist with the legacy Rust backend tables in db/rust_backend.sql.
USE synthetic_brain;

CREATE TABLE IF NOT EXISTS research_experiments (
    id CHAR(36) PRIMARY KEY,
    project_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'created',
    backend VARCHAR(32) NOT NULL DEFAULT 'auto',
    configuration_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_research_experiments_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_research_experiments_project (project_id),
    INDEX idx_research_experiments_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS research_jobs (
    id CHAR(36) PRIMARY KEY,
    experiment_id CHAR(36) NOT NULL,
    operation VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    payload_json JSON NULL,
    result_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    CONSTRAINT fk_research_jobs_experiment FOREIGN KEY (experiment_id) REFERENCES research_experiments(id) ON DELETE CASCADE,
    INDEX idx_research_jobs_experiment (experiment_id),
    INDEX idx_research_jobs_status (status)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS research_telemetry_events (
    id CHAR(36) PRIMARY KEY,
    experiment_id CHAR(36) NOT NULL,
    metric VARCHAR(128) NOT NULL,
    value DOUBLE NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json JSON NULL,
    CONSTRAINT fk_research_telemetry_experiment FOREIGN KEY (experiment_id) REFERENCES research_experiments(id) ON DELETE CASCADE,
    INDEX idx_research_telemetry_experiment_metric (experiment_id, metric),
    INDEX idx_research_telemetry_timestamp (timestamp)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS research_audit_log (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NULL,
    action VARCHAR(128) NOT NULL,
    resource_type VARCHAR(64) NULL,
    resource_id CHAR(36) NULL,
    details_json JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_research_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_research_audit_user (user_id),
    INDEX idx_research_audit_created (created_at)
) ENGINE=InnoDB;
