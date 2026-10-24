# Synthetic Human Brain — MySQL maintenance & scheduled jobs (cron / Task Scheduler)
#
# Linux crontab (crontab -e):
#   0 3 * * *   /usr/bin/mysql synthetic_brain < /opt/synthetic-brain/server/config/mysql/maintenance.sql
#   0 4 * * 0   /usr/bin/mysqldump --single-transaction synthetic_brain | gzip > /var/backups/synthetic_brain-$(date +\%F).sql.gz
#
# Windows Task Scheduler (PowerShell, elevated):
#   Register-ScheduledJob -Name "SHB Maintenance" -Trigger (New-JobTrigger -Daily -At 3am) `
#     -ScriptBlock { & mysql synthetic_brain < C:\synthetic-brain\server\config\mysql\maintenance.sql }

-- 1) Expire stale sessions (older than session_minutes setting, default 480 min)
DELETE FROM sessions
WHERE expires_at < NOW() OR revoked_at IS NOT NULL;

-- 2) Mark workers offline when heartbeats stop (10 minutes)
UPDATE workers
SET status = 'offline'
WHERE last_heartbeat IS NULL OR last_heartbeat < NOW() - INTERVAL 10 MINUTE;

-- 3) Mark servers offline on the same rule
UPDATE servers
SET status = 'offline'
WHERE last_heartbeat IS NULL OR last_heartbeat < NOW() - INTERVAL 10 MINUTE;

-- 4) Fail jobs stuck in 'running' for over 1 hour
UPDATE research_jobs
SET status = 'failed', completed_at = NOW()
WHERE status = 'running' AND started_at < NOW() - INTERVAL 1 HOUR;

-- 5) Trim telemetry beyond 90 days (retain aggregated latest via v_telemetry_latest)
DELETE FROM research_telemetry_events
WHERE timestamp < NOW() - INTERVAL 90 DAY;

-- 6) Trim audit log beyond 1 year
DELETE FROM research_audit_log
WHERE created_at < NOW() - INTERVAL 1 YEAR;

-- 7) Optimize hot tables after deletes
OPTIMIZE TABLE research_telemetry_events, research_audit_log, sessions;
