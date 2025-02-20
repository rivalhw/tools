import requests
from bs4 import BeautifulSoup
import os

# 输入公众号文章链接，下载图片，保存到本地文件夹
def download_images_from_wechat_article(url):
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 发送请求获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查是否请求成功

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取文章标题作为文件夹名称
        title = soup.find('h1', class_='rich_media_title')
        title_text = title.text.strip() if title else '未知标题'

        # 创建以文章标题命名的保存图片文件夹
        save_folder = os.path.join('微信文章图片', title_text)
        os.makedirs(save_folder, exist_ok=True)

        # 查找所有图片标签
        img_tags = soup.find_all('img')

        # 下载图片
        for index, img in enumerate(img_tags, 1):
            img_url = img.get('data-src') or img.get('src')
            
            if img_url and img_url.startswith('http'):
                try:
                    # 下载图片
                    img_response = requests.get(img_url, headers=headers)
                    img_response.raise_for_status()

                    # 保存图片
                    file_path = os.path.join(save_folder, f'image_{index}.jpg')
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f'成功下载图片：{file_path}')

                except Exception as img_error:
                    print(f'下载图片时出错：{img_error}')

    except Exception as e:
        print(f'获取网页内容时出错：{e}')

# 提示用户输入公众号文章地址
url = input('请输入要下载图片的公众号文章地址：')
download_images_from_wechat_article(url)
