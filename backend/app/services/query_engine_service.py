"""
Moteur NL2SQL — T5 fine-tuné + RAG + Fallback robuste
Version finale pour soutenance
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, date
import os
import re
import json
import time
import numpy as np
from pathlib import Path
from unidecode import unidecode

try:
    import torch
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    HAS_T5 = True
except ImportError:
    HAS_T5 = False

try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False

T5_MODEL_PATH        = "models/nl2sql_t5"
RAG_THRESHOLD        = 0.85
LEARNED_QUERIES_PATH = Path("models/learned_queries.json")

RAG_EXAMPLES = [
    {"question": "Combien d'employés actifs",
     "sql": "SELECT COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e WHERE e.flag_employe_actif = 1;"},
    {"question": "Combien d'employés inactifs",
     "sql": "SELECT COUNT(DISTINCT nudoss) as total_inactifs FROM dim.dim_employe WHERE flag_employe_actif = 0;"},
    {"question": "Employés inactifs liste",
     "sql": "SELECT DISTINCT e.nom, e.prenom FROM dim.dim_employe e WHERE e.flag_employe_actif = 0 AND e.nom IS NOT NULL AND e.nom != '--' ORDER BY e.nom LIMIT 100;"},
    {"question": "Salaire moyen des employés",
     "sql": "SELECT ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL;"},
    {"question": "Quel est le salaire moyen",
     "sql": "SELECT ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL;"},
    {"question": "5 postes les mieux rémunérés",
     "sql": "SELECT af.libelle_poste, ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen, COUNT(DISTINCT e.nudoss) as nb_employes FROM dim.dim_employe e LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY salaire_moyen DESC LIMIT 5;"},
    {"question": "10 postes les mieux rémunérés",
     "sql": "SELECT af.libelle_poste, ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen, COUNT(DISTINCT e.nudoss) as nb_employes FROM dim.dim_employe e LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY salaire_moyen DESC LIMIT 10;"},
    {"question": "Qui est absent aujourd'hui",
     "sql": "SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss WHERE e.nom IS NOT NULL AND e.nom != '--' AND DATE(a.date_debut_absence) <= CURRENT_DATE AND DATE(a.date_debut_absence) + INTERVAL '1 day' * a.duree_absence_jours >= CURRENT_DATE LIMIT 50;"},
    {"question": "Absents aujourd'hui",
     "sql": "SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss WHERE e.nom IS NOT NULL AND e.nom != '--' AND DATE(a.date_debut_absence) <= CURRENT_DATE AND DATE(a.date_debut_absence) + INTERVAL '1 day' * a.duree_absence_jours >= CURRENT_DATE LIMIT 50;"},
    {"question": "Taux de turnover",
     "sql": "SELECT SUM(CASE WHEN flag_employe_actif=1 THEN 1 ELSE 0 END) as actifs, SUM(CASE WHEN flag_employe_actif=0 THEN 1 ELSE 0 END) as inactifs, COUNT(*) as total FROM dim.dim_employe;"},
    {"question": "Rotation du personnel turnover",
     "sql": "SELECT SUM(CASE WHEN flag_employe_actif=1 THEN 1 ELSE 0 END) as actifs, SUM(CASE WHEN flag_employe_actif=0 THEN 1 ELSE 0 END) as inactifs, COUNT(*) as total FROM dim.dim_employe;"},
    {"question": "Répartition hommes femmes",
     "sql": "SELECT e.libelle_sexe, COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.libelle_sexe IS NOT NULL GROUP BY e.libelle_sexe ORDER BY total DESC;"},
    {"question": "Combien d'hommes et de femmes",
     "sql": "SELECT e.libelle_sexe, COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.libelle_sexe IS NOT NULL GROUP BY e.libelle_sexe ORDER BY total DESC;"},
    {"question": "Employés par département",
     "sql": "SELECT af.libelle_poste, COUNT(DISTINCT e.nudoss) as nombre FROM dim.dim_employe e JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY nombre DESC;"},
    {"question": "Nombre d'employés par poste",
     "sql": "SELECT af.libelle_poste, COUNT(DISTINCT e.nudoss) as nombre FROM dim.dim_employe e JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY nombre DESC;"},
    {"question": "Top 10 des employés les plus anciens",
     "sql": "SELECT e.nom, e.prenom, MIN(c.date_debut_contrat) as premiere_embauche, EXTRACT(YEAR FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat)))::integer as anciennete FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL AND e.nom IS NOT NULL AND e.nom != '--' GROUP BY e.nom, e.prenom, e.nudoss ORDER BY anciennete DESC LIMIT 10;"},
    {"question": "Taux absentéisme par département",
     "sql": "SELECT af.libelle_poste, COUNT(DISTINCT a.nudoss) as nb_absents, COUNT(DISTINCT e.nudoss) as nb_employes, ROUND(CAST(COUNT(DISTINCT a.nudoss)*100.0/NULLIF(COUNT(DISTINCT e.nudoss),0) AS NUMERIC), 2) as taux FROM dim.dim_employe e LEFT JOIN fait.fait_affectation af ON e.nudoss=af.nudoss AND af.flag_affectation_active=1 LEFT JOIN fait.fait_absence a ON e.nudoss=a.nudoss WHERE e.flag_employe_actif=1 AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY taux DESC LIMIT 20;"},
    {"question": "taux absenteisme departement",
     "sql": "SELECT af.libelle_poste, COUNT(DISTINCT a.nudoss) as nb_absents, COUNT(DISTINCT e.nudoss) as nb_employes, ROUND(CAST(COUNT(DISTINCT a.nudoss)*100.0/NULLIF(COUNT(DISTINCT e.nudoss),0) AS NUMERIC), 2) as taux FROM dim.dim_employe e LEFT JOIN fait.fait_affectation af ON e.nudoss=af.nudoss AND af.flag_affectation_active=1 LEFT JOIN fait.fait_absence a ON e.nudoss=a.nudoss WHERE e.flag_employe_actif=1 AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY taux DESC LIMIT 20;"},
    {"question": "absentéisme département service",
     "sql": "SELECT af.libelle_poste, COUNT(DISTINCT a.nudoss) as nb_absents, COUNT(DISTINCT e.nudoss) as nb_employes, ROUND(CAST(COUNT(DISTINCT a.nudoss)*100.0/NULLIF(COUNT(DISTINCT e.nudoss),0) AS NUMERIC), 2) as taux FROM dim.dim_employe e LEFT JOIN fait.fait_affectation af ON e.nudoss=af.nudoss AND af.flag_affectation_active=1 LEFT JOIN fait.fait_absence a ON e.nudoss=a.nudoss WHERE e.flag_employe_actif=1 AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY taux DESC LIMIT 20;"},
    {"question": "Évolution des embauches par année",
     "sql": "SELECT EXTRACT(YEAR FROM c.date_debut_contrat)::integer as annee, COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE c.date_debut_contrat IS NOT NULL GROUP BY annee ORDER BY annee;"},
    {"question": "Masse salariale totale",
     "sql": "SELECT ROUND(CAST(SUM(c.salaire_mensuel) AS NUMERIC), 2) as masse_salariale FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL;"},
    {"question": "Compare salaires hommes femmes",
     "sql": "SELECT e.libelle_sexe, ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen, COUNT(DISTINCT e.nudoss) as nb_employes FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND e.libelle_sexe IS NOT NULL GROUP BY e.libelle_sexe;"},
    {"question": "Répartition types contrats CDI CDD",
     "sql": "SELECT c.libelle_type_contrat, COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND c.libelle_type_contrat IS NOT NULL GROUP BY c.libelle_type_contrat ORDER BY total DESC;"},
    {"question": "Age moyen des employés",
     "sql": "SELECT ROUND(CAST(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance))) AS NUMERIC), 1) as age_moyen FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.date_naissance IS NOT NULL;"},
    {"question": "Absences par motif",
     "sql": "SELECT a.libelle_motif_absence, COUNT(*) as nombre, SUM(a.duree_absence_jours) as total_jours FROM fait.fait_absence a WHERE a.libelle_motif_absence IS NOT NULL GROUP BY a.libelle_motif_absence ORDER BY nombre DESC;"},
    {"question": "Employés plus de 10 ans ancienneté",
     "sql": "SELECT e.nom, e.prenom, MIN(c.date_debut_contrat) as premiere_embauche, EXTRACT(YEAR FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat)))::integer as anciennete FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL AND e.nom IS NOT NULL GROUP BY e.nom, e.prenom, e.nudoss HAVING EXTRACT(YEAR FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat))) >= 10 ORDER BY anciennete DESC;"},
    {"question": "Embauches en 2023",
     "sql": "SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat, c.libelle_type_contrat FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE EXTRACT(YEAR FROM c.date_debut_contrat) = 2023 AND e.nom IS NOT NULL AND e.nom != '--' AND c.libelle_type_contrat IS NOT NULL ORDER BY c.date_debut_contrat DESC LIMIT 100;"},
    {"question": "Embauches en 2022",
     "sql": "SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat, c.libelle_type_contrat FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE EXTRACT(YEAR FROM c.date_debut_contrat) = 2022 AND e.nom IS NOT NULL AND e.nom != '--' AND c.libelle_type_contrat IS NOT NULL ORDER BY c.date_debut_contrat DESC LIMIT 100;"},
    {"question": "Employés recrutés entre 2020 et 2023",
     "sql": "SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat, c.libelle_type_contrat FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE EXTRACT(YEAR FROM c.date_debut_contrat) BETWEEN 2020 AND 2023 AND e.nom IS NOT NULL AND c.libelle_type_contrat IS NOT NULL ORDER BY c.date_debut_contrat DESC LIMIT 100;"},
    {"question": "Masse salariale par département",
     "sql": "SELECT af.libelle_poste, ROUND(CAST(SUM(c.salaire_mensuel) AS NUMERIC), 2) as masse_salariale, COUNT(DISTINCT e.nudoss) as nb_employes FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY masse_salariale DESC;"},
    {"question": "Durée moyenne des absences",
     "sql": "SELECT ROUND(CAST(AVG(a.duree_absence_jours) AS NUMERIC), 1) as duree_moyenne FROM fait.fait_absence a WHERE a.duree_absence_jours IS NOT NULL;"},
    {"question": "Top 5 employés les plus absents",
     "sql": "SELECT e.nom, e.prenom, COUNT(*) as nb_absences FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss WHERE e.nom IS NOT NULL AND e.nom != '--' GROUP BY e.nom, e.prenom, e.nudoss ORDER BY nb_absences DESC LIMIT 5;"},
    {"question": "Salaire moyen par poste",
     "sql": "SELECT af.libelle_poste, ROUND(CAST(AVG(c.salaire_mensuel) AS NUMERIC), 2) as salaire_moyen, COUNT(DISTINCT e.nudoss) as nb_employes FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY salaire_moyen DESC;"},
    {"question": "Ancienneté moyenne des employés",
     "sql": "SELECT ROUND(CAST(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_debut_contrat))) AS NUMERIC), 1) as anciennete_moyenne FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL;"},
    {"question": "Pyramide des âges",
     "sql": "SELECT e.tranche_age, COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.tranche_age IS NOT NULL GROUP BY e.tranche_age ORDER BY e.tranche_age;"},
    {"question": "Combien employés en CDI",
     "sql": "SELECT COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDI%';"},
    {"question": "Combien employés en CDD",
     "sql": "SELECT COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDD%';"},
    {"question": "Absences en 2024",
     "sql": "SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence, a.duree_absence_jours FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss WHERE a.annee_absence = 2024 AND e.nom IS NOT NULL AND e.nom != '--' ORDER BY a.date_debut_absence DESC LIMIT 100;"},
    {"question": "Absences par année",
     "sql": "SELECT a.annee_absence, COUNT(*) as nombre, SUM(a.duree_absence_jours) as total_jours FROM fait.fait_absence a WHERE a.annee_absence IS NOT NULL GROUP BY a.annee_absence ORDER BY a.annee_absence;"},
    {"question": "Qui gagne le plus",
     "sql": "SELECT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND e.nom IS NOT NULL ORDER BY c.salaire_mensuel DESC LIMIT 1;"},
    {"question": "Qui gagne le moins",
     "sql": "SELECT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND e.nom IS NOT NULL ORDER BY c.salaire_mensuel ASC LIMIT 1;"},
    {"question": "Ancienneté par département",
     "sql": "SELECT af.libelle_poste, ROUND(CAST(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_debut_contrat))) AS NUMERIC), 1) as anciennete_moyenne FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL AND af.libelle_poste IS NOT NULL GROUP BY af.libelle_poste ORDER BY anciennete_moyenne DESC;"},
    {"question": "Absences ce mois",
     "sql": "SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss WHERE a.mois_absence = EXTRACT(MONTH FROM CURRENT_DATE) AND a.annee_absence = EXTRACT(YEAR FROM CURRENT_DATE) AND e.nom IS NOT NULL AND e.nom != '--' ORDER BY a.date_debut_absence LIMIT 100;"},
    {"question": "Combien d'employés ont quitté",
     "sql": "SELECT COUNT(DISTINCT nudoss) as total_inactifs FROM dim.dim_employe WHERE flag_employe_actif = 0;"},
    {"question": "Employés de moins de 30 ans",
     "sql": "SELECT DISTINCT e.nom, e.prenom, EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance))::integer as age FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.date_naissance IS NOT NULL AND e.nom IS NOT NULL AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance)) < 30 ORDER BY age ASC LIMIT 100;"},
    {"question": "Employés de plus de 50 ans",
     "sql": "SELECT DISTINCT e.nom, e.prenom, EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance))::integer as age FROM dim.dim_employe e WHERE e.flag_employe_actif = 1 AND e.date_naissance IS NOT NULL AND e.nom IS NOT NULL AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance)) > 50 ORDER BY age DESC LIMIT 100;"},
    {"question": "Masse salariale totale entreprise",
     "sql": "SELECT ROUND(CAST(SUM(c.salaire_mensuel) AS NUMERIC), 2) as masse_salariale FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL;"},
    {"question": "Salaire minimum employés",
     "sql": "SELECT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND e.nom IS NOT NULL ORDER BY c.salaire_mensuel ASC LIMIT 10;"},
    {"question": "Salaire maximum employés",
     "sql": "SELECT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND e.nom IS NOT NULL ORDER BY c.salaire_mensuel DESC LIMIT 10;"},
    {"question": "Effectif total entreprise",
     "sql": "SELECT COUNT(DISTINCT nudoss) as total FROM dim.dim_employe WHERE flag_employe_actif = 1;"},
    {"question": "Liste tous les employés actifs",
     "sql": "SELECT DISTINCT e.nom, e.prenom, e.libelle_sexe, af.libelle_poste FROM dim.dim_employe e LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1 WHERE e.flag_employe_actif = 1 AND e.nom IS NOT NULL ORDER BY e.nom LIMIT 100;"},
]


class QueryEngineService:

    def __init__(self, db: Session):
        self.db = db
        self.query_history = []
        self.metrics = {
            "t5_used": 0, "rag_reused": 0, "fallback_used": 0,
            "total_queries": 0, "successful_queries": 0, "failed_queries": 0,
            "total_response_time": 0.0, "avg_response_time": 0.0,
        }
        print("\n" + "="*60)
        print("🚀 MOTEUR NL2SQL — T5 + RAG + Fallback robuste")
        print("="*60)
        self._load_t5_model()
        self._load_rag()
        self._load_learned_queries()
        self._setup_database()
        print("✅ MOTEUR PRÊT\n")

    def _load_t5_model(self):
        if not HAS_T5 or not Path(T5_MODEL_PATH).exists():
            print(f"⚠️  T5 non disponible — RAG + Fallback actifs")
            self.t5_model = None
            self.t5_tokenizer = None
            return
        print("🔄 Chargement T5...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.t5_tokenizer = T5Tokenizer.from_pretrained(T5_MODEL_PATH)
        self.t5_model = T5ForConditionalGeneration.from_pretrained(T5_MODEL_PATH)
        self.t5_model.to(self.device)
        self.t5_model.eval()
        print(f"✅ T5 chargé sur {self.device}")

    def _load_rag(self):
        if not HAS_SEMANTIC:
            self.semantic_model = None
            self.rag_embeddings = None
            return
        print("🔄 Chargement RAG...")
        self.semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        questions = [ex["question"] for ex in RAG_EXAMPLES]
        self.rag_embeddings = self.semantic_model.encode(questions, convert_to_tensor=True)
        print(f"✅ RAG prêt — {len(RAG_EXAMPLES)} exemples")

    def _load_learned_queries(self):
        try:
            if LEARNED_QUERIES_PATH.exists():
                with open(LEARNED_QUERIES_PATH, 'r', encoding='utf-8') as f:
                    self.learned_queries = json.load(f)
                if self.learned_queries and HAS_SEMANTIC and self.semantic_model:
                    questions = [q["question"] for q in self.learned_queries]
                    self.learned_embeddings = self.semantic_model.encode(questions, convert_to_tensor=True)
                else:
                    self.learned_embeddings = None
                print(f"✅ {len(self.learned_queries)} requêtes apprises")
            else:
                self.learned_queries = []
                self.learned_embeddings = None
        except:
            self.learned_queries = []
            self.learned_embeddings = None

    def _setup_database(self):
        os.environ.setdefault('PGCLIENTENCODING', 'UTF8')
        dwh_url = (
            f"postgresql://{os.getenv('DWH_USER','hr_user')}"
            f":{os.getenv('DWH_PASSWORD','hr_password123')}"
            f"@{os.getenv('DWH_HOST','localhost')}"
            f":{os.getenv('DWH_PORT','5432')}"
            f"/{os.getenv('DWH_DB','hr_datawarehouse')}"
        )
        self.dwh_engine = create_engine(
            dwh_url, pool_size=5, max_overflow=10, pool_pre_ping=True,
            connect_args={"client_encoding": "utf8"}
        )

    def _rag_search(self, question: str) -> Tuple[Optional[str], float, str]:
        if not HAS_SEMANTIC or self.semantic_model is None:
            return None, 0.0, ""
        q_emb = self.semantic_model.encode(question, convert_to_tensor=True)
        base_sims = util.cos_sim(q_emb, self.rag_embeddings)[0]
        best_idx = int(base_sims.argmax())
        best_sim = float(base_sims[best_idx])
        best_sql = RAG_EXAMPLES[best_idx]["sql"]
        best_q   = RAG_EXAMPLES[best_idx]["question"]
        if self.learned_embeddings is not None and len(self.learned_queries) > 0:
            learned_sims = util.cos_sim(q_emb, self.learned_embeddings)[0]
            learned_idx  = int(learned_sims.argmax())
            learned_sim  = float(learned_sims[learned_idx])
            if learned_sim > best_sim:
                best_sim = learned_sim
                best_sql = self.learned_queries[learned_idx]["sql"]
                best_q   = self.learned_queries[learned_idx]["question"]
        return best_sql, best_sim, best_q

    def _t5_generate(self, question: str) -> Optional[str]:
        if not HAS_T5 or self.t5_model is None:
            return None
        input_text = f"translate to SQL: {question}"
        inputs = self.t5_tokenizer(
            input_text, return_tensors="pt", max_length=128, truncation=True
        ).to(self.device)
        with torch.no_grad():
            outputs = self.t5_model.generate(
                **inputs, max_length=256, num_beams=4,
                early_stopping=True, no_repeat_ngram_size=2
            )
        sql = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        if not sql.endswith(';'):
            sql += ';'
        sql = sql.replace('salaire_brut', 'salaire_mensuel')
        return sql

    def _is_valid_sql(self, sql: str) -> bool:
        if not sql:
            return False
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith('select'):
            return False
        if 'from' not in sql_lower:
            return False
        broken_patterns = [
            r'from\s+\w+[\.\w]*\s*=',
            r'from\s+\w+[\.\w]*\s+order\s+by\s+\d+',
            r'from\s+\w+[\.\w]*\s+desc\b',
            r'from\s+\w+[\.\w]*\s+like\b',
            r'select\s+\S+\s+from\s*;',
            r'from\s+dim\.\w+_actif',
        ]
        for pattern in broken_patterns:
            if re.search(pattern, sql_lower):
                return False
        if sql.count('(') != sql.count(')'):
            return False
        return True

    def _get_fallback_sql(self, question: str) -> Optional[str]:
        q = unidecode(question.lower().strip())

        is_absence  = any(w in q for w in ["absence", "absent", "absenteisme", "absentéisme"])
        is_salaire  = any(w in q for w in ["salaire", "salary", "remuneration", "paie", "masse salariale"])
        is_embauche = any(w in q for w in ["embauche", "recrut", "nouvel"])

        # ── Absentéisme ──
        if any(w in q for w in ["absenteisme", "absentéisme", "taux absence"]):
            if any(w in q for w in ["departement", "département", "poste", "service"]):
                return """SELECT af.libelle_poste,
    COUNT(DISTINCT a.nudoss) as nb_absents,
    COUNT(DISTINCT e.nudoss) as nb_employes,
    ROUND(CAST(COUNT(DISTINCT a.nudoss)*100.0/NULLIF(COUNT(DISTINCT e.nudoss),0) AS NUMERIC), 2) as taux
FROM dim.dim_employe e
LEFT JOIN fait.fait_affectation af ON e.nudoss=af.nudoss AND af.flag_affectation_active=1
LEFT JOIN fait.fait_absence a ON e.nudoss=a.nudoss
WHERE e.flag_employe_actif=1 AND af.libelle_poste IS NOT NULL
GROUP BY af.libelle_poste ORDER BY taux DESC LIMIT 20;"""
            return """SELECT COUNT(DISTINCT a.nudoss) as nb_absents,
    COUNT(DISTINCT e.nudoss) as nb_employes,
    ROUND(CAST(COUNT(DISTINCT a.nudoss)*100.0/NULLIF(COUNT(DISTINCT e.nudoss),0) AS NUMERIC), 2) as taux_global
FROM dim.dim_employe e
LEFT JOIN fait.fait_absence a ON e.nudoss=a.nudoss
WHERE e.flag_employe_actif=1;"""

        # ── Employés inactifs ──
        if any(w in q for w in ["inactif", "inactifs", "quitte", "parti"]):
            if any(w in q for w in ["combien", "nombre", "total"]):
                return """SELECT COUNT(DISTINCT nudoss) as total_inactifs
FROM dim.dim_employe WHERE flag_employe_actif = 0;"""
            return """SELECT DISTINCT e.nom, e.prenom
FROM dim.dim_employe e
WHERE e.flag_employe_actif = 0
AND e.nom IS NOT NULL AND e.nom != '--'
ORDER BY e.nom LIMIT 100;"""

        # ── Années ──
        years = re.findall(r'\b(20\d{2}|19\d{2})\b', q)

        if len(years) == 2:
            y1, y2 = sorted(years)
            if is_absence:
                return f"""SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence
FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss
WHERE a.annee_absence BETWEEN {y1} AND {y2}
AND e.nom IS NOT NULL AND e.nom != '--'
ORDER BY a.date_debut_absence DESC LIMIT 100;"""
            return f"""SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat, c.libelle_type_contrat
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE EXTRACT(YEAR FROM c.date_debut_contrat) BETWEEN {y1} AND {y2}
AND e.nom IS NOT NULL AND e.nom != '--' AND c.libelle_type_contrat IS NOT NULL
ORDER BY c.date_debut_contrat DESC LIMIT 100;"""

        if len(years) == 1:
            y = years[0]
            if is_absence:
                if any(w in q for w in ["combien", "nombre", "total"]):
                    return f"SELECT COUNT(*) as total_absences FROM fait.fait_absence a WHERE a.annee_absence = {y};"
                return f"""SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence, a.duree_absence_jours
FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss
WHERE a.annee_absence = {y} AND e.nom IS NOT NULL AND e.nom != '--'
ORDER BY a.date_debut_absence DESC LIMIT 100;"""
            if any(w in q for w in ["combien", "nombre", "total"]):
                return f"""SELECT COUNT(DISTINCT e.nudoss) as total
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE EXTRACT(YEAR FROM c.date_debut_contrat) = {y};"""
            return f"""SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat, c.libelle_type_contrat
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE EXTRACT(YEAR FROM c.date_debut_contrat) = {y}
AND e.nom IS NOT NULL AND e.nom != '--' AND c.libelle_type_contrat IS NOT NULL
ORDER BY c.date_debut_contrat DESC LIMIT 100;"""

        # ── Ancienneté avec seuil ──
        seuil = re.findall(r'\b(\d+)\s*ans?\b', q)
        if seuil and any(w in q for w in ["anciennete", "ancienneté", "plus de"]):
            n = seuil[0]
            return f"""SELECT e.nom, e.prenom,
    MIN(c.date_debut_contrat) as premiere_embauche,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat)))::integer as anciennete
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL
AND e.nom IS NOT NULL AND e.nom != '--'
GROUP BY e.nom, e.prenom, e.nudoss
HAVING EXTRACT(YEAR FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat))) >= {n}
ORDER BY anciennete DESC;"""

        # ── Salaire avec seuil ──
        montant = re.findall(r'\b(\d{3,5})\b', q)
        if montant and is_salaire:
            m = montant[0]
            if any(w in q for w in ["superieur", "supérieur", "plus de", "depasse"]):
                return f"""SELECT DISTINCT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1
WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel > {m} AND e.nom IS NOT NULL
ORDER BY c.salaire_mensuel DESC LIMIT 100;"""
            if any(w in q for w in ["inferieur", "inférieur", "moins de"]):
                return f"""SELECT DISTINCT e.nom, e.prenom, af.libelle_poste, c.salaire_mensuel
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1
WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel < {m} AND e.nom IS NOT NULL
ORDER BY c.salaire_mensuel ASC LIMIT 100;"""

        # ── Masse salariale ──
        if "masse salariale" in q:
            if any(w in q for w in ["departement", "département", "poste", "service"]):
                return """SELECT af.libelle_poste,
    ROUND(CAST(SUM(c.salaire_mensuel) AS NUMERIC), 2) as masse_salariale
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1
WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL AND af.libelle_poste IS NOT NULL
GROUP BY af.libelle_poste ORDER BY masse_salariale DESC;"""
            return """SELECT ROUND(CAST(SUM(c.salaire_mensuel) AS NUMERIC), 2) as masse_salariale
FROM fait.fait_contrat c JOIN dim.dim_employe e ON c.nudoss = e.nudoss
WHERE e.flag_employe_actif = 1 AND c.salaire_mensuel IS NOT NULL;"""

        # ── Durée absences ──
        if any(w in q for w in ["duree", "durée"]) and is_absence:
            return """SELECT ROUND(CAST(AVG(a.duree_absence_jours) AS NUMERIC), 1) as duree_moyenne_jours
FROM fait.fait_absence a WHERE a.duree_absence_jours IS NOT NULL;"""

        # ── Absences par année ──
        if is_absence and any(w in q for w in ["annee", "année", "annuel", "par an"]):
            return """SELECT a.annee_absence, COUNT(*) as nombre, SUM(a.duree_absence_jours) as total_jours
FROM fait.fait_absence a WHERE a.annee_absence IS NOT NULL
GROUP BY a.annee_absence ORDER BY a.annee_absence;"""

        # ── Absences ce mois ──
        if is_absence and any(w in q for w in ["mois", "ce mois", "mensuel"]):
            return """SELECT e.nom, e.prenom, a.libelle_motif_absence, a.date_debut_absence
FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss
WHERE a.mois_absence = EXTRACT(MONTH FROM CURRENT_DATE)
AND a.annee_absence = EXTRACT(YEAR FROM CURRENT_DATE)
AND e.nom IS NOT NULL AND e.nom != '--'
ORDER BY a.date_debut_absence LIMIT 100;"""

        # ── Top absents ──
        top_match = re.search(r'\b(\d+)\b', q)
        n_limit = top_match.group(1) if top_match else "10"
        if is_absence and any(w in q for w in ["plus absent", "top", "le plus"]):
            return f"""SELECT e.nom, e.prenom, COUNT(*) as nb_absences
FROM fait.fait_absence a JOIN dim.dim_employe e ON a.nudoss = e.nudoss
WHERE e.nom IS NOT NULL AND e.nom != '--'
GROUP BY e.nom, e.prenom, e.nudoss ORDER BY nb_absences DESC LIMIT {n_limit};"""

        # ── Pyramide âges ──
        if any(w in q for w in ["pyramide", "tranche age", "tranche d age"]):
            return """SELECT e.tranche_age, e.libelle_sexe, COUNT(DISTINCT e.nudoss) as total
FROM dim.dim_employe e WHERE e.flag_employe_actif = 1
AND e.tranche_age IS NOT NULL AND e.libelle_sexe IS NOT NULL
GROUP BY e.tranche_age, e.libelle_sexe ORDER BY e.tranche_age;"""

        # ── Ancienneté par département ──
        if any(w in q for w in ["anciennete", "ancienneté"]) and any(w in q for w in ["departement", "département", "poste"]):
            return """SELECT af.libelle_poste,
    ROUND(CAST(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_debut_contrat))) AS NUMERIC), 1) as anciennete_moyenne
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
JOIN fait.fait_affectation af ON e.nudoss = af.nudoss AND af.flag_affectation_active = 1
WHERE e.flag_employe_actif = 1 AND c.date_debut_contrat IS NOT NULL AND af.libelle_poste IS NOT NULL
GROUP BY af.libelle_poste ORDER BY anciennete_moyenne DESC;"""

        # ── Age < X ans ──
        age_match = re.search(r'\b(\d{2})\s*ans?\b', q)
        if age_match:
            age = age_match.group(1)
            if any(w in q for w in ["moins de", "moins", "inferieur"]):
                return f"""SELECT DISTINCT e.nom, e.prenom,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance))::integer as age
FROM dim.dim_employe e WHERE e.flag_employe_actif = 1
AND e.date_naissance IS NOT NULL AND e.nom IS NOT NULL
AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance)) < {age}
ORDER BY age ASC LIMIT 100;"""
            if any(w in q for w in ["plus de", "plus", "superieur"]):
                return f"""SELECT DISTINCT e.nom, e.prenom,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance))::integer as age
FROM dim.dim_employe e WHERE e.flag_employe_actif = 1
AND e.date_naissance IS NOT NULL AND e.nom IS NOT NULL
AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_naissance)) > {age}
ORDER BY age DESC LIMIT 100;"""

        # ── CDI / CDD ──
        if "cdi" in q:
            if any(w in q for w in ["combien", "nombre", "total"]):
                return """SELECT COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e
JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDI%';"""
            return """SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDI%'
AND e.nom IS NOT NULL ORDER BY e.nom LIMIT 100;"""

        if "cdd" in q:
            if any(w in q for w in ["combien", "nombre", "total"]):
                return """SELECT COUNT(DISTINCT e.nudoss) as total FROM dim.dim_employe e
JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDD%';"""
            return """SELECT DISTINCT e.nom, e.prenom, c.date_debut_contrat
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.flag_employe_actif = 1 AND UPPER(c.libelle_type_contrat) LIKE '%CDD%'
AND e.nom IS NOT NULL ORDER BY e.nom LIMIT 100;"""

        # ── Contrats expirant ──
        if any(w in q for w in ["expire", "expir", "termine", "fin contrat"]):
            return """SELECT DISTINCT e.nom, e.prenom, c.libelle_type_contrat, c.date_fin_contrat
FROM dim.dim_employe e JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE c.date_fin_contrat BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
AND e.nom IS NOT NULL ORDER BY c.date_fin_contrat;"""

        return None

    async def process_query(self, question: str, user_id: int) -> Dict[str, Any]:
        start_time = time.time()
        try:
            self.metrics["total_queries"] += 1
            print(f"\n{'─'*60}")
            print(f"🔍 QUESTION : {question}")

            sql_query   = None
            engine_used = "t5"
            rag_info    = None

            rag_sql, rag_sim, rag_q = self._rag_search(question)
            print(f"🔎 RAG similarité: {rag_sim:.3f} — '{rag_q[:50]}'")

            if rag_sim >= RAG_THRESHOLD and rag_sql:
                print(f"✨ RAG MATCH → SQL réutilisé")
                sql_query   = rag_sql
                engine_used = "rag"
                self.metrics["rag_reused"] += 1
                rag_info = {"matched_question": rag_q, "similarity": rag_sim}
            else:
                print(f"🤖 T5 génère le SQL...")
                t5_sql = self._t5_generate(question)
                print(f"📝 SQL T5: {(t5_sql or '')[:80]}...")

                if t5_sql and self._is_valid_sql(t5_sql):
                    print("✅ SQL T5 valide")
                    sql_query   = t5_sql
                    engine_used = "t5_finetuned"
                    self.metrics["t5_used"] += 1
                else:
                    print("⚠️  SQL T5 invalide → fallback")
                    fallback = self._get_fallback_sql(question)
                    if fallback:
                        print("✅ Fallback trouvé")
                        sql_query   = fallback
                        engine_used = "fallback"
                        self.metrics["fallback_used"] += 1
                    else:
                        print(f"📋 Meilleur RAG disponible (sim={rag_sim:.3f})")
                        sql_query   = rag_sql
                        engine_used = "rag_best_effort"

            if not sql_query:
                self.metrics["failed_queries"] += 1
                return {
                    "success": False,
                    "answer": "Je n'ai pas compris votre question. Essayez de reformuler.",
                    "query_type": "error",
                    "suggestions": self._get_suggestions()
                }

            if not self._is_safe_query(sql_query):
                self.metrics["failed_queries"] += 1
                return {"success": False, "answer": "Seules les requêtes SELECT sont autorisées.", "query_type": "error"}

            rows, columns = self._execute_on_dwh(sql_query)
            response_time = time.time() - start_time
            self._update_metrics(response_time)

            if not rows:
                return {
                    "success": True, "answer": "Aucun résultat trouvé.",
                    "query_type": "empty", "sql_query": sql_query,
                    "sql_explanation": self.explain_sql(sql_query),
                    "data": {"rows": [], "columns": columns, "count": 0},
                    "visualization": {"type": "empty"},
                    "nlp_engine": engine_used,
                    "response_time": round(response_time, 2),
                    "rag_info": rag_info
                }

            self.metrics["successful_queries"] += 1
            answer        = self._generate_answer(question, rows, columns)
            visualization = self._detect_visualization(rows, columns, question)

            result = {
                "success": True, "answer": answer,
                "query_type": "query_success", "sql_query": sql_query,
                "sql_explanation": self.explain_sql(sql_query),
                "data": {"rows": rows, "columns": columns, "count": len(rows)},
                "visualization": visualization,
                "nlp_engine": engine_used,
                "response_time": round(response_time, 2),
                "metrics": self.get_metrics(),
                "rag_info": rag_info
            }

            self._save_to_history(question, result, user_id)

            if engine_used == "t5_finetuned":
                self._save_learned_query(question, sql_query)

            return result

        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(response_time)
            self.metrics["failed_queries"] += 1
            msg = str(e)
            if "connection" in msg.lower():
                return {"success": False, "answer": "Base de données inaccessible.", "query_type": "error"}
            return {"success": False, "answer": f"Erreur: {msg}", "query_type": "error"}

    def _save_learned_query(self, question: str, sql: str):
        if not HAS_SEMANTIC or self.semantic_model is None:
            return
        try:
            q_emb = self.semantic_model.encode(question, convert_to_tensor=True)
            if self.learned_embeddings is not None:
                sims = util.cos_sim(q_emb, self.learned_embeddings)[0]
                if float(sims.max()) > 0.95:
                    return
            self.learned_queries.append({
                "question": question, "sql": sql,
                "learned_at": datetime.now().isoformat()
            })
            questions = [q["question"] for q in self.learned_queries]
            self.learned_embeddings = self.semantic_model.encode(questions, convert_to_tensor=True)
            LEARNED_QUERIES_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(LEARNED_QUERIES_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.learned_queries, f, ensure_ascii=False, indent=2)
            print(f"🎓 Appris: '{question[:50]}' (Total: {len(self.learned_queries)})")
        except Exception as e:
            print(f"⚠️  Auto-learning error: {e}")

    def _is_safe_query(self, sql: str) -> bool:
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith('select'):
            return False
        for kw in ['insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate']:
            if re.search(rf'\b{kw}\b', sql_lower):
                return False
        return True

    def _execute_on_dwh(self, sql: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        with self.dwh_engine.connect() as conn:
            result  = conn.execute(text(sql))
            columns = list(result.keys())
            rows    = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    v = row[i]
                    if hasattr(v, 'isoformat'):             v = v.isoformat()
                    elif isinstance(v, (bytes, bytearray)):  v = v.decode('utf-8')
                    row_dict[col] = v
                rows.append(row_dict)
            return rows, columns

    def explain_sql(self, sql: str) -> str:
        sql_lower = sql.lower().strip()
        parts = []
        if 'count(' in sql_lower:   parts.append("📊 Comptage")
        elif 'avg(' in sql_lower:   parts.append("📊 Moyenne")
        elif 'sum(' in sql_lower:   parts.append("📊 Somme")
        elif 'max(' in sql_lower:   parts.append("📊 Maximum")
        elif 'min(' in sql_lower:   parts.append("📊 Minimum")
        else:                        parts.append("📋 Liste de résultats")
        tables = []
        if 'dim_employe'      in sql_lower: tables.append("Employés")
        if 'fait_contrat'     in sql_lower: tables.append("Contrats")
        if 'fait_absence'     in sql_lower: tables.append("Absences")
        if 'fait_affectation' in sql_lower: tables.append("Affectations")
        if 'dim_calendrier'   in sql_lower: tables.append("Calendrier")
        if tables: parts.append(f"🗂️ Tables: {', '.join(tables)}")
        if 'group by'  in sql_lower: parts.append("📊 Groupement par catégorie")
        if 'having'    in sql_lower: parts.append("🔍 Filtre sur agrégat (HAVING)")
        if 'distinct'  in sql_lower: parts.append("🔁 Suppression des doublons")
        if 'order by'  in sql_lower:
            parts.append("📉 Tri décroissant" if 'desc' in sql_lower else "📈 Tri croissant")
        m = re.search(r'limit\s+(\d+)', sql_lower)
        if m: parts.append(f"⚡ Limite: {m.group(1)} résultats")
        return "\n".join(parts)

    def _generate_answer(self, question: str, rows: List[Dict], columns: List[str]) -> str:
        count = len(rows)
        if len(columns) == 1 and count == 1:
            v   = rows[0][columns[0]]
            col = columns[0].lower()
            if 'total' in col or 'count' in col or 'inactif' in col:
                return f"**{v}**"
            if 'salaire' in col or 'moyen' in col or 'masse' in col:
                try:    return f"**{float(v):,.2f} DT**"
                except: return f"**{v}**"
            if 'age' in col or 'anciennete' in col or 'duree' in col:
                try:    return f"**{float(v):.1f}**"
                except: return f"**{v}**"
            return f"**{v}**"
        if "actifs" in columns and "inactifs" in columns:
            actifs   = rows[0].get("actifs", 0)
            inactifs = rows[0].get("inactifs", 0)
            total    = actifs + inactifs
            taux     = (inactifs / total * 100) if total > 0 else 0
            return f"**{actifs}** actifs · **{inactifs}** inactifs · Turnover : **{taux:.1f}%**"
        if count == 0: return "Aucun résultat trouvé."
        if count == 1: return "Voici le résultat trouvé."
        return f"**{count} résultat(s)** trouvé(s)."

    def _detect_visualization(self, rows: List[Dict], columns: List[str], question: str) -> Dict[str, Any]:
        count = len(rows)
        if count == 0: return {"type": "empty"}
        if len(columns) == 1 and count == 1:
            return {"type": "metric", "value": rows[0][columns[0]], "label": columns[0]}
        if "actifs" in columns and "inactifs" in columns:
            return {"type": "pie_chart", "categories": ["Actifs", "Inactifs"],
                    "values": [rows[0].get("actifs", 0), rows[0].get("inactifs", 0)]}
        if len(columns) >= 2:
            c0 = columns[0].lower()
            if any(w in c0 for w in ["annee", "mois", "date", "year", "month"]):
                return {"type": "line_chart", "x": columns[0], "y": columns[-1], "data": rows}
        if len(columns) == 2 and count <= 20:
            return {"type": "bar_chart", "x": columns[0], "y": columns[1], "data": rows}
        return {"type": "table", "columns": columns, "data": rows}

    def _get_suggestions(self) -> List[str]:
        return [
            "Combien d'employés actifs ?",
            "Salaire moyen des employés",
            "Qui est absent aujourd'hui ?",
            "Taux de turnover",
            "5 postes les mieux rémunérés",
            "Compare les salaires entre hommes et femmes",
            "Employés avec plus de 10 ans d'ancienneté",
            "Absences en 2024",
        ]

    def _update_metrics(self, response_time: float):
        self.metrics["total_response_time"] += response_time
        if self.metrics["total_queries"] > 0:
            self.metrics["avg_response_time"] = round(
                self.metrics["total_response_time"] / self.metrics["total_queries"], 3
            )

    def _save_to_history(self, query: str, result: Dict[str, Any], user_id: int):
        self.query_history.append({
            "timestamp":     datetime.now().isoformat(),
            "user_id":       user_id,
            "query":         query,
            "success":       result.get("success", False),
            "nlp_engine":    result.get("nlp_engine", ""),
            "response_time": result.get("response_time", 0),
        })

    def get_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        return [h for h in self.query_history if h["user_id"] == user_id][-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        total = self.metrics["t5_used"] + self.metrics["rag_reused"] + self.metrics["fallback_used"]
        return {
            **self.metrics,
            "t5_pct":       round(self.metrics["t5_used"] / total * 100, 1) if total > 0 else 0,
            "rag_pct":      round(self.metrics["rag_reused"] / total * 100, 1) if total > 0 else 0,
            "fallback_pct": round(self.metrics["fallback_used"] / total * 100, 1) if total > 0 else 0,
            "success_rate": round(self.metrics["successful_queries"] / self.metrics["total_queries"] * 100, 1) if self.metrics["total_queries"] > 0 else 0,
        }

    def get_learned_queries_summary(self) -> Dict[str, Any]:
        return {
            "total_learned": len(self.learned_queries),
            "recent_queries": [
                {"question": q["question"][:80], "learned_at": q.get("learned_at", "")}
                for q in self.learned_queries[-10:]
            ]
        }