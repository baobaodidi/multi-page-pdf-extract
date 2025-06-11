# PDF 字段抽取工具

基于 Qwen-VL-Max 大模型的多页 PDF 文档字段抽取工具，支持自定义字段抽取和多种格式输出。

## 功能特点

- 🔍 **多页 PDF 处理**：自动处理多页 PDF 文档
- 🤖 **AI 驱动**：使用阿里云 Qwen-VL-Max 视觉语言模型
- 📊 **多格式输出**：支持 JSON、Excel、Markdown 格式
- ⚙️ **灵活配置**：可自定义抽取字段和输出格式
- 🔒 **环境变量管理**：使用 .env 文件安全管理 API 密钥

## 安装和使用

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd multi_page_pdf_extract

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

创建 `.env` 文件并添加您的 Dashscope API 密钥：

```bash
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 运行程序

```bash
source venv/bin/activate
python app.py
```

## 配置说明

在 `app.py` 中可以调整以下参数：

- `PDF_FILE`: 要处理的 PDF 文件路径
- `FIELDS`: 要抽取的字段列表
- `DPI`: 图像分辨率（影响识别精度和处理速度）

## 输出文件

程序会生成以下文件：

- `result.json`: JSON 格式结果
- `result.xlsx`: Excel 格式结果  
- `result.md`: Markdown 格式结果

## 依赖包

- `openai`: AI 模型调用
- `pymupdf`: PDF 处理
- `pandas`: 数据处理
- `pillow`: 图像处理
- `python-dotenv`: 环境变量管理
- `openpyxl`: Excel 文件导出
- `tabulate`: Markdown 表格格式化

## 许可证

MIT License

## 作者

baobaodidi 