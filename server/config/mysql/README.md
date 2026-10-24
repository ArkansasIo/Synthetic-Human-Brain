# Synthetic Human Brain — MySQL configuration reference
#
# The server reads a SQLAlchemy URL from the environment:
#   SYNTHETIC_BRAIN_DATABASE_URL=mysql+asyncmy://synthetic_brain:<password>@127.0.0.1:3306/synthetic_brain
#
# Files in this directory:
#
#   provision.sql    — one-time: create database `synthetic_brain` + app user + grants
#   schema.sql       — all tables (users, roles, projects, sessions, servers,
#                      workers, research_experiments, research_jobs,
#                      research_telemetry_events, research_audit_log)
#   seed.sql         — baseline roles and the local rust backend registration
#   views.sql        — v_project_summary, v_job_status, v_telemetry_latest
#   my.ini / my.cnf  — server options tuned for JSON telemetry workloads
#   maintenance.sql  — daily housekeeping (session expiry, stale workers,
#                      stuck jobs, telemetry/audit retention) + backup schedule
#
# Apply order:
#   1. mysql -u root -p < provision.sql
#   2. mysql -u root -p < schema.sql
#   3. mysql -u root -p < views.sql
#   4. mysql -u root -p < seed.sql
#
# Character set: utf8mb4 / utf8mb4_unicode_ci throughout (matches schema.sql).
# Engine: InnoDB for every table; foreign keys with CASCADE / SET NULL rules.
