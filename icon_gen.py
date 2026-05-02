"""Generate app icon — a blue circle with 'P' letter."""
from PIL import Image, ImageDraw, ImageFont

sizes = [16, 32, 48, 64, 128, 256]

for size in sizes:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 10
    draw.ellipse([margin, margin, size - margin, size - margin], fill=(66, 133, 244))
    font_size = int(size * 0.55)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "P", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "P", fill="white", font=font)
    img.save(f"assets/icon_{size}.png")

img256 = Image.open("assets/icon_256.png")
img256.save("assets/icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
img256.save("assets/icon.icns", format="ICNS")
print("Icons generated.")
