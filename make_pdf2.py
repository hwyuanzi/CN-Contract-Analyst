from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))

c = canvas.Canvas("Data/Regulations/Rental/National (全国)/regulations.pdf")
c.setFont("SimSun", 12)

with open("Data/Regulations/Rental/National (全国)/regulations.txt", "r", encoding="utf-8") as f:
    text = f.read()

y = 800
for line in text.split('\n'):
    c.drawString(50, y, line[:50]) # Simple truncation for now, just to get a non-empty pdf
    y -= 20

c.save()
print("Saved regulations.pdf")
