from app.db.base import engine
from sqlalchemy import text

conn = engine.connect()
trans = conn.begin()

try:
    # 1. Trouver ou créer le département RH
    print("=" * 60)
    print("ÉTAPE 1: Vérifier/Créer département RH")
    print("=" * 60)
    
    result = conn.execute(text("SELECT id, name FROM departments WHERE name = 'RH' OR name = 'Ressources Humaines'"))
    row = result.fetchone()
    
    if row:
        dept_id = row[0]
        print(f"✅ Département RH trouvé: {row[1]} (ID: {dept_id})")
    else:
        # Créer le département RH
        result = conn.execute(text(
            "INSERT INTO departments (name, description, created_at, updated_at) "
            "VALUES ('RH', 'Département des Ressources Humaines', NOW(), NOW()) "
            "RETURNING id, name"
        ))
        row = result.fetchone()
        dept_id = row[0]
        print(f"✅ Département RH créé: {row[1]} (ID: {dept_id})")
    
    # 2. Assigner Salma au département RH
    print("\n" + "=" * 60)
    print("ÉTAPE 2: Assigner Salma au département RH")
    print("=" * 60)
    
    conn.execute(text(
        f"UPDATE employees SET department_id = {dept_id} "
        f"WHERE email = 'Salma.d@soprahr.com'"
    ))
    print(f"✅ Profil employé Salma (ID: 283) assigné au département RH ({dept_id})")
    
    # 3. Lier le compte user au profil employé
    print("\n" + "=" * 60)
    print("ÉTAPE 3: Lier le compte user au profil employé")
    print("=" * 60)
    
    conn.execute(text(
        "UPDATE users SET employee_id = 283 "
        "WHERE email = 'Salma.d@soprahr.com'"
    ))
    print("✅ Compte user Salma (ID: 32) lié au profil employé (ID: 283)")
    
    # Commit
    trans.commit()
    print("\n" + "=" * 60)
    print("✅ SUCCÈS: Toutes les modifications ont été appliquées")
    print("=" * 60)
    
    # Vérifier
    print("\nVÉRIFICATION:")
    result = conn.execute(text(
        "SELECT u.id, u.email, u.employee_id, e.first_name, e.last_name, e.department_id, d.name "
        "FROM users u "
        "LEFT JOIN employees e ON u.employee_id = e.id "
        "LEFT JOIN departments d ON e.department_id = d.id "
        "WHERE u.email = 'Salma.d@soprahr.com'"
    ))
    row = result.fetchone()
    
    if row:
        print(f"   User ID: {row[0]}")
        print(f"   Email: {row[1]}")
        print(f"   Employee ID: {row[2]} ✅")
        print(f"   Nom: {row[3]} {row[4]}")
        print(f"   Department ID: {row[5]} ✅")
        print(f"   Département: {row[6]}")
    
    print("\n🎯 RÉSULTAT:")
    print("   Salma peut maintenant se connecter et voir son équipe!")
    print("   Son équipe = tous les employés du département RH")
    
except Exception as e:
    trans.rollback()
    print(f"❌ ERREUR: {e}")
    raise
finally:
    conn.close()
