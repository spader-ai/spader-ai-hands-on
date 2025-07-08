# inference_server_vllm.py
from fastapi import FastAPI
from pydantic import BaseModel
from tool_schemas import tool_schemas, tool_map
from utils.tool_call_utils import extract_tool_calls, clean_output_strict
from utils.formatters import format_function_response

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import asyncio
import time


app = FastAPI()

# 加载 tokenizer（vLLM 不支持 transformers generate，但 tokenizer 仍需手动管理 prompt）
model_path = "../Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
tokenizer.pad_token_id = tokenizer.eos_token_id

# 初始化 vLLM
llm = LLM(model=model_path, dtype="float16", trust_remote_code=True)

class QueryInput(BaseModel):
    user_query: str

def build_prompt(messages, tool_call=False):
    return tokenizer.apply_chat_template(
        messages,
        tools=tool_schemas if tool_call else [],
        add_generation_prompt=True,
        tokenize=False,
        enable_thinking=False,
        output_tool_calls=tool_call
    )

@app.post("/chat")
async def chat(input_data: QueryInput):
    # 初始化对话上下文
    messages = [{
        "role": "system",
        "content": (
            "你是一个文件系统助手。用户提出问题后，请判断是否需要调用文件/目录相关的工具函数。"
            "你只能调用文件系统相关的工具函数（如读写文件、创建/删除/列出目录、移动、搜索、获取元数据等）。"
            "不要冗余调用工具，也不要试图补充用户没问的内容。"
        )
    }, {
        "role": "user",
        "content": input_data.user_query
    }]

    prompt = build_prompt(messages, tool_call=True)
    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=512,
        stop=["<|im_end|>"]
    )

    # 第一步：vLLM 推理 + 工具调用分析
    outputs = llm.generate(prompt, sampling_params)
    generated_text = outputs[0].outputs[0].text
    tool_calls = extract_tool_calls(generated_text)

    # 如果不需要工具，直接返回
    if not tool_calls:
        return {"response": clean_output_strict(generated_text)}

    # 否则调用工具
    tool_messages = []
    for call in tool_calls:
        name = call["name"]
        args = call.get("arguments", {})
        func = tool_map.get(name)
        if func:
            response = func(**args)
            response_text = format_function_response(name, response)
        else:
            response_text = f"工具 {name} 不存在。"
        tool_messages.append({"role": "tool", "name": name, "content": response_text})

    # 第二轮输入：总结工具结果
    messages.insert(0, {
        "role": "system",
        "content": "你已经获得工具调用结果，请整理为自然语言回复用户。不要输出代码块。"
    })
    messages += [{"role": "assistant", "tool_calls": tool_calls}] + tool_messages

    followup_prompt = build_prompt(messages, tool_call=False)
    outputs = llm.generate(followup_prompt, sampling_params)
    final_text = outputs[0].outputs[0].text
    return {"response": clean_output_strict(final_text)}
