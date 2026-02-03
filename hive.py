import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re
from datetime import datetime
from urllib.parse import urlparse

class HiveBlogDownloader:
    """Hive博客下载器 - 功能完整版"""
    
    def __init__(self, username, save_folder=None, max_retries=3, timeout=10, delay=1.5, debug=False):
        """
        初始化下载器
        
        Args:
            username: Hive用户名
            save_folder: 保存文件夹，默认为hive_blog_{username}
            max_retries: 最大重试次数
            timeout: 请求超时（秒）
            delay: 请求间隔（秒），避免频繁请求
            debug: 调试模式，显示详细信息
        """
        self.username = username
        self.base_url = f"https://hive.blog/@{username}/posts"
        self.save_folder = save_folder or f"hive_blog_{username}"
        self.max_retries = max_retries
        self.timeout = timeout
        self.delay = delay
        self.debug = debug
        self.downloaded_count = 0
        self.failed_count = 0
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 创建保存文件夹
        os.makedirs(self.save_folder, exist_ok=True)
        
        # 创建日志文件
        self.log_file = os.path.join(self.save_folder, 'download_log.json')
        self.download_record = self._load_download_record()
    
    def _load_download_record(self):
        """加载已下载记录，避免重复下载"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'downloaded': [], 'failed': [], 'total_count': 0}
        return {'downloaded': [], 'failed': [], 'total_count': 0}
    
    def _save_download_record(self):
        """保存下载记录"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存记录失败: {e}")
    
    def _sanitize_filename(self, title):
        """清理文件名，移除非法字符"""
        # 移除特殊字符
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # 限制长度
        title = title[:100]
        return title.strip()
    
    def _request_with_retry(self, url):
        """带重试机制的HTTP请求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                print(f"⏱️ 请求超时 (第 {attempt+1}/{self.max_retries} 次)")
            except requests.exceptions.ConnectionError:
                print(f"🔌 连接错误 (第 {attempt+1}/{self.max_retries} 次)")
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求失败 (第 {attempt+1}/{self.max_retries} 次): {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
        
        return None
    
    def _extract_article_metadata(self, article_elem):
        """从文章元素中提取元数据"""
        try:
            title_elem = article_elem.find('a')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            href = title_elem.get('href', '')
            
            if not href:
                return None
            
            return {
                'title': title,
                'url': f"https://hive.blog{href}",
                'href': href
            }
        except Exception as e:
            print(f"❌ 提取元数据失败: {e}")
            return None
    
    def _extract_article_content(self, article_soup, title, article_url):
        """从文章页面中提取内容和元信息"""
        try:
            # 尝试多个可能的内容选择器
            content_elem = None
            content_selectors = [
                ('div', {'class': 'markdown-rendered'}),
                ('div', {'class': 'entry-content'}),
                ('article', {}),
                ('div', {'class': 'post-content'}),
                ('div', {'class': 'article-content'}),
                ('main', {}),
            ]
            
            for tag, attrs in content_selectors:
                if attrs:
                    content_elem = article_soup.find(tag, attrs)
                else:
                    content_elem = article_soup.find(tag)
                
                if content_elem:
                    if self.debug:
                        print(f"  ℹ️ 找到内容元素: {tag} {attrs}")
                    break
            
            # 如果都没找到，尝试获取整个页面的文本
            if not content_elem:
                if self.debug:
                    print(f"  ⚠️ 未找到标准内容元素，尝试备选方案...")
                
                # 移除脚本和样式
                for script in article_soup(['script', 'style', 'nav', 'header', 'footer']):
                    script.decompose()
                
                # 尝试从body中提取
                body = article_soup.find('body')
                if body:
                    content_elem = body
                else:
                    if self.debug:
                        print(f"  ❌ 无法找到任何内容")
                    return None
            
            # 提取文本内容
            if content_elem:
                # 移除脚本和样式
                for script in content_elem(['script', 'style', 'nav', 'header', 'footer']):
                    script.decompose()
                
                # 使用改进的文本提取方法
                content = self._extract_structured_text(content_elem)
                
                if not content or len(content) < 50:  # 内容太短可能是错误
                    if self.debug:
                        print(f"  ⚠️ 内容为空或过短 ({len(content)} 字符)")
                    return None
                
                if self.debug:
                    print(f"  ✓ 成功提取内容 ({len(content)} 字符)")
            else:
                return None
            
            # 提取发布日期
            date_elem = article_soup.find('span', class_='published')
            if not date_elem:
                date_elem = article_soup.find('time')
            publish_date = date_elem.text.strip() if date_elem else '未知'
            
            # 提取作者
            author_elem = article_soup.find('a', class_='author-name')
            if not author_elem:
                author_elem = article_soup.find('span', class_='author')
            author = author_elem.text.strip() if author_elem else self.username
            
            return {
                'title': title,
                'content': content,
                'url': article_url,
                'author': author,
                'publish_date': publish_date,
                'download_date': datetime.now().isoformat()
            }
        except Exception as e:
            if self.debug:
                print(f"  ⚠️ 提取异常: {str(e)[:100]}")
            return None
    
    def _extract_structured_text(self, elem):
        """提取保留结构的文本内容"""
        content = elem.get_text(separator='\n').strip()
        
        # 清理多余空行
        lines = []
        prev_empty = False
        for line in content.split('\n'):
            line = line.strip()
            if line:
                lines.append(line)
                prev_empty = False
            elif not prev_empty and lines:  # 保留单个空行分隔
                lines.append('')
                prev_empty = True
        
        content = '\n'.join(lines)
        
        # 限制长度
        if len(content) > 15000:
            content = content[:15000] + '\n\n[内容已截断...]'
        
        return content
    
    def diagnose_page(self, url):
        """诊断页面结构，帮助调试"""
        print(f"\n🔍 诊断页面: {url}")
        try:
            response = self._request_with_retry(url)
            if not response:
                print("❌ 无法获取页面")
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"✓ 页面大小: {len(response.text)} 字节")
            print(f"✓ 页面标题: {soup.title.string if soup.title else '无标题'}")
            
            # 查找所有可能的内容容器
            print("\n📋 可能的内容容器:")
            containers = [
                ('div.markdown-rendered', soup.find('div', class_='markdown-rendered')),
                ('div.entry-content', soup.find('div', class_='entry-content')),
                ('article', soup.find('article')),
                ('div.post-content', soup.find('div', class_='post-content')),
                ('main', soup.find('main')),
            ]
            
            for selector, elem in containers:
                if elem:
                    text_len = len(elem.get_text())
                    print(f"  ✓ {selector}: {text_len} 字符")
                else:
                    print(f"  ✗ {selector}: 未找到")
            
        except Exception as e:
            print(f"❌ 诊断失败: {e}")
    
    def _save_article(self, article_data):
        """保存文章到文件"""
        try:
            title_clean = self._sanitize_filename(article_data['title'])
            filename = os.path.join(self.save_folder, f"{title_clean}.md")
            
            # 如果文件已存在，添加时间戳
            if os.path.exists(filename):
                timestamp = int(time.time())
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{timestamp}{ext}"
            
            # 格式化并保存内容
            formatted_content = self._format_article_content(article_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return False
    
    def _format_article_content(self, article_data):
        """格式化文章内容为美观的Markdown"""
        title = article_data['title']
        author = article_data['author']
        publish_date = article_data['publish_date']
        download_date = article_data['download_date']
        url = article_data['url']
        content = article_data['content']
        
        # 构建格式化的Markdown文档
        formatted = f"""# {title}

---

**基本信息**

| 字段 | 内容 |
|------|------|
| 作者 | {author} |
| 发布日期 | {publish_date} |
| 原文链接 | [{url}]({url}) |

---

## 文章正文

{content}

---

*本文档由Hive博客下载工具自动生成 | 下载时间: {download_date}*
""".strip()
        
        return formatted
    
    def download(self, max_pages=None):
        """
        下载博文
        
        Args:
            max_pages: 最多下载页数，None表示下载所有
        """
        print(f"\n📚 开始下载 {self.username} 的Hive博客文章...")
        print(f"💾 保存文件夹: {os.path.abspath(self.save_folder)}")
        print("-" * 60)
        
        start_time = time.time()
        page = 1
        total_attempted = 0
        
        while max_pages is None or page <= max_pages:
            try:
                url = f"{self.base_url}?page={page}"
                print(f"🔄 正在获取第 {page} 页...")
                
                response = self._request_with_retry(url)
                if not response:
                    print(f"⚠️ 第 {page} 页获取失败，停止下载")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找文章列表
                articles = soup.find_all('h2', class_='articles__h2 entry-title')
                
                if not articles:
                    print(f"ℹ️ 第 {page} 页没有文章，下载完成")
                    break
                
                print(f"📄 本页找到 {len(articles)} 篇文章")
                
                # 遍历每篇文章
                for idx, article in enumerate(articles, 1):
                    article_meta = self._extract_article_metadata(article)
                    if not article_meta:
                        continue
                    
                    title = article_meta['title']
                    article_url = article_meta['url']
                    
                    # 检查是否已下载
                    if article_url in self.download_record['downloaded']:
                        print(f"⏭️ 跳过已下载: {title}")
                        continue
                    
                    # 获取文章详细内容
                    article_response = self._request_with_retry(article_url)
                    if not article_response:
                        self.failed_count += 1
                        self.download_record['failed'].append({'title': title, 'url': article_url})
                        print(f"❌ 获取失败: {title}")
                        continue
                    
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    article_data = self._extract_article_content(article_soup, title, article_url)
                    
                    if not article_data:
                        self.failed_count += 1
                        self.download_record['failed'].append({'title': title, 'url': article_url})
                        print(f"❌ 提取内容失败: {title}")
                        continue
                    
                    # 保存文章
                    if self._save_article(article_data):
                        self.downloaded_count += 1
                        self.download_record['downloaded'].append(article_url)
                        print(f"✓ 已下载 ({self.downloaded_count}): {title}")
                    else:
                        self.failed_count += 1
                        self.download_record['failed'].append({'title': title, 'url': article_url})
                    
                    total_attempted += 1
                    time.sleep(self.delay)
                
                page += 1
                time.sleep(self.delay)
            
            except KeyboardInterrupt:
                print("\n⚠️ 用户中断下载")
                break
            except Exception as e:
                print(f"❌ 下载过程出错: {e}")
                break
        
        # 保存记录
        self.download_record['total_count'] = self.downloaded_count
        self._save_download_record()
        
        # 打印统计信息
        elapsed_time = time.time() - start_time
        print("-" * 60)
        print(f"✨ 下载完成！")
        print(f"✓ 成功下载: {self.downloaded_count} 篇")
        print(f"❌ 失败: {self.failed_count} 篇")
        print(f"⏱️ 耗时: {elapsed_time:.2f} 秒")
        print(f"📁 文件保存在: {os.path.abspath(self.save_folder)}")
        print()


def main():
    """主函数"""
    print("=" * 60)
    print("🐝 Hive博客下载工具 v2.1")
    print("=" * 60)
    
    username = input("\n请输入Hive博主的用户名 (例如: rivalhw): ").strip()
    
    if not username:
        print("❌ 用户名不能为空")
        return
    
    # 询问是否使用调试模式
    debug_mode = input("启用调试模式? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 如果开启调试模式，先诊断一个页面
    if debug_mode:
        downloader = HiveBlogDownloader(username, debug=True)
        print("\n首先诊断一个示例页面...")
        downloader.diagnose_page(f"https://hive.blog/@{username}/posts")
    
    # 询问其他选项
    max_pages_input = input("请输入最多下载的页数 (按Enter下载所有): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else None
    
    delay_input = input("请输入请求间隔（秒，默认1.5）: ").strip()
    delay = float(delay_input) if delay_input else 1.5
    
    # 创建下载器并开始下载
    downloader = HiveBlogDownloader(username, delay=delay, debug=debug_mode)
    downloader.download(max_pages=max_pages)


if __name__ == "__main__":
    main()
