"""
app_doubao.py
使用 Doubao-1.5-vision-pro 模型抽取多页 PDF 指定字段
"""

import os, base64, fitz, json
from pathlib import Path
from typing import List, Dict

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ---------- 0. 参数区 ----------
PDF_FILE = "CV00111931S提单.pdf"            # ← 用户上传的 PDF 路径
FIELDS    = ["Place of Receipt", "Port of Discharge", "Port of Loading", "Place of Delivery", "Gross Weight","Measurement","Invoice No.","Invoice Date","Customer Name","Telephone","Fax","E-Mail","Customer Code"]  # ← 你要抽取的字段（可改）
MODEL     = "Doubao-1.5-vision-pro"         # 使用 Doubao-1.5-vision-pro 模型
DPI       = 300                              # 分辨率（影响识别率&token 消耗）

# ---------- 1. 工具函数 ----------
def pdf_to_png_list(pdf_path: str, dpi: int = 300) -> List[Path]:
    """把多页 PDF 转成临时 PNG，返回路径列表"""
    doc = fitz.open(pdf_path)
    out_paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        out = Path(f"/tmp/page_{i+1}.png")
        pix.save(out)
        out_paths.append(out)
    return out_paths

def img_to_openai_block(img_path: Path) -> Dict:
    """把本地图片转成 OpenAI image block（base64 data URI）"""
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{b64}"}
    }

def call_doubao_vision_pro(image_blocks: List[Dict], fields: List[str]) -> str:
    """调用 Doubao-1.5-vision-pro 模型，返回模型原始 JSON 字符串"""
    api_key = os.getenv("ARK_API_KEY")  # Doubao 使用 ARK_API_KEY
    if not api_key:
        raise ValueError("ARK_API_KEY 环境变量未设置，请设置豆包大模型的 API Key")
    
    print(f"使用 Doubao API Key: {api_key[:10]}...")  # 只显示前10个字符用于调试
    
    # 豆包大模型的 API 端点
    client = OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"  # 豆包大模型 API 地址
    )

    system_prompt = {
        "type": "text",
        "text": (
            "你是文档信息抽取引擎，只输出 JSON 数组，多页对应一个对象，"
            f"字段包含 {fields}，其余内容不要出现。"
        )
    }
    
    user_prompt = {
        "type": "text",
        "text": "请从以下多页扫描件中提取指定字段。"
    }

    try:
        # 使用豆包大模型的预置模型ID
        resp = client.chat.completions.create(
            model="doubao-1.5-vision-pro-250328",  # 豆包1.5视觉专业版的预置模型ID
            messages=[
                {"role": "system", "content": system_prompt["text"]},
                {"role": "user", "content": image_blocks + [user_prompt]}
            ],
            temperature=0.1,  # 降低温度以获得更稳定的结果
            max_tokens=4000   # 设置最大token数
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"调用 Doubao 模型时出错: {e}")
        print(f"错误详情: {type(e).__name__}: {str(e)}")
        raise

# ---------- 2. 主流程 ----------
def extract_pdf_fields(pdf_path: str, fields: List[str]) -> pd.DataFrame:
    """从PDF中提取指定字段"""
    print(f"开始处理PDF文件: {pdf_path}")
    print(f"使用模型: {MODEL}")
    print(f"提取字段: {fields}")
    
    # 2-1 PDF ⇒ PNG
    print("正在将PDF转换为图片...")
    png_paths = pdf_to_png_list(pdf_path, dpi=DPI)
    print(f"已转换 {len(png_paths)} 页")
    
    image_blocks = [img_to_openai_block(p) for p in png_paths]

    # 2-2 调用大模型
    print("正在调用 Doubao-1.5-vision-pro 模型进行字段提取...")
    raw_json = call_doubao_vision_pro(image_blocks, fields)
    print("模型调用完成")

    # 2-3 解析 JSON 字符串
    # 去掉可能的 markdown 代码块包装
    clean_json = raw_json.strip()
    if clean_json.startswith("```json"):
        clean_json = clean_json[7:]  # 去掉 ```json
    if clean_json.startswith("```"):
        clean_json = clean_json[3:]   # 去掉 ```
    if clean_json.endswith("```"):
        clean_json = clean_json[:-3]  # 去掉结尾的 ```
    clean_json = clean_json.strip()
    
    print("正在解析模型返回的JSON数据...")
    try:
        data = json.loads(clean_json)
        if not isinstance(data, list):
            # 如果返回的不是数组，尝试包装成数组
            data = [data]
    except json.JSONDecodeError as e:
        print(f"JSON解析失败，原始返回内容：\n{raw_json}")
        raise ValueError(f"模型返回非合法 JSON：{raw_json}") from e

    # 2-4 转换为DataFrame
    df = pd.DataFrame(data)
    
    # 清理临时文件
    for png_path in png_paths:
        try:
            png_path.unlink()
        except:
            pass
    
    return df

def main():
    """主函数"""
    try:
        # 检查PDF文件是否存在
        if not os.path.exists(PDF_FILE):
            print(f"错误：PDF文件 '{PDF_FILE}' 不存在")
            return
        
        # 提取字段
        df_result = extract_pdf_fields(PDF_FILE, FIELDS)

        # --- 输出结果 ---
        print("\n" + "="*60)
        print("📋 PDF 字段抽取结果 (使用 Doubao-1.5-vision-pro)")
        print("="*60)
        
        # 显示 JSON 格式结果
        result_json = df_result.to_dict('records')
        print(json.dumps(result_json, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print(f"📊 共处理 {len(df_result)} 条记录")
        print("="*60)
        
        # 保存文件
        output_files = {
            "result_doubao.json": lambda: df_result.to_json("result_doubao.json", orient="records", force_ascii=False, indent=2),
            "result_doubao.xlsx": lambda: df_result.to_excel("result_doubao.xlsx", index=False)
        }
        
        for filename, save_func in output_files.items():
            try:
                save_func()
                print(f"✔️ 已保存 {filename}")
            except Exception as e:
                print(f"❌ 保存 {filename} 失败: {e}")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    main() 