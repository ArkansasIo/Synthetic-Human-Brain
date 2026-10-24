-- Synthetic Human Brain — database & user provisioning (run as MySQL root)
-- Idempotent: safe to re-run.

CREATE DATABASE IF NOT EXISTS synthetic_brain
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'synthetic_brain'@'localhost' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';
CREATE USER IF NOT EXISTS 'synthetic_brain'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';

GRANT SELECT, INSERT, UPDATE, DELETE ON synthetic_brain.* TO 'synthetic_brain'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON synthetic_brain.* TO 'synthetic_brain'@'127.0.0.1';
FLUSH PRIVILEGES;

-- After provisioning, set the real password and update the server env:
--   ALTER USER 'synthetic_brain'@'127.0.0.1' IDENTIFIED BY '<new password>';
--   SYNTHETIC_BRAIN_DATABASE_URL=mysql+asyncmy://synthetic_brain:<password>@127.0.0.1:3306/synthetic_brain
