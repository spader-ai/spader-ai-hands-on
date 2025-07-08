import json

def format_function_response(tool_name: str, response_data: dict) -> str:
    """
    格式化工具函数响应为可读文本。
    要求 response_data 是 dict 类型，避免重复 JSON 序列化。
    """
    if not isinstance(response_data, dict):
        return f"⚠️ 工具 {tool_name} 返回值类型错误，应为 dict 类型。"

    # 检查是否有错误
    if "error" in response_data:
        return f"❌ {tool_name}: {response_data['error']}"
    
    # 检查是否成功
    if "success" in response_data and response_data["success"]:
        return f"✅ {tool_name}: 操作成功"
    
    # 对于文件内容，格式化显示
    if "content" in response_data:
        content = response_data["content"]
        size = response_data.get("size", "未知")
        return f"📄 {tool_name}: 文件大小 {size} 字节\n\n{content}"
    
    # 对于文件列表，格式化显示
    if "items" in response_data:
        items = response_data["items"]
        dir_path = response_data.get("dir_path", "")
        return f"📁 {tool_name}: 目录 {dir_path} 包含 {len(items)} 个项目\n\n" + "\n".join(items)
    
    # 对于搜索结果，格式化显示
    if "files" in response_data:
        files = response_data["files"]
        pattern = response_data.get("pattern", "")
        return f"🔍 {tool_name}: 模式 '{pattern}' 找到 {len(files)} 个文件\n\n" + "\n".join(files)
    
    # 对于元数据，格式化显示
    if "size" in response_data and "mtime" in response_data:
        file_path = response_data.get("file_path", "")
        size = response_data["size"]
        mtime = response_data["mtime"]
        is_file = response_data.get("is_file", False)
        is_dir = response_data.get("is_dir", False)
        type_str = "文件" if is_file else "目录" if is_dir else "未知"
        return f"📊 {tool_name}: {type_str} {file_path}\n大小: {size} 字节\n修改时间: {mtime}"
    
    # 默认返回 JSON 格式
    return f"📦 {tool_name} 返回数据：\n```json\n{json.dumps(response_data, ensure_ascii=False, indent=2)}\n```" 