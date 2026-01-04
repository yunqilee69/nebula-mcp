"""
分层架构规范工具模块
提供各种分层架构的规范和建议
"""

from mcp.server.fastmcp import FastMCP
from .base import BaseTool


# MVC 架构规范
MVC_STANDARD = """
# MVC (Model-View-Controller) 架构规范

## 架构说明
MVC 是一种经典的 UI 架构模式，将应用分为三个核心部分：

1. **Model（模型）**：数据和业务逻辑
2. **View（视图）**：用户界面展示
3. **Controller（控制器）**：处理用户输入

## 目录结构
```
project/
├── models/           # 数据模型
│   ├── user.py
│   └── product.py
├── views/            # 视图/模板
│   ├── home.html
│   └── profile.html
├── controllers/      # 控制器
│   ├── user_controller.py
│   └── auth_controller.py
└── routes/           # 路由配置
    └── __init__.py
```

## 职责划分

### Model（模型层）
- 定义数据结构和验证规则
- 实现业务逻辑和数据处理
- 与数据库交互
- 不依赖 View 和 Controller

### View（视图层）
- 负责数据展示
- 从 Model 接收数据并渲染
- 不包含业务逻辑
- 通过模板引擎生成 HTML

### Controller（控制器层）
- 接收并处理用户请求
- 调用 Model 进行业务处理
- 选择合适的 View 进行响应
- 协调 Model 和 View

## 通信规则
- Controller → Model：调用业务方法
- Controller → View：传递数据用于渲染
- View → Controller：用户交互触发请求
- Model 不直接与 View 通信

## 适用场景
- 传统 Web 应用
- 需要快速开发的中小型项目
- 团队熟悉 MVC 模式
"""

# Clean Architecture 规范
CLEAN_ARCHITECTURE_STANDARD = """
# Clean Architecture（整洁架构）规范

## 架构说明
由 Robert C. Martin 提出，强调依赖倒置和分层隔离。

## 核心原则
1. **依赖规则**：依赖只能由外向内，内层不知道外层的存在
2. **框架独立**：内层不依赖任何框架、库或数据库
3. **可测试性**：内层业务逻辑可以在没有 UI、数据库、Web 服务器的情况下测试

## 分层结构（由内向外）

### 1. Entities（实体层）- 最内层
- 企业级业务规则
- 跨应用的核心业务逻辑
- 与外部变化无关

### 2. Use Cases（用例层）
- 应用特定的业务规则
- 编排数据流
- 调用 Entities 实现业务逻辑

### 3. Interface Adapters（接口适配器层）
- 数据格式转换
- Presenters, Controllers, Gateways
- 将外层数据格式转换为内层可用格式

### 4. Frameworks & Drivers（框架和驱动层）- 最外层
- Web 框架、数据库、UI
- 工具和外部服务
- 这层的细节最易变化

## 目录结构
```
project/
├── src/
│   ├── core/                    # 核心层（Entities）
│   │   ├── entities/
│   │   │   ├── user.py
│   │   │   └── domain_events.py
│   │   └── value_objects/
│   ├── application/             # 应用层（Use Cases）
│   │   ├── use_cases/
│   │   │   ├── register_user.py
│   │   │   └── authenticate_user.py
│   │   ├── dto/
│   │   └── interfaces/
│   ├── infrastructure/          # 基础设施层
│   │   ├── persistence/
│   │   │   ├── repositories/
│   │   │   └── models.py
│   │   ├── external_services/
│   │   └── config.py
│   └── interfaces/              # 接口适配器层
│       ├── api/
│       │   ├── controllers/
│       │   ├── routes/
│       │   └── schemas.py
│       ├── cli/
│       └── web/
│           └── views/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## 依赖规则示例
```python
# ✅ 正确：外层依赖内层
from src.application.use_cases import register_user
from src.core.entities import User

# ❌ 错误：内层不能依赖外层
# from src.interfaces.api import UserController  # 禁止！
```

## 适用场景
- 大型企业应用
- 需要长期维护的项目
- 复杂业务逻辑
- 需要高可测试性
"""

# Hexagonal Architecture（六边形架构）规范
HEXAGONAL_ARCHITECTURE_STANDARD = """
# Hexagonal Architecture（六边形/端口适配器架构）规范

## 架构说明
由 Alistair Cockburn 提出，将应用分为内部核心和外部适配器。

## 核心概念
1. **Application Core（应用核心）**：纯业务逻辑，不依赖外部
2. **Ports（端口）**：定义核心与外部的交互接口
3. **Adapters（适配器）**：实现端口，连接外部系统

## 架构组件

### Ports（端口）
- **Primary Ports（驱动端口）**：被外部调用的接口（Use Case/Application Service）
- **Secondary Ports（被驱动端口）**：调用外部的接口（Repository, Gateway）

### Adapters（适配器）
- **Primary Adapters（驱动适配器）**：调用 Primary Ports
  - REST API
  - CLI
  - Web UI
  - Tests
- **Secondary Adapters（被驱动适配器）**：实现 Secondary Ports
  - Database
  - External API
  - Message Queue
  - File System

## 目录结构
```
project/
├── src/
│   ├── application/             # 应用核心
│   │   ├── ports/              # 端口接口定义
│   │   │   ├── primary/        # 驱动端口（输入）
│   │   │   │   ├── user_service.py
│   │   │   │   └── order_service.py
│   │   │   └── secondary/      # 被驱动端口（输出）
│   │   │       ├── user_repository.py
│   │   │       └── email_gateway.py
│   │   ├── services/           # 应用服务实现
│   │   │   ├── user_service_impl.py
│   │   │   └── order_service_impl.py
│   │   ├── domain/             # 领域模型
│   │   │   ├── entities/
│   │   │   └── value_objects/
│   │   └── dto/                # 数据传输对象
│   │
│   ├── infrastructure/          # 基础设施适配器
│   │   ├── persistence/        # 持久化适配器
│   │   │   ├── sql/
│   │   │   │   ├── user_repository_impl.py
│   │   │   │   └── models.py
│   │   │   └── nosql/
│   │   ├── messaging/          # 消息适配器
│   │   │   ├── rabbitmq_publisher.py
│   │   │   └── kafka_consumer.py
│   │   └── external/           # 外部服务适配器
│   │       └── email_sender.py
│   │
│   └── interfaces/             # 接口适配器
│       ├── rest/               # REST API 适配器
│       │   ├── controllers/
│       │   ├── routes/
│       │   └── middleware/
│       ├── graphql/            # GraphQL 适配器
│       ├── cli/                # CLI 适配器
│       └── grpc/               # gRPC 适配器
│
└── tests/
    ├── unit/                   # 单元测试（也是驱动适配器）
    ├── integration/            # 集成测试
    └── fixtures/
```

## 示例代码

### 定义端口(接口)
代码示例:
from abc import ABC, abstractmethod
from typing import Optional

class UserRepository(ABC):
    # 用户仓库接口

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass

### 实现适配器
代码示例:
from application.ports.secondary.user_repository import UserRepository

class SQLUserRepository(UserRepository):
    # SQL 用户仓库实现

    def __init__(self, db_connection):
        self.db = db_connection

    async def find_by_id(self, user_id: str) -> Optional[User]:
        # SQL 实现
        pass

    async def save(self, user: User) -> None:
        # SQL 实现
        pass

### 使用端口
代码示例:
class UserServiceImpl:
    # 用户服务实现

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: str) -> UserDTO:
        user = await self.user_repo.find_by_id(user_id)
        return UserDTO.from_entity(user)

## 优势
1. **可替换性**：适配器可以轻松替换（如切换数据库）
2. **可测试性**：可以模拟适配器进行单元测试
3. **隔离性**：核心业务逻辑不受外部技术变化影响
4. **灵活性**：支持多种接口（REST, GraphQL, CLI 等）

## 适用场景
- 微服务架构
- 需要支持多种客户端
- 频繁变更的技术栈
- 高可测试性要求
"""


# DDD 分层架构规范
DDD_LAYERED_STANDARD = """
# Domain-Driven Design（领域驱动设计）分层架构规范

## 架构说明
基于 DDD 的分层架构，强调领域模型和业务逻辑。

## 分层结构

### 1. User Interface Layer（用户界面层）
- 负责向用户展示信息和解释用户指令
- REST API、GraphQL、Web UI、CLI 等

### 2. Application Layer（应用层）
- 编排领域对象执行业务用例
- 不包含业务逻辑，只负责协调
- 事务管理、安全控制、任务调度

### 3. Domain Layer（领域层）- 核心
- 包含业务概念和规则
- 领域模型、领域服务、领域事件
- 不依赖任何外层

### 4. Infrastructure Layer（基础设施层）
- 提供技术支持
- 持久化、消息传递、外部服务
- 实现领域层定义的接口

## 目录结构
```
project/
├── src/
│   ├── interfaces/              # 用户界面层
│   │   ├── rest/               # REST API
│   │   │   ├── controllers/
│   │   │   ├── dto/
│   │   │   ├── request/
│   │   │   ├── response/
│   │   │   └── routes/
│   │   ├── graphql/            # GraphQL
│   │   └── cli/                # 命令行
│   │
│   ├── application/             # 应用层
│   │   ├── services/           # 应用服务
│   │   ├── use_cases/          # 用例
│   │   ├── commands/           # 命令
│   │   ├── queries/            # 查询
│   │   ├── handlers/           # 命令/查询处理器
│   │   └── dto/                # 应用层数据传输对象
│   │
│   ├── domain/                  # 领域层（核心）
│   │   ├── model/              # 领域模型
│   │   │   ├── entities/       # 实体
│   │   │   ├── value_objects/  # 值对象
│   │   │   ├── aggregates/     # 聚合
│   │   │   └── repositories/   # 仓储接口（仅接口）
│   │   ├── services/           # 领域服务
│   │   ├── events/             # 领域事件
│   │   ├── exceptions/         # 领域异常
│   │   └── specifications/     # 规约模式
│   │
│   └── infrastructure/          # 基础设施层
│       ├── persistence/         # 持久化
│       │   ├── repositories/   # 仓储实现
│       │   ├── models/         # ORM 模型
│       │   └── mappers/        # 数据映射
│       ├── messaging/           # 消息传递
│       │   ├── kafka/
│       │   ├── rabbitmq/
│       │   └── redis/
│       ├── external/            # 外部服务
│       │   └── clients/
│       ├── caching/             # 缓存
│       └── config/              # 配置
│
└── shared/                      # 共享内核
    ├── utils/
    ├── constants/
    └── types/
```

## DDD 核心概念

### Entity（实体）
有唯一标识的对象，标识符相同即为同一对象。

### Value Object（值对象）
不可变的、通过属性值判断相等的对象。

### Aggregate（聚合）
一组相关领域的对象集合，通过聚合根访问。

### Repository（仓储）
封装对象存储和检索的集合式接口。

### Domain Event（领域事件）
表示领域内发生的重要业务事件。

## 示例代码

### 领域实体
代码示例:
class User(Entity):
    def __init__(self, user_id: UserId, email: Email, name: str):
        self._id = user_id
        self._email = email
        self._name = name
        self._created_at = datetime.now()

    def change_email(self, new_email: Email):
        if self._email == new_email:
            raise DomainException("Email is the same")
        self._email = new_email
        self.add_domain_event(EmailChangedEvent(self._id, new_email))

### 应用服务
代码示例:
class UserApplicationService:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService
    ):
        self._user_repo = user_repository
        self._email_service = email_service

    async def register_user(self, command: RegisterUserCommand):
        # 1. 创建领域对象
        user = User.create(command.email, command.name)

        # 2. 执行业务逻辑（在领域层）
        # 3. 保存（基础设施层）
        await self._user_repo.save(user)

        # 4. 发布事件
        for event in user.pull_domain_events():
            await self._event_bus.publish(event)

## 适用场景
- 复杂业务领域
- 大型企业应用
- 需要与业务专家紧密协作
- 长期演进的项目
"""


async def get_standard(layer_type: str) -> str:
    """
    获取指定类型的分层架构规范

    Args:
        layer_type: 分层类型

    Returns:
        该分层架构的规范说明
    """
    layer_type = layer_type.lower().replace("-", "_").replace(" ", "_")

    standards_map = {
        "mvc": MVC_STANDARD,
        "clean": CLEAN_ARCHITECTURE_STANDARD,
        "clean_architecture": CLEAN_ARCHITECTURE_STANDARD,
        "cleanarchitecture": CLEAN_ARCHITECTURE_STANDARD,
        "hexagonal": HEXAGONAL_ARCHITECTURE_STANDARD,
        "hex": HEXAGONAL_ARCHITECTURE_STANDARD,
        "ports_adapters": HEXAGONAL_ARCHITECTURE_STANDARD,
        "ddd": DDD_LAYERED_STANDARD,
        "domain_driven_design": DDD_LAYERED_STANDARD,
    }

    standard = standards_map.get(layer_type)

    if standard:
        # 标题格式化
        title = layer_type.replace("_", " ").replace("-", " ").upper()
        return f"{standard}"
    else:
        available = ["MVC", "Clean Architecture", "Hexagonal Architecture", "DDD Layered"]
        return f"暂时不支持 '{layer_type}' 架构。\n\n支持的架构：{', '.join(available)}"


async def suggest_structure(project_type: str) -> str:
    """
    根据项目类型建议目录结构

    Args:
        project_type: 项目类型

    Returns:
        建议的目录结构
    """
    project_type = project_type.lower().replace("-", " ")

    if project_type in ["web api", "webapi", "web_api", "rest api", "rest_api"]:
        return """
# Web API 项目推荐架构

对于 Web API 项目，推荐使用 **Clean Architecture** 或 **Hexagonal Architecture**

## 推荐目录结构
```
project/
├── src/
│   ├── application/
│   │   ├── use_cases/
│   │   ├── dto/
│   │   └── interfaces/
│   ├── domain/
│   │   ├── entities/
│   │   └── repositories/
│   ├── infrastructure/
│   │   ├── persistence/
│   │   └── external_services/
│   └── interfaces/
│       └── rest/
│           ├── controllers/
│           ├── routes/
│           └── schemas/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── requirements.txt
```

## 优点
- 业务逻辑与框架解耦
- 易于测试
- 支持多协议（可同时提供 REST 和 GraphQL）
"""

    elif project_type in ["microservice", "micro_service", "micro-services"]:
        return """
# 微服务项目推荐架构

对于微服务项目，推荐使用 **Hexagonal Architecture**

## 推荐目录结构
```
service-name/
├── src/
│   ├── application/
│   │   ├── ports/
│   │   │   ├── primary/
│   │   │   └── secondary/
│   │   ├── services/
│   │   └── domain/
│   ├── infrastructure/
│   │   ├── persistence/
│   │   ├── messaging/
│   │   └── config/
│   └── interfaces/
│       ├── rest/
│       ├── graphql/
│       └── grpc/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 关键点
- 清晰的端口和适配器分离
- 易于替换数据库和消息队列
- 支持多种通信协议
- 独立部署能力
"""

    elif project_type in ["library", "lib", "package", "sdk"]:
        return """
# 库/SDK 项目推荐架构

对于库或 SDK 项目，推荐使用 **简化的分层架构**

## 推荐目录结构
```
library-name/
├── src/
│   ├── package_name/
│   │   ├── __init__.py
│   │   ├── core/              # 核心功能
│   │   ├── utils/             # 工具函数
│   │   ├── exceptions/        # 自定义异常
│   │   ├── constants.py       # 常量
│   │   └── types.py           # 类型定义
│   └── package_name/
│       └── __init__.py
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── examples/
├── pyproject.toml
├── setup.py
├── README.md
└── LICENSE
```

## 关键点
- 简单清晰的公共 API
- 完善的文档和示例
- 高测试覆盖率
- 最小化依赖
"""

    elif project_type in ["monolith", "monolithic", "单体应用"]:
        return """
# 单体应用推荐架构

对于单体应用，推荐使用 **DDD 分层架构**

## 推荐目录结构
```
monolith-app/
├── src/
│   ├── interfaces/
│   │   ├── rest/
│   │   ├── web/
│   │   └── cli/
│   ├── application/
│   │   ├── services/
│   │   ├── commands/
│   │   └── queries/
│   ├── domain/
│   │   ├── model/
│   │   ├── services/
│   │   └── events/
│   └── infrastructure/
│       ├── persistence/
│       ├── messaging/
│       └── caching/
│
├── modules/                    # 按业务模块划分
│   ├── user/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── order/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   └── product/
│       ├── application/
│       ├── domain/
│       └── infrastructure/
│
├── shared/                     # 共享内核
│   ├── utils/
│   ├── constants/
│   └── types/
└── tests/
```

## 关键点
- 按业务模块组织（模块化单体）
- 清晰的层次边界
- 共享基础设施
- 便于未来拆分为微服务
"""

    else:
        return f"""
# 通用项目架构建议

项目类型 "{project_type}" 未识别。

## 支持的项目类型：
1. **web_api** - Web API 项目
2. **microservice** - 微服务项目
3. **library** - 库/SDK 项目
4. **monolith** - 单体应用

请指定项目类型以获取具体的架构建议。

## 通用原则
- 根据项目规模选择合适的架构
- 保持代码组织清晰
- 优先考虑可维护性
- 选择团队熟悉的模式
"""


class LayerStandardsTool(BaseTool):
    """分层架构规范工具类"""

    @classmethod
    def register(cls, mcp: FastMCP):
        """注册分层架构规范相关工具"""

        @mcp.tool()
        async def get_layer_standard(layer_type: str) -> str:
            """
            获取指定类型的分层架构规范

            Args:
                layer_type: 分层类型,如 mvc, clean_architecture, hexagonal 等

            Returns:
                该分层架构的规范说明
            """
            return await get_standard(layer_type)

        @mcp.tool()
        async def suggest_layer_structure(project_type: str) -> str:
            """
            根据项目类型建议目录结构

            Args:
                project_type: 项目类型,如 web_api, microservice, library 等

            Returns:
                建议的目录结构
            """
            return await suggest_structure(project_type)

