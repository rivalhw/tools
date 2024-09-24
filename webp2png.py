from PIL import Image
import os

# 用户输入要转换的图片文件路径
input_file = input("请输入 .webp 图片的路径: ")

# 检查文件是否是 .webp 格式
if input_file.endswith('.webp') and os.path.exists(input_file):
    # 打开 .webp 图像
    img = Image.open(input_file)
    
    # 获取当前文件夹和文件名
    file_directory, file_name = os.path.split(input_file)
    
    # 获取文件名（不带扩展名）和扩展名
    file_base_name = os.path.splitext(file_name)[0]
    
    # 生成新的文件名，扩展名为 .png
    output_file = os.path.join(file_directory, file_base_name + '.png')
    
    # 保存为 .png 格式
    img.save(output_file, 'PNG')
    print(f"转换完成！新文件生成在: {output_file}")
else:
    print("输入的文件不是 .webp 格式或文件不存在。")
