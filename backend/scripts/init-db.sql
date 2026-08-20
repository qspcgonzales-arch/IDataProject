-- IDataProject — PostgreSQL initialisation script
-- Runs once when the postgres container is first created.
-- The idata_dev database is created automatically by the POSTGRES_DB
-- environment variable; this script adds any extra setup needed.

-- Ensure the odoo user has the correct role attributes
ALTER USER odoo CREATEDB;
