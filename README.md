# nebula MCP Server

提供 Nebula 中台 Java 后端编码规范的 MCP (Model Context Protocol) 服务器。

## 功能特性

### Nebula 中台 Java 后端编码规范

提供完整的 Nebula 中台 Java 后端编码规范文档，包括：

#### 1. 获取编码规范
查询 Nebula 中台各个维度的编码规范：
- **架构设计规范**：模块结构、分层架构、数据流转
- **命名规范**：包命名、类命名、方法命名、字段命名
- **Controller 层规范**：注解规范、方法设计、参数校验
- **Service 层规范**：轻量级 DDD、事务管理、日志记录
- **DAO 层规范**：Mapper 接口、返回类型、MyBatis Plus 使用
- **数据转换规范**：MapStruct 使用、转换场景、复杂转换
- **API 设计规范**：OpenAPI v3 注解、请求参数、响应体
- **异常处理规范**：异常体系、错误码、全局异常处理
- **常量和枚举规范**：常量类、枚举类、使用场景
- **数据库设计规范**：表命名、字段命名、必选字段、主键规范、雪花算法配置
- **配置管理规范**：配置文件结构、环境配置、敏感配置管理
- **其他规范**：MyBatis Plus、缓存、代码风格、JavaDoc 规范

#### 2. 命名规范检查
检查代码是否符合 Nebula 命名规范：
- 类命名检查
- 方法命名检查
- 字段命名检查
- 包命名检查

#### 3. 包结构建议
根据模块类型推荐 Nebula 中台的包结构：
- API 模块包结构
- Core 模块包结构
- Local 模块包结构
- Remote 模块包结构
- Service 模块包结构

#### 4. 分层职责查询
查询各层职责说明：
- Controller 层职责
- Service 层职责
- DAO 层职责

#### 5. 命名规范速查表
快速查询各种命名规范：
- 类命名速查表
- 方法命名速查表
- 字段命名速查表
- 包命名速查表
- 常量命名速查表
- 枚举命名速查表

## 项目结构

```
nebula-mcp/
├── .venv/                  # 虚拟环境
├── main.py                 # MCP 服务主程序
├── pyproject.toml          # 项目配置和依赖管理
├── .python-version         # Python 版本锁定
├── uv.lock                 # UV 依赖锁定文件
├── Dockerfile              # Docker 构建文件
├── .dockerignore           # Docker 忽略文件
├── tools/                  # 工具模块
│   ├── __init__.py
│   ├── base.py             # 工具基类
│   └── nebula_standards.py  # Nebula 中台编码规范工具
└── README.md              # 项目文档
```

## 快速开始

### 前置要求

- Python 3.12 或更高版本
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器

### 1. 安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 同步依赖

```bash
# 使用 uv 同步依赖（自动创建虚拟环境并安装依赖）
uv sync
```

### 3. 启动服务

**方式一：使用 uv 运行**

```bash
# 激活虚拟环境
uv shell

# 启动服务
python main.py
```

或者直接使用：

```bash
uv run python main.py
```

服务将在 `http://127.0.0.1:8000` 启动。

**方式二：使用 Docker 启动**

```bash
# 构建镜像
docker build -t nebula-mcp .

# 运行容器
docker run -p 8000:8000 nebula-mcp
```

**方式三：指定主机和端口**

```bash
# 监听所有接口，使用自定义端口
uv run python main.py --host 0.0.0.0 --port 8080
```

### 4. 访问服务

- SSE 端点: `http://localhost:8000/sse`
- 消息端点: `http://localhost:8000/messages/`
- 根路径: `http://localhost:8000/`

## 使用示例

### 获取架构设计规范

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_nebula_standard",
      "arguments": {
        "category": "architecture"
      }
    }
  }'
```

### 获取命名规范

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_nebula_standard",
      "arguments": {
        "category": "naming"
      }
    }
  }'
```

### 检查类命名规范

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_naming_convention",
      "arguments": {
        "code": "public class user_entity extends BaseEntity { }",
        "code_type": "class"
      }
    }
  }'
```

### 获取 Core 模块包结构建议

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "suggest_nebula_package_structure",
      "arguments": {
        "module_type": "core"
      }
    }
  }'
```

### 获取 Service 层职责说明

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_nebula_layer_responsibilities",
      "arguments": {
        "layer": "service"
      }
    }
  }'
```

### 获取类命名规范速查表

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_nebula_naming_convention",
      "arguments": {
        "convention_type": "class"
      }
    }
  }'
```

## 可用工具列表

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `get_nebula_standard` | 获取 Nebula 中台指定类别的编码规范 | `category` (str) |
| `check_naming_convention` | 检查代码是否符合 Nebula 命名规范 | `code` (str), `code_type` (str) |
| `suggest_nebula_package_structure` | 根据模块类型建议 Nebula 中台的包结构 | `module_type` (str) |
| `get_nebula_layer_responsibilities` | 获取 Nebula 中台分层职责说明 | `layer` (str) |
| `get_nebula_naming_convention` | 获取 Nebula 中台命名规范速查表 | `convention_type` (str) |
| `check_table_name` | 检查数据库表名是否符合 Nebula 中台规范 | `table_name` (str) |
| `check_configuration` | 检查配置文件是否符合 Nebula 中台规范 | `config_content` (str), `config_type` (str) |

## 开发说明

### 添加新依赖

```bash
# 添加生产依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name
```

### 扩展 Nebula 编码规范

编辑 `tools/nebula_standards.py`：

1. **添加新的规范类别**：
   - 在对应的规范常量中添加内容（如 `ARCHITECTURE_STANDARD`）
   - 在 `get_standard` 函数的 `standards_map` 中添加映射

2. **添加命名检查规则**：
   - 在 `check_naming_convention` 函数中添加检查逻辑

3. **添加新的工具**：
   - 在 `NebulaStandardsTool` 类中添加新的工具方法

## 配置

### 修改端口

编辑 `main.py` 最后一行：

```python
mcp.run(transport="streamable-http", host="0.0.0.0", port=YOUR_PORT)
```

### 添加环境变量

可以在项目中创建 `.env` 文件并使用 `python-dotenv` 加载配置。

## 技术栈

- **Python 3.12+**
- **uv**: 快速的 Python 包管理器
- **MCP SDK**: Model Context Protocol SDK (FastMCP)
- **pyproject.toml**: 现代化 Python 项目配置标准

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 联系。
