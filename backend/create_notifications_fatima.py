from sqlalchemy import text
from app.db.base import SessionLocal
from datetime import datetime

db = SessionLocal()

try:
    # 1. Récupérer les infos nécessaires
    fatima = db.execute(text("""
        SELECT e.id as emp_id, e.first_name, e.last_name, e.manager_id,
               u.id as manager_user_id, u.email as manager_email
        FROM employees e
        JOIN employees m ON e.manager_id = m.id
        JOIN users u ON m.id = u.employee_id
        WHERE e.email = 'fatima.alaoui@soprahr.com'
    """)).fetchone()
    
    if not fatima:
        print("❌ Fatima ou son manager introuvable")
        exit(1)
    
    print(f"✓ Fatima (ID: {fatima.emp_id})")
    print(f"✓ Manager User ID: {fatima.manager_user_id}")
    print(f"✓ Manager Email: {fatima.manager_email}\n")
    
    # 2. Récupérer les demandes de congé en attente de Fatima
    leaves = db.execute(text("""
        SELECT id, leave_type, start_date, end_date, days_requested
        FROM leave_requests
        WHERE employee_id = :emp_id AND status = 'pending'
        ORDER BY created_at DESC
    """), {"emp_id": fatima.emp_id}).fetchall()
    
    if not leaves:
        print("ℹ️ Aucune demande en attente")
        exit(0)
    
    print(f"Demandes en attente: {len(leaves)}\n")
    
    # 3. Créer une notification pour chaque demande
    for leave in leaves:
        message = f"{fatima.first_name} {fatima.last_name} a demandé un congé ({leave.leave_type}) du {leave.start_date} au {leave.end_date} ({leave.days_requested} jours)"
        
        # Vérifier si la notification existe déjà
        existing = db.execute(text("""
            SELECT id FROM notifications
            WHERE user_id = :user_id
            AND message = :message
        """), {
            "user_id": fatima.manager_user_id,
            "message": message
        }).fetchone()
        
        if existing:
            print(f"  - Congé ID {leave.id}: notification existe déjà")
            continue
        
        # Créer la notification
        db.execute(text("""
            INSERT INTO notifications (user_id, type, title, message, is_read, link, created_at)
            VALUES (:user_id, :type, :title, :message, :is_read, :link, :created_at)
        """), {
            "user_id": fatima.manager_user_id,
            "type": "leave_pending",
            "title": "Nouvelle demande de congé",
            "message": message,
            "is_read": False,
            "link": f"/leaves/{leave.id}",
            "created_at": datetime.now()
        })
        
        print(f"  ✓ Notification créée pour congé ID {leave.id}")
    
    db.commit()
    print(f"\n✅ Notifications créées avec succès!")
    
    # 4. Vérifier les notifications de Karim
    notifs = db.execute(text("""
        SELECT id, title, message, is_read, created_at
        FROM notifications
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT 5
    """), {"user_id": fatima.manager_user_id}).fetchall()
    
    print(f"\n📬 Notifications de {fatima.manager_email}:")
    for notif in notifs:
        status = "✓ Lu" if notif.is_read else "⚪ Non lu"
        print(f"  {status} - {notif.title}")
        print(f"      {notif.message[:80]}...")
        print()

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
