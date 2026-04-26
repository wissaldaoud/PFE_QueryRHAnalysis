from app.db.base import SessionLocal
from app.models.user import User
from app.core.security import verify_password

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@company.com').first()

print(f'User trouvé: {user}')
if user:
    print(f'Email: {user.email}')
    print(f'Hashed password: {user.hashed_password[:20]}...')
    result = verify_password('admin123', user.hashed_password)
    print(f'Password OK: {result}')
else:
    print('Utilisateur non trouvé!')

db.close()
