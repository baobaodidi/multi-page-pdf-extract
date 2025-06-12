# PDF字段抽取工具 - Doubao版本

这是使用 **Doubao-1.5-vision-pro** 模型的PDF字段抽取工具。

## 主要特性

- 🤖 使用字节跳动的 Doubao-1.5-vision-pro 视觉大模型
- 📄 支持多页PDF文档处理
- 🎯 精确提取指定字段信息
- 📊 支持多种输出格式（JSON、Excel、Markdown）
- 🔧 可自定义提取字段

## 环境配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 设置API密钥
在项目根目录创建 `.env` 文件，添加以下内容：
```
ARK_API_KEY=your_doubao_api_key_here
```

> **注意**: Doubao模型使用 `ARK_API_KEY` 环境变量，不同于其他模型的API密钥名称。

## 使用方法

### 基本使用
```bash
python app_doubao.py
```

### 自定义配置
在 `app_doubao.py` 文件中修改以下参数：

```python
# 修改PDF文件路径
PDF_FILE = "your_pdf_file.pdf"

# 修改要提取的字段
FIELDS = ["字段1", "字段2", "字段3"]

# 调整图片分辨率（影响识别精度和处理速度）
DPI = 300
```

## 输出文件

程序运行后会生成以下文件：
- `result_doubao.json` - JSON格式结果
- `result_doubao.xlsx` - Excel格式结果  
- `result_doubao.md` - Markdown格式结果

## 模型特点

**Doubao-1.5-vision-pro** 模型具有以下优势：
- 🎯 高精度的文档理解能力
- 🚀 快速的处理速度
- 🌐 对中文文档的优秀支持
- 💡 智能的字段识别和提取

## 与其他版本的区别

| 特性 | Doubao版本 | Qwen版本 |
|------|------------|----------|
| 模型 | Doubao-1.5-vision-pro | qwen-vl-max |
| API密钥 | ARK_API_KEY | DASHSCOPE_API_KEY |
| API端点 | ark.cn-beijing.volces.com | dashscope.aliyuncs.com |
| 中文支持 | 优秀 | 优秀 |
| 处理速度 | 快 | 快 |

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误：ARK_API_KEY 环境变量未设置
   ```
   解决：检查 `.env` 文件中的 `ARK_API_KEY` 设置

2. **PDF文件不存在**
   ```
   错误：PDF文件 'xxx.pdf' 不存在
   ```
   解决：确认PDF文件路径正确，文件存在

3. **模型调用失败**
   ```
   调用 Doubao 模型时出错
   ```
   解决：检查网络连接和API密钥有效性

### 调试技巧

- 程序会显示API密钥的前10个字符用于验证
- 详细的处理进度信息会实时显示
- JSON解析失败时会显示原始返回内容

## 性能优化建议

1. **调整DPI**: 降低DPI可以加快处理速度，但可能影响识别精度
2. **字段优化**: 减少不必要的字段可以提高处理效率
3. **批量处理**: 对于大量文档，建议分批处理

## 技术支持

如果遇到问题，请检查：
1. API密钥是否正确设置
2. 网络连接是否正常
3. PDF文件是否可正常打开
4. 依赖包是否正确安装

---

*使用 Doubao-1.5-vision-pro 模型，体验更智能的文档处理！* 