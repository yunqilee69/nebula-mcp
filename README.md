# Cludix MCP Server

提供编码规范、分层规范等开发工具的 MCP (Model Context Protocol) 服务器。

## 功能特性

### 1. 编码规范工具
- **获取编码规范**: 查询多种编程语言的编码规范
  - Python (PEP 8)
  - Java
  - JavaScript/TypeScript
- **代码规范检查**: 检查代码是否符合编码规范，提供改进建议

### 2. 分层架构规范工具
- **获取架构规范**: 查询各种分层架构的规范说明
  - MVC (Model-View-Controller)
  - Clean Architecture (整洁架构)
  - Hexagonal Architecture (六边形/端口适配器架构)
  - DDD Layered Architecture (领域驱动设计分层)
- **项目结构建议**: 根据项目类型推荐合适的目录结构
  - Web API 项目
  - 微服务项目
  - 库/SDK 项目
  - 单体应用

## 项目结构

```
cludix-mcp/
├── .venv/                  # 虚拟环境
├── main.py                 # MCP 服务主程序
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 构建文件
├── .dockerignore           # Docker 忽略文件
├── tools/                  # 工具模块
│   ├── __init__.py
│   ├── coding_standards.py    # 编码规范工具
│   └── layer_standards.py     # 分层规范工具
└── README.md              # 项目文档
```

## 快速开始

### 1. 激活虚拟环境

```bash
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

**方式一：使用虚拟环境启动**

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

服务将在 `http://127.0.0.1:8000` 启动。

**方式二：使用 Docker 启动**

```bash
# 构建镜像
docker build -t cludix-mcp .

# 运行容器
docker run -p 8000:8000 cludix-mcp
```

**方式三：指定主机和端口**

```bash
# 监听所有接口，使用自定义端口
python main.py --host 0.0.0.0 --port 8080
```

### 4. 访问服务

- SSE 端点: `http://localhost:8000/sse`
- 消息端点: `http://localhost:8000/messages/`
- 根路径: `http://localhost:8000/`

## 使用示例

### 获取 Python 编码规范

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_coding_standard",
      "arguments": {
        "language": "python"
      }
    }
  }'
```

### 检查代码规范

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_code_convention",
      "arguments": {
        "code": "def myFunction(): print(\"hello\")",
        "language": "python"
      }
    }
  }'
```

### 获取 Clean Architecture 规范

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_layer_standard",
      "arguments": {
        "layer_type": "clean_architecture"
      }
    }
  }'
```

### 获取微服务项目结构建议

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "suggest_layer_structure",
      "arguments": {
        "project_type": "microservice"
      }
    }
  }'
```

## 可用工具列表

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `get_coding_standard` | 获取指定语言的编码规范 | `language` (str) |
| `check_code_convention` | 检查代码是否符合编码规范 | `code` (str), `language` (str) |
| `get_layer_standard` | 获取分层架构规范 | `layer_type` (str) |
| `suggest_layer_structure` | 根据项目类型建议目录结构 | `project_type` (str) |

## 开发说明

### 添加新工具

1. 在 `tools/` 目录下创建新的工具模块
2. 在 `main.py` 中注册工具：

```python
@server.tool()
async def your_tool(param: str) -> str:
    """工具描述"""
    # 实现你的工具逻辑
    return result
```

### 扩展编码规范

编辑 `tools/coding_standards.py`，添加新的语言规范：

```python
YOUR_LANGUAGE_STANDARDS = """
# 你的语言编码规范
...
"""

# 在 get_standard 函数中添加映射
standards_map = {
    ...
    "your_language": YOUR_LANGUAGE_STANDARDS,
}
```

### 扩展架构规范

编辑 `tools/layer_standards.py`，添加新的架构规范或项目类型建议。

## 配置

### 修改端口

编辑 `main.py` 最后一行：

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

### 添加环境变量

可以在项目中创建 `.env` 文件并使用 `python-dotenv` 加载配置。

## 技术栈

- **Python 3.13+**
- **FastAPI**: Web 框架
- **MCP SDK**: Model Context Protocol SDK
- **Uvicorn**: ASGI 服务器

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 联系。
