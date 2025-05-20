from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a blue background
img = Image.new('RGB', (32, 32), color='#003366')
d = ImageDraw.Draw(img)

# Draw "RMU" in white
d.text((4, 8), "RMU", fill='white')

# Save as ICO file
img.save('app/static/img/favicon.ico', format='ICO', sizes=[(32, 32)])
