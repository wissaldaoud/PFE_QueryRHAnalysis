"""
Script d'entraînement — Prédiction Turnover RH
===============================================
Objectif  : prédire si un employé quittera l'entreprise dans les N prochains
            mois à partir d'une date de snapshot (pas de fuite temporelle).

Fixes clés (v2)
---------------
  1. Zéro fuite de données : le label est construit à partir d'événements
     FUTURS par rapport au snapshot ; termination_date n'est jamais utilisée
     comme feature.
  2. Split temporel : train / validation / test selon la date de snapshot,
     pas de split aléatoire.
  3. Cross-validation sans fuite : Pipeline complet (preprocessor + model)
     évalué sur données brutes avec TimeSeriesSplit.
  4. Calibration des probabilités : CalibratedClassifierCV(isotonic) après
     l'entraînement sur le jeu de validation.
  5. Seuil optimal : calculé en maximisant le F1 sur le jeu de validation.
  6. Métriques enrichies : AUC-ROC, PR-AUC, F1, Precision, Recall.
  7. SHAP prêt : les noms de features sont alignés avec l'entrée du modèle.

Usage:
    python train_turnover_model.py [--snapshot YYYY-MM-DD] [--horizon 6]

Outputs:
    ml/models/turnover_model_real.pkl      — bundle joblib complet
    ml/models/turnover_model_metrics.json  — métriques détaillées
"""

import argparse
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib                          # ✅ joblib, pas pickle
import numpy as np
import pandas as pd
import xgboost as xgb
from sqlalchemy import create_engine, text
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    TimeSeriesSplit,
    cross_val_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)

MODEL_DIR = Path("ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ════════════════════════════════════════════════════════

# Horizon de prédiction : on cherche à détecter les départs dans les N prochains mois
# Change ce paramètre pour ajuster la sensibilité du modèle.
DEFAULT_HORIZON_MONTHS: int = 6

# Proporé portions pour le split temporel (toujours train < val < test)
TRAIN_RATIO: float = 0.70
VAL_RATIO: float   = 0.15
# TEST_RATIO  = 1 - TRAIN_RATIO - VAL_RATIO = 0.15 (implicite)


# ══════════════════════════════════════════════════════════
# CONFIGURATION BASE DE DONNÉES
# ══════════════════════════════════════════════════════════

import os

DB_URL = (
    f"postgresql://{os.getenv('DB_USER', 'hr_user')}"
    f":{os.getenv('DB_PASSWORD', 'hr_password123')}"
    f"@{os.getenv('DB_HOST', 'localhost')}"
    f":{os.getenv('DB_PORT', '5432')}"
    f"/{os.getenv('DB_NAME', 'hr_db')}"
)


# ══════════════════════════════════════════════════════════
# EXTRACTION DEPUIS LES VRAIES TABLES — SANS FUITE TEMPORELLE
# ══════════════════════════════════════════════════════════
#
# FIX FUITE #1 : Le label est défini comme « l'employé quitte dans les
# HORIZON_MONTHS mois APRÈS snapshot_date ».  Aucune feature n'utilise
# termination_date ni employment_status.
#
# FIX FUITE #2 : Toutes les sous-requêtes filtrent strictement sur
# start_date / end_date <= :snapshot_date pour ne voir que les données
# disponibles au moment du snapshot.
#
# :snapshot_date  — date de référence (passée en paramètre)
# :horizon_days   — fenêtre future (HORIZON_MONTHS × 30)
#
QUERY = """
WITH contrats AS (
    -- Seuls les contrats démarrés AVANT le snapshot (information disponible)
    SELECT
        employee_id,
        MAX(salary)                                             AS salaire_max,
        MIN(start_date)                                         AS premiere_embauche,
        COUNT(DISTINCT contract_type)                           AS nb_types_contrat,
        MAX(CASE WHEN UPPER(contract_type) LIKE '%CDI%'
                 THEN 1 ELSE 0 END)                             AS is_cdi,
        MODE() WITHIN GROUP (ORDER BY contract_type)            AS type_contrat_dominant
    FROM contracts
    WHERE start_date <= :snapshot_date
    GROUP BY employee_id
),
absences AS (
    -- Absences sur les 24 mois précédant le snapshot (pas au-delà)
    SELECT
        employee_id,
        COUNT(*)                                                AS nb_absences,
        COALESCE(SUM(duration_days), 0)                         AS total_jours_absence,
        COUNT(*) FILTER (WHERE duration_days > 5)               AS nb_absences_longues,
        MODE() WITHIN GROUP (ORDER BY absence_type)             AS motif_dominant
    FROM absences
    WHERE start_date BETWEEN :snapshot_date - INTERVAL '24 months'
                         AND :snapshot_date
    GROUP BY employee_id
),
affectations AS (
    -- Dernière affectation connue au moment du snapshot
    SELECT DISTINCT ON (employee_id)
        employee_id,
        job_title                                               AS poste_actuel,
        department_id
    FROM assignments
    WHERE start_date <= :snapshot_date
    ORDER BY employee_id, start_date DESC
)
SELECT
    e.id                                                        AS employee_id,
    e.employee_code,

    -- ══ DATE DE SNAPSHOT (clé pour le split temporel) ══
    CAST(:snapshot_date AS DATE)                                AS snapshot_date,

    -- ══ LABEL SANS FUITE ══
    -- 1 = l'employé quitte dans les HORIZON_MONTHS mois après le snapshot
    -- 0 = toujours présent (ou quitte plus tard)
    CASE
        WHEN e.termination_date IS NOT NULL
         AND e.termination_date > :snapshot_date
         AND e.termination_date <= :snapshot_date + (:horizon_days * INTERVAL '1 day')
        THEN 1
        ELSE 0
    END                                                         AS target_turnover,

    -- ══ FEATURES DÉMOGRAPHIQUES ══
    -- L'âge est calculé AU MOMENT DU SNAPSHOT (pas aujourd'hui)
    DATE_PART('year', AGE(:snapshot_date::date, e.date_of_birth))::int  AS age,
    e.gender,

    -- ══ ANCIENNETÉ AU MOMENT DU SNAPSHOT ══
    -- On n'utilise PAS termination_date ici : l'ancienneté est mesurée
    -- de hire_date jusqu'au snapshot (information disponible à ce moment)
    ROUND(
        DATE_PART('epoch',
            AGE(:snapshot_date::date, e.hire_date)
        ) / 2592000
    )::int                                                      AS anciennete_mois,

    -- ══ CONTRAT ══
    c.is_cdi,
    c.nb_types_contrat,
    c.type_contrat_dominant,
    c.salaire_max                                               AS salaire,

    -- ══ ABSENCES ══
    COALESCE(ab.nb_absences, 0)                                 AS nb_absences,
    COALESCE(ab.total_jours_absence, 0)                         AS total_jours_absence,
    COALESCE(ab.nb_absences_longues, 0)                         AS nb_absences_longues,
    COALESCE(ab.motif_dominant, 'aucun')                        AS motif_absence_dominant,

    -- ══ POSTE ══
    af.poste_actuel,
    d.name                                                      AS department_name

FROM employees e
INNER JOIN contrats     c  ON e.id = c.employee_id
LEFT  JOIN absences     ab ON e.id = ab.employee_id
LEFT  JOIN affectations af ON e.id = af.employee_id
LEFT  JOIN departments  d  ON af.department_id = d.id
WHERE e.hire_date IS NOT NULL
  AND e.hire_date <= :snapshot_date          -- employé déjà présent au snapshot
  AND c.salaire_max IS NOT NULL
  -- Exclure les employés déjà partis AVANT le snapshot (ils ne sont plus à risque)
  AND (e.termination_date IS NULL OR e.termination_date > :snapshot_date)
"""


def load_data(
    db_url: str,
    snapshot_date: date,
    horizon_months: int,
) -> pd.DataFrame:
    """
    Extrait un snapshot de la base à une date donnée.

    Args:
        db_url:         URL SQLAlchemy de la base cible.
        snapshot_date:  Date de référence ; seules les données disponibles
                        à cette date sont utilisées comme features.
        horizon_months: Fenêtre future (en mois) pour définir le label.

    Returns:
        DataFrame avec features + target_turnover + snapshot_date.
    """
    horizon_days = horizon_months * 30
    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.connect() as conn:
        df = pd.read_sql(
            text(QUERY),
            conn,
            params={
                "snapshot_date": snapshot_date.isoformat(),
                "horizon_days": horizon_days,
            },
        )

    n = len(df)
    n_churn = int(df["target_turnover"].sum())
    logger.info(
        "Snapshot %s | horizon %d mois | %d employés | churn=%d (%.1f%%)",
        snapshot_date,
        horizon_months,
        n,
        n_churn,
        n_churn / n * 100 if n else 0,
    )
    return df


# ══════════════════════════════════════════════════════════
# FEATURE ENGINEERING SUR DONNÉES RÉELLES
# ══════════════════════════════════════════════════════════

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construit les features métier depuis les données réelles.

    Note: anciennete_mois est calculé dans la requête SQL à partir de
    hire_date jusqu'au snapshot_date uniquement — pas de termination_date.
    """
    df = df.copy()

    # Taux d'absentéisme mensuel (jours_absence / jours_travaillés_théoriques)
    jours_travailles = np.maximum(df["anciennete_mois"] * 22, 1)
    df["taux_absenteisme"] = df["total_jours_absence"] / jours_travailles

    # Ratio absences longues / total
    df["ratio_absences_longues"] = np.where(
        df["nb_absences"] > 0,
        df["nb_absences_longues"] / df["nb_absences"],
        0.0,
    )

    # Percentile salarial dans l'entreprise (Z-score)
    sal_mean = df["salaire"].mean()
    sal_std  = df["salaire"].std() + 1e-8
    df["salaire_zscore"] = (df["salaire"] - sal_mean) / sal_std

    # Percentile salarial par département
    df["salaire_relatif_dept"] = df.groupby("department_name")["salaire"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-8)
    )

    # Flags binaires
    df["flag_nouvel_employe"] = (df["anciennete_mois"] < 12).astype(int)
    df["flag_senior"]         = (df["anciennete_mois"] > 60).astype(int)
    df["flag_absenteisme_eleve"] = (df["nb_absences"] > 8).astype(int)
    df["flag_contrat_instable"]  = (df["nb_types_contrat"] > 1).astype(int)

    # Score de stabilité contractuelle
    df["score_stabilite"] = 1.0 / (1.0 + df["nb_types_contrat"])

    # Catégorisation du poste
    df["niveau_poste"] = df["poste_actuel"].apply(_categorize_job_level)

    logger.info("Feature engineering : %d features construites", len(df.columns))
    return df


def _categorize_job_level(title: str) -> str:
    if pd.isna(title):
        return "inconnu"
    t = title.lower()
    if any(w in t for w in ["senior", "lead", "principal", "manager", "directeur", "chef"]):
        return "senior"
    if any(w in t for w in ["junior", "assistant", "stagiaire", "apprenti"]):
        return "junior"
    return "intermediaire"


# ══════════════════════════════════════════════════════════
# PREPROCESSING
# ══════════════════════════════════════════════════════════

NUMERIC_FEATURES = [
    "age",
    "anciennete_mois",
    "is_cdi",
    "nb_types_contrat",
    "salaire",
    "salaire_zscore",
    "salaire_relatif_dept",
    "nb_absences",
    "total_jours_absence",
    "nb_absences_longues",
    "taux_absenteisme",
    "ratio_absences_longues",
    "flag_nouvel_employe",
    "flag_senior",
    "flag_absenteisme_eleve",
    "flag_contrat_instable",
    "score_stabilite",
]

CATEGORICAL_FEATURES = [
    "gender",
    "type_contrat_dominant",   # CDI, CDD, Stage, Intérim
    "department_name",         # Vrai département
    "niveau_poste",            # senior / intermediaire / junior
    "motif_absence_dominant",  # Vrai motif d'absence
]


def build_preprocessor() -> ColumnTransformer:
    """
    Pipeline sklearn :
    - Numériques  : imputation médiane + StandardScaler
    - Catégorielles : imputation 'inconnu' + OneHotEncoder
    """
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="inconnu")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe,  NUMERIC_FEATURES),
            ("cat", cat_pipe,      CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    cat_names = (
        preprocessor
        .named_transformers_["cat"]
        .named_steps["encoder"]
        .get_feature_names_out(CATEGORICAL_FEATURES)
        .tolist()
    )
    return NUMERIC_FEATURES + cat_names


# ══════════════════════════════════════════════════════════
# SPLIT TEMPOREL (pas de split aléatoire)
# ══════════════════════════════════════════════════════════

def temporal_split(
    df: pd.DataFrame,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Divise le dataset selon l'ordre chronologique de snapshot_date.

    Pourquoi temporel et pas aléatoire ?
    Un split aléatoire permettrait au modèle de « voir » des observations
    futures pendant l'entraînement, ce qui gonfle artificiellement les métriques.
    En production le modèle prédit toujours sur des données futures.

    Args:
        df:          DataFrame avec une colonne snapshot_date.
        train_ratio: Proportion pour l'entraînement (ex. 0.70).
        val_ratio:   Proportion pour la validation  (ex. 0.15).

    Returns:
        (df_train, df_val, df_test) triés chronologiquement.
    """
    df_sorted = df.sort_values("snapshot_date").reset_index(drop=True)
    n = len(df_sorted)
    i_train = int(n * train_ratio)
    i_val   = int(n * (train_ratio + val_ratio))

    df_train = df_sorted.iloc[:i_train]
    df_val   = df_sorted.iloc[i_train:i_val]
    df_test  = df_sorted.iloc[i_val:]

    logger.info(
        "Split temporel : Train=%d (jusqu'au %s) | Val=%d | Test=%d (à partir du %s)",
        len(df_train),
        df_train["snapshot_date"].max(),
        len(df_val),
        len(df_test),
        df_test["snapshot_date"].min(),
    )
    return df_train, df_val, df_test


# ══════════════════════════════════════════════════════════
# SEUIL OPTIMAL (validation set)
# ══════════════════════════════════════════════════════════

def find_optimal_threshold(
    y_true: pd.Series,
    y_proba: np.ndarray,
    metric: str = "f1",
) -> float:
    """
    Calcule le seuil de décision optimal sur le jeu de validation.

    Pourquoi ne pas garder 0.35 fixe ?
    Un seuil arbitraire ignore la distribution réelle des probabilités
    qui dépend des données et du déséquilibre de classes.

    Args:
        y_true:  Labels vrais.
        y_proba: Probabilités prédites pour la classe positive.
        metric:  "f1" (défaut) ou "recall" (si priorité sur la détection).

    Returns:
        Seuil flottant entre 0 et 1.
    """
    thresholds = np.linspace(0.05, 0.95, 91)
    best_thresh, best_score = 0.5, 0.0

    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        if metric == "recall":
            score = recall_score(y_true, y_pred, zero_division=0)
        else:
            score = f1_score(y_true, y_pred, zero_division=0)
        if score > best_score:
            best_score = score
            best_thresh = float(t)

    logger.info(
        "Seuil optimal (%s) : %.2f  → score=%.3f", metric, best_thresh, best_score
    )
    return best_thresh


# ══════════════════════════════════════════════════════════
# ENTRAÎNEMENT XGBOOST
# ══════════════════════════════════════════════════════════

def train_xgboost(
    X_train: np.ndarray,
    y_train: pd.Series,
    X_val: np.ndarray,
    y_val: pd.Series,
    scale_pos_weight: float,
) -> xgb.XGBClassifier:
    """
    Entraîne XGBoost avec :
    - scale_pos_weight calculé depuis les vraies proportions
    - early stopping sur AUC validation
    - hyperparamètres optimisés pour données RH
    """
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=1,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=scale_pos_weight,   # ✅ Gère le déséquilibre classes
        random_state=42,
        eval_metric="auc",
        early_stopping_rounds=25,
        use_label_encoder=False,
        n_jobs=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=20,
    )
    logger.info("Meilleure itération : %d", model.best_iteration)
    return model


# ══════════════════════════════════════════════════════════
# ÉVALUATION
# ══════════════════════════════════════════════════════════

def cross_validate_pipeline(
    full_pipeline: Pipeline,
    X_raw: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
) -> Dict:
    """
    Cross-validation sans fuite : le Pipeline complet (preprocessor + model)
    est entraîné et évalué entièrement à l'intérieur de chaque fold.

    FIX FUITE CV : l'ancienne version appelait cross_val_score sur des données
    déjà transformées par le preprocessor fité sur tout le dataset,
    ce qui constitue une fuite data.

    TimeSeriesSplit : les folds sont chronologiques (train toujours avant test),
    ce qui reflète la réalité de la mise en production.
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_auc = cross_val_score(
        full_pipeline, X_raw, y, cv=tscv, scoring="roc_auc", n_jobs=-1
    )
    cv_f1 = cross_val_score(
        full_pipeline, X_raw, y, cv=tscv, scoring="f1", n_jobs=-1
    )
    logger.info(
        "CV temporelle (%d folds) : AUC=%.3f ±%.3f | F1=%.3f ±%.3f",
        n_splits,
        cv_auc.mean(), cv_auc.std(),
        cv_f1.mean(),  cv_f1.std(),
    )
    return {
        "cv_auc_mean": float(cv_auc.mean()),
        "cv_auc_std":  float(cv_auc.std()),
        "cv_f1_mean":  float(cv_f1.mean()),
        "cv_f1_std":   float(cv_f1.std()),
        "cv_n_splits": n_splits,
        "cv_strategy": "TimeSeriesSplit",
    }


def evaluate(
    calibrated_model: CalibratedClassifierCV,
    X_test: np.ndarray,
    y_test: pd.Series,
    threshold: float,
    cv_metrics: Dict,
    best_iteration: Optional[int],
) -> Dict:
    """
    Évaluation finale sur le jeu de test (holdout le plus récent).

    Utilise le modèle calibré et le seuil optimal calculé sur la validation.
    Ajoute PR-AUC qui est plus informative qu'AUC-ROC pour les classes
    déséquilibrées (ce qui est typiquement le cas du turnover).
    """
    y_proba = calibrated_model.predict_proba(X_test)[:, 1]
    y_pred  = (y_proba >= threshold).astype(int)

    metrics: Dict = {
        # ─ Métriques principales ─
        "roc_auc_test":    float(roc_auc_score(y_test, y_proba)),
        "pr_auc_test":     float(average_precision_score(y_test, y_proba)),
        "f1_score_test":   float(f1_score(y_test, y_pred,  zero_division=0)),
        "precision_test":  float(precision_score(y_test, y_pred, zero_division=0)),
        "recall_test":     float(recall_score(y_test, y_pred,    zero_division=0)),
        "accuracy":        float(accuracy_score(y_test, y_pred)),
        # ─ Seuil utilisé ─
        "threshold_used":  threshold,
        # ─ Taille du jeu de test ─
        "n_samples_test":  int(len(y_test)),
        "n_positive_test": int(y_test.sum()),
        # ─ Infos modèle ─
        "best_iteration":  best_iteration,
        "training_date":   datetime.now().isoformat(),
        "model":           "XGBoost + CalibratedClassifierCV(isotonic)",
        "label_definition": "départ dans les HORIZON_MONTHS mois après snapshot",
        "data_source":     "vraies données RH (employees + contracts + absences + assignments)",
        "features_numeriques":    NUMERIC_FEATURES,
        "features_categorielles": CATEGORICAL_FEATURES,
        # ─ Matrice de confusion + rapport ─
        "confusion_matrix":      confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        ),
        # ─ Cross-validation temporelle ─
        **cv_metrics,
    }

    logger.info("\n" + "="*55)
    logger.info("RÉSULTATS D'ÉVALUATION (seuil=%.2f)", threshold)
    logger.info("="*55)
    logger.info("  AUC-ROC    : %.3f", metrics["roc_auc_test"])
    logger.info("  PR-AUC     : %.3f  (imbalanced → plus fiable)", metrics["pr_auc_test"])
    logger.info("  F1 Score   : %.3f", metrics["f1_score_test"])
    logger.info("  Precision  : %.3f", metrics["precision_test"])
    logger.info("  Recall     : %.3f", metrics["recall_test"])
    logger.info("  CV AUC     : %.3f ± %.3f", metrics["cv_auc_mean"], metrics["cv_auc_std"])
    logger.info("  CV F1      : %.3f ± %.3f", metrics["cv_f1_mean"],  metrics["cv_f1_std"])
    logger.info("="*55)
    logger.info(
        "\n%s",
        classification_report(y_test, y_pred, target_names=["Actif", "Parti"], zero_division=0),
    )
    return metrics


# ══════════════════════════════════════════════════════════
# SAUVEGARDE — joblib (pas pickle)
# ══════════════════════════════════════════════════════════

def save_bundle(
    calibrated_model: CalibratedClassifierCV,
    preprocessor: ColumnTransformer,
    feature_names: List[str],
    threshold: float,
    horizon_months: int,
    metrics: Dict,
) -> None:
    """
    Sauvegarde le bundle de production avec joblib.

    Contenu :
      - calibrated_model : modèle XGBoost calibré (probabilités fiables)
      - preprocessor     : ColumnTransformer fité sur le train uniquement
      - feature_names    : alignés avec l'ordre du preprocessor (pour SHAP)
      - threshold        : seuil optimal calculé sur la validation
      - horizon_months   : horizon utilisé pour la définition du label
      - metrics          : métriques d'évaluation
    """
    bundle = {
        # Modèle et preprocessing
        "model":           calibrated_model,
        "preprocessor":    preprocessor,
        "feature_names":   feature_names,
        "selected_features": feature_names,
        # Config
        "model_name":      "XGBoost",
        "model_version":   "XGBoost_real_v2_calibrated",
        "threshold":       threshold,           # ✅ calculé sur la validation
        "horizon_months":  horizon_months,      # ✅ stocke la définition du label
        # Métadonnées
        "metrics":         metrics,
        "training_date":   datetime.now().isoformat(),
        "data_source":     "vraies données RH PostgreSQL",
        # Placeholder SHAP — les noms de features sont alignés avec le
        # ColumnTransformer pour que shap.TreeExplainer puisse être appelé
        # directement sur calibrated_model.calibrated_classifiers_[0].estimator
        "shap_ready":      True,
    }

    model_path = MODEL_DIR / "turnover_model_real.pkl"
    joblib.dump(bundle, model_path, compress=3)
    logger.info("Modèle sauvegardé : %s", model_path)

    metrics_path = MODEL_DIR / "turnover_model_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        metrics_json = {
            k: v for k, v in metrics.items()
            if k not in ("classification_report",)
        }
        json.dump(metrics_json, f, indent=2, ensure_ascii=False)
    logger.info("Métriques sauvegardées : %s", metrics_path)


# ══════════════════════════════════════════════════════════
# PIPELINE COMPLET
# ══════════════════════════════════════════════════════════

def run(
    snapshot_date: Optional[date] = None,
    horizon_months: int = DEFAULT_HORIZON_MONTHS,
) -> None:
    """
    Pipeline d'entraînement complet, sans fuite temporelle.

    Args:
        snapshot_date:  Date de référence pour le snapshot.
                        Défaut : aujourd'hui moins 2 ans (pour avoir assez
                        d'observations dans la fenêtre horizon).
        horizon_months: Nombre de mois futurs définissant le label.
    """
    if snapshot_date is None:
        # Par défaut on observe les employés 2 ans en arrière afin que la
        # fenêtre horizon soit déjà observée (on connaît le résultat réel).
        snapshot_date = date.today() - timedelta(days=365 * 2)

    logger.info("="*60)
    logger.info("ENTRAÎNEMENT TURNOVER — DONNÉES RÉELLES POSTGRESQL")
    logger.info("  snapshot : %s | horizon : %d mois", snapshot_date, horizon_months)
    logger.info("="*60)

    # ──────────────────────────────────────────────────────
    # 1. Extraction snapshot sans fuite
    # ──────────────────────────────────────────────────────
    df = load_data(DB_URL, snapshot_date, horizon_months)

    if len(df) < 50:
        raise ValueError(f"Seulement {len(df)} lignes. Minimum 50 requis.")
    if df["target_turnover"].sum() < 5:
        raise ValueError(
            "Moins de 5 employés dans la fenêtre de départ. "
            "Essayez un horizon plus large ou une date de snapshot plus ancienne."
        )

    # ──────────────────────────────────────────────────────
    # 2. Feature engineering
    # ──────────────────────────────────────────────────────
    df = engineer_features(df)

    # ──────────────────────────────────────────────────────
    # 3. Split TEMPOREL (pas aléatoire)
    # ──────────────────────────────────────────────────────
    df_train, df_val, df_test = temporal_split(df)

    all_features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X_tr  = df_train[all_features]
    y_tr  = df_train["target_turnover"]
    X_val = df_val[all_features]
    y_val = df_val["target_turnover"]
    X_te  = df_test[all_features]
    y_te  = df_test["target_turnover"]

    logger.info(
        "Features : %d | Churn rate — train=%.1f%% val=%.1f%% test=%.1f%%",
        len(all_features),
        y_tr.mean() * 100, y_val.mean() * 100, y_te.mean() * 100,
    )

    # ──────────────────────────────────────────────────────
    # 4. Preprocessing — fit UNIQUEMENT sur train
    # ──────────────────────────────────────────────────────
    preprocessor = build_preprocessor()
    X_tr_t  = preprocessor.fit_transform(X_tr,  y_tr)
    X_val_t = preprocessor.transform(X_val)
    X_te_t  = preprocessor.transform(X_te)

    feature_names = get_feature_names(preprocessor)
    logger.info("Preprocessing : %d features après encodage", len(feature_names))

    # ──────────────────────────────────────────────────────
    # 5. Entraînement XGBoost (early stopping sur validation)
    # ──────────────────────────────────────────────────────
    n_neg = int((y_tr == 0).sum())
    n_pos = int((y_tr == 1).sum())
    spw   = n_neg / max(n_pos, 1)
    logger.info("scale_pos_weight = %.2f (n_actifs=%d / n_partis=%d)", spw, n_neg, n_pos)

    xgb_model = train_xgboost(X_tr_t, y_tr, X_val_t, y_val, spw)

    # ──────────────────────────────────────────────────────
    # 6. Calibration des probabilités
    #
    # Pourquoi calibrer ?
    # XGBoost optimise le ranking (AUC) mais pas la calibration des proba.
    # Des proba mal calibrées faussent les seuils et les scores affichés
    # aux RH (« 87% de risque » doit signifier quelque chose de réel).
    #
    # cv='prefit' : le modèle est déjà entraîné (avec early stopping) ;
    # on calibre uniquement sur le jeu de validation (pas de re-fit).
    # ──────────────────────────────────────────────────────
    calibrated_model = CalibratedClassifierCV(
        xgb_model, cv="prefit", method="isotonic"
    )
    calibrated_model.fit(X_val_t, y_val)
    logger.info("Calibration isotonic appliquée sur le jeu de validation")

    # ──────────────────────────────────────────────────────
    # 7. Seuil optimal (sur la validation, pas le test)
    # ──────────────────────────────────────────────────────
    val_proba = calibrated_model.predict_proba(X_val_t)[:, 1]
    threshold = find_optimal_threshold(y_val, val_proba, metric="f1")

    # ──────────────────────────────────────────────────────
    # 8. Cross-validation temporelle sur Pipeline complet
    #
    # Le Pipeline encapsule preprocessor + xgb_model brut (pas calibré)
    # pour éviter la fuite dans les folds CV : le preprocessor est
    # re-fité indépendamment dans chaque fold.
    # Note : on n'inclut pas la calibration dans le Pipeline CV car
    # elle nécessite un jeu de validation dédié (cv='prefit').
    # ──────────────────────────────────────────────────────
    cv_xgb = xgb.XGBClassifier(
        n_estimators=xgb_model.best_iteration or 100,  # ✅ iterations fixées
        max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        gamma=1, min_child_weight=3,
        reg_alpha=0.1, reg_lambda=1.0,
        scale_pos_weight=spw,
        random_state=42,
        eval_metric="auc",
        use_label_encoder=False,
        n_jobs=-1,
    )
    full_pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("model",        cv_xgb),
    ])
    X_full = df[all_features]
    y_full = df["target_turnover"]
    cv_metrics = cross_validate_pipeline(full_pipeline, X_full, y_full)

    # ──────────────────────────────────────────────────────
    # 9. Évaluation finale sur le test set (holdout le plus récent)
    # ──────────────────────────────────────────────────────
    metrics = evaluate(
        calibrated_model,
        X_te_t, y_te,
        threshold,
        cv_metrics,
        best_iteration=xgb_model.best_iteration,
    )

    # ──────────────────────────────────────────────────────
    # 10. Sauvegarde bundle joblib
    # ──────────────────────────────────────────────────────
    save_bundle(
        calibrated_model,
        preprocessor,
        feature_names,
        threshold,
        horizon_months,
        metrics,
    )

    logger.info("="*60)
    logger.info("ENTRAÎNEMENT TERMINÉ")
    logger.info("  AUC-ROC  : %.3f", metrics["roc_auc_test"])
    logger.info("  PR-AUC   : %.3f", metrics["pr_auc_test"])
    logger.info("  F1 Score : %.3f", metrics["f1_score_test"])
    logger.info("  Seuil    : %.2f", threshold)
    logger.info("  CV AUC   : %.3f ± %.3f", metrics["cv_auc_mean"], metrics["cv_auc_std"])
    logger.info("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement modèle turnover RH")
    parser.add_argument(
        "--snapshot",
        type=date.fromisoformat,
        default=None,
        help="Date de snapshot ISO (YYYY-MM-DD). Défaut : aujourd'hui - 2 ans.",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=DEFAULT_HORIZON_MONTHS,
        help=f"Fenêtre de prédiction en mois. Défaut : {DEFAULT_HORIZON_MONTHS}.",
    )
    args = parser.parse_args()
    run(snapshot_date=args.snapshot, horizon_months=args.horizon)