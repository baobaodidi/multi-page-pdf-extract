"""
app.py
抽取多页 PDF 指定字段（示例：申请人, 部门, 金额, 日期）
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
MODEL     = "qwen-vl-max"
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

def call_qwen_vl_max(image_blocks: List[Dict], fields: List[str]) -> str:
    """一次调用 Qwen-VL-Max，返回模型原始 JSON 字符串"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
    
    print(f"使用 API Key: {api_key[:10]}...")  # 只显示前10个字符用于调试
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 中国站地址
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

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": [system_prompt]},
            {"role": "user",   "content": image_blocks + [user_prompt]}
        ],
        temperature=0
    )
    return resp.choices[0].message.content.strip()

# ---------- 2. 主流程 ----------
def extract_pdf_fields(pdf_path: str, fields: List[str]) -> pd.DataFrame:
    # 2-1 PDF ⇒ PNG
    png_paths = pdf_to_png_list(pdf_path, dpi=DPI)
    image_blocks = [img_to_openai_block(p) for p in png_paths]

    # 2-2 调用大模型
    raw_json = call_qwen_vl_max(image_blocks, fields)

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
    
    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"模型返回非合法 JSON：{raw_json}") from e

    # 2-4 合并 / 清洗
    df = pd.DataFrame(data)
    # df.insert(0, "page", range(1, len(df) + 1))  # 保留页码（已注释掉）
    return df

if __name__ == "__main__":
    df_result = extract_pdf_fields(PDF_FILE, FIELDS)

    # --- 输出 ---
    print("\n" + "="*60)
    print("📋 PDF 字段抽取结果 (JSON 格式)")
    print("="*60)
    
    # 显示 JSON 格式结果
    import json
    result_json = df_result.to_dict('records')
    print(json.dumps(result_json, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60)
    print(f"📊 共处理 {len(df_result)} 条记录")
    print("="*60)
    
    # 保存文件
    df_result.to_json("result.json", orient="records", force_ascii=False, indent=2)
    df_result.to_excel("result.xlsx", index=False)
    print("✔️ 已保存 result.json / result.xlsx")
    
    # 同时保存 Markdown 格式文件
    try:
        with open("result.md", "w", encoding="utf-8") as f:
            f.write("# PDF 字段抽取结果\n\n")
            f.write(df_result.to_markdown(index=False, tablefmt="pipe"))
            f.write(f"\n\n**共处理 {len(df_result)} 条记录**")
        print("✔️ 已保存 result.md (Markdown 格式)")
    except Exception:
        pass
