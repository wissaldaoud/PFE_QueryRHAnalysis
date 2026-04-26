"""
Test d'extraction de CV du dataset Kaggle
"""
import sys
sys.path.insert(0, 'C:\\Users\\wdaoud\\Desktop\\test\\backend')

from app.services.cv_parser import CVParser

# Tester avec un CV Python Developer du dataset
pdf_path = r'C:\Users\wdaoud\Downloads\archive\Resumes PDF\Python Developer\10.pdf'

parser = CVParser()

# Lire le fichier
with open(pdf_path, 'rb') as f:
    content = f.read()

# Parser
result = parser.parse_cv('10.pdf', content)

print("="*80)
print(f"📄 Test extraction CV: {pdf_path}")
print("="*80)

if result['success']:
    print(f"\n✅ Extraction réussie!")
    print(f"\n📝 TEXTE BRUT ({len(result['text'])} caractères):")
    print("-"*80)
    print(result['text'][:1000])  # Premiers 1000 caractères
    print("-"*80)
    
    print(f"\n🔍 DONNÉES EXTRAITES:")
    print("-"*80)
    data = result['data']
    print(f"Compétences ({len(data['skills'])}): {data['skills']}")
    print(f"Années exp: {data['years_of_experience']}")
    print(f"Titres postes: {data['job_titles']}")
    print(f"Formation: {data['education']}")
    print(f"Expériences: {data['experiences'][:2] if data['experiences'] else []}")
else:
    print(f"\n❌ Échec: {result.get('error', 'Erreur inconnue')}")
