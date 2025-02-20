import requests
from bs4 import BeautifulSoup
import os
import time

# 未完成
def download_hive_blog_posts(username):
    # 构建博客列表基础URL
    base_url = f"https://hive.blog/@{username}/posts"
    
    # 创建保存博文的文件夹
    save_folder = f"hive_blog_{username}"
    os.makedirs(save_folder, exist_ok=True)
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 跟踪已下载文章数量
    downloaded_count = 0
    
    # 分页加载文章
    page = 1
    while True:
        try:
            # 发送请求获取网页内容
            url = f"{base_url}?page={page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章列表
            articles = soup.find_all('h2', class_='articles__h2 entry-title')
            
            # 如果没有更多文章，结束循环
            if not articles:
                break
            
            # 遍历每篇文章
            for article in articles:
                # 获取文章标题
                title_elem = article.find('a')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                article_url = f"https://hive.blog{title_elem['href']}"
                
                # 获取文章详细内容
                article_response = requests.get(article_url, headers=headers)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # 查找文章内容
                content_elem = article_soup.find('div', class_='markdown-rendered')
                if not content_elem:
                    continue
                
                content = content_elem.text.strip()
                
                # 使用当前时间戳作为文件名前缀
                timestamp = str(int(time.time()))
                
                # 保存文章为Markdown文件
                filename = os.path.join(save_folder, f"{timestamp}_{title}.md")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n{content}")
                
                # 提示用户已下载文章
                downloaded_count += 1
                print(f"已下载文章：{title} (第 {downloaded_count} 篇)")
                
                # 避免频繁请求
                time.sleep(1)
            
            # 翻页
            page += 1
        
        except Exception as e:
            print(f"下载过程中出错：{e}")
            break
    
    print(f"全部文章下载完成，共下载 {downloaded_count} 篇文章")

# 使用示例
if __name__ == "__main__":
    username = input("请输入Hive博主的用户名（例如 rivalhw）：")
    download_hive_blog_posts(username)
