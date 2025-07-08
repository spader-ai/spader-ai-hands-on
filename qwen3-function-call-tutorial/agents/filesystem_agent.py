import os
import shutil
import glob
import time

def read_file_content(file_path: str, max_size: int = 100 * 1024) -> dict:
    """
    读取指定文件内容，限制最大读取字节数，返回 dict 格式，包含内容或错误信息。
    """
    if not os.path.isfile(file_path):
        return {"error": f"文件不存在: {file_path}"}
    try:
        size = os.path.getsize(file_path)
        if size > max_size:
            return {"error": f"文件过大（{size}字节），最大支持{max_size}字节。"}
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "size": size}
    except Exception as e:
        return {"error": str(e)}

def write_file_content(file_path: str, content: str, overwrite: bool = False) -> dict:
    """
    写入内容到指定文件。默认不覆盖已存在文件。
    """
    if os.path.exists(file_path) and not overwrite:
        return {"error": f"文件已存在: {file_path}"}
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}

def create_directory(dir_path: str) -> dict:
    """
    创建目录。
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return {"success": True, "dir_path": dir_path}
    except Exception as e:
        return {"error": str(e)}

def list_directory(dir_path: str) -> dict:
    """
    列出目录下的文件和子目录。
    """
    if not os.path.isdir(dir_path):
        return {"error": f"目录不存在: {dir_path}"}
    try:
        items = os.listdir(dir_path)
        return {"items": items, "dir_path": dir_path}
    except Exception as e:
        return {"error": str(e)}

def delete_directory(dir_path: str) -> dict:
    """
    删除目录及其内容。
    """
    if not os.path.isdir(dir_path):
        return {"error": f"目录不存在: {dir_path}"}
    try:
        shutil.rmtree(dir_path)
        return {"success": True, "dir_path": dir_path}
    except Exception as e:
        return {"error": str(e)}

def move_path(src_path: str, dst_path: str) -> dict:
    """
    移动文件或目录。
    """
    if not os.path.exists(src_path):
        return {"error": f"源路径不存在: {src_path}"}
    try:
        shutil.move(src_path, dst_path)
        return {"success": True, "src": src_path, "dst": dst_path}
    except Exception as e:
        return {"error": str(e)}

def search_files(pattern: str) -> dict:
    """
    按通配符模式搜索文件（如 /path/**/*.txt）。
    """
    try:
        files = glob.glob(pattern, recursive=True)
        return {"files": files, "pattern": pattern}
    except Exception as e:
        return {"error": str(e)}

def get_file_metadata(file_path: str) -> dict:
    """
    获取文件或目录的元数据（大小、修改时间、类型等）。
    """
    if not os.path.exists(file_path):
        return {"error": f"路径不存在: {file_path}"}
    try:
        stat = os.stat(file_path)
        return {
            "file_path": file_path,
            "size": stat.st_size,
            "mtime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
            "is_file": os.path.isfile(file_path),
            "is_dir": os.path.isdir(file_path)
        }
    except Exception as e:
        return {"error": str(e)} 