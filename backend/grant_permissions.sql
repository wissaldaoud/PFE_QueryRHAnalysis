-- Script pour donner les droits à hr_user sur hr_datawarehouse
-- Exécuter ce script en tant que superuser (postgres)

\c hr_datawarehouse

-- Donner tous les droits sur le schéma public
GRANT ALL ON SCHEMA public TO hr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hr_user;

-- Permettre à hr_user de créer des tables
GRANT CREATE ON SCHEMA public TO hr_user;

-- Définir les permissions par défaut pour les futurs objets
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hr_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hr_user;

-- Vérifier les droits
SELECT grantee, privilege_type 
FROM information_schema.schema_privileges 
WHERE schema_name = 'public' AND grantee = 'hr_user';
