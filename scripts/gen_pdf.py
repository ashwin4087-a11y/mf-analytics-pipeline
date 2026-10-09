import markdown
from xhtml2pdf import pisa
import sys

md_file = r"C:\Users\USER\Downloads\intern\w3\sprint2_submission\Documentation\Sprint2_Verification_Report.md"
pdf_file = r"C:\Users\USER\Downloads\intern\w3\sprint2_submission\Documentation\Sprint2_Documentation.pdf"

with open(md_file, "r") as f:
    text = f.read()

html = markdown.markdown(text, extensions=['tables'])
html = f"<html><body>{html}</body></html>"

with open(pdf_file, "w+b") as out_pdf:
    pisa.CreatePDF(html, dest=out_pdf)

print("PDF generated successfully.")
