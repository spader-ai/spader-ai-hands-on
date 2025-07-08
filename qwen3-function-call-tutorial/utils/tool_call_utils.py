import re
import json
from typing import List, Dict

def extract_tool_calls(text: str) -> List[Dict]:
    """
    从 assistant 输出中提取所有 <tool_call>...</tool_call> 中的 JSON，并去重。
    """
    pattern = r"<tool_call>\s*({.*?})\s*</tool_call>"
    matches = re.findall(pattern, text, flags=re.DOTALL)

    seen = set()
    results = []
    for match in matches:
        try:
            parsed = json.loads(match)
            sig = json.dumps(parsed, sort_keys=True)
            if sig not in seen:
                seen.add(sig)
                results.append(parsed)
        except json.JSONDecodeError:
            continue
    return results

def clean_output_strict(text: str) -> str:
    # 删除 <think> 块（包含跨多行的）
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # 防止模型输出残留孤立的 </think>
    text = re.sub(r"</think>", "", text, flags=re.IGNORECASE)

    # <tool_response> / <tool_call>
    text = re.sub(r"<tool_response>\s*</tool_response>", "", text)
    text = re.sub(r"<tool_call>\s*</tool_call>", "", text)

    # 删除尾部 markdown 代码块（空 block）
    text = re.sub(r"```(?:\s*\n)*```", "", text)

    # 删除尾部 markdown 代码块 ```json ... ```
    text = re.sub(r"```json\n.*?\n```", "", text, flags=re.DOTALL)
    # 移除 markdown 格式残留 JSON 块
    text = re.sub(r"```json\n.*?$", "", text, flags=re.DOTALL)
    # 移除末尾半截 JSON（比如以 { 开头的）
    text = re.sub(r"\n?\{[\s\S]*$", "", text)
    
    # 删除多余空白与换行
    text = re.sub(r"\n{3,}", "\n\n", text)         # 连续空行缩减
    text = re.sub(r"[ \t]+\n", "\n", text)         # 清行末空格
    text = re.sub(r"[\s\n]+$", "", text)           # 删除结尾空白

     # 最关键：去除结尾残留的 ```（即使是孤立的一行）
    lines = text.strip().splitlines()
    while lines and lines[-1].strip() == "```":
        lines.pop()
        
    return "\n".join(lines).strip()
