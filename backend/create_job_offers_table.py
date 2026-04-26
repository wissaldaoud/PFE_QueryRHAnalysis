"""
Script de migration pour créer la table job_offers (offres d'emploi)
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
import sys

def create_job_offers_table():
    """Créer la table job_offers"""
    
    # Connexion à la base de données
    engine = create_engine(settings.DATABASE_URL)
    
    create_table_sql = """
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
    COMMENT ON COLUMN job_offers.required_education IS 'Liste des diplômes/formations requis en JSON';
    COMMENT ON COLUMN job_offers.required_experience_years IS 'Années d''expérience requises';
    COMMENT ON COLUMN job_offers.salary_range IS 'Fourchette de salaire (ex: 40000-60000 EUR)';
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Table job_offers créée avec succès!")
            
            # Insérer des données d'exemple
            insert_sample_data(conn)
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la table: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


def insert_sample_data(conn):
    """Insérer des offres d'exemple"""
    
    sample_jobs = [
        {
            "title": "Data Scientist Senior",
            "description": "Nous recherchons un Data Scientist expérimenté pour rejoindre notre équipe Analytics. Vous travaillerez sur des projets de machine learning et d'analyse prédictive.",
            "category": "Data Science",
            "required_skills": ["Python", "Machine Learning", "SQL", "Pandas", "Scikit-learn"],
            "preferred_skills": ["TensorFlow", "Deep Learning", "MLflow", "Docker"],
            "required_education": ["Master en Data Science", "Ingénieur"],
            "required_experience_years": 5.0,
            "location": "Paris",
            "salary_range": "50000-70000 EUR",
            "contract_type": "CDI",
            "department": "Data & Analytics"
        },
        {
            "title": "Développeur Python Backend",
            "description": "Développeur Python pour concevoir et maintenir des APIs REST avec FastAPI. Expérience avec PostgreSQL et Docker requise.",
            "category": "Python Developer",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST API", "Git"],
            "preferred_skills": ["Docker", "Kubernetes", "CI/CD", "Redis"],
            "required_education": ["Licence Informatique", "Ingénieur"],
            "required_experience_years": 3.0,
            "location": "Lyon",
            "salary_range": "40000-55000 EUR",
            "contract_type": "CDI",
            "department": "Engineering"
        },
        {
            "title": "Développeur Full Stack React/Node",
            "description": "Rejoignez notre équipe pour développer des applications web modernes avec React et Node.js.",
            "category": "React",
            "required_skills": ["JavaScript", "React", "Node.js", "TypeScript", "REST API"],
            "preferred_skills": ["Next.js", "GraphQL", "MongoDB", "AWS"],
            "required_education": ["Licence Informatique"],
            "required_experience_years": 2.0,
            "location": "Remote",
            "salary_range": "35000-50000 EUR",
            "contract_type": "CDI",
            "department": "Product"
        },
        {
            "title": "Ingénieur DevOps",
            "description": "Automatisation et gestion de l'infrastructure cloud. Experience avec AWS, Kubernetes et Terraform.",
            "category": "DevOps Engineer",
            "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
            "preferred_skills": ["Terraform", "Ansible", "Prometheus", "ELK"],
            "required_education": ["Ingénieur"],
            "required_experience_years": 4.0,
            "location": "Paris",
            "salary_range": "45000-65000 EUR",
            "contract_type": "CDI",
            "department": "Infrastructure"
        },
        {
            "title": "Business Analyst Junior",
            "description": "Analyste pour soutenir les décisions business avec des analyses de données et reporting.",
            "category": "Business Analyst",
            "required_skills": ["SQL", "Excel", "Power BI", "Analysis"],
            "preferred_skills":["Python", "Tableau", "Statistics"],
            "required_education": ["Licence Commerce", "Gestion"],
            "required_experience_years": 1.0,
            "location": "Marseille",
            "salary_range": "30000-40000 EUR",
            "contract_type": "CDD",
            "department": "Business Intelligence"
        }
    ]
    
    insert_sql = """
    INSERT INTO job_offers (
        title, description, category, required_skills, preferred_skills,
        required_education, required_experience_years, location, 
        salary_range, contract_type, department, is_active
    ) VALUES (
        :title, :description, :category, :required_skills::jsonb, :preferred_skills::jsonb,
        :required_education::jsonb, :required_experience_years, :location,
        :salary_range, :contract_type, :department, TRUE
    )
    """
    
    import json
    
    try:
        for job in sample_jobs:
            # Convertir les listes en JSON
            job_data = job.copy()
            job_data['required_skills'] = json.dumps(job_data['required_skills'])
            job_data['preferred_skills'] = json.dumps(job_data['preferred_skills'])
            job_data['required_education'] = json.dumps(job_data['required_education'])
            
            conn.execute(text(insert_sql), job_data)
        
        conn.commit()
        print(f"✅ {len(sample_jobs)} offres d'exemple insérées!")
        
    except Exception as e:
        print(f"⚠️  Erreur insertion données exemple (peut-être déjà présentes): {e}")


if __name__ == "__main__":
    print("🚀 Création de la table job_offers...")
    create_job_offers_table()
    print("✨ Migration terminée!")
