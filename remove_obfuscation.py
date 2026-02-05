import os
import re

def remove_obfuscation_content(file_path):
    """
    移除文件中从 <!-- obfuscation begins here --> 到 <!-- obfuscation ends here --> 之间的内容
    
    Args:
        file_path: 要处理的文件路径
    
    Returns:
        bool: 处理是否成功
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 错误：文件不存在 - {file_path}")
            return False
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_length = len(content)
        
        # 使用正则表达式匹配并删除从 <!-- obfuscation begins here --> 到 <!-- obfuscation ends here --> 之间的内容
        # re.DOTALL 标志使 . 匹配包括换行符在内的所有字符
        pattern = r'<!--\s*obfuscation\s+begins\s+here\s*-->.*?<!--\s*obfuscation\s+ends\s+here\s*-->'
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        removed_length = original_length - len(cleaned_content)
        
        # 如果内容有变化，保存文件
        if removed_length > 0:
            # 保存处理后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✓ 处理成功！")
            print(f"  原文件大小: {original_length} 字符")
            print(f"  删除内容: {removed_length} 字符")
            print(f"  处理后大小: {len(cleaned_content)} 字符")
            print(f"  文件已保存: {file_path}")
            return True
        else:
            print(f"ℹ️ 文件中未找到需要删除的内容")
            return True
    
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
            
            original_length = len(content)
            pattern = r'<!--\s*obfuscation\s+begins\s+here\s*-->.*?<!--\s*obfuscation\s+ends\s+here\s*-->'
            cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            
            removed_length = original_length - len(cleaned_content)
            
            if removed_length > 0:
                with open(file_path, 'w', encoding='gbk') as f:
                    f.write(cleaned_content)
                
                print(f"✓ 处理成功！")
                print(f"  原文件大小: {original_length} 字符")
                print(f"  删除内容: {removed_length} 字符")
                print(f"  处理后大小: {len(cleaned_content)} 字符")
                print(f"  文件已保存: {file_path}")
                return True
            else:
                print(f"ℹ️ 文件中未找到需要删除的内容")
                return True
        
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            return False
    
    except Exception as e:
        print(f"❌ 处理文件时出错: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("📝 文本混淆内容移除工具")
    print("=" * 60)
    print("功能：移除文件中从 <!-- obfuscation begins here --> 到 <!-- obfuscation ends here --> 之间的内容")
    print("-" * 60)
    
    # 获取用户输入的文件路径
    file_path = input("\n请输入要处理的文件路径（支持相对路径和绝对路径）: ").strip()
    
    if not file_path:
        print("❌ 错误：文件路径不能为空")
        return
    
    # 移除路径两端的引号（如果用户复制粘贴时带引号）
    file_path = file_path.strip('"').strip("'")
    
    # 处理文件
    success = remove_obfuscation_content(file_path)
    
    if success:
        print("\n✨ 处理完成！")
    else:
        print("\n❌ 处理失败，请检查文件路径和权限")


if __name__ == "__main__":
    main()
