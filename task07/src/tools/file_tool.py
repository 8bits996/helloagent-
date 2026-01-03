import os

class FileEditTool:
    name = "file_edit"
    description = "编辑或创建文件（支持全量写入）"

    def get_parameters(self):
        return {
            "path": {
                "type": "str", 
                "description": "文件路径（相对路径）", 
                "required": True
            },
            "content": {
                "type": "str",
                "description": "要写入的文件内容",
                "required": True
            }
        }

    def run(self, parameters):
        if isinstance(parameters, dict):
            path = parameters.get("path")
            content = parameters.get("content")
        else:
            return "错误：参数格式不正确，需要 path 和 content"

        if not path or not content:
            return "错误：路径或内容不能为空"

        # 安全检查：只允许当前目录下操作
        if os.path.isabs(path) or ".." in path or path.startswith("/"):
            return "安全拒绝：只允许在当前项目目录下创建或编辑文件"

        try:
            # 确保目录存在
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return f"✅ 文件 '{path}' 已成功写入 ({len(content)} 字符)。"
        except Exception as e:
            return f"❌ 文件写入失败: {str(e)}"
