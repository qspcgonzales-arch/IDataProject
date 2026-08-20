-- IDataProject PostgreSQL initialization script
-- Used by docker-compose postgres service on first database bootstrap.
--
-- Purpose (Aug 24 foundation task):
-- - Keep DB bootstrap deterministic
-- - Add commonly used extension for future migrations/log correlation
-- - Avoid direct DML into Odoo domain tables during raw Postgres init

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

