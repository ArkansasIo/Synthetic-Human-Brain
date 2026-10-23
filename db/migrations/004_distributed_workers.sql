-- Distributed research server and worker routing metadata.
USE synthetic_brain;

ALTER TABLE servers
    ADD COLUMN endpoint_url VARCHAR(2048) NULL,
    ADD COLUMN platform VARCHAR(32) NOT NULL DEFAULT 'linux',
    ADD COLUMN capabilities_json JSON NULL;

ALTER TABLE workers
    ADD COLUMN name VARCHAR(255) NOT NULL DEFAULT 'worker',
    ADD COLUMN endpoint_url VARCHAR(2048) NULL;

ALTER TABLE research_jobs
    ADD COLUMN worker_id CHAR(36) NULL,
    ADD CONSTRAINT fk_research_jobs_worker FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE SET NULL;

CREATE INDEX idx_research_jobs_worker ON research_jobs(worker_id);
