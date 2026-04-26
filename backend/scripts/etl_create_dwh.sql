-- ==============================================================================
-- SCRIPT ETL - DATA WAREHOUSE HR POUR QLIK SENSE
-- Transforme les données de hr_analytics_db vers hr_datawarehouse
-- Date: 25 février 2026
-- ==============================================================================

-- CONNEXION À: hr_datawarehouse
-- Exécuter avec: psql -h localhost -U hr_user -d hr_datawarehouse -f etl_create_dwh.sql

\echo '========================================='
\echo '  CRÉATION DU DATA WAREHOUSE HR'
\echo '========================================='

-- ==============================================================================
-- CRÉATION DES SCHÉMAS
-- ==============================================================================

\echo 'Création des schémas dim et fait...'

DROP SCHEMA IF EXISTS dim CASCADE;
DROP SCHEMA IF EXISTS fait CASCADE;

CREATE SCHEMA dim;
CREATE SCHEMA fait;

\echo '✅ Schémas créés'

-- ==============================================================================
-- DIMENSION CALENDRIER
-- ==============================================================================

\echo 'Création de dim.dim_calendrier...'

CREATE TABLE dim.dim_calendrier (
    date DATE PRIMARY KEY,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    jour INTEGER NOT NULL,
    semaine INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,  -- 1=Lundi, 7=Dimanche
    premier_jour_mois DATE NOT NULL,
    trimestre INTEGER NOT NULL
);

-- Générer calendrier pour 10 ans (2020-2030)
INSERT INTO dim.dim_calendrier (
    date, annee, mois, jour, semaine, jour_semaine, premier_jour_mois, trimestre
)
SELECT 
    date_jour::DATE AS date,
    EXTRACT(YEAR FROM date_jour)::INTEGER AS annee,
    EXTRACT(MONTH FROM date_jour)::INTEGER AS mois,
    EXTRACT(DAY FROM date_jour)::INTEGER AS jour,
    EXTRACT(WEEK FROM date_jour)::INTEGER AS semaine,
    EXTRACT(ISODOW FROM date_jour)::INTEGER AS jour_semaine,
    DATE_TRUNC('month', date_jour)::DATE AS premier_jour_mois,
    EXTRACT(QUARTER FROM date_jour)::INTEGER AS trimestre
FROM generate_series(
    '2020-01-01'::DATE,
    '2030-12-31'::DATE,
    '1 day'::interval
) AS date_jour;

\echo '✅ dim_calendrier: ' :'ROW_COUNT' ' lignes insérées'

-- ==============================================================================
-- DIMENSION EMPLOYÉ
-- ==============================================================================

\echo 'Création de dim.dim_employe...'

CREATE TABLE dim.dim_employe (
    nudoss INTEGER PRIMARY KEY,
    code_societe VARCHAR(10) DEFAULT 'SOPRAHR',
    type_dossier VARCHAR(50) DEFAULT 'Employé',
    matricule VARCHAR(50),
    nom VARCHAR(100),
    prenom VARCHAR(100),
    nom_complet VARCHAR(200),
    code_sexe VARCHAR(1),
    libelle_sexe VARCHAR(20),
    date_naissance DATE,
    age INTEGER,
    tranche_age VARCHAR(20),
    flag_employe_actif BOOLEAN
);

-- Charger depuis hr_analytics_db.public.employees via dblink
-- Note: dblink doit être installé (CREATE EXTENSION dblink;)

\echo 'Installation de dblink si nécessaire...'
CREATE EXTENSION IF NOT EXISTS dblink;

\echo 'Chargement des employés depuis hr_analytics_db...'

INSERT INTO dim.dim_employe (
    nudoss, matricule, nom, prenom, nom_complet, 
    code_sexe, libelle_sexe, date_naissance, age, tranche_age, flag_employe_actif
)
SELECT 
    id AS nudoss,
    COALESCE(employee_id, 'EMP' || id::TEXT) AS matricule,
    COALESCE(last_name, SPLIT_PART(full_name, ' ', 2)) AS nom,
    COALESCE(first_name, SPLIT_PART(full_name, ' ', 1)) AS prenom,
    full_name AS nom_complet,
    CASE 
        WHEN gender = 'male' THEN 'M'
        WHEN gender = 'female' THEN 'F'
        ELSE 'U'
    END AS code_sexe,
    CASE 
        WHEN gender = 'male' THEN 'Homme'
        WHEN gender = 'female' THEN 'Femme'
        ELSE 'Non spécifié'
    END AS libelle_sexe,
    date_of_birth AS date_naissance,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))::INTEGER AS age,
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) < 25 THEN '< 25 ans'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 25 AND 34 THEN '25-34 ans'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 35 AND 44 THEN '35-44 ans'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) BETWEEN 45 AND 54 THEN '45-54 ans'
        ELSE '55+ ans'
    END AS tranche_age,
    (employment_status = 'active') AS flag_employe_actif
FROM dblink(
    'host=localhost port=5432 dbname=hr_analytics_db user=hr_user password=hr_password123',
    'SELECT id, employee_id, first_name, last_name, full_name, gender, date_of_birth, employment_status FROM employees'
) AS emp(
    id INTEGER,
    employee_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    gender VARCHAR(20),
    date_of_birth DATE,
    employment_status VARCHAR(20)
);

\echo '✅ dim_employe: ' :'ROW_COUNT' ' lignes insérées'

-- ==============================================================================
-- FAIT CONTRAT
-- ==============================================================================

\echo 'Création de fait.fait_contrat...'

CREATE TABLE fait.fait_contrat (
    id_contrat SERIAL PRIMARY KEY,
    nudoss INTEGER REFERENCES dim.dim_employe(nudoss),
    code_societe VARCHAR(10) DEFAULT 'SOPRAHR',
    date_debut_contrat DATE NOT NULL,
    date_fin_contrat DATE,
    duree_contrat_jours INTEGER,
    flag_contrat_actif BOOLEAN,
    code_type_contrat VARCHAR(10),
    libelle_type_contrat VARCHAR(50),
    code_nature_contrat VARCHAR(10),
    libelle_nature_contrat VARCHAR(50),
    categorie_contrat VARCHAR(50),
    annee_debut INTEGER,
    mois_debut INTEGER
);

INSERT INTO fait.fait_contrat (
    nudoss, date_debut_contrat, date_fin_contrat, duree_contrat_jours,
    flag_contrat_actif, code_type_contrat, libelle_type_contrat,
    code_nature_contrat, libelle_nature_contrat, categorie_contrat,
    annee_debut, mois_debut
)
SELECT 
    id AS nudoss,
    hire_date AS date_debut_contrat,
    termination_date AS date_fin_contrat,
    CASE 
        WHEN termination_date IS NOT NULL THEN (termination_date - hire_date)
        ELSE (CURRENT_DATE - hire_date)
    END AS duree_contrat_jours,
    (employment_status = 'active') AS flag_contrat_actif,
    'CDI' AS code_type_contrat,
    'Contrat à Durée Indéterminée' AS libelle_type_contrat,
    'FT' AS code_nature_contrat,
    'Temps Plein' AS libelle_nature_contrat,
    CASE 
        WHEN employment_status = 'active' THEN 'Contrat Actif'
        WHEN employment_status = 'terminated' THEN 'Contrat Terminé'
        ELSE 'Autre'
    END AS categorie_contrat,
    EXTRACT(YEAR FROM hire_date)::INTEGER AS annee_debut,
    EXTRACT(MONTH FROM hire_date)::INTEGER AS mois_debut
FROM dblink(
    'host=localhost port=5432 dbname=hr_analytics_db user=hr_user password=hr_password123',
    'SELECT id, hire_date, termination_date, employment_status FROM employees WHERE hire_date IS NOT NULL'
) AS emp(
    id INTEGER,
    hire_date DATE,
    termination_date DATE,
    employment_status VARCHAR(20)
);

\echo '✅ fait_contrat: ' :'ROW_COUNT' ' lignes insérées'

-- ==============================================================================
-- FAIT AFFECTATION (Postes)
-- ==============================================================================

\echo 'Création de fait.fait_affectation...'

CREATE TABLE fait.fait_affectation (
    id_affectation SERIAL PRIMARY KEY,
    nudoss INTEGER REFERENCES dim.dim_employe(nudoss),
    code_societe VARCHAR(10) DEFAULT 'SOPRAHR',
    date_debut_affectation DATE NOT NULL,
    date_fin_affectation DATE,
    flag_affectation_active BOOLEAN,
    code_poste VARCHAR(20),
    libelle_poste VARCHAR(200)
);

INSERT INTO fait.fait_affectation (
    nudoss, date_debut_affectation, date_fin_affectation,
    flag_affectation_active, code_poste, libelle_poste
)
SELECT 
    e.id AS nudoss,
    e.hire_date AS date_debut_affectation,
    e.termination_date AS date_fin_affectation,
    (e.employment_status = 'active') AS flag_affectation_active,
    'P' || LPAD(d.id::TEXT, 4, '0') AS code_poste,
    COALESCE(e.job_title, d.name || ' - ' || 'Employé') AS libelle_poste
FROM dblink(
    'host=localhost port=5432 dbname=hr_analytics_db user=hr_user password=hr_password123',
    'SELECT id, hire_date, termination_date, employment_status, job_title, department_id FROM employees WHERE hire_date IS NOT NULL'
) AS e(
    id INTEGER,
    hire_date DATE,
    termination_date DATE,
    employment_status VARCHAR(20),
    job_title VARCHAR(200),
    department_id INTEGER
)
LEFT JOIN dblink(
    'host=localhost port=5432 dbname=hr_analytics_db user=hr_user password=hr_password123',
    'SELECT id, name FROM departments'
) AS d(id INTEGER, name VARCHAR(100)) ON e.department_id = d.id;

\echo '✅ fait_affectation: ' :'ROW_COUNT' ' lignes insérées'

-- ==============================================================================
-- FAIT ABSENCE (Congés)
-- ==============================================================================

\echo 'Création de fait.fait_absence...'

CREATE TABLE fait.fait_absence (
    id_absence SERIAL PRIMARY KEY,
    nudoss INTEGER REFERENCES dim.dim_employe(nudoss),
    date_debut_absence DATE NOT NULL,
    date_fin_absence DATE NOT NULL,
    duree_absence_jours INTEGER,
    flag_absence_en_cours BOOLEAN,
    code_motif_absence VARCHAR(20),
    libelle_motif_absence VARCHAR(100),
    annee_absence INTEGER,
    mois_absence INTEGER
);

INSERT INTO fait.fait_absence (
    nudoss, date_debut_absence, date_fin_absence, duree_absence_jours,
    flag_absence_en_cours, code_motif_absence, libelle_motif_absence,
    annee_absence, mois_absence
)
SELECT 
    employee_id AS nudoss,
    start_date AS date_debut_absence,
    end_date AS date_fin_absence,
    (end_date - start_date + 1) AS duree_absence_jours,
    (status = 'approved' AND end_date >= CURRENT_DATE) AS flag_absence_en_cours,
    CASE 
        WHEN leave_type = 'annual' THEN 'ANN'
        WHEN leave_type = 'sick' THEN 'MAL'
        WHEN leave_type = 'parental' THEN 'PAR'
        WHEN leave_type = 'unpaid' THEN 'SNP'
        ELSE 'AUT'
    END AS code_motif_absence,
    CASE 
        WHEN leave_type = 'annual' THEN 'Congé Annuel'
        WHEN leave_type = 'sick' THEN 'Congé Maladie'
        WHEN leave_type = 'parental' THEN 'Congé Parental'
        WHEN leave_type = 'unpaid' THEN 'Congé Sans Solde'
        ELSE 'Autre'
    END AS libelle_motif_absence,
    EXTRACT(YEAR FROM start_date)::INTEGER AS annee_absence,
    EXTRACT(MONTH FROM start_date)::INTEGER AS mois_absence
FROM dblink(
    'host=localhost port=5432 dbname=hr_analytics_db user=hr_user password=hr_password123',
    'SELECT employee_id, start_date, end_date, leave_type, status FROM leave_requests WHERE start_date IS NOT NULL AND end_date IS NOT NULL'
) AS lr(
    employee_id INTEGER,
    start_date DATE,
    end_date DATE,
    leave_type VARCHAR(50),
    status VARCHAR(20)
);

\echo '✅ fait_absence: ' :'ROW_COUNT' ' lignes insérées'

-- ==============================================================================
-- INDEX POUR PERFORMANCES
-- ==============================================================================

\echo 'Création des index...'

-- Index sur les clés étrangères
CREATE INDEX idx_fait_contrat_nudoss ON fait.fait_contrat(nudoss);
CREATE INDEX idx_fait_contrat_date ON fait.fait_contrat(date_debut_contrat);
CREATE INDEX idx_fait_contrat_actif ON fait.fait_contrat(flag_contrat_actif);

CREATE INDEX idx_fait_affectation_nudoss ON fait.fait_affectation(nudoss);
CREATE INDEX idx_fait_affectation_date ON fait.fait_affectation(date_debut_affectation);
CREATE INDEX idx_fait_affectation_active ON fait.fait_affectation(flag_affectation_active);

CREATE INDEX idx_fait_absence_nudoss ON fait.fait_absence(nudoss);
CREATE INDEX idx_fait_absence_date_debut ON fait.fait_absence(date_debut_absence);
CREATE INDEX idx_fait_absence_date_fin ON fait.fait_absence(date_fin_absence);
CREATE INDEX idx_fait_absence_annee ON fait.fait_absence(annee_absence);

-- Index sur dim_calendrier
CREATE INDEX idx_calendrier_annee ON dim.dim_calendrier(annee);
CREATE INDEX idx_calendrier_mois ON dim.dim_calendrier(mois);
CREATE INDEX idx_calendrier_trimestre ON dim.dim_calendrier(trimestre);

\echo '✅ Index créés'

-- ==============================================================================
-- STATISTIQUES DE CHARGEMENT
-- ==============================================================================

\echo ''
\echo '========================================='
\echo '  STATISTIQUES DE CHARGEMENT'
\echo '========================================='

SELECT 
    'dim.dim_employe' AS table_name,
    COUNT(*) AS nb_lignes
FROM dim.dim_employe
UNION ALL
SELECT 
    'dim.dim_calendrier',
    COUNT(*)
FROM dim.dim_calendrier
UNION ALL
SELECT 
    'fait.fait_contrat',
    COUNT(*)
FROM fait.fait_contrat
UNION ALL
SELECT 
    'fait.fait_affectation',
    COUNT(*)
FROM fait.fait_affectation
UNION ALL
SELECT 
    'fait.fait_absence',
    COUNT(*)
FROM fait.fait_absence
ORDER BY table_name;

\echo ''
\echo '========================================='
\echo '  ✅ CRÉATION DU DWH TERMINÉE'
\echo '========================================='
\echo ''
\echo 'Prochaine étape: Exécutez votre script Qlik Sense pour charger les données'
