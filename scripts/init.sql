-- Initialization script for PostgreSQL
-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial tables will be handled by Alembic migrations
-- This file can be used for initial data seeding

-- Example: Insert default departments
INSERT INTO departments (name, code, description) VALUES
    ('Ressources Humaines', 'RH', 'Département des ressources humaines'),
    ('IT', 'IT', 'Département informatique'),
    ('Finance', 'FIN', 'Département financier'),
    ('Marketing', 'MKT', 'Département marketing'),
    ('Operations', 'OPS', 'Département opérations')
ON CONFLICT DO NOTHING;
