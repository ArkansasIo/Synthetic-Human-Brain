-- Synthetic Human Brain — reporting views (run after schema.sql)

CREATE OR REPLACE VIEW v_project_summary AS
SELECT
    p.id,
    p.name,
    p.visibility,
    u.username AS owner,
    COUNT(DISTINCT m.user_id) AS member_count,
    COUNT(DISTINCT e.id)      AS experiment_count
FROM projects p
JOIN users u           ON u.id = p.owner_user_id
LEFT JOIN project_members m ON m.project_id = p.id
LEFT JOIN research_experiments e ON e.project_id = p.id
GROUP BY p.id, p.name, p.visibility, u.username;

CREATE OR REPLACE VIEW v_job_status AS
SELECT
    j.id,
    j.operation,
    j.status,
    e.name AS experiment,
    p.name AS project,
    w.name AS worker,
    j.created_at,
    j.started_at,
    j.completed_at,
    TIMESTAMPDIFF(SECOND, j.started_at, j.completed_at) AS runtime_seconds
FROM research_jobs j
JOIN research_experiments e ON e.id = j.experiment_id
JOIN projects p             ON p.id = e.project_id
LEFT JOIN workers w         ON w.id = j.worker_id;

CREATE OR REPLACE VIEW v_telemetry_latest AS
SELECT t.experiment_id, t.metric, t.value, t.timestamp
FROM research_telemetry_events t
JOIN (
    SELECT experiment_id, metric, MAX(timestamp) AS max_ts
    FROM research_telemetry_events
    GROUP BY experiment_id, metric
) latest
  ON latest.experiment_id = t.experiment_id
 AND latest.metric = t.metric
 AND latest.max_ts = t.timestamp;
