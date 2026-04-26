#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de débogage : Tendance des contrats par année
"""

print("=" * 70)
print("🐛 DEBUG : 'Tendance des contrats par année'")
print("=" * 70)

question = "Tendance des contrats par année"
question_lower = question.lower()

print(f"\n📝 Question : '{question}'")

# Simuler la détection NLP
has_par = " par " in question_lower
has_plus = "plus" in question_lower
has_moins = "moins" in question_lower
has_departement = any(word in question_lower for word in ["département", "departement", "service", "direction", "division"])

print(f"\n🔍 Détection patterns :")
print(f"   - has_par : {has_par}")
print(f"   - has_departement : {has_departement}")

print(f"\n🎯 Intent attendu : trend")
print(f"   - Entity : contrat")
print(f"   - Filters : {{}}")

print(f"\n📊 SQL généré ATTENDU :")
sql_attendu = """
SELECT EXTRACT(YEAR FROM c.date_debut_contrat)::integer as annee, 
       COUNT(*) as total
FROM dim.dim_employe e
LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
GROUP BY annee
ORDER BY annee;
"""
print(sql_attendu)

print("✅ Ce SQL devrait retourner ~10-15 lignes (une par année)")
print("✅ Visualisation : line_chart avec x=annee, y=total")

print("\n" + "=" * 70)
print("⚠️  SI 45 LIGNES SONT RETOURNÉES :")
print("=" * 70)
print("\n❌ PROBLÈME 1 : Intent mal détecté")
print("   - Vérifier que l'intent détecté est bien 'trend' et non 'stats'")
print("   - Mots-clés trend : 'évolution', 'tendance', 'historique', 'progression'")
print("   - La question 'par année' peut déclencher 'stats' au lieu de 'trend'")

print("\n❌ PROBLÈME 2 : GROUP BY incorrect")
print("   - Vérifier que le GROUP BY n'inclut pas c.libelle_type_contrat")
print("   - Doit être : GROUP BY annee")
print("   - Pas : GROUP BY annee, c.libelle_type_contrat")

print("\n❌ PROBLÈME 3 : SELECT inclut type_contrat")
print("   - Vérifier que SELECT ne contient pas c.libelle_type_contrat")
print("   - Doit être : SELECT EXTRACT(YEAR...) as annee, COUNT(*) as total")

print("\n" + "=" * 70)
print("🔧 SOLUTION :")
print("=" * 70)
print("\n1️⃣  Améliorer détection intent 'trend' :")
print("    - Ajouter 'par année', 'par mois', 'année' dans INTENT_PATTERNS trend")

print("\n2️⃣  Forcer intent=trend quand 'année' est dans la question :")
print("    - if 'année' in tokens or 'annee' in tokens:")
print("          boost trend intent score")

print("\n3️⃣  Vérifier que le SQL ne groupe pas par type_contrat :")
print("    - Ajouter un print du SQL complet dans les logs backend")

print("\n" + "=" * 70)
print("📋 ACTION IMMÉDIATE :")
print("=" * 70)
print("\n👉 Tester la question et COPIER LE SQL GÉNÉRÉ ICI")
print("👉 Vérifier dans les logs backend quel intent est détecté")
print("👉 Vérifier combien de colonnes sont retournées (doit être 2: annee, total)")

print("\n" + "=" * 70)
