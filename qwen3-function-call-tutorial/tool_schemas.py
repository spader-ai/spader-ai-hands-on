from agents.filesystem_agent import (
    read_file_content,
    write_file_content,
    create_directory,
    list_directory,
    delete_directory,
    move_path,
    search_files,
    get_file_metadata,
)

# 文件系统相关工具 schema

tool_schemas = [
    {
        "name": "filesystem_read_file",
        "description": "读取指定路径的文件内容，返回文本内容。可用于查看本地文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "要读取的文件绝对路径或相对路径"},
                "max_size": {"type": "integer", "description": "最大读取字节数，默认100KB。", "default": 102400}
            },
            "required": ["file_path"]
        },
        "tags": ["文件系统", "读取文件", "filesystem", "read file"]
    },
    {
        "name": "filesystem_write_file",
        "description": "将内容写入指定文件。可选择是否覆盖已存在文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "要写入的文件路径"},
                "content": {"type": "string", "description": "要写入的文本内容"},
                "overwrite": {"type": "boolean", "description": "如文件已存在是否覆盖，默认否。", "default": False}
            },
            "required": ["file_path", "content"]
        },
        "tags": ["文件系统", "写文件", "filesystem", "write file"]
    },
    {
        "name": "filesystem_create_directory",
        "description": "创建新目录，支持递归创建多级目录。",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "要创建的目录路径"}
            },
            "required": ["dir_path"]
        },
        "tags": ["文件系统", "创建目录", "filesystem", "create directory"]
    },
    {
        "name": "filesystem_list_directory",
        "description": "列出指定目录下的所有文件和子目录。",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "要列出的目录路径"}
            },
            "required": ["dir_path"]
        },
        "tags": ["文件系统", "列目录", "filesystem", "list directory"]
    },
    {
        "name": "filesystem_delete_directory",
        "description": "删除指定目录及其所有内容（递归删除）。",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "要删除的目录路径"}
            },
            "required": ["dir_path"]
        },
        "tags": ["文件系统", "删除目录", "filesystem", "delete directory"]
    },
    {
        "name": "filesystem_move_path",
        "description": "移动文件或目录到新位置。",
        "parameters": {
            "type": "object",
            "properties": {
                "src_path": {"type": "string", "description": "源文件或目录路径"},
                "dst_path": {"type": "string", "description": "目标文件或目录路径"}
            },
            "required": ["src_path", "dst_path"]
        },
        "tags": ["文件系统", "移动文件", "移动目录", "filesystem", "move"]
    },
    {
        "name": "filesystem_search_files",
        "description": "按通配符模式搜索文件（如 /path/**/*.txt ）。",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "glob 通配符模式，如 /path/**/*.py"}
            },
            "required": ["pattern"]
        },
        "tags": ["文件系统", "搜索文件", "filesystem", "search"]
    },
    {
        "name": "filesystem_get_file_metadata",
        "description": "获取文件或目录的元数据（大小、修改时间、类型等信息）。",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "要查询的文件或目录路径"}
            },
            "required": ["file_path"]
        },
        "tags": ["文件系统", "文件信息", "元数据", "filesystem", "metadata"]
    },
]

tool_map = {
    "filesystem_read_file": read_file_content,
    "filesystem_write_file": write_file_content,
    "filesystem_create_directory": create_directory,
    "filesystem_list_directory": list_directory,
    "filesystem_delete_directory": delete_directory,
    "filesystem_move_path": move_path,
    "filesystem_search_files": search_files,
    "filesystem_get_file_metadata": get_file_metadata,
}