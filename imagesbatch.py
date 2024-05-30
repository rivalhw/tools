import os
from PIL import Image, ExifTags
from datetime import datetime
import concurrent.futures
import time

# 定义处理图片的函数
def process_image(file_path, output_folder, max_width=1280, max_size=1000 * 1024, month='', day='', counter=1):
    try:
        original_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        filename = os.path.basename(file_path)
        print(f"正在处理图片 {filename} 中，原图文件名 {filename}，大小 {original_size:.2f}M")

        with Image.open(file_path) as img:
            # 处理EXIF元数据，确保图像方向正确
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
                # 如果没有EXIF信息或无法读取方向信息，忽略处理
                pass

            # 获取原始尺寸
            original_width, original_height = img.size
            # 如果宽度超过最大宽度，则按比例缩放
            if original_width > max_width:
                scale_factor = max_width / original_width
                new_width = max_width
                new_height = int(original_height * scale_factor)
                img = img.resize((new_width, new_height), Image.LANCZOS)

            # 生成新的文件名
            new_filename = f"{month}_{day}_{counter:03d}.jpg"
            # 保存图片到输出文件夹，并控制文件大小
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
    # 获取当前日期，并格式化为字符串
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.now().strftime('%m')
    current_day = datetime.now().strftime('%d')
    output_folder = os.path.join(input_folder, current_date)

    if not os.path.isdir(input_folder):
        print("输入的路径不是一个有效的文件夹，请重试。")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取所有待处理的图片文件
    image_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder)
                   if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]

    success_count = 0
    fail_count = 0

    # 记录开始时间
    start_time = time.time()

    # 使用多线程处理图片
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_image, file, output_folder, 1280, 1000 * 1024, current_month, current_day, i + 1): file for i, file in enumerate(image_files)}
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1
            else:
                fail_count += 1

    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"所有图片已处理完毕，保存在文件夹: {output_folder}")
    print(f"处理成功 {success_count} 张，处理失败 {fail_count} 张")
    print(f"处理完成所花费的时间: {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    main()
