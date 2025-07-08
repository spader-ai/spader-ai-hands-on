import torch
import json
import re
import argparse
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from utils.tool_call_utils import extract_tool_calls, clean_output_strict
from utils.formatters import format_function_response
from tool_schemas import tool_schemas, tool_map
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, sys
sys.path.append(os.path.dirname(__file__))


class FileSystemAgentSession:
    def __init__(self, model, tokenizer, enable_thinking=False):
        self.model = model
        self.tokenizer = tokenizer
        self.enable_thinking = enable_thinking
        self.max_new_tokens = 512
        self.messages = []

    def run_user_query(self, user_query: str):
        self.messages = [{
            "role": "system",
            "content": (
                "你是一个文件系统助手。用户提出问题后，请判断是否需要调用文件/目录相关的工具函数。"
                "你只能调用文件系统相关的工具函数（如读写文件、创建/删除/列出目录、移动、搜索、获取元数据等）。"
                "不要冗余调用工具，也不要试图补充用户没问的内容。"
            )
        }] + self.messages
        self.messages.append({"role": "user", "content": user_query})
        input_ids = self.tokenizer.apply_chat_template(
            self.messages,
            tools=tool_schemas,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            enable_thinking=self.enable_thinking
        ).to(self.model.device)

        attention_mask = (input_ids != self.tokenizer.pad_token_id).long()  # 注意 pad_token_id 要设置对
        self.model.generation_config = GenerationConfig(
            do_sample=False,
            top_k=None,
            top_p=None,
            temperature=None,
            num_beams=1,
            tool_choice="auto",
            repetition_penalty=1.2,  # 可尝试 1.1~1.5，避免模式重复
            max_new_tokens=512,
            
        )
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )

        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        #output_text = clean_output_strict(output_text)
        tool_calls = extract_tool_calls(output_text)
        #print("tool_calls will be called: ", tool_calls)
        self.messages.append({"role": "assistant", "tool_calls": tool_calls})
        #print("self messges after user query: ", self.messages)
        return output_text, tool_calls

    def call_tools(self, tool_calls):
        tool_messages = []
    
        def invoke_tool(call):
            name = call["name"]
            args = call.get("arguments", {})
            func = tool_map.get(name)
            if func is None:
                response = {"error": f"Tool {name} not found."}
            else:
                response = func(**args)
            response_text = format_function_response(name, response)
            return {"role": "tool", "name": name, "content": response_text}
    
        # 并发调用工具函数
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(invoke_tool, call) for call in tool_calls]
            for future in as_completed(futures):
                tool_messages.append(future.result())
    
        self.messages.extend(tool_messages)
        #print("self messges after call_tools: ", self.messages)
        return tool_messages

    def run_followup(self):
        # 插入系统指令，告诉模型不要再调用工具，而是总结回答
        self.messages.insert(0, {
            "role": "system",
            "content": (
                "你是一个文件系统助手。你已经调用过工具函数并获得结果，"
                "现在请你将这些结果整理为自然语言回答用户问题。不用输出代码块。"
            )
        })
        
        input_ids = self.tokenizer.apply_chat_template(
            self.messages,
            tools=[],
            output_tool_calls=False,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            enable_thinking=self.enable_thinking
        ).to(self.model.device)
    
        input_len = input_ids.shape[-1]  # 原始输入 token 长度

        attention_mask = (input_ids != self.tokenizer.pad_token_id).long()  # 注意 pad_token_id 要设置对
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=self.max_new_tokens,
                attention_mask=attention_mask,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=False
            )
    
        # ✅ 只解码新增生成部分
        generated_tokens = outputs[0][input_len:]
        output_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        output_text = clean_output_strict(output_text)

        #print("run_followup output: ", output_text)
        self.messages.append({
            "role": "assistant",
            "content": output_text
        })

        #print("run_followup self.messages: ", self.messages)
        return output_text


def load_filesystem_model(model_path: str):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        attn_implementation="flash_attention_2"
    ).eval()
    return model, tokenizer


def main(model_path: str, enable_thinking: bool = False):
    model, tokenizer = load_filesystem_model(model_path)
    session = FileSystemAgentSession(model=model, tokenizer=tokenizer, enable_thinking=enable_thinking)

    print("\n 文件系统助手已启动，输入 exit、quit 或 q 退出。\n")
    while True:
        query = input("\n\n用户: ")
        if query.strip().lower() in {"exit", "quit", "q"}:
            break

        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', query)

        try:
            start = time.time()
            output_text, tool_calls = session.run_user_query(cleaned)
            #print(f"run user query 耗时: {time.time() - start:.2f} 秒")
            #print("\n 初步响应:\n", output_text)
            if tool_calls:
                start = time.time()
                session.call_tools(tool_calls)
                #print(f"工具调用耗时: {time.time() - start:.2f} 秒")
                start = time.time()
                final_response = session.run_followup()
                #print(f"run followup 耗时: {time.time() - start:.2f} 秒")
                print("\n\n文件系统助手: ", final_response)
        except Exception as e:
            print(f" 错误: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to the model")
    parser.add_argument("--enable_thinking", action="store_true", help="Enable <think> block in generation")
    args = parser.parse_args()

    main(model_path=args.model_path, enable_thinking=args.enable_thinking)
