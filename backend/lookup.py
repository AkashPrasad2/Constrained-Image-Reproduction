from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


img_size = (64, 64)  # tuple

# 64 pixels, greyscale and white background
img = Image.new("L",  size=img_size, color=255)
draw = ImageDraw.Draw(img)

font = ImageFont.truetype("arial.ttf", 70)  # true font not bitmap font
print(f"Font: {font}")  # debug

draw.text((16, -10), 'a', font=font, fill=0)  # black a

plt.imshow(img, cmap="gray")
plt.show()
