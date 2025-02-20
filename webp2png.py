from PIL import Image
import os

# 指定要转换的文件夹路径
input_directory = r"C:\Users\EDY\Desktop\ai"

# 遍历文件夹中的所有文件
for filename in os.listdir(input_directory):
    # 检查文件是否是 .webp 格式
    if filename.endswith('.webp'):
        # 构建完整的文件路径
        input_file = os.path.join(input_directory, filename)
        
        try:
            # 打开 .webp 图像
            img = Image.open(input_file)
            
            # 获取文件名（不带扩展名）
            file_base_name = os.path.splitext(filename)[0]
            
            # 生成新的文件名，扩展名为 .png
            output_file = os.path.join(input_directory, file_base_name + '.png')
            
            # 保存为 .png 格式
            img.save(output_file, 'PNG')
            print(f"转换完成！新文件生成在: {output_file}")
        
        except Exception as e:
            print(f"转换 {filename} 时出错: {e}")
