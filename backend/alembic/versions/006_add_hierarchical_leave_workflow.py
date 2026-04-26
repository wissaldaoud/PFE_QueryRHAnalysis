"""add hierarchical leave workflow

Revision ID: 006
Revises: 005
Create Date: 2026-02-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Étape 1: Ajouter les nouvelles colonnes
    op.add_column('leave_requests', sa.Column('manager_approved_by', sa.Integer(), nullable=True))
    op.add_column('leave_requests', sa.Column('manager_approval_date', sa.DateTime(), nullable=True))
    op.add_column('leave_requests', sa.Column('hr_approved_by', sa.Integer(), nullable=True))
    op.add_column('leave_requests', sa.Column('hr_approval_date', sa.DateTime(), nullable=True))
    op.add_column('leave_requests', sa.Column('rejected_by', sa.Integer(), nullable=True))
    op.add_column('leave_requests', sa.Column('rejection_date', sa.DateTime(), nullable=True))
    
    # Étape 2: Créer les foreign keys
    op.create_foreign_key(
        'fk_leave_manager_approved_by',
        'leave_requests', 'users',
        ['manager_approved_by'], ['id']
    )
    op.create_foreign_key(
        'fk_leave_hr_approved_by',
        'leave_requests', 'users',
        ['hr_approved_by'], ['id']
    )
    op.create_foreign_key(
        'fk_leave_rejected_by',
        'leave_requests', 'users',
        ['rejected_by'], ['id']
    )
    
    # Étape 3: Mettre à jour l'enum LeaveStatus
    # IMPORTANT: En PostgreSQL, on doit COMMIT après ajout de valeurs enum
    # avant de les utiliser. Alembic le fait automatiquement.
    conn = op.get_bind()
    
    # Vérifier si les valeurs existent déjà
    result = conn.execute(sa.text(
        "SELECT enumlabel FROM pg_enum WHERE enumtypid = "
        "(SELECT oid FROM pg_type WHERE typname = 'leavestatus')"
    ))
    existing_values = {row[0] for row in result}
    
    if 'manager_approved' not in existing_values:
        conn.execute(sa.text("ALTER TYPE leavestatus ADD VALUE 'manager_approved'"))
    if 'hr_approved' not in existing_values:
        conn.execute(sa.text("ALTER TYPE leavestatus ADD VALUE 'hr_approved'"))
    
    # Étape 4: Mettre à jour l'enum NotificationType si la table notifications existe
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'notificationtype')"
    ))
    type_exists = result.scalar()
    
    if type_exists:
        result = conn.execute(sa.text(
            "SELECT enumlabel FROM pg_enum WHERE enumtypid = "
            "(SELECT oid FROM pg_type WHERE typname = 'notificationtype')"
        ))
        existing_notif_values = {row[0] for row in result}
        
        if 'leave_manager_approved' not in existing_notif_values:
            conn.execute(sa.text("ALTER TYPE notificationtype ADD VALUE 'leave_manager_approved'"))
        if 'leave_hr_approved' not in existing_notif_values:
            conn.execute(sa.text("ALTER TYPE notificationtype ADD VALUE 'leave_hr_approved'"))
        if 'leave_rejected' not in existing_notif_values:
            conn.execute(sa.text("ALTER TYPE notificationtype ADD VALUE 'leave_rejected'"))
    
    # Note: La migration des données existantes (approved → hr_approved) 
    # doit être faite dans une migration séparée ou un script Python
    # car PostgreSQL nécessite un COMMIT entre l'ajout d'enum et son utilisation


def downgrade():
    # Supprimer les foreign keys
    op.drop_constraint('fk_leave_rejected_by', 'leave_requests', type_='foreignkey')
    op.drop_constraint('fk_leave_hr_approved_by', 'leave_requests', type_='foreignkey')
    op.drop_constraint('fk_leave_manager_approved_by', 'leave_requests', type_='foreignkey')
    
    # Supprimer les colonnes
    op.drop_column('leave_requests', 'rejection_date')
    op.drop_column('leave_requests', 'rejected_by')
    op.drop_column('leave_requests', 'hr_approval_date')
    op.drop_column('leave_requests', 'hr_approved_by')
    op.drop_column('leave_requests', 'manager_approval_date')
    op.drop_column('leave_requests', 'manager_approved_by')
    
    # Migrer les données: hr_approved → approved
    op.execute("""
        UPDATE leave_requests 
        SET status = 'approved'
        WHERE status = 'hr_approved' OR status = 'manager_approved'
    """)
    
    # Note: PostgreSQL ne permet pas de supprimer des valeurs d'enum facilement
    # Les valeurs ajoutées resteront dans l'enum mais ne seront pas utilisées
