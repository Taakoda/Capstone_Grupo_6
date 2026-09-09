DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kallicode_app_local') THEN
    CREATE ROLE kallicode_app_local LOGIN PASSWORD 'dev' IN ROLE kallicode_app;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kallicode_admin_local') THEN
    CREATE ROLE kallicode_admin_local LOGIN PASSWORD 'dev' IN ROLE kallicode_admin;
    ALTER ROLE kallicode_admin_local BYPASSRLS;
  END IF;
END $$;

GRANT USAGE ON SCHEMA core, audit, vec TO kallicode_app_local, kallicode_admin_local;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA core TO kallicode_app_local, kallicode_admin_local;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA audit TO kallicode_app_local, kallicode_admin_local;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA vec TO kallicode_app_local, kallicode_admin_local;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core, audit, vec TO kallicode_app_local, kallicode_admin_local;
