from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))

c = canvas.Canvas("sample_contract.pdf")
c.setFont("SimSun", 12)

with open("sample_contract.txt", "r", encoding="utf-8") as f:
    text = f.read()

y = 800
for line in text.split('\n'):
    c.drawString(50, y, line)
    y -= 20

c.save()
print("Saved sample_contract.pdf")
