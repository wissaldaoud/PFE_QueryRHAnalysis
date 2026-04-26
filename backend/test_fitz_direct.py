"""
Test direct avec PyMuPDF
"""
import fitz  # PyMuPDF

pdf_path = r'C:\Users\wdaoud\Downloads\archive\Resumes PDF\Python Developer\10.pdf'

doc = fitz.open(pdf_path)

print(f"📄 PDF: {pdf_path}")
print(f"Pages: {len(doc)}")
print()

for i, page in enumerate(doc):
    text = page.get_text()
    print(f"Page {i+1} ({len(text)} chars):")
    print(text[:500])
    print("-"*80)
    
    # Check if it's an image-based PDF
    image_list = page.get_images()
    print(f"Images on page: {len(image_list)}")
    print("="*80)

doc.close()
