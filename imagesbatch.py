import os
from PIL import Image, ExifTags, ImageFont, ImageDraw
from datetime import datetime
import concurrent.futures
import time

# 相框与水印样式参数（可在此统一调整）
FRAME_INNER_RATIO = 0.012   # 内白边占短边比例
FRAME_OUTER_RATIO = 0.006   # 外灰边占短边比例
FRAME_FEATHER_RATIO = 0.5   # 羽化宽度占内边比例（0~1，越大过渡越宽）
WATERMARK_TEXT = "@rivalhw"
WATERMARK_FONT_SIZE_RATIO = 0.048   # 水印字号
WATERMARK_MARGIN_RATIO = 0.024      # 与边缘距离
WATERMARK_LETTER_SPACING = 2        # 字间距（像素），0 为无
# 立体质感：柔和投影层数及偏移（层数多更柔和）
WATERMARK_SOFT_SHADOW_STEPS = [(3, 3), (2, 2), (1, 1)]  # (dx, dy) 从远到近

def _load_font(size):
    """立体水印用略粗字体更出效果，优先粗体/半粗"""
    candidates = (
        "C:\\Windows\\Fonts\\segoeuib.ttf",  # Segoe UI Bold
        "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "segoeuib.ttf", "arialbd.ttf", "arial.ttf",
        "DejaVuSans-Bold.ttf", "DejaVuSans.ttf",
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _make_feather_mask(width, height, feather_width):
    """生成边缘羽化蒙版：中心不透明，四边在 feather_width 内线性过渡到透明。"""
    if feather_width <= 0:
        return Image.new('L', (width, height), 255)
    mask = Image.new('L', (width, height), 255)
    pix = mask.load()
    # 只遍历边缘带，减少大图时的计算量
    for y in range(height):
        for x in range(width):
            d = min(x, width - 1 - x, y, height - 1 - y)
            if d < feather_width:
                pix[x, y] = min(255, int(255 * d / feather_width))
    return mask


def _draw_text_layer(draw, x, y, text, font, fill, letter_spacing=0):
    """画一层文字，支持字间距"""
    if letter_spacing <= 0:
        draw.text((x, y), text, font=font, fill=fill)
        return
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), ch, font=font)
        cx += bbox[2] - bbox[0] + letter_spacing


def _draw_watermark_3d(draw, x, y, text, font, letter_spacing=0,
                      fill=(132, 132, 130),
                      outline=(62, 62, 60),
                      soft_shadow_steps=None,
                      bevel_highlight=(228, 228, 226),
                      bevel_shadow=(72, 72, 70)):
    """立体质感水印：柔和投影 + 深色描边 + 斜面高光/阴影，无底色"""
    if soft_shadow_steps is None:
        soft_shadow_steps = WATERMARK_SOFT_SHADOW_STEPS
    n = len(soft_shadow_steps)
    # 由远到近的投影色（远暗近浅）
    shadow_colors = [(50 + i * 22, 50 + i * 22, 48 + i * 22) for i in range(n)]
    for (dx, dy), color in zip(soft_shadow_steps, shadow_colors):
        _draw_text_layer(draw, x + dx, y + dy, text, font, color, letter_spacing)
    # 深色描边，让轮廓清晰
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                _draw_text_layer(draw, x + dx, y + dy, text, font, outline, letter_spacing)
    # 斜面阴影（右下）
    _draw_text_layer(draw, x + 1, y + 1, text, font, bevel_shadow, letter_spacing)
    # 主色
    _draw_text_layer(draw, x, y, text, font, fill, letter_spacing)
    # 斜面高光（左上）
    _draw_text_layer(draw, x - 1, y - 1, text, font, bevel_highlight, letter_spacing)


def process_image(file_path, output_folder, max_width=1280, max_size=1000 * 1024, month='', day='', counter=1):
    try:
        original_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        filename = os.path.basename(file_path)
        print(f"正在处理图片 {filename} 中，原图文件名 {filename}，大小 {original_size:.2f}M")

        with Image.open(file_path) as img:
            # 统一转为 RGB，避免 RGBA/P 等模式导致粘贴或保存异常
            if img.mode in ("RGBA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 处理 EXIF 方向
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(orientation)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass

            original_width, original_height = img.size
            if original_width > max_width:
                scale_factor = max_width / original_width
                new_width = max_width
                new_height = int(original_height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            short_side = min(img.size)
            inner_border = max(8, int(short_side * FRAME_INNER_RATIO))   # 内白边
            outer_border = max(2, int(short_side * FRAME_OUTER_RATIO))   # 外灰边
            total_border = inner_border + outer_border

            # 暖白内边 + 浅灰外边，更柔和
            frame_color = (250, 250, 248)
            outer_color = (228, 228, 225)
            inner_line_color = (215, 215, 212)

            w, h = img.width + 2 * total_border, img.height + 2 * total_border
            framed_img = Image.new('RGB', (w, h), outer_color)
            inner_rect = [outer_border, outer_border, w - 1 - outer_border, h - 1 - outer_border]
            draw_fill = ImageDraw.Draw(framed_img)
            draw_fill.rectangle(inner_rect, fill=frame_color)

            # 羽化：图片边缘与相框柔和过渡
            feather_width = max(2, int(inner_border * FRAME_FEATHER_RATIO))
            alpha_mask = _make_feather_mask(img.width, img.height, feather_width)
            img_rgba = img.convert('RGBA')
            img_rgba.putalpha(alpha_mask)
            framed_img.paste(img_rgba, (total_border, total_border))

            draw = ImageDraw.Draw(framed_img)
            # 外框线
            draw.rectangle([0, 0, w - 1, h - 1], outline=outer_color, width=outer_border)
            draw.rectangle(inner_rect, outline=inner_line_color, width=1)
            # 内缘细线（相框与图片交界，羽化后略柔和）
            draw.rectangle([
                total_border, total_border,
                w - 1 - total_border, h - 1 - total_border
            ], outline=inner_line_color, width=1)

            # 水印：立体质感（柔和投影 + 斜面高光/阴影），无底色
            font_size = max(18, int(short_side * WATERMARK_FONT_SIZE_RATIO))
            font = _load_font(font_size)
            spacing = WATERMARK_LETTER_SPACING
            if spacing <= 0:
                bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            else:
                text_h = 0
                text_w = 0
                for ch in WATERMARK_TEXT:
                    bbox = draw.textbbox((0, 0), ch, font=font)
                    text_w += bbox[2] - bbox[0]
                    text_h = max(text_h, bbox[3] - bbox[1])
                text_w += (len(WATERMARK_TEXT) - 1) * spacing
            margin = max(16, int(short_side * WATERMARK_MARGIN_RATIO))
            wx = w - text_w - total_border - margin
            wy = h - text_h - total_border - margin
            _draw_watermark_3d(
                draw, wx, wy, WATERMARK_TEXT, font,
                letter_spacing=spacing,
                fill=(128, 128, 126),
                outline=(58, 58, 56),
                bevel_highlight=(240, 240, 238),
                bevel_shadow=(68, 68, 66),
            )

            img = framed_img

            # 若源文件名以 IMG 开头则保持原文件名，否则按日期+序号命名
            if filename.upper().startswith('IMG'):
                name_without_ext = os.path.splitext(filename)[0]
                new_filename = name_without_ext + '.jpg'
            else:
                new_filename = f"{month}_{day}_{counter:03d}.jpg"
            output_path = os.path.join(output_folder, new_filename)
            img.save(output_path, format='JPEG', quality=95, optimize=True)

            # 如果图片大小超过1000KB，降低质量再保存
            quality = 90
            while os.path.getsize(output_path) > max_size and quality > 10:
                quality -= 5
                img.save(output_path, format='JPEG', quality=quality, optimize=True)

        new_size = os.path.getsize(output_path) / 1024  # 转换为KB
        print(f"处理完成，新图片名已命名为 {new_filename}，大小 {new_size:.2f}KB")
        return True

    except Exception as e:
        print(f"处理图片 {filename} 失败: {e}")
        return False

# 主函数，获取用户输入的文件夹路径
def main():
    input_folder = input("请输入要处理的图片文件夹路径: ")
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.now().strftime('%m')
    current_day = datetime.now().strftime('%d')
    output_folder = os.path.join(input_folder, current_date)

    if not os.path.isdir(input_folder):
        print("输入的路径不是一个有效的文件夹，请重试。")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取所有待处理的图片文件并按文件名排序
    image_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder)
                   if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))])

    success_count = 0
    fail_count = 0

    start_time = time.time()

    # 使用多线程处理图片
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_image, file, output_folder, 1280, 1000 * 1024, current_month, current_day, i + 1): file for i, file in enumerate(image_files)}
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1
            else:
                fail_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"所有图片已处理完毕，保存在文件夹: {output_folder}")
    print(f"处理成功 {success_count} 张，处理失败 {fail_count} 张")
    print(f"处理完成所花费的时间: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    main()
