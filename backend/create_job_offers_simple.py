"""
Script simple pour créer la table job_offers
"""
import psycopg2
from psycopg2.extras import Json
import json

# Configuration de connexion (à adapter selon votre environnement)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "hr_analytics",
    "user": "postgres",
    "password": "postgres"
}

def create_table():
    """Créer la table job_offers"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Créer la table
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
    
    -- Index
    CREATE INDEX IF NOT EXISTS idx_job_offers_title ON job_offers(title);
    CREATE INDEX IF NOT EXISTS idx_job_offers_category ON job_offers(category);
    CREATE INDEX IF NOT EXISTS idx_job_offers_is_active ON job_offers(is_active);
    CREATE INDEX IF NOT EXISTS idx_job_offers_created_at ON job_offers(created_at);
    """
    
    try:
        cur.execute(create_table_sql)
        conn.commit()
        print("✅ Table job_offers créée avec succès!")
        
        # Insérer des données d'exemple
        insert_sample_data(cur, conn)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def insert_sample_data(cur, conn):
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
            "preferred_skills": ["Python", "Tableau", "Statistics"],
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
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
    )
    """
    
    try:
        for job in sample_jobs:
            cur.execute(insert_sql, (
                job["title"],
                job["description"],
                job["category"],
                Json(job["required_skills"]),
                Json(job["preferred_skills"]),
                Json(job["required_education"]),
                job["required_experience_years"],
                job["location"],
                job["salary_range"],
                job["contract_type"],
                job["department"]
            ))
        
        conn.commit()
        print(f"✅ {len(sample_jobs)} offres d'exemple insérées!")
        
    except Exception as e:
        print(f"⚠️  Erreur insertion (peut-être déjà présentes): {e}")
        conn.rollback()


if __name__ == "__main__":
    print("🚀 Création de la table job_offers...")
    create_table()
    print("✨ Migration terminée!")
