from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

W, H = 512, 512

# === Background ===
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw_bg = ImageDraw.Draw(img)
draw_bg.rounded_rectangle([(0, 0), (W-1, H-1)], radius=90, fill=(10, 22, 40, 255))

# Inner subtle border glow
for i in range(3):
    border = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(border)
    db.rounded_rectangle([(8, 8), (W-9, H-9)], radius=82, outline=(6, 182, 212, 30 - i*8), width=2+i)
    img = Image.alpha_composite(img, border)

draw = ImageDraw.Draw(img)

# === Enhanced radar/pulse arcs ===
wave_cx, wave_cy = 256, 355

for r in [20, 45, 75, 110, 150, 195]:
    alpha = max(15, 80 - r // 4)
    width = 2 if r < 80 else 3
    draw.arc([(wave_cx-r, wave_cy - r*0.55), (wave_cx+r, wave_cy + r*0.55)],
             start=0, end=180, fill=(6, 182, 212, alpha), width=width)

for r in [58, 95, 140]:
    draw.arc([(wave_cx-r, wave_cy - r*0.55), (wave_cx+r, wave_cy + r*0.55)],
             start=0, end=180, fill=(59, 130, 246, 35), width=1)

# Bright radar origin dot
for glow_r in [8, 5]:
    draw.ellipse([(wave_cx-glow_r, wave_cy-glow_r), (wave_cx+glow_r, wave_cy+glow_r)],
                 fill=(6, 182, 212, 60))
draw.ellipse([(249, 348), (263, 362)], fill=(6, 182, 212, 220))
draw.ellipse([(251, 350), (261, 360)], fill=(255, 255, 255, 230))

# Scan line
draw.line([(wave_cx+8, wave_cy), (wave_cx+180, wave_cy)], fill=(6, 182, 212, 80), width=2)
draw.line([(wave_cx-180, wave_cy), (wave_cx-8, wave_cy)], fill=(6, 182, 212, 80), width=2)

# Ticks on scan line
for tx in range(wave_cx-170, wave_cx+171, 35):
    if abs(tx - wave_cx) > 15:
        draw.line([(tx, wave_cy-4), (tx, wave_cy+4)], fill=(6, 182, 212, 100), width=1)

# === "PW" Text ===
try:
    font = ImageFont.truetype('C:/Windows/Fonts/calibrib.ttf', 220)
except:
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 220)
    except:
        font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 200)

text = "PW"
bbox = draw.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
tx = (W - tw) // 2 - bbox[0]
ty = (H - th) // 2 - bbox[1] - 30

# Create text layer
text_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
text_draw = ImageDraw.Draw(text_layer)
text_draw.text((tx, ty), text, font=font, fill=(255, 255, 255, 255))

# Create gradient overlay
gradient = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for y in range(H):
    t = y / H
    if t < 0.5:
        s = t / 0.5
        r = int(6 + (59 - 6) * s)
        g = int(182 + (130 - 182) * s)
        b = int(212 + (246 - 212) * s)
    else:
        s = (t - 0.5) / 0.5
        r = int(59 + (139 - 59) * s)
        g = int(130 + (92 - 130) * s)
        b = int(246 + (246 - 246) * s)
    for x in range(W):
        if text_layer.getpixel((x, y))[3] > 0:
            gradient.putpixel((x, y), (r, g, b, 255))

# Apply gradient
text_data = text_layer.getdata()
gradient_data = gradient.getdata()
combined = []
for i in range(len(text_data)):
    if text_data[i][3] > 0:
        combined.append(gradient_data[i])
    else:
        combined.append((0, 0, 0, 0))

result_text = Image.new('RGBA', (W, H))
result_text.putdata(combined)

# Glow behind text
text_glow = result_text.filter(ImageFilter.GaussianBlur(radius=12))
for _ in range(2):
    img = Image.alpha_composite(img, text_glow)
img = Image.alpha_composite(img, result_text)

# === CRITICAL: re-create draw after composite! ===
draw = ImageDraw.Draw(img)

# === Accent: top-left dots ===
for i, offset in enumerate([(40, 60), (70, 60), (100, 60)]):
    alpha = 255 - i * 80
    size = 8 - i * 1
    draw.ellipse([(offset[0]-size, offset[1]-size), (offset[0]+size, offset[1]+size)],
                 fill=(6, 182, 212, alpha))

# === Accent: top-left lines ===
draw.line([(40, 90), (110, 90)], fill=(139, 92, 246, 100), width=2)
draw.line([(40, 96), (80, 96)], fill=(6, 182, 212, 100), width=1)

# === "powered by root_objs" centered at bottom ===
try:
    credit_font = ImageFont.truetype('C:/Windows/Fonts/calibri.ttf', 26)
except:
    credit_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 24)

credit_text = "powered by root_objs"
cbox = draw.textbbox((0, 0), credit_text, font=credit_font)
ctw = cbox[2] - cbox[0]
cth = cbox[3] - cbox[1]

ctx = (W - ctw) // 2
cty = H - cth - 25

draw.text((ctx, cty), credit_text, font=credit_font, fill=(6, 182, 212, 160))

# === Resize and save ===
img = img.resize((256, 256), Image.LANCZOS)
img.save('d:/项目代码-临时/pikaw/web/public/logo.png', 'PNG')
print(f"Logo saved! Credit text at ({ctx}, {cty}), size={ctw}x{cth}, font loaded: {credit_font}")
