# tools 工具包

本仓库是一组实用小工具，涵盖微信公众号/博客内容抓取、图片批处理与格式转换、文档生成及在线排版等场景。

---

## 程序文件功能说明

### 内容抓取与下载

| 文件 | 功能描述 |
|------|----------|
| **getWechatandsave2pics.py** | **微信公众号文章图片下载**：输入公众号文章链接，解析页面中的图片（`data-src`/`src`），下载并保存到本地「微信文章图片」目录下以文章标题命名的子文件夹中，图片按序号命名（如 `image_1.jpg`）。依赖：`requests`、`beautifulsoup4`。 |
| **hive.py** | **Hive 博客下载器**：根据 Hive 用户名（如 rivalhw）从 hive.blog 抓取该用户的博文列表，逐篇获取正文并保存为 Markdown 文件。支持分页、请求重试、去重（已下载记录）、可配置请求间隔与调试模式；输出包含标题、作者、发布日期、原文链接及正文，文件名自动清理非法字符。依赖：`requests`、`beautifulsoup4`。 |

### 图片批处理

| 文件 | 功能描述 |
|------|----------|
| **imagesbatch.py** | **图片批处理（带水印与相框）**：对指定文件夹内的图片进行批量处理。功能包括：按最大宽度 1280px 等比缩放、EXIF 方向校正、添加白色相框与细灰边、右下角浅灰水印「@rivalhw」、JPEG 质量 95 且单张超过 1000KB 时自动降质量。输出到「输入目录/当前日期」子文件夹；若原文件名以 `IMG` 开头则保留原文件名，否则按「月_日_序号」命名。支持多线程。依赖：`Pillow`。 |
| **imagesbatchmark.py** | **图片批处理（黑边黑字水印）**：与 `imagesbatch.py` 类似，但边框更粗（约 2%）、外框为黑色细线、水印为黑色文字「@rivalhw」；输出文件名统一为「月_日_序号.jpg」。同样支持多线程与 1000KB 体积控制。依赖：`Pillow`。 |

### 文档与格式转换

| 文件 | 功能描述 |
|------|----------|
| **save2onepage.py** | **图片文件夹转 Word 文档**：输入包含以 `image_` 开头图片的文件夹路径，按文件名中的序号排序，将每张图片插入 Word 文档，每图一页、宽度 6 英寸，页脚居中显示页码，最终保存为与文件夹同名的 `.docx` 文件到上级目录。依赖：`python-docx`、`Pillow`。 |
| **webp2png.py** | **WebP 转 PNG**：遍历指定目录（脚本内需修改 `input_directory` 变量）下所有 `.webp` 文件，转换为 `.png` 并保存在同一目录。依赖：`Pillow`。 |

### 文本处理

| 文件 | 功能描述 |
|------|----------|
| **remove_obfuscation.py** | **移除混淆内容**：输入文本文件路径，自动查找并删除文件中从 `<!-- obfuscation begins here -->` 到 `<!-- obfuscation ends here -->` 之间的所有内容（包括标记本身），支持跨行匹配，处理完成后直接覆盖原文件。自动处理 UTF-8 和 GBK 编码，显示删除的字符数统计。无需额外依赖（仅使用 Python 标准库）。 |

### 在线工具

| 文件 | 功能描述 |
|------|----------|
| **autotypesetting.html** | **在线自动排版编辑器**：单文件 HTML 页面，提供 Markdown 实时排版、一键复制、清空、新窗口预览、字数/行数统计、Curl 转 Python 请求代码等功能；使用 marked.js 渲染 Markdown，无需后端，浏览器打开即可使用。 |

### 测试与验证

| 文件 | 功能描述 |
|------|----------|
| **test_watermark.py** | **水印/批处理单元测试**：创建红色测试图，调用 `imagesbatch.process_image` 进行缩放、边框、水印等处理，检查是否成功并验证输出文件（如 `11_24_001.jpg`）是否生成，用于自动化验证批处理与水印逻辑。依赖：`Pillow`、`imagesbatch`。 |
| **verify_watermark.py** | **水印效果验证脚本**：在 `test_output` 目录下生成测试图并调用 `process_image` 处理，便于人工打开输出图片检查水印与边框效果。依赖：`Pillow`、`imagesbatch`。 |

---

## 依赖与运行

- **Python 脚本**：建议使用 Python 3.7+，按需安装：
  - `pip install requests beautifulsoup4 Pillow python-docx`
- **HTML 工具**：用浏览器直接打开 `autotypesetting.html` 即可，需联网以加载 marked.js CDN。

---

## 使用提示

- **getWechatandsave2pics.py**：运行后按提示输入公众号文章 URL。
- **hive.py**：运行后输入 Hive 用户名、是否调试、最大页数、请求间隔等。
- **imagesbatch.py / imagesbatchmark.py**：运行后输入待处理图片所在文件夹路径。
- **save2onepage.py**：适用于由 `getWechatandsave2pics.py` 等生成的 `image_1.jpg`、`image_2.jpg` 等命名规则的文件夹。
- **webp2png.py**：使用前在脚本中修改 `input_directory` 为实际要转换的目录路径。
- **remove_obfuscation.py**：运行后输入要处理的文件路径（支持相对路径和绝对路径），程序会自动删除混淆标记之间的内容并保存。
