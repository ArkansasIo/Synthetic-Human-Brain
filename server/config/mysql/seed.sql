-- Synthetic Human Brain — seed data (run after schema.sql)

-- Roles
INSERT INTO roles (id, name, description) VALUES
    ('10000000-0000-0000-0000-000000000001', 'administrator', 'Full server administration'),
    ('10000000-0000-0000-0000-000000000002', 'researcher',    'Create projects, experiments, jobs')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- Reserved view: never edit these rows.
INSERT INTO servers (id, name, host, port, platform, status) VALUES
    ('20000000-0000-0000-0000-000000000001', 'local-rust-backend', '127.0.0.1', 7800, 'windows', 'offline')
ON DUPLICATE KEY UPDATE name = VALUES(name);
