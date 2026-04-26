"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    PIPELINE ETL COMPLET — RH ANALYTICS                    ║
║  Source : PostgreSQL DWH (données brutes)                                 ║
║  Cible  : PostgreSQL DWH (tables nettoyées et enrichies)                  ║
║  Features : Extract + Transform + Validate + Load + Logs + Rapport        ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, logging, hashlib
from datetime import datetime
from typing import Dict
import pandas as pd
from sqlalchemy import create_engine, text

# ══════════════════════════════════════════════════════
# CONFIGURATION LOGS
# ══════════════════════════════════════════════════════
os.makedirs("logs", exist_ok=True)
log_file = f"logs/etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL_RH")


class ETLPipeline:
    """
    Pipeline ETL PostgreSQL → PostgreSQL
    1. EXTRACT   — Lecture tables brutes DWH
    2. TRANSFORM  — Nettoyage + enrichissement + déduplication
    3. VALIDATE   — Contrôle qualité (complétude, NULL, doublons)
    4. LOAD       — Chargement UPSERT incrémental
    5. REPORT     — Rapport JSON + logs
    """

    def __init__(self):
        self.start_time = datetime.now()
        self.stats      = {}
        self.errors     = []

        logger.info("=" * 70)
        logger.info("🚀 DÉMARRAGE PIPELINE ETL RH")
        logger.info(f"   Date    : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Source  : PostgreSQL DWH (tables brutes)")
        logger.info(f"   Cible   : PostgreSQL DWH (tables enrichies)")
        logger.info("=" * 70)

        # Connexion PostgreSQL
        dwh_url = (
            f"postgresql://{os.getenv('DWH_USER','hr_user')}"
            f":{os.getenv('DWH_PASSWORD','hr_password123')}"
            f"@{os.getenv('DWH_HOST','localhost')}"
            f":{os.getenv('DWH_PORT','5432')}"
            f"/{os.getenv('DWH_DB','hr_datawarehouse')}"
        )
        self.engine = create_engine(
            dwh_url, pool_size=5, max_overflow=10, pool_pre_ping=True,
            connect_args={"client_encoding": "utf8"}
        )
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Connexion PostgreSQL DWH établie")
        except Exception as e:
            logger.error(f"❌ Connexion échouée : {e}")
            sys.exit(1)

    # ══════════════════════════════════════════════════
    # PHASE 1 — EXTRACT
    # ══════════════════════════════════════════════════

    def extract(self) -> Dict[str, pd.DataFrame]:
        logger.info("\n" + "─" * 50)
        logger.info("PHASE 1 — EXTRACTION DEPUIS DWH")
        logger.info("─" * 50)

        queries = {
            "employe": "SELECT * FROM dim.dim_employe",
            "contrat": "SELECT * FROM fait.fait_contrat",
            "affectation": "SELECT * FROM fait.fait_affectation",
            "absence": "SELECT * FROM fait.fait_absence",
        }

        data = {}
        for name, query in queries.items():
            try:
                df = pd.read_sql(query, self.engine)
                logger.info(f"   ✅ {name:15s} : {len(df):6d} lignes extraites")
                self.stats[name] = {"extracted": len(df)}
                data[name] = df
            except Exception as e:
                logger.error(f"   ❌ {name} : {e}")
                self.errors.append(f"Extract {name} : {e}")

        logger.info(f"\n   📊 Total : {sum(s['extracted'] for s in self.stats.values())} lignes extraites")
        return data

    # ══════════════════════════════════════════════════
    # PHASE 2 — TRANSFORM
    # ══════════════════════════════════════════════════

    def transform(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        logger.info("\n" + "─" * 50)
        logger.info("PHASE 2 — TRANSFORMATION + DÉDUPLICATION")
        logger.info("─" * 50)
        transformed = {}

        # ── DIM_EMPLOYE ──────────────────────────────
        if "employe" in data:
            df     = data["employe"].copy()
            before = len(df)

            # Déduplication
            df = df.drop_duplicates(subset=["nudoss"], keep="last")
            logger.info(f"   DIM_EMPLOYE : {before} → {len(df)} ({before-len(df)} doublons supprimés)")

            # Nettoyage noms
            for col in ["nom","prenom"]:
                if col in df.columns:
                    df[col] = df[col].str.strip().replace("", None)
                    df[col] = df[col].str.upper() if col == "nom" else df[col].str.capitalize()

            # Calcul tranche d'âge
            def tranche_age(age):
                if pd.isna(age): return "Non renseigné"
                age = int(age)
                if age < 25:  return "< 25 ans"
                if age < 35:  return "25-34 ans"
                if age < 45:  return "35-44 ans"
                if age < 55:  return "45-54 ans"
                if age < 65:  return "55-64 ans"
                return "65+ ans"

            if "date_naissance" in df.columns:
                df["date_naissance"] = pd.to_datetime(df["date_naissance"], errors="coerce")
                df["age"] = df["date_naissance"].apply(
                    lambda d: int((datetime.now() - d).days / 365.25) if pd.notna(d) else None
                )
                df["tranche_age"] = df["age"].apply(tranche_age)

            # Flag actif depuis contrats
            if "contrat" in data:
                actifs = data["contrat"].groupby("nudoss")["flag_contrat_actif"].max().reset_index()
                actifs.columns = ["nudoss","flag_employe_actif"]
                df = df.drop(columns=["flag_employe_actif"], errors="ignore")
                df = df.merge(actifs, on="nudoss", how="left")
                df["flag_employe_actif"] = df["flag_employe_actif"].fillna(0).astype(int)

            self.stats["employe"]["transformed"] = len(df)
            transformed["employe"] = df
            logger.info(f"   ✅ DIM_EMPLOYE transformé ({len(df)} lignes)")

        # ── FAIT_CONTRAT ─────────────────────────────
        if "contrat" in data:
            df     = data["contrat"].copy()
            before = len(df)

            # Déduplication
            df = df.drop_duplicates(
                subset=["nudoss","date_debut_contrat","libelle_type_contrat"],
                keep="last"
            )
            logger.info(f"   FAIT_CONTRAT : {before} → {len(df)} ({before-len(df)} doublons supprimés)")

            # Nettoyage dates
            for col in ["date_debut_contrat","date_fin_contrat"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            # Calcul durée
            df["duree_contrat_jours"] = df.apply(
                lambda r: (r["date_fin_contrat"] - r["date_debut_contrat"]).days
                if pd.notna(r.get("date_fin_contrat")) and pd.notna(r.get("date_debut_contrat"))
                else None, axis=1
            )

            # Catégorie contrat
            def categorie(t):
                if pd.isna(t): return "Autre"
                t = str(t).upper()
                if "CDI" in t or t == "PR": return "Permanent"
                if "CDD" in t or t in ["DI","FX"]: return "Temporaire"
                if "STAGE" in t or t == "ST": return "Stage"
                if "INTERIM" in t: return "Intérim"
                return "Autre"

            df["categorie_contrat"] = df["libelle_type_contrat"].apply(categorie)

            # Clé unique
            df["id_contrat_hash"] = df.apply(
                lambda r: hashlib.md5(
                    f"{r['nudoss']}|{r.get('date_debut_contrat','')}|{r.get('libelle_type_contrat','')}".encode()
                ).hexdigest()[:16], axis=1
            )

            self.stats["contrat"]["transformed"] = len(df)
            transformed["contrat"] = df
            logger.info(f"   ✅ FAIT_CONTRAT transformé ({len(df)} lignes)")

        # ── FAIT_ABSENCE ─────────────────────────────
        if "absence" in data:
            df     = data["absence"].copy()
            before = len(df)

            # Déduplication
            df = df.drop_duplicates(
                subset=["nudoss","date_debut_absence","libelle_motif_absence"],
                keep="last"
            )
            logger.info(f"   FAIT_ABSENCE : {before} → {len(df)} ({before-len(df)} doublons supprimés)")

            # Nettoyage motif
            df["libelle_motif_absence"] = df["libelle_motif_absence"].fillna("Non renseigné")
            df["libelle_motif_absence"] = df["libelle_motif_absence"].replace("","Non renseigné")

            # Nettoyage durée
            if "duree_absence_jours" in df.columns:
                df["duree_absence_jours"] = pd.to_numeric(df["duree_absence_jours"], errors="coerce")
                df["duree_absence_jours"] = df["duree_absence_jours"].clip(lower=0)

            # Dimensions temporelles
            if "date_debut_absence" in df.columns:
                df["date_debut_absence"] = pd.to_datetime(df["date_debut_absence"], errors="coerce")
                df["annee_absence"] = df["date_debut_absence"].dt.year
                df["mois_absence"]  = df["date_debut_absence"].dt.month
                df["annee_mois"]    = df["date_debut_absence"].dt.strftime("%Y-%m")

            self.stats["absence"]["transformed"] = len(df)
            transformed["absence"] = df
            logger.info(f"   ✅ FAIT_ABSENCE transformé ({len(df)} lignes)")

        # ── FAIT_AFFECTATION ─────────────────────────
        if "affectation" in data:
            df     = data["affectation"].copy()
            before = len(df)

            df = df.drop_duplicates(
                subset=["nudoss","date_debut_affectation","libelle_poste"],
                keep="last"
            )
            logger.info(f"   FAIT_AFFECTATION : {before} → {len(df)} ({before-len(df)} doublons supprimés)")

            df["libelle_poste"] = df["libelle_poste"].fillna("Non renseigné")
            df["libelle_poste"] = df["libelle_poste"].replace("","Non renseigné")

            self.stats["affectation"]["transformed"] = len(df)
            transformed["affectation"] = df
            logger.info(f"   ✅ FAIT_AFFECTATION transformé ({len(df)} lignes)")

        return transformed

    # ══════════════════════════════════════════════════
    # PHASE 3 — VALIDATE
    # ══════════════════════════════════════════════════

    def validate(self, data: Dict[str, pd.DataFrame]) -> bool:
        logger.info("\n" + "─" * 50)
        logger.info("PHASE 3 — VALIDATION QUALITÉ")
        logger.info("─" * 50)
        all_valid = True

        checks = {
            "employe":    {"pk": "nudoss",       "min_rows": 10},
            "contrat":    {"pk": "nudoss",        "min_rows": 5},
            "absence":    {"pk": "nudoss",        "min_rows": 1},
            "affectation":{"pk": "nudoss",        "min_rows": 1},
        }

        for table, rules in checks.items():
            if table not in data:
                continue

            df     = data[table]
            pk     = rules["pk"]
            errors = []

            # Nb lignes minimum
            if len(df) < rules["min_rows"]:
                errors.append(f"Trop peu de lignes : {len(df)}")

            # NULL sur clé primaire
            if pk in df.columns:
                nulls = df[pk].isna().sum()
                if nulls > 0:
                    errors.append(f"{nulls} NULL dans {pk}")
                    all_valid = False

            # Doublons
            if pk in df.columns:
                dupes = df.duplicated(subset=[pk]).sum()

            # Complétude globale
            total_cells = len(df) * len(df.columns)
            null_cells  = df.isna().sum().sum()
            completeness = round((1 - null_cells/max(total_cells,1)) * 100, 1)

            status = "✅" if not errors else "⚠️"
            logger.info(f"\n   {status} {table.upper()}")
            logger.info(f"      Lignes      : {len(df)}")
            logger.info(f"      Complétude  : {completeness}%")
            logger.info(f"      Doublons    : {dupes}")
            logger.info(f"      NULL {pk:10s}: {df[pk].isna().sum() if pk in df.columns else 'N/A'}")
            if errors:
                for e in errors:
                    logger.warning(f"      ⚠️  {e}")

            if table in self.stats:
                self.stats[table]["completeness"] = completeness
                self.stats[table]["doublons"]     = int(dupes) if pk in df.columns else 0

        return all_valid

    # ══════════════════════════════════════════════════
    # PHASE 4 — LOAD (UPSERT incrémental)
    # ══════════════════════════════════════════════════

    def load(self, data: Dict[str, pd.DataFrame]) -> bool:
        logger.info("\n" + "─" * 50)
        logger.info("PHASE 4 — CHARGEMENT DWH (UPSERT incrémental)")
        logger.info("─" * 50)

        # IMPORTANT : employe en premier (clé étrangère)
        targets = {
            "employe":     ("dim", "dim_employe",     "nudoss"),
            "contrat":     ("fait","fait_contrat",    "id_contrat"),
            "absence":     ("fait","fait_absence",    "id_absence"),
            "affectation": ("fait","fait_affectation","id_affectation"),
        }

        success = True
        for source, (schema, table, pk) in targets.items():
            if source not in data:
                logger.warning(f"   ⚠️  {source} absent — skipped")
                continue

            df       = data[source].copy()
            target   = f"{schema}.{table}"
            logger.info(f"\n   📥 {source} → {target} ({len(df)} lignes)")

            try:
                # Compter avant
                with self.engine.connect() as conn:
                    try:
                        before = conn.execute(text(f"SELECT COUNT(*) FROM {target}")).scalar()
                    except:
                        before = 0

                # Étape 1 : Vider la table avec DELETE (pas TRUNCATE)
                try:
                    with self.engine.begin() as conn:
                        conn.execute(text(f"DELETE FROM {target}"))
                        logger.info(f"   🔄 DELETE {target} OK")
                except Exception as de:
                    logger.warning(f"   ⚠️  DELETE échoué ({de}) — INSERT direct sans vider")

                # Étape 2 : Insérer les données
                with self.engine.begin() as conn:
                    df.to_sql(
                        table, conn, schema=schema,
                        if_exists="append", index=False,
                        method="multi", chunksize=500
                    )

                # Compter après
                with self.engine.connect() as conn:
                    after = conn.execute(text(f"SELECT COUNT(*) FROM {target}")).scalar()

                new_rows = after - before
                logger.info(f"   ✅ {len(df)} lignes chargées | +{new_rows} nouvelles | Total : {after}")
                self.stats[source]["loaded"]   = len(df)
                self.stats[source]["new_rows"] = new_rows

            except Exception as e:
                logger.error(f"   ❌ Erreur chargement {source} : {e}")
                self.errors.append(f"Load {source} : {e}")
                success = False

        return success

    # ══════════════════════════════════════════════════
    # PHASE 5 — RAPPORT
    # ══════════════════════════════════════════════════

    def generate_report(self):
        end      = datetime.now()
        duration = (end - self.start_time).total_seconds()
        status   = "SUCCESS" if not self.errors else "PARTIAL"

        report = {
            "etl_run": {
                "start":       self.start_time.isoformat(),
                "end":         end.isoformat(),
                "duration_s":  round(duration, 2),
                "status":      status,
                "nb_errors":   len(self.errors),
            },
            "tables": self.stats,
            "errors": self.errors,
        }

        path = f"logs/etl_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info("\n" + "=" * 70)
        logger.info("📊 RAPPORT FINAL ETL")
        logger.info("=" * 70)
        logger.info(f"   Durée   : {duration:.1f}s")
        logger.info(f"   Statut  : {'✅ SUCCESS' if not self.errors else '⚠️ PARTIAL'}")
        logger.info(f"   Erreurs : {len(self.errors)}")
        logger.info(f"   Rapport : {path}")
        logger.info(f"   Log     : {log_file}")
        logger.info("\n   📋 Résumé par table :")
        for table, s in self.stats.items():
            extracted   = s.get("extracted", 0)
            transformed = s.get("transformed", 0)
            loaded      = s.get("loaded", 0)
            completeness= s.get("completeness", 0)
            logger.info(f"   {table:15s} | Extract:{extracted:5d} | Transform:{transformed:5d} | Load:{loaded:5d} | Complétude:{completeness}%")
        if self.errors:
            logger.warning("\n   ❌ Erreurs :")
            for err in self.errors:
                logger.warning(f"      {err}")
        logger.info("=" * 70)
        return report

    # ══════════════════════════════════════════════════
    # RUN COMPLET
    # ══════════════════════════════════════════════════

    def run(self):
        try:
            # Phase 1 — Extract
            data = self.extract()
            if not data:
                logger.error("❌ Aucune donnée extraite")
                return False

            # Phase 2 — Transform
            transformed = self.transform(data)

            # Phase 3 — Validate
            valid = self.validate(transformed)
            if not valid:
                logger.warning("⚠️  Validation avec avertissements — chargement continue")

            # Phase 4 — Load
            loaded = self.load(transformed)

            # Phase 5 — Rapport
            self.generate_report()
            return loaded

        except Exception as e:
            logger.error(f"❌ ERREUR CRITIQUE : {e}")
            self.errors.append(str(e))
            self.generate_report()
            return False


if __name__ == "__main__":
    pipeline = ETLPipeline()
    success  = pipeline.run()
    sys.exit(0 if success else 1)
