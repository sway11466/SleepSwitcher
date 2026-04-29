"""
assets/icon.ico を生成するスクリプト。
緑の円にグレーの Z を描いた複数サイズ埋め込み ico を出力する。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SIZES   = [16, 32, 48, 64, 128, 256]
COLOR_BG   = (76, 175, 80)   # #4CAF50 green
COLOR_Z    = (80, 80, 80)    # dark gray
FONT_PATH  = r'C:\Windows\Fonts\segoeuib.ttf'
OUT_PATH   = Path(__file__).parent / 'icon.ico'


def make_frame(size: int) -> Image.Image:
    img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = max(1, size // 16)
    draw.ellipse([margin, margin, size - margin, size - margin], fill=COLOR_BG)

    font_size = int(size * 0.70)
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), 'Z', font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), 'Z', font=font, fill=COLOR_Z)

    return img


if __name__ == '__main__':
    frames = [make_frame(s) for s in SIZES]
    frames[0].save(
        OUT_PATH,
        format='ICO',
        sizes=[(s, s) for s in SIZES],
        append_images=frames[1:],
    )
    print(f'saved: {OUT_PATH}')
