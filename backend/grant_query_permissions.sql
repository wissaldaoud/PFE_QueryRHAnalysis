-- Grant permissions to hr_user for query engine access
GRANT USAGE ON SCHEMA dim TO hr_user;
GRANT SELECT ON ALL TABLES IN SCHEMA dim TO hr_user;

GRANT USAGE ON SCHEMA fait TO hr_user;
GRANT SELECT ON ALL TABLES IN SCHEMA fait TO hr_user;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA dim GRANT SELECT ON TABLES TO hr_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA fait GRANT SELECT ON TABLES TO hr_user;

-- Verify permissions
\du hr_user
