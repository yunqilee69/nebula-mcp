"""
Nebula 中台 Java 后端编码规范工具模块
提供 Nebula 框架的完整编码规范、命名规范、架构设计规范等
"""

from mcp.server.fastmcp import FastMCP
from .base import BaseTool
from .standards_loader import StandardsLoader


# ==============================================================================
# 注意：规范内容已迁移到 standards 目录下的独立文件中
# ==============================================================================
async def get_standard(category: str) -> str:
    """
    获取 Nebula 编码规范

    Args:
        category: 规范分类

    Returns:
        规范文档
    """
    return StandardsLoader.load_standard(category)


async def check_naming_convention(code: str, code_type: str) -> str:
    """
    检查代码是否符合 Nebula 命名规范

    Args:
        code: 代码片段
        code_type: 代码类型（class, method, field, package）

    Returns:
        检查结果和建议
    """
    code_type = code_type.lower().strip()
    issues = []
    suggestions = []

    # 类命名检查
    if code_type == "class":
        lines = code.split("\n")
        for line in lines:
            line = line.strip()

            # 检查 Entity
            if line.startswith("class ") and line.endswith("Entity {"):
                class_name = line.split(" ")[1].replace("Entity", "")
                if not class_name[0].isupper() or "_" in class_name:
                    issues.append(
                        f"Entity 类名 '{line.split(' ')[1]}' 应使用 PascalCase"
                    )

            # 检查 Mapper
            if line.startswith("public interface ") and line.endswith("Mapper {"):
                class_name = line.split(" ")[3].replace("Mapper", "")
                if not class_name[0].isupper() or "_" in class_name:
                    issues.append(
                        f"Mapper 接口名 '{line.split(' ')[3]}' 应使用 PascalCase"
                    )

            # 检查 Service 接口
            if line.startswith("public interface I") and "Service {":
                class_name = line.split(" ")[3].replace("Service", "")
                if not class_name[0].isupper():
                    issues.append(
                        f"Service 接口名 '{line.split(' ')[3]}' 应使用 I{{业务名称}}Service 格式"
                    )

            # 检查 Service 实现
            if "implements I" in line and line.endswith("ServiceImpl {"):
                impl_name = line.split("implements ")[1].split(" {")[0].strip()
                if not impl_name.endswith("ServiceImpl"):
                    issues.append(
                        f"Service 实现类名应使用 {{业务名称}}ServiceImpl 格式"
                    )

    # 方法命名检查
    elif code_type == "method":
        lines = code.split("\n")
        for line in lines:
            line = line.strip()

            # 检查 Mapper 方法
            if "public " in line and "(" in line:
                method_name = line.split(" ")[2].split("(")[0]

                # find* 返回 List
                if method_name.startswith("find") and "List<" not in line:
                    issues.append(
                        f"Mapper 方法 '{method_name}' 以 find 开头，应返回 List"
                    )

                # get* 返回单个
                if (
                    method_name.startswith("get")
                    and "<" not in line
                    and line.split(" ")[1] != "List"
                ):
                    if "Optional" not in line:
                        issues.append(
                            f"Mapper 方法 '{method_name}' 以 get 开头，应返回 Optional 或单个对象"
                        )

                # page* 返回 Page
                if method_name.startswith("page") and "Page<" not in line:
                    issues.append(
                        f"Mapper 方法 '{method_name}' 以 page 开头，应返回 Page"
                    )

    # 字段命名检查
    elif code_type == "field":
        lines = code.split("\n")
        for line in lines:
            line = line.strip()

            # 检查驼峰命名
            if "private " in line and ";" in line:
                field_name = line.split(" ")[2].split(";")[0]
                if "_" in field_name:
                    issues.append(f"字段 '{field_name}' 应使用驼峰命名（camelCase）")

    # 生成建议
    if not issues:
        suggestions.append("✅ 代码符合 Nebula 命名规范！")
    else:
        suggestions.append(f"发现 {len(issues)} 个命名问题：")
        suggestions.extend(issues)
        suggestions.append("\n💡 建议：参考 Nebula 命名规范文档")

    return "\n".join(suggestions)


async def suggest_package_structure(module_type: str) -> str:
    """
    根据模块类型建议包结构

    Args:
        module_type: 模块类型（api, core, local, remote, service）

    Returns:
        建议的包结构
    """
    module_type = module_type.lower().strip()

    if module_type == "api":
        return """
# API 模块包结构

```
nebula-uaa-api/
└── com/nebula/uaa/api/
    ├── service/               # 服务接口
    │   ├── IUserService.java
    │   └── IOrderService.java
    ├── model/                 # 数据模型
    │   ├── dto/               # 数据传输对象
    │   │   ├── UserDto.java
    │   │   └── OrderDto.java
    │   ├── command/           # 写命令
    │   │   ├── CreateUserCommand.java
    │   │   └── UpdateUserCommand.java
    │   └── query/             # 读查询
    │       ├── GetUserByIdQuery.java
    │       └── ListUsersQuery.java
    ├── constant/              # 常量
    │   └── UserConstant.java
    └── enumerate/             # 枚举
        └── UserStatusEnum.java
```

**职责**：定义基础契约（接口定义），无实现
"""

    elif module_type == "core":
        return """
# Core 模块包结构

```
nebula-uaa-core/
└── com/nebula/uaa/core/
    ├── service/               # Service 层
    │   ├── IUserService.java
    │   └── impl/              # Service 实现
    │       ├── UserServiceImpl.java
    │       └── OrderServiceImpl.java
    ├── dao/
    │   └── mapper/            # MyBatis Mapper 接口
    │       ├── UserMapper.java
    │       └── OrderMapper.java
    ├── model/                 # 数据模型
    │   ├── entity/            # 实体类
    │   │   ├── UserEntity.java
    │   │   └── OrderEntity.java
    │   ├── dto/               # 数据传输对象
    │   │   ├── UserDto.java
    │   │   └── OrderDto.java
    │   ├── command/           # 写命令
    │   │   ├── CreateUserCommand.java
    │   │   └── UpdateUserCommand.java
    │   ├── query/             # 读查询
    │   │   ├── GetUserByIdQuery.java
    │   │   └── ListUsersQuery.java
    │   └── param/             # DAO 查询参数
    │       ├── UserQueryParam.java
    │       └── OrderQueryParam.java
    └── config/               # 配置类
        └── MyBatisPlusConfig.java
```

**职责**：服务实现 + 数据访问（无 Controller）
"""

    elif module_type == "local":
        return """
# Local 模块包结构

```
nebula-uaa-local/
└── com/nebula/uaa/local/
    ├── controller/            # Controller 层
    │   ├── UserController.java
    │   └── OrderController.java
    ├── model/
    │   ├── req/               # 请求参数
    │   │   ├── CreateUserReq.java
    │   │   └── UpdateUserReq.java
    │   └── resp/              # 响应参数
    │       ├── UserResp.java
    │       └── UserDetailResp.java
    ├── converter/             # MapStruct 转换器
    │   ├── UserConverter.java
    │   └── OrderConverter.java
    └── config/               # 配置类
        └── WebConfig.java
```

**职责**：封装 Controller 层，负责 HTTP 请求/响应处理
"""

    elif module_type == "remote":
        return """
# Remote 模块包结构

```
nebula-uaa-remote/
└── com/nebula/uaa/remote/
    ├── feign/                 # Feign 客户端
    │   ├── UserFeignClient.java
    │   └── OrderFeignClient.java
    └── config/               # 配置类
        └── FeignConfig.java
```

**职责**：远程调用客户端（微服务使用）
"""

    elif module_type == "service":
        return """
# Service 模块包结构

```
nebula-uaa-service/
└── com/nebula/uaa/service/
    ├── application/           # 启动类
    │   └── NebulaUaaApplication.java
    └── resources/            # 配置文件
        ├── application.yml
        └── logback.xml
```

**职责**：独立应用（包含 local 模块）
"""

    else:
        return f"""
# Nebula 中台模块包结构建议

模块类型 "{module_type}" 未识别。

## 支持的模块类型：
1. **api** - API 模块（基础契约）
2. **core** - Core 模块（服务实现）
3. **local** - Local 模块（Controller 层）
4. **remote** - Remote 模块（远程调用）
5. **service** - Service 模块（独立应用）

请指定模块类型以获取详细的包结构建议。
"""


async def get_layer_responsibilities(layer: str) -> str:
    """
    获取分层职责说明

    Args:
        layer: 层名称（controller, service, dao）

    Returns:
        分层职责说明
    """
    layer = layer.lower().strip()

    if layer == "controller":
        return """
# Controller 层职责

## 主要职责
- 处理 HTTP 请求和响应
- 参数校验（使用 Jakarta Validation）
- 将 Req 转换为 Command/Query
- 调用 Service 层
- 返回 Resp

## 不包含
- 业务逻辑
- 数据访问
- 复杂计算

## 注解规范
- `@RestController`
- `@RequestMapping("/users")`
- `@Tag(name = "用户管理")`
- `@Operation(summary = "创建用户")`
- `@Schema(description = "用户名")`
- `@Valid`（参数校验）

## 方法示例
```java
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);
    return userService.createUser(cmd);
}
```

## 异常处理
不需要捕获异常，由全局异常处理器统一处理
"""

    elif layer == "service":
        return """
# Service 层职责

## 主要职责
- 编排业务流程
- 封装核心业务逻辑
- 事务管理
- 调用 DAO 层
- 调用外部服务（通过 API 接口）

## 轻量级 DDD
- 不严格区分应用服务和领域服务
- 可在 Service 层内部拆分 Internal Service
- Internal Service 封装可复用的业务逻辑
- 避免过度设计，保持简单

## 注解规范
- `@Service`
- `@Transactional`（写操作必须加）
- `@Transactional(readOnly = true)`（复杂查询可加）
- `@Slf4j`（日志）

## 方法示例
```java
@Service
@Slf4j
public class UserServiceImpl implements IUserService {

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        log.info("创建用户，参数：{}", cmd);

        userInternalService.validateUsername(cmd.getUsername());

        UserEntity entity = new UserEntity();
        // ...

        userRepo.save(entity);

        log.info("用户创建成功，ID：{}", entity.getId());
        return entity.getId();
    }
}
```

## 异常处理
抛出业务异常，由全局异常处理器统一处理
"""

    elif layer == "dao":
        return """
# DAO 层职责

## 主要职责
- 数据库操作
- 单表查询（使用 MyBatis Plus）
- 复杂查询（自定义 SQL）
- 缓存管理（如果需要）

## 返回类型规范
- 单表查询：返回 Entity
- 多表联查：返回 DTO
- 自定义返回字段：返回 DTO

## 方法命名规范
| 前缀 | 返回类型 | 说明 |
|------|---------|------|
| `find*` | `List<T>` | 查询多个实体 |
| `get*` | `T` | 查询单个实体 |
| `getOpt*` | `Optional<T>` | 查询单个实体（Optional） |
| `page*` | `Page<T>` | 分页查询 |
| `count*` | `Long` | 统计数量 |
| `exists*` | `boolean` | 判断是否存在 |

## Mapper 示例
```java
public interface UserMapper extends BaseMapper<UserEntity> {

    UserEntity findByUsername(String username);
    boolean existsByUsername(String username);
    List<UserEntity> listByParam(UserQueryParam param);
    Page<UserEntity> pageByParam(Page<UserEntity> page, UserQueryParam param);
    Long countByStatus(Integer status);
}
```

## Param 类
查询参数 > 3 个时，封装为 Param 类，继承 `BasePageParam`
"""

    else:
        return f"""
# Nebula 中台分层职责说明

层名称 "{layer}" 未识别。

## 支持的层：
1. **controller** - Controller 层职责
2. **service** - Service 层职责
3. **dao** - DAO 层职责

请指定层名称以获取详细的职责说明。
"""


async def check_table_name(table_name: str) -> str:
    """
    检查数据库表名是否符合 Nebula 中台规范

    Args:
        table_name: 表名

    Returns:
        检查结果和建议
    """
    table_name = table_name.strip()
    issues = []
    suggestions = []

    # 检查表前缀
    if not table_name.startswith("cx_"):
        issues.append(f"表名 '{table_name}' 缺少 'cx_' 前缀")

    # 检查是否为复数形式（简单判断）
    base_name = table_name.replace("cx_", "")
    if (
        base_name.endswith("s")
        and not base_name.endswith("ss")
        and not base_name.endswith("us")
    ):
        issues.append(f"表名 '{table_name}' 使用了复数形式，应使用单数形式")

    # 检查是否使用蛇形命名
    if any(c.isupper() for c in base_name):
        issues.append(
            f"表名 '{table_name}' 使用了大写字母，应使用蛇形命名（snake_case）"
        )

    # 检查必选字段
    issues.append(f"表 '{table_name}' 必须包含以下字段：id, create_time, update_time")

    # 生成建议
    if len(issues) == 1 and issues[0].startswith("表"):
        suggestions.append("✅ 表名符合 Nebula 中台规范！")
        suggestions.append("\n📋 请确保表包含必选字段：id, create_time, update_time")
    else:
        suggestions.append(f"发现 {len(issues)} 个问题：")
        suggestions.extend(issues)
        suggestions.append("\n💡 建议：")
        suggestions.append("- 表名必须以 'cx_' 开头")
        suggestions.append("- 表名使用单数形式")
        suggestions.append("- 表名使用蛇形命名（snake_case）")
        suggestions.append("- 所有表必须包含 id, create_time, update_time 字段")

    return "\n".join(suggestions)


async def check_configuration(config_content: str, config_type: str) -> str:
    """
    检查配置文件是否符合 Nebula 中台规范

    Args:
        config_content: 配置内容
        config_type: 配置类型（yml, properties）

    Returns:
        检查结果和建议
    """
    config_type = config_type.lower().strip()
    issues = []
    suggestions = []

    # 检查 YAML 配置
    if config_type == "yml":
        # 检查是否配置了雪花算法
        if "snowflake:" not in config_content.lower():
            issues.append("配置中缺少雪花算法配置（nebula.snowflake）")

        # 检查是否配置了主键类型
        if "id-type" not in config_content:
            issues.append("MyBatis Plus 配置中缺少主键类型设置（id-type: ASSIGN_ID）")

        # 检查是否配置了驼峰命名转换
        if "map-underscore-to-camel-case" not in config_content:
            issues.append(
                "MyBatis Plus 配置中缺少驼峰命名转换（map-underscore-to-camel-case）"
            )

        # 检查是否使用环境变量
        if "password:" in config_content.lower():
            lines = config_content.split("\n")
            for line in lines:
                if (
                    "password:" in line.lower()
                    and not "${" in line
                    and not "ENC(" in line
                ):
                    issues.append(
                        "敏感信息使用明文，应使用环境变量（${PASSWORD}）或加密（ENC(密文)）"
                    )

    # 检查 Properties 配置
    elif config_type == "properties":
        # 检查是否配置了雪花算法
        if "nebula.snowflake" not in config_content:
            issues.append(
                "配置中缺少雪花算法配置（nebula.snowflake.cluster-id 和 nebula.snowflake.node-id）"
            )

        # 检查是否配置了主键类型
        if "mybatis-plus.global-config.db-config.id-type" not in config_content:
            issues.append("MyBatis Plus 配置中缺少主键类型设置（ASSIGN_ID）")

        # 检查是否使用环境变量
        if "password" in config_content.lower():
            lines = config_content.split("\n")
            for line in lines:
                if "password" in line.lower() and "${" not in line:
                    issues.append("敏感信息使用明文，应使用环境变量（${PASSWORD}）")

    else:
        return f"""
# Nebula 中台配置文件检查

配置类型 "{config_type}" 未识别。

## 支持的配置类型：
1. **yml** - YAML 配置文件
2. **properties** - Properties 配置文件

请指定配置类型以进行检查。
"""

    # 生成建议
    if not issues:
        suggestions.append("✅ 配置文件符合 Nebula 中台规范！")
    else:
        suggestions.append(f"发现 {len(issues)} 个问题：")
        suggestions.extend(issues)
        suggestions.append("\n💡 建议：")
        suggestions.append(
            "- 配置雪花算法：nebula.snowflake.cluster-id 和 nebula.snowflake.node-id"
        )
        suggestions.append(
            "- 配置主键类型：mybatis-plus.global-config.db-config.id-type: ASSIGN_ID"
        )
        suggestions.append(
            "- 配置驼峰命名转换：mybatis-plus.configuration.map-underscore-to-camel-case: true"
        )
        suggestions.append("- 敏感信息使用环境变量或加密")

    return "\n".join(suggestions)


async def get_naming_convention(convention_type: str) -> str:
    """
    获取命名规范速查表

    Args:
        convention_type: 命名类型（class, method, field, package, constant, enum）

    Returns:
        命名规范速查表
    """
    convention_type = convention_type.lower().strip()

    if convention_type == "class":
        return """
# 类命名规范速查表

| 类型 | 规则 | 示例 |
|------|------|------|
| Entity | 业务名称 + `Entity` | `UserEntity`, `OrderEntity` |
| Mapper | 业务名称 + `Mapper` | `UserMapper`, `OrderMapper` |
| Service 接口 | `I` + 业务名称 + `Service` | `IUserService`, `IOrderService` |
| Service 实现 | 业务名称 + `ServiceImpl` | `UserServiceImpl`, `OrderServiceImpl` |
| Controller | 业务名称 + `Controller` | `UserController`, `OrderController` |
| DTO | 业务名称 + `Dto` | `UserDto`, `OrderDto` |
| Command | 动作 + 业务名称 + `Command` | `CreateUserCommand`, `UpdateUserCommand` |
| Query | 动作 + 业务名称 + `Query` | `GetUserByIdQuery`, `ListUsersQuery` |
| Param | 业务名称 + `Param` | `UserQueryParam`, `OrderQueryParam` |
| Req | 动作 + 业务名称 + `Req` | `CreateUserReq`, `UpdateUserReq` |
| Resp | 动作 + 业务名称 + `Resp` | `UserResp`, `OrderResp` |
| Converter | 业务名称 + `Converter` | `UserConverter`, `OrderConverter` |
| Constant | 业务名称 + `Constant` | `UserConstant`, `OrderConstant` |
| Enum | 业务名称 + `Enum` | `UserStatusEnum`, `OrderTypeEnum` |
| Exception | 业务名称 + `Exception` | `UserException`, `OrderException` |
"""

    elif convention_type == "method":
        return """
# 方法命名规范速查表

## Mapper 方法

| 前缀 | 返回类型 | 说明 | 示例 |
|------|---------|------|------|
| `find*` | `List<T>` | 查询多个实体 | `findByUsername()` |
| `get*` | `T` | 查询单个实体 | `getById()` |
| `getOpt*` | `Optional<T>` | 查询单个实体（Optional） | `getOptById()` |
| `page*` | `Page<T>` | 分页查询 | `pageQuery()` |
| `count*` | `Long` | 统计数量 | `countByStatus()` |
| `exists*` | `boolean` | 判断是否存在 | `existsByUsername()` |

## Service 方法

| 前缀 | 说明 | 示例 |
|------|------|------|
| `create*` | 创建 | `createUser()` |
| `update*` | 更新 | `updateUser()` |
| `delete*` | 删除 | `deleteUser()` |
| `get*` | 查询单个 | `getById()` |
| `list*` | 查询多个 | `listUsers()` |
| `page*` | 分页查询 | `pageUsers()` |
| `count*` | 统计数量 | `countUsers()` |
| `exists*` | 判断是否存在 | `existsByUsername()` |
"""

    elif convention_type == "field":
        return """
# 字段命名规范速查表

## Java 字段（驼峰命名）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `userName` | `String` | 用户名 |
| `createTime` | `Date` | 创建时间 |
| `updateTime` | `Date` | 更新时间 |
| `deleted` | `Boolean` | 是否删除 |
| `isDeleted` | `Boolean` | 是否删除（Boolean 建议加 is 前缀） |

## 数据库字段（蛇形命名）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `user_name` | `VARCHAR` | 用户名 |
| `create_time` | `DATETIME` | 创建时间 |
| `update_time` | `DATETIME` | 更新时间 |
| `is_deleted` | `TINYINT` | 是否删除 |

## 常量（全大写）

| 常量名 | 类型 | 说明 |
|--------|------|------|
| `DEFAULT_USERNAME` | `String` | 默认用户名 |
| `MAX_RETRY_COUNT` | `Integer` | 最大重试次数 |
| `CACHE_EXPIRE_TIME` | `Long` | 缓存过期时间 |

## 枚举值（全大写）

| 枚举值 | 说明 |
|--------|------|
| `ACTIVE` | 活跃 |
| `INACTIVE` | 非活跃 |
| `LOCKED` | 锁定 |
| `DELETED` | 已删除 |
"""

    elif convention_type == "package":
        return """
# 包命名规范速查表

## 基本规则
- 全小写
- 使用点（.）分隔
- 按功能分层组织

## 标准包结构
```
com.nebula.{module}/{layer}/{function}
```

## 包示例

| 包路径 | 说明 |
|--------|------|
| `com.nebula.uaa.api.service` | API 服务接口 |
| `com.nebula.uaa.core.service.impl` | Core Service 实现 |
| `com.nebula.uaa.core.dao.mapper` | Mapper 接口 |
| `com.nebula.uaa.core.model.entity` | 实体类 |
| `com.nebula.uaa.core.model.dto` | DTO |
| `com.nebula.uaa.core.model.command` | Command |
| `com.nebula.uaa.core.model.query` | Query |
| `com.nebula.uaa.core.model.param` | Param |
| `com.nebula.uaa.local.controller` | Controller 类 |
| `com.nebula.uaa.local.model.req` | Req |
| `com.nebula.uaa.local.model.resp` | Resp |
| `com.nebula.uaa.local.converter` | Converter |
| `com.nebula.uaa.remote.feign` | Feign 客户端 |
| `com.nebula.uaa.constant` | 常量 |
| `com.nebula.uaa.enumerate` | 枚举 |
"""

    elif convention_type == "constant":
        return """
# 常量命名规范速查表

## 命名规则
- 全大写
- 下划线分隔
- 位置：`constant/` 包

## 示例

```java
public class UserConstant {

    public static final String DEFAULT_USERNAME = "admin";
    public static final Integer MAX_USER_COUNT = 1000;
    public static final Integer USERNAME_MIN_LENGTH = 3;
    public static final Integer USERNAME_MAX_LENGTH = 20;
    public static final Long CACHE_EXPIRE_TIME = 3600L;
    public static final Integer STATUS_ACTIVE = 1;
    public static final Integer STATUS_INACTIVE = 0;
}
```

## 使用常量
```java
if (cmd.getUsername().length() < UserConstant.USERNAME_MIN_LENGTH) {
    throw new BusinessException(ErrorCode.USERNAME_LENGTH_ERROR);
}
```
"""

    elif convention_type == "enum":
        return """
# 枚举命名规范速查表

## 命名规则
- 类名：业务名称 + `Enum`
- 位置：`enumerate/` 包
- 枚举值：全大写，下划线分隔

## 示例

```java
public enum UserStatusEnum {

    ACTIVE(1, "活跃"),
    INACTIVE(0, "非活跃"),
    LOCKED(-1, "锁定"),
    DELETED(-2, "已删除");

    private final Integer code;
    private final String desc;

    UserStatusEnum(Integer code, String desc) {
        this.code = code;
        this.desc = desc;
    }

    public Integer getCode() {
        return code;
    }

    public String getDesc() {
        return desc;
    }

    public static UserStatusEnum of(Integer code) {
        for (UserStatusEnum item : values()) {
            if (item.getCode().equals(code)) {
                return item;
            }
        }
        return null;
    }
}
```

## MyBatis Plus 枚举处理
```java
public enum UserStatusEnum implements IEnum<Integer> {

    ACTIVE(1, "活跃"),
    INACTIVE(0, "非活跃"),
    LOCKED(-1, "锁定"),
    DELETED(-2, "已删除");

    private final Integer code;
    private final String desc;

    UserStatusEnum(Integer code, String desc) {
        this.code = code;
        this.desc = desc;
    }

    @Override
    public Integer getValue() {
        return code;
    }
}
```
"""

    else:
        return f"""
# Nebula 中台命名规范速查表

命名类型 "{convention_type}" 未识别。

## 支持的命名类型：
1. **class** - 类命名规范
2. **method** - 方法命名规范
3. **field** - 字段命名规范
4. **package** - 包命名规范
5. **constant** - 常量命名规范
6. **enum** - 枚举命名规范

请指定命名类型以获取详细的规范说明。
"""


class NebulaStandardsTool(BaseTool):
    """Nebula 中台编码规范工具类"""

    @classmethod
    def register(cls, mcp: FastMCP):
        """注册 Nebula 编码规范相关工具"""

        @mcp.tool()
        async def get_nebula_standard(category: str) -> str:
            """
            获取 Nebula 中台指定类别的编码规范

            Args:
                category: 规范分类，支持：
                    - architecture (架构设计规范)
                    - naming (命名规范)
                    - controller (Controller 层规范)
                    - service (Service 层规范)
                    - dao/mapper (DAO 层规范)
                    - converter (数据转换规范)
                    - api (API 设计规范)
                    - exception (异常处理规范)
                    - constant/enum (常量和枚举规范)
                    - other (其他规范)

            Returns:
                该类别的编码规范文档
            """
            return await get_standard(category)

        @mcp.tool()
        async def check_naming_convention(code: str, code_type: str) -> str:
            """
            检查代码是否符合 Nebula 命名规范

            Args:
                code: 代码片段（类定义、方法定义、字段定义等）
                code_type: 代码类型，支持：
                    - class (类命名)
                    - method (方法命名)
                    - field (字段命名)
                    - package (包命名)

            Returns:
                检查结果和建议
            """
            return await check_naming_convention(code, code_type)

        @mcp.tool()
        async def suggest_nebula_package_structure(module_type: str) -> str:
            """
            根据模块类型建议 Nebula 中台的包结构

            Args:
                module_type: 模块类型，支持：
                    - api (API 模块)
                    - core (Core 模块)
                    - local (Local 模块)
                    - remote (Remote 模块)
                    - service (Service 模块)

            Returns:
                建议的包结构
            """
            return await suggest_package_structure(module_type)

        @mcp.tool()
        async def get_nebula_layer_responsibilities(layer: str) -> str:
            """
            获取 Nebula 中台分层职责说明

            Args:
                layer: 层名称，支持：
                    - controller (Controller 层)
                    - service (Service 层)
                    - dao (DAO 层)

            Returns:
                分层职责说明
            """
            return await get_layer_responsibilities(layer)

        @mcp.tool()
        async def get_nebula_naming_convention(convention_type: str) -> str:
            """
            获取 Nebula 中台命名规范速查表

            Args:
                convention_type: 命名类型，支持：
                    - class (类命名)
                    - method (方法命名)
                    - field (字段命名)
                    - package (包命名)
                    - constant (常量命名)
                    - enum (枚举命名)

            Returns:
                命名规范速查表
            """
            return await get_naming_convention(convention_type)

        @mcp.tool()
        async def check_table_name(table_name: str) -> str:
            """
            检查数据库表名是否符合 Nebula 中台规范

            Args:
                table_name: 表名

            Returns:
                检查结果和建议
            """
            return await check_table_name(table_name)

        @mcp.tool()
        async def check_configuration(config_content: str, config_type: str) -> str:
            """
            检查配置文件是否符合 Nebula 中台规范

            Args:
                config_content: 配置内容
                config_type: 配置类型（yml、properties）

            Returns:
                检查结果和建议
            """
            return await check_configuration(config_content, config_type)
