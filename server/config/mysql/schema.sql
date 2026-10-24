-- Synthetic Human Brain — MySQL schema (mirrors server/python/app/models.py)
-- Apply to database `synthetic_brain`. Character set / collation enforced per table.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- users, roles, user_roles
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id              CHAR(36)     NOT NULL,
    username        VARCHAR(128) NOT NULL,
    display_name    VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    status          VARCHAR(32)  NOT NULL DEFAULT 'active',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at   DATETIME     NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    KEY ix_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS roles (
    id          CHAR(36)     NOT NULL,
    name        VARCHAR(64)  NOT NULL,
    description VARCHAR(255) NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_roles (
    user_id    CHAR(36) NOT NULL,
    role_id    CHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- projects, project_members
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS projects (
    id            CHAR(36)     NOT NULL,
    name          VARCHAR(255) NOT NULL,
    description   TEXT         NULL,
    owner_user_id CHAR(36)     NOT NULL,
    visibility    VARCHAR(32)  NOT NULL DEFAULT 'private',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_projects_owner (owner_user_id),
    CONSTRAINT fk_projects_owner FOREIGN KEY (owner_user_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS project_members (
    project_id   CHAR(36) NOT NULL,
    user_id      CHAR(36) NOT NULL,
    project_role VARCHAR(32) NOT NULL DEFAULT 'researcher',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    CONSTRAINT fk_pm_project FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    CONSTRAINT fk_pm_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- sessions
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sessions (
    id           CHAR(36)     NOT NULL,
    user_id      CHAR(36)     NOT NULL,
    client_id    VARCHAR(128) NOT NULL,
    platform     VARCHAR(32)  NOT NULL,
    expires_at   DATETIME     NOT NULL,
    revoked_at   DATETIME     NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_sessions_user (user_id),
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- servers, workers
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS servers (
    id                CHAR(36)     NOT NULL,
    name              VARCHAR(255) NOT NULL,
    host              VARCHAR(255) NOT NULL DEFAULT '127.0.0.1',
    port              INT          NOT NULL DEFAULT 8787,
    endpoint_url      VARCHAR(2048) NULL,
    platform          VARCHAR(32)  NOT NULL DEFAULT 'linux',
    status            VARCHAR(32)  NOT NULL DEFAULT 'offline',
    capabilities_json JSON         NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat    DATETIME     NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS workers (
    id                CHAR(36)     NOT NULL,
    server_id         CHAR(36)     NOT NULL,
    name              VARCHAR(255) NOT NULL DEFAULT 'worker',
    backend           VARCHAR(32)  NOT NULL DEFAULT 'hybrid',
    endpoint_url      VARCHAR(2048) NULL,
    status            VARCHAR(32)  NOT NULL DEFAULT 'offline',
    capabilities_json JSON         NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat    DATETIME     NULL,
    PRIMARY KEY (id),
    KEY ix_workers_server (server_id),
    CONSTRAINT fk_workers_server FOREIGN KEY (server_id) REFERENCES servers (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- research_experiments, research_jobs
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS research_experiments (
    id                 CHAR(36)     NOT NULL,
    project_id         CHAR(36)     NOT NULL,
    name               VARCHAR(255) NOT NULL,
    status             VARCHAR(32)  NOT NULL DEFAULT 'created',
    backend            VARCHAR(32)  NOT NULL DEFAULT 'auto',
    configuration_json JSON         NULL,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_experiments_project (project_id),
    CONSTRAINT fk_experiments_project FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS research_jobs (
    id              CHAR(36)     NOT NULL,
    experiment_id   CHAR(36)     NOT NULL,
    operation       VARCHAR(128) NOT NULL,
    status          VARCHAR(32)  NOT NULL DEFAULT 'queued',
    worker_id       CHAR(36)     NULL,
    payload_json    JSON         NULL,
    result_json     JSON         NULL,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at      DATETIME     NULL,
    completed_at    DATETIME     NULL,
    PRIMARY KEY (id),
    KEY ix_jobs_experiment (experiment_id),
    KEY ix_jobs_status (status),
    CONSTRAINT fk_jobs_experiment FOREIGN KEY (experiment_id) REFERENCES research_experiments (id) ON DELETE CASCADE,
    CONSTRAINT fk_jobs_worker FOREIGN KEY (worker_id) REFERENCES workers (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- research_telemetry_events, research_audit_log
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS research_telemetry_events (
    id            CHAR(36)     NOT NULL,
    experiment_id CHAR(36)     NOT NULL,
    metric        VARCHAR(128) NOT NULL,
    value         DOUBLE       NOT NULL,
    timestamp     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json JSON         NULL,
    PRIMARY KEY (id),
    KEY ix_telemetry_experiment (experiment_id),
    KEY ix_telemetry_metric (metric),
    KEY ix_telemetry_timestamp (timestamp),
    CONSTRAINT fk_telemetry_experiment FOREIGN KEY (experiment_id) REFERENCES research_experiments (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS research_audit_log (
    id            CHAR(36)     NOT NULL,
    user_id       CHAR(36)     NULL,
    action        VARCHAR(128) NOT NULL,
    resource_type VARCHAR(64)  NULL,
    resource_id   CHAR(36)     NULL,
    details_json  JSON         NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_audit_user (user_id),
    KEY ix_audit_created (created_at),
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
