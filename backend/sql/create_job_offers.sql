-- ====================================================
-- Script SQL: Création de la table job_offers
-- ====================================================

-- Créer la table
CREATE TABLE IF NOT EXISTS job_offers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    
    -- Compétences en JSON
    required_skills JSONB DEFAULT '[]'::jsonb,
    preferred_skills JSONB DEFAULT '[]'::jsonb,
    
    -- Éducation 
    required_education JSONB DEFAULT '[]'::jsonb,
    
    -- Expérience
    required_experience_years FLOAT,
    
    -- Informations additionnelles
    location VARCHAR(255),
    salary_range VARCHAR(100),
    contract_type VARCHAR(50),
    department VARCHAR(100),
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_job_offers_title ON job_offers(title);
CREATE INDEX IF NOT EXISTS idx_job_offers_category ON job_offers(category);
CREATE INDEX IF NOT EXISTS idx_job_offers_is_active ON job_offers(is_active);
CREATE INDEX IF NOT EXISTS idx_job_offers_created_at ON job_offers(created_at);

-- Commentaires
COMMENT ON TABLE job_offers IS 'Table des offres d''emploi pour le matching CV';
COMMENT ON COLUMN job_offers.category IS 'Catégorie professionnelle (Data Science, Python Developer, etc.)';
COMMENT ON COLUMN job_offers.required_skills IS 'Liste des compétences requises en JSON';
COMMENT ON COLUMN job_offers.preferred_skills IS 'Liste des compétences préférées en JSON';

-- ====================================================
-- Données d'exemple
-- ====================================================

INSERT INTO job_offers (
    title, description, category, required_skills, preferred_skills, 
    required_education, required_experience_years, location, 
    salary_range, contract_type, department, is_active
) VALUES 
(
    'Data Scientist Senior',
    'Nous recherchons un Data Scientist expérimenté pour rejoindre notre équipe Analytics. Vous travaillerez sur des projets de machine learning et d''analyse prédictive.',
    'Data Science',
    '["Python", "Machine Learning", "SQL", "Pandas", "Scikit-learn"]'::jsonb,
    '["TensorFlow", "Deep Learning", "MLflow", "Docker"]'::jsonb,
    '["Master en Data Science", "Ingénieur"]'::jsonb,
    5.0,
    'Paris',
    '50000-70000 EUR',
    'CDI',
    'Data & Analytics',
    TRUE
),
(
    'Développeur Python Backend',
    'Développeur Python pour concevoir et maintenir des APIs REST avec FastAPI. Expérience avec PostgreSQL et Docker requise.',
    'Python Developer',
    '["Python", "FastAPI", "PostgreSQL", "REST API", "Git"]'::jsonb,
    '["Docker", "Kubernetes", "CI/CD", "Redis"]'::jsonb,
    '["Licence Informatique", "Ingénieur"]'::jsonb,
    3.0,
    'Lyon',
    '40000-55000 EUR',
    'CDI',
    'Engineering',
    TRUE
),
(
    'Développeur Full Stack React/Node',
    'Rejoignez notre équipe pour développer des applications web modernes avec React et Node.js.',
    'React',
    '["JavaScript", "React", "Node.js", "TypeScript", "REST API"]'::jsonb,
    '["Next.js", "GraphQL", "MongoDB", "AWS"]'::jsonb,
    '["Licence Informatique"]'::jsonb,
    2.0,
    'Remote',
    '35000-50000 EUR',
    'CDI',
    'Product',
    TRUE
),
(
    'Ingénieur DevOps',
    'Automatisation et gestion de l''infrastructure cloud. Experience avec AWS, Kubernetes et Terraform.',
    'DevOps Engineer',
    '["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"]'::jsonb,
    '["Terraform", "Ansible", "Prometheus", "ELK"]'::jsonb,
    '["Ingénieur"]'::jsonb,
    4.0,
    'Paris',
    '45000-65000 EUR',
    'CDI',
    'Infrastructure',
    TRUE
),
(
    'Business Analyst Junior',
    'Analyste pour soutenir les décisions business avec des analyses de données et reporting.',
    'Business Analyst',
    '["SQL", "Excel", "Power BI", "Analysis"]'::jsonb,
    '["Python", "Tableau", "Statistics"]'::jsonb,
    '["Licence Commerce", "Gestion"]'::jsonb,
    1.0,
    'Marseille',
    '30000-40000 EUR',
    'CDD',
    'Business Intelligence',
    TRUE
);

-- Vérification
SELECT COUNT(*) as total_offres FROM job_offers;
SELECT title, category, location FROM job_offers;
