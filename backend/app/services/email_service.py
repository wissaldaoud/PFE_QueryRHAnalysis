"""
Email Service for HR Analytics
Envoie des notifications par email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration email
SMTP_HOST = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "hr-analytics@soprahr.com")
FROM_NAME = os.getenv("SMTP_FROM_NAME", "Query HR Analytics")

# Mode simulation (pour développement sans SMTP)
EMAIL_SIMULATION_MODE = os.getenv("EMAIL_SIMULATION_MODE", "true").lower() == "true"

print(f"[EMAIL] Email config: SMTP={SMTP_HOST}, User={SMTP_USER}, Simulation={EMAIL_SIMULATION_MODE}")


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Envoyer un email
    
    Args:
        to_email: Adresse email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML de l'email
        text_content: Contenu texte (optionnel)
    
    Returns:
        True si envoyé avec succès
    """
    if EMAIL_SIMULATION_MODE:
        # Mode simulation - juste logger l'email
        print(f"\n{'='*50}")
        print(f"📧 EMAIL SIMULÉ")
        print(f"{'='*50}")
        print(f"À: {to_email}")
        print(f"Sujet: {subject}")
        print(f"Contenu: {text_content or 'HTML content'}")
        print(f"{'='*50}\n")
        return True
    
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Ajouter le contenu texte et HTML
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Envoyer via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False


# ============================================
# TEMPLATES EMAIL
# ============================================

def send_account_pending_email(user_email: str, user_name: str):
    """Email envoyé à l'utilisateur après inscription"""
    subject = "🔐 Inscription en attente de validation - SopraHR"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .status {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SopraHR Analytics</h1>
            </div>
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                <p>Merci de vous être inscrit sur SopraHR Analytics !</p>
                
                <div class="status">
                    <strong>⏳ Statut: En attente de validation</strong>
                    <p>Votre compte a été créé mais doit être validé par un administrateur avant que vous puissiez vous connecter.</p>
                </div>
                
                <p>Vous recevrez un email dès que votre compte sera activé.</p>
                
                <p>Cordialement,<br>L'équipe SopraHR</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Bonjour {user_name},
    
    Merci de vous être inscrit sur SopraHR Analytics !
    
    Statut: En attente de validation
    
    Votre compte a été créé mais doit être validé par un administrateur 
    avant que vous puissiez vous connecter.
    
    Vous recevrez un email dès que votre compte sera activé.
    
    Cordialement,
    L'équipe SopraHR
    """
    
    return send_email(user_email, subject, html_content, text_content)


def send_account_approved_email(user_email: str, user_name: str):
    """Email envoyé quand le compte est approuvé"""
    subject = "✅ Compte activé - Bienvenue sur SopraHR !"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .success {{ background: #d4edda; border: 1px solid #28a745; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ display: inline-block; background: #E31837; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Bienvenue sur SopraHR !</h1>
            </div>
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                
                <div class="success">
                    <strong>✅ Votre compte a été approuvé !</strong>
                    <p>Vous pouvez maintenant vous connecter à SopraHR Analytics.</p>
                </div>
                
                <p>Vous avez accès à :</p>
                <ul>
                    <li>📊 Votre tableau de bord personnel</li>
                    <li>📅 Gestion de vos demandes de congés</li>
                    <li>⚙️ Paramètres de votre compte</li>
                </ul>
                
                <a href="http://localhost:3000/login" class="btn">Se connecter</a>
                
                <p style="margin-top: 30px;">Cordialement,<br>L'équipe SopraHR</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Bonjour {user_name},
    
    Votre compte a été approuvé !
    
    Vous pouvez maintenant vous connecter à SopraHR Analytics.
    
    Lien: http://localhost:3000/login
    
    Cordialement,
    L'équipe SopraHR
    """
    
    return send_email(user_email, subject, html_content, text_content)


def send_account_rejected_email(user_email: str, user_name: str, reason: str = ""):
    """Email envoyé quand le compte est rejeté"""
    subject = "❌ Demande de compte refusée - SopraHR"
    
    reason_text = f"<p><strong>Motif:</strong> {reason}</p>" if reason else ""
    reason_plain = f"\nMotif: {reason}" if reason else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .error {{ background: #f8d7da; border: 1px solid #dc3545; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SopraHR Analytics</h1>
            </div>
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                
                <div class="error">
                    <strong>❌ Votre demande de compte a été refusée</strong>
                    {reason_text}
                </div>
                
                <p>Si vous pensez qu'il s'agit d'une erreur, veuillez contacter l'administrateur.</p>
                
                <p>Cordialement,<br>L'équipe SopraHR</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Bonjour {user_name},
    
    Votre demande de compte a été refusée.
    {reason_plain}
    
    Si vous pensez qu'il s'agit d'une erreur, veuillez contacter l'administrateur.
    
    Cordialement,
    L'équipe SopraHR
    """
    
    return send_email(user_email, subject, html_content, text_content)


def send_leave_approved_email(user_email: str, user_name: str, leave_type: str, start_date: str, end_date: str, approver_name: str):
    """Email envoyé quand un congé est approuvé"""
    subject = "✅ Congé approuvé - SopraHR"
    
    leave_types = {
        "annual": "Congé annuel",
        "sick": "Congé maladie",
        "unpaid": "Congé sans solde",
        "maternity": "Congé maternité",
        "paternity": "Congé paternité"
    }
    leave_label = leave_types.get(leave_type, leave_type)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .success {{ background: #d4edda; border: 1px solid #28a745; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .details {{ background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Demande de Congé</h1>
            </div>
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                
                <div class="success">
                    <strong style="font-size: 18px;">✅ Votre demande de congé a été APPROUVÉE !</strong>
                    
                    <div class="details">
                        <p><strong>Type:</strong> {leave_label}</p>
                        <p><strong>Du:</strong> {start_date}</p>
                        <p><strong>Au:</strong> {end_date}</p>
                        <p><strong>Approuvé par:</strong> {approver_name}</p>
                    </div>
                </div>
                
                <p>Bon repos ! 🌴</p>
                
                <p>Cordialement,<br>L'équipe SopraHR</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Bonjour {user_name},
    
    ✅ Votre demande de congé a été APPROUVÉE !
    
    Détails:
    - Type: {leave_label}
    - Du: {start_date}
    - Au: {end_date}
    - Approuvé par: {approver_name}
    
    Bon repos !
    
    Cordialement,
    L'équipe SopraHR
    """
    
    return send_email(user_email, subject, html_content, text_content)


def send_leave_rejected_email(user_email: str, user_name: str, leave_type: str, start_date: str, end_date: str, reason: str, rejector_name: str):
    """Email envoyé quand un congé est rejeté"""
    subject = "❌ Congé refusé - SopraHR"
    
    leave_types = {
        "annual": "Congé annuel",
        "sick": "Congé maladie",
        "unpaid": "Congé sans solde",
        "maternity": "Congé maternité",
        "paternity": "Congé paternité"
    }
    leave_label = leave_types.get(leave_type, leave_type)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .error {{ background: #f8d7da; border: 1px solid #dc3545; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .details {{ background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Demande de Congé</h1>
            </div>
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                
                <div class="error">
                    <strong style="font-size: 18px;">❌ Votre demande de congé a été REFUSÉE</strong>
                    
                    <div class="details">
                        <p><strong>Type:</strong> {leave_label}</p>
                        <p><strong>Du:</strong> {start_date}</p>
                        <p><strong>Au:</strong> {end_date}</p>
                        <p><strong>Refusé par:</strong> {rejector_name}</p>
                        <p><strong>Motif:</strong> {reason}</p>
                    </div>
                </div>
                
                <p>Pour plus d'informations, contactez votre responsable.</p>
                
                <p>Cordialement,<br>L'équipe SopraHR</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Bonjour {user_name},
    
    ❌ Votre demande de congé a été REFUSÉE
    
    Détails:
    - Type: {leave_label}
    - Du: {start_date}
    - Au: {end_date}
    - Refusé par: {rejector_name}
    - Motif: {reason}
    
    Pour plus d'informations, contactez votre responsable.
    
    Cordialement,
    L'équipe SopraHR
    """
    
    return send_email(user_email, subject, html_content, text_content)


def send_new_account_notification_to_admin(admin_email: str, new_user_name: str, new_user_email: str):
    """Email envoyé aux admins quand un nouveau compte est créé"""
    subject = "🔔 Nouveau compte en attente de validation - SopraHR"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E31837, #c41530); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .alert {{ background: #cce5ff; border: 1px solid #0d6efd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ display: inline-block; background: #E31837; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Nouveau compte</h1>
            </div>
            <div class="content">
                <h2>Notification Admin</h2>
                
                <div class="alert">
                    <strong>Un nouveau compte est en attente de validation</strong>
                    <p><strong>Nom:</strong> {new_user_name}</p>
                    <p><strong>Email:</strong> {new_user_email}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                </div>
                
                <a href="http://localhost:3000/admin/accounts" class="btn">Gérer les comptes</a>
                
                <p style="margin-top: 30px;">SopraHR Analytics</p>
            </div>
            <div class="footer">
                <p>© 2026 SopraHR Analytics</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Notification Admin - SopraHR
    
    Un nouveau compte est en attente de validation:
    - Nom: {new_user_name}
    - Email: {new_user_email}
    - Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    
    Lien: http://localhost:3000/admin/accounts
    """
    
    return send_email(admin_email, subject, html_content, text_content)
