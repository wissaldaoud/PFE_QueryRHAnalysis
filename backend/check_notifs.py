from app.db.base import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Vérifier les notifications
    result = conn.execute(text('SELECT * FROM notifications'))
    notifs = result.fetchall()
    print(f'Notifications: {len(notifs)}')
    for n in notifs:
        print(n)
    
    # Vérifier les admins
    result2 = conn.execute(text("SELECT id, email, role FROM users WHERE role = 'admin'"))
    admins = result2.fetchall()
    print(f'\nAdmins: {len(admins)}')
    for a in admins:
        print(a)
    
    # Vérifier les comptes en attente
    result3 = conn.execute(text("SELECT id, email, full_name, account_status FROM users WHERE account_status = 'pending'"))
    pending = result3.fetchall()
    print(f'\nComptes en attente: {len(pending)}')
    for p in pending:
        print(p)
