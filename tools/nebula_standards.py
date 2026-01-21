"""
Nebula 中台 Java 后端编码规范工具模块
提供 Nebula 框架的完整编码规范、命名规范、架构设计规范等
"""

from mcp.server.fastmcp import FastMCP
from .base import BaseTool


# ==============================================================================
# 1. 架构设计规范
# ==============================================================================

ARCHITECTURE_STANDARD = """
# Nebula 中台 Java 后端架构设计规范

## 整体架构

采用传统 MVC 三层架构 + 轻量级 DDD 设计思想

```
Controller 层（local/）
  ↓
Service 层（core/service/ + internal service）
  ↓
DAO 层（core/dao/mapper/）
```

---

## 模块结构

Nebula 中台采用按业务域划分的模块化设计，支持构建单体项目和微服务项目。

### 模块类型

#### 1. API 模块（api/）
**职责**：定义基础契约（接口定义）

**包结构**：
```
nebula-uaa-api/
└── com/nebula/uaa/api/
    ├── service/               # 服务接口
    ├── model/                 # 数据模型
    │   ├── dto/               # 数据传输对象
    │   ├── command/           # 写命令
    │   └── query/             # 读查询
    ├── constant/              # 常量
    └── enumerate/             # 枚举
```

**特点**：
- 纯接口定义，无实现
- 可被 core、local、remote 模块依赖
- 包含跨模块使用的常量和枚举

---

#### 2. Core 模块（core/）
**职责**：服务实现 + 数据访问（无 Controller）

**包结构**：
```
nebula-uaa-core/
└── com/nebula/uaa/core/
    ├── service/               # Service 层
    │   └── impl/              # Service 实现
    ├── dao/
    │   └── mapper/            # MyBatis Mapper 接口
    ├── model/                 # 数据模型
    │   ├── entity/            # 实体类（对应数据库表）
    │   ├── dto/               # 数据传输对象
    │   ├── command/           # 写命令（Service 入参）
    │   ├── query/             # 读查询（Service 入参）
    │   └── param/             # DAO 查询参数（>3 参数时）
    └── config/               # 配置类
```

**特点**：
- 包含完整的业务逻辑实现
- 无 Controller 层
- 可被 local 和 remote 模块依赖

---

#### 3. Local 模块（local/）
**职责**：封装 Controller 层（单体应用使用）

**包结构**：
```
nebula-uaa-local/
└── com/nebula/uaa/local/
    ├── controller/            # Controller 层
    ├── model/
    │   ├── req/               # 请求参数（Controller 入参）
    │   └── resp/              # 响应参数（Controller 返回）
    ├── converter/             # MapStruct 转换器
    └── config/               # 配置类
```

**特点**：
- 封装 Controller 层
- 负责 HTTP 请求/响应处理
- 进行 Req/Resp → Command/Query 的转换
- 可被 service 模块依赖

---

#### 4. Remote 模块（remote/）
**职责**：远程调用客户端（微服务使用）

**包结构**：
```
nebula-uaa-remote/
└── com/nebula/uaa/remote/
    ├── feign/                 # Feign 客户端
    └── config/               # 配置类
```

**特点**：
- 引入 base-cloud 和 api 模块
- 提供 Feign 客户端
- 其他服务通过 remote 模块调用

---

#### 5. Service 模块（service/）
**职责**：独立应用（包含 local 模块）

**包结构**：
```
nebula-uaa-service/
└── com/nebula/uaa/service/
    ├── application/           # 启动类
    └── resources/            # 配置文件
```

**特点**：
- 独立部署的应用
- 包含 local 模块
- 其他服务通过 remote 模块调用本服务

---

#### 6. Base 基础模块
**职责**：提供通用能力

**子模块**：
```
base/
├── base-model/               # 基础数据模型
├── base-mybatis/             # MyBatis 配置和转换
├── base-web/                 # Web 基础配置
└── base-cloud/               # 微服务基础配置
```

---

## 分层职责

### Controller 层（local/controller/）

**职责**：
- 处理 HTTP 请求和响应
- 参数校验（使用 Jakarta Validation）
- 将 Req 转换为 Command/Query
- 调用 Service 层
- 返回 Resp

**不包含**：
- 业务逻辑
- 数据访问
- 复杂计算

---

### Service 层（core/service/）

**职责**：
- 编排业务流程
- 封装核心业务逻辑
- 事务管理
- 调用 DAO 层
- 调用外部服务（通过 API 接口）

**轻量级 DDD**：
- 可拆分 Internal Service（内部服务）
- Internal Service 封装可复用的业务逻辑
- 避免过度设计，保持简单

**示例**：
```java
// 对外接口（编排业务流程）
@Service
public class UserServiceImpl implements IUserService {
    @Autowired
    private UserInternalService userInternalService;

    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        // 调用内部服务进行业务校验
        userInternalService.validateUsername(cmd.getUsername());
        userInternalService.validateEmail(cmd.getEmail());

        // 创建用户
        User user = new User();
        // ...

        // 保存
        return userRepo.save(user);
    }
}

// 内部服务（封装可复用的业务逻辑）
@Service
public class UserInternalService {
    public void validateUsername(String username) {
        if (userRepo.existsByUsername(username)) {
            throw new BusinessException("用户名已存在");
        }
    }
}
```

---

### DAO 层（core/dao/mapper/）

**职责**：
- 数据库操作
- 单表查询（使用 MyBatis Plus）
- 复杂查询（自定义 SQL）
- 缓存管理（如果需要）

**返回类型规则**：
- 单表查询：返回 Entity
- 多表联查：返回 DTO
- 只读查询：返回 DTO

---

## 数据流转

```
HTTP 请求
  ↓
Controller 入参
  ↓
Req (local/model/req/)
  ↓
MapStruct 转换
  ↓
Command/Query (core/model/command|query/)
  ↓
Service 层
  ↓
DTO/Entity (core/model/dto|entity/)
  ↓
Mapper
  ↓
数据库
```

返回流程相反。

---

## 架构优势

### 1. 灵活性
- 同一套代码可构建单体应用或微服务
- 通过包组合实现不同部署方式

### 2. 可维护性
- 按业务域划分，职责清晰
- 模块间低耦合，易于修改

### 3. 可扩展性
- 新增业务模块只需遵循现有规范
- 可独立开发和部署

### 4. 复用性
- API 模块可被多个模块依赖
- Base 模块提供通用能力
"""

# ==============================================================================
# 2. 命名规范
# ==============================================================================

NAMING_STANDARD = """
# Nebula 中台 Java 后端命名规范

## 包命名规范

### 基本规则
- 全小写
- 使用点（.）分隔
- 按功能分层组织

### 标准包结构
```
com.nebua.{module}/{layer}/{function}
```

**示例**：
```
com.nebula.uaa.api.service          # API 服务接口
com.nebula.uaa.core.service.impl    # Core Service 实现
com.nebula.uaa.core.dao.mapper      # Mapper 接口
com.nebula.uaa.core.model.entity    # 实体类
com.nebula.uaa.local.controller     # Controller 类
com.nebula.uaa.local.converter      # MapStruct 转换器
com.nebula.uaa.remote.feign         # Feign 客户端
```

---

## 类命名规范

### 1. Entity（实体类）
**规则**：业务名称 + `Entity`

**示例**：
```java
UserEntity
OrderEntity
ProductEntity
```

**位置**：`core/model/entity/`

---

### 2. Mapper（MyBatis Mapper）
**规则**：业务名称 + `Mapper`

**示例**：
```java
UserMapper
OrderMapper
ProductMapper
```

**位置**：`core/dao/mapper/`

---

### 3. Service（服务层）

#### Service 接口
**规则**：`I` + 业务名称 + `Service`

**示例**：
```java
IUserService
IOrderService
IProductService
```

**位置**：`core/service/` 或 `api/service/`

#### Service 实现
**规则**：业务名称 + `ServiceImpl`

**示例**：
```java
UserServiceImpl
OrderServiceImpl
ProductServiceImpl
```

**位置**：`core/service/impl/`

---

### 4. Controller（控制器）
**规则**：业务名称 + `Controller`

**示例**：
```java
UserController
OrderController
ProductController
```

**位置**：`local/controller/`

---

### 5. DTO（数据传输对象）
**规则**：业务名称 + `Dto`

**示例**：
```java
UserDto
OrderDto
ProductDto
```

**位置**：`core/model/dto/` 或 `api/model/dto/`

---

### 6. Command（写命令）
**规则**：动作 + 业务名称 + `Command`

**示例**：
```java
CreateUserCommand
UpdateUserCommand
DeleteUserCommand
CreateOrderCommand
```

**位置**：`core/model/command/` 或 `api/model/command/`

---

### 7. Query（读查询）
**规则**：动作 + 业务名称 + `Query`

**示例**：
```java
GetUserByIdQuery
ListUsersQuery
PageUsersQuery
```

**位置**：`core/model/query/` 或 `api/model/query/`

---

### 8. Param（DAO 查询参数）
**规则**：业务名称 + `Param`（>3 参数时使用）

**示例**：
```java
UserQueryParam
OrderQueryParam
ProductQueryParam
```

**位置**：`core/model/param/`

**基类**：继承 `BasePageParam`（分页参数）

---

### 9. Req（请求参数）
**规则**：动作 + 业务名称 + `Req`

**示例**：
```java
CreateUserReq
UpdateUserReq
GetUserByIdReq
ListUsersReq
```

**位置**：`local/model/req/`

---

### 10. Resp（响应参数）
**规则**：动作 + 业务名称 + `Resp`

**示例**：
```java
UserResp
OrderResp
UserDetailResp
```

**位置**：`local/model/resp/`

---

### 11. Converter（转换器）
**规则**：业务名称 + `Converter`

**示例**：
```java
UserConverter
OrderConverter
ProductConverter
```

**位置**：`local/converter/` 或 `core/converter/`

---

### 12. Constant（常量类）
**规则**：业务名称 + `Constant`

**示例**：
```java
UserConstant
OrderConstant
ProductConstant
```

**位置**：`constant/`（与 service 平级）

---

### 13. Enum（枚举类）
**规则**：业务名称 + `Enum`

**示例**：
```java
UserStatusEnum
OrderStatusEnum
ProductTypeEnum
```

**位置**：`enumerate/`（与 service 平级）

---

### 14. Exception（异常类）
**规则**：业务名称 + `Exception`

**示例**：
```java
UserException
OrderException
BusinessException  # 通用业务异常
SystemException     # 通用系统异常
```

**位置**：各层的 `exception/` 包下

---

### 15. Config（配置类）
**规则**：业务名称 + `Config`

**示例**：
```java
UserConfig
OrderConfig
RedisConfig
MyBatisPlusConfig
```

**位置**：各层的 `config/` 包下

---

## 方法命名规范

### Mapper 方法

| 前缀 | 返回类型 | 说明 |
|------|---------|------|
| `find*` | `List<T>` | 查询多个实体 |
| `get*` | `T` | 查询单个实体 |
| `getOpt*` | `Optional<T>` | 查询单个实体（Optional） |
| `page*` | `Page<T>` | 分页查询 |
| `count*` | `Long` | 统计数量 |
| `exists*` | `boolean` | 判断是否存在 |

**示例**：
```java
List<UserEntity> findByUsername(String username);
UserEntity getById(Long id);
Optional<UserEntity> getOptById(Long id);
Page<UserEntity> pageQuery(UserQueryParam param);
Long countByStatus(Integer status);
boolean existsByUsername(String username);
```

---

### Service 方法

| 前缀 | 说明 |
|------|------|
| `create*` | 创建 |
| `update*` | 更新 |
| `delete*` | 删除 |
| `get*` | 查询单个 |
| `list*` | 查询多个 |
| `page*` | 分页查询 |
| `count*` | 统计数量 |
| `exists*` | 判断是否存在 |

**示例**：
```java
Long createUser(CreateUserCommand cmd);
void updateUser(UpdateUserCommand cmd);
void deleteUser(Long id);
UserDto getById(Long id);
List<UserDto> listUsers(UserQueryParam param);
Page<UserDto> pageUsers(UserQueryParam param);
```

---

## 字段命名规范

### 数据库字段
**规则**：蛇形命名（snake_case）

**示例**：
```sql
user_name
create_time
update_time
is_deleted
```

### Java 字段
**规则**：驼峰命名（camelCase）

**示例**：
```java
private String userName;
private Date createTime;
private Date updateTime;
private Boolean deleted;
```

**注意**：MyBatis Plus 开启驼峰自动转换

---

### 常量
**规则**：全大写，下划线分隔

**示例**：
```java
public static final String DEFAULT_USERNAME = "admin";
public static final Integer MAX_RETRY_COUNT = 3;
public static final Long CACHE_EXPIRE_TIME = 3600L;
```

---

### 枚举值
**规则**：全大写，下划线分隔

**示例**：
```java
public enum UserStatusEnum {
    ACTIVE,
    INACTIVE,
    LOCKED,
    DELETED
}
```

---

## 特殊命名

### Boolean 类型字段
**规则**：使用 `is`、`has`、`can` 前缀

**示例**：
```java
private Boolean isDeleted;
private Boolean hasPermission;
private Boolean canEdit;
```

### 集合类型字段
**规则**：使用复数形式

**示例**：
```java
private List<String> usernames;
private Set<Long> userIds;
private Map<String, Object> attributes;
```
"""

# ==============================================================================
# 3. Controller 层规范
# ==============================================================================

CONTROLLER_STANDARD = """
# Nebula 中台 Controller 层规范

## 职责

Controller 层负责：
- 处理 HTTP 请求和响应
- 参数校验（使用 Jakarta Validation）
- 将 Req 转换为 Command/Query
- 调用 Service 层
- 返回 Resp

Controller 层**不包含**：
- 业务逻辑
- 数据访问
- 复杂计算

---

## 注解规范

### 基础注解
```java
@RestController
@RequestMapping("/users")
@Tag(name = "用户管理", description = "用户相关接口")
public class UserController {
    // ...
}
```

---

### 方法注解

#### OpenAPI v3 注解（API 文档）
```java
@Operation(summary = "创建用户", description = "创建新用户")
@Parameters({
    @Parameter(name = "req", description = "创建用户请求参数", required = true)
})
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // ...
}
```

#### Jakarta Validation 注解（参数校验）
```java
public class CreateUserReq {

    @NotNull(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度3-20")
    @Schema(description = "用户名", required = true, example = "zhangsan")
    private String username;

    @NotNull(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    @Schema(description = "邮箱", required = true, example = "zhangsan@example.com")
    private String email;

    @NotNull(message = "年龄不能为空")
    @Min(value = 18, message = "年龄不能小于18")
    @Max(value = 120, message = "年龄不能大于120")
    @Schema(description = "年龄", required = true, example = "25")
    private Integer age;
}
```

---

## 方法设计规范

### 1. 创建
```java
@Operation(summary = "创建用户", description = "创建新用户")
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // 1. 转换 Req → Command
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);

    // 2. 调用 Service
    return userService.createUser(cmd);
}
```

---

### 2. 更新
```java
@Operation(summary = "更新用户", description = "更新用户信息")
@PutMapping("/{id}")
public void updateUser(
    @PathVariable Long id,
    @Valid @RequestBody UpdateUserReq req) {

    UpdateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);
    cmd.setId(id);

    userService.updateUser(cmd);
}
```

---

### 3. 删除
```java
@Operation(summary = "删除用户", description = "根据 ID 删除用户")
@DeleteMapping("/{id}")
public void deleteUser(@PathVariable Long id) {
    userService.deleteUser(id);
}
```

---

### 4. 查询单个
```java
@Operation(summary = "获取用户详情", description = "根据 ID 获取用户详情")
@GetMapping("/{id}")
public UserResp getUserById(@PathVariable Long id) {
    GetUserByIdQuery query = new GetUserByIdQuery(id);
    UserDto dto = userService.getById(query);

    return UserConverter.INSTANCE.toResp(dto);
}
```

---

### 5. 查询列表
```java
@Operation(summary = "查询用户列表", description = "根据条件查询用户列表")
@GetMapping
public List<UserResp> listUsers(UserQueryParam param) {
    List<UserDto> dtos = userService.listUsers(param);

    return UserConverter.INSTANCE.toRespList(dtos);
}
```

---

### 6. 分页查询
```java
@Operation(summary = "分页查询用户", description = "分页查询用户列表")
@GetMapping("/page")
public PageResp<UserResp> pageUsers(UserQueryParam param) {
    Page<UserDto> page = userService.pageUsers(param);

    PageResp<UserResp> resp = new PageResp<>();
    resp.setRecords(UserConverter.INSTANCE.toRespList(page.getRecords()));
    resp.setTotal(page.getTotal());
    resp.setCurrent(page.getCurrent());
    resp.setSize(page.getSize());

    return resp;
}
```

---

## 参数校验规范

### Jakarta Validation 常用注解

| 注解 | 说明 |
|------|------|
| `@NotNull` | 不能为 null |
| `@NotEmpty` | 集合不能为空 |
| `@NotBlank` | 字符串不能为空（去除空格后） |
| `@Size(min, max)` | 大小范围（字符串、集合） |
| `@Min(value)` | 最小值 |
| `@Max(value)` | 最大值 |
| `@Email` | 邮箱格式 |
| `@Pattern(regexp)` | 正则表达式 |
| `@Past` | 过去日期 |
| `@Future` | 未来日期 |

---

### 分组校验（不同场景使用不同校验规则）

```java
// 定义分组
public interface Create {
}

public interface Update {
}

// Req 类
public class UserReq {

    @Null(message = "创建时 ID 必须为空", groups = Create.class)
    @NotNull(message = "更新时 ID 不能为空", groups = Update.class)
    private Long id;

    @NotBlank(message = "用户名不能为空", groups = {Create.class, Update.class})
    private String username;
}

// Controller 方法
@PostMapping
public Long createUser(@Validated(Create.class) @RequestBody UserReq req) {
    // ...
}

@PutMapping("/{id}")
public void updateUser(
    @PathVariable Long id,
    @Validated(Update.class) @RequestBody UserReq req) {
    // ...
}
```

---

## 异常处理

Controller 层**不需要**捕获业务异常，由全局异常处理器统一处理。

```java
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // 不需要 try-catch，业务异常向上抛出
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);
    return userService.createUser(cmd);
}
```

---

## 日志记录

Controller 层**不需要**记录日志，由全局异常处理器统一记录错误日志。

---

## 响应体规范

Controller 方法直接返回 data 类型，由 `@RestControllerAdvice` 统一封装。

**格式**：
```json
{
  "code": 200,
  "msg": "success",
  "data": ...
}
```

**忽略统一封装**（如果需要自定义 Resp）：
```java
@IgnoreResponseAdvice
@PostMapping
public CustomResp customResp() {
    // 直接返回自定义 Resp
}
```
"""

# ==============================================================================
# 4. Service 层规范
# ==============================================================================

SERVICE_STANDARD = """
# Nebula 中台 Service 层规范

## 职责

Service 层负责：
- 编排业务流程
- 封装核心业务逻辑
- 事务管理
- 调用 DAO 层
- 调用外部服务（通过 API 接口）

---

## 轻量级 DDD

### 基本思想

- 不严格区分应用服务和领域服务
- 可在 Service 层内部拆分 Internal Service
- Internal Service 封装可复用的业务逻辑
- 避免过度设计，保持简单

---

### Service 接口

**规则**：
- 接口命名：`I{业务名称}Service`
- 接口位置：`core/service/` 或 `api/service/`

**示例**：
```java
public interface IUserService {
    Long createUser(CreateUserCommand cmd);
    void updateUser(UpdateUserCommand cmd);
    void deleteUser(Long id);
    UserDto getById(GetUserByIdQuery query);
    List<UserDto> listUsers(UserQueryParam param);
    Page<UserDto> pageUsers(UserQueryParam param);
}
```

---

### Service 实现

**规则**：
- 实现类命名：`{业务名称}ServiceImpl`
- 实现类位置：`core/service/impl/`
- 实现 `@Service` 注解

**示例**：
```java
@Service
@Slf4j
public class UserServiceImpl implements IUserService {

    @Autowired
    private IUserRepository userRepo;

    @Autowired
    private UserInternalService userInternalService;

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        log.info("创建用户，参数：{}", cmd);

        // 1. 业务校验（调用 Internal Service）
        userInternalService.validateUsername(cmd.getUsername());
        userInternalService.validateEmail(cmd.getEmail());

        // 2. 创建实体
        UserEntity entity = new UserEntity();
        entity.setUsername(cmd.getUsername());
        entity.setEmail(cmd.getEmail());
        entity.setCreateTime(new Date());

        // 3. 保存
        userRepo.save(entity);

        log.info("用户创建成功，ID：{}", entity.getId());
        return entity.getId();
    }

    @Override
    @Transactional
    public void updateUser(UpdateUserCommand cmd) {
        log.info("更新用户，参数：{}", cmd);

        UserEntity entity = userRepo.getById(cmd.getId());
        if (entity == null) {
            throw new BusinessException("用户不存在");
        }

        entity.setUsername(cmd.getUsername());
        entity.setEmail(cmd.getEmail());
        entity.setUpdateTime(new Date());

        userRepo.updateById(entity);

        log.info("用户更新成功，ID：{}", entity.getId());
    }

    @Override
    @Transactional
    public void deleteUser(Long id) {
        log.info("删除用户，ID：{}", id);

        UserEntity entity = userRepo.getById(id);
        if (entity == null) {
            throw new BusinessException("用户不存在");
        }

        userRepo.deleteById(id);

        log.info("用户删除成功，ID：{}", id);
    }

    @Override
    public UserDto getById(GetUserByIdQuery query) {
        UserEntity entity = userRepo.getById(query.getId());

        if (entity == null) {
            return null;
        }

        return UserConverter.INSTANCE.toDto(entity);
    }

    @Override
    public List<UserDto> listUsers(UserQueryParam param) {
        List<UserEntity> entities = userRepo.listByParam(param);

        return UserConverter.INSTANCE.toDtoList(entities);
    }

    @Override
    public Page<UserDto> pageUsers(UserQueryParam param) {
        Page<UserEntity> page = userRepo.pageByParam(param);

        List<UserDto> dtos = UserConverter.INSTANCE.toDtoList(page.getRecords());

        Page<UserDto> result = new Page<>(page.getCurrent(), page.getSize(), page.getTotal());
        result.setRecords(dtos);

        return result;
    }
}
```

---

### Internal Service（内部服务）

**规则**：
- 命名：`{业务名称}InternalService`
- 位置：`core/service/`
- 封装可复用的业务逻辑
- 可被多个 Service 复用

**示例**：
```java
@Service
@Slf4j
public class UserInternalService {

    @Autowired
    private IUserRepository userRepo;

    /**
     * 校验用户名唯一性
     */
    public void validateUsername(String username) {
        if (userRepo.existsByUsername(username)) {
            throw new BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS);
        }
    }

    /**
     * 校验邮箱唯一性
     */
    public void validateEmail(String email) {
        if (userRepo.existsByEmail(email)) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS);
        }
    }

    /**
     * 检查用户配额
     */
    public void checkUserQuota(Long userId) {
        Long count = userRepo.countByUserId(userId);
        if (count >= UserConstant.MAX_USER_COUNT) {
            throw new BusinessException(ErrorCode.USER_QUOTA_EXCEEDED);
        }
    }

    /**
     * 校验用户状态
     */
    public void validateUserStatus(Long userId) {
        UserEntity entity = userRepo.getById(userId);
        if (entity == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        if (entity.getStatus() == UserStatusEnum.LOCKED) {
            throw new BusinessException(ErrorCode.USER_LOCKED);
        }
    }
}
```

---

## 事务管理

### 基本规则

1. **写操作必须加 `@Transactional`**
2. **读操作不需要加 `@Transactional`**（简单查询）
3. **复杂查询（多表）可加 `@Transactional(readOnly = true)`**

---

### 事务传播行为

使用默认传播行为（`Propagation.REQUIRED`），特殊情况自行设置。

---

### 只读事务（方案 1）

**简单查询不加只读事务**：
```java
// 不加只读事务
public UserDto getById(GetUserByIdQuery query) {
    return userRepo.getById(query.getId());
}
```

**复杂查询加只读事务**：
```java
@Transactional(readOnly = true)
public OrderDetailDto getOrderDetail(Long orderId) {
    // 多表查询，需要保证一致性
    OrderEntity order = orderRepo.getById(orderId);
    List<OrderItemEntity> items = orderItemRepo.getByOrderId(orderId);
    // ...
}
```

---

### 事务示例

```java
@Service
public class OrderServiceImpl implements IOrderService {

    @Autowired
    private IOrderRepository orderRepo;
    private IOrderItemRepository orderItemRepo;

    /**
     * 创建订单（含多表操作，必须加事务）
     */
    @Override
    @Transactional
    public Long createOrder(CreateOrderCommand cmd) {
        // 1. 创建订单
        OrderEntity order = new OrderEntity();
        order.setUserId(cmd.getUserId());
        order.setAmount(cmd.getAmount());
        orderRepo.save(order);

        // 2. 创建订单项
        for (CreateOrderItemCommand itemCmd : cmd.getItems()) {
            OrderItemEntity item = new OrderItemEntity();
            item.setOrderId(order.getId());
            item.setProductId(itemCmd.getProductId());
            item.setQuantity(itemCmd.getQuantity());
            orderItemRepo.save(item);
        }

        return order.getId();
    }
}
```

---

## 日志记录

### 日志级别使用

| 级别 | 使用场景 |
|------|---------|
| `DEBUG` | 详细调试信息 |
| `INFO` | 关键业务操作 |
| `WARN` | 可恢复的异常 |
| `ERROR` | 严重错误 |

---

### 日志记录规范

1. **try-catch 异常必须输出错误日志**
2. **尽可能添加相关上下文和调用链路**
3. **业务异常可直接向上抛出或阻断**

---

### 日志示例

```java
@Service
@Slf4j
public class UserServiceImpl implements IUserService {

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        log.info("创建用户开始，参数：{}", cmd);

        try {
            // 业务逻辑
            Long userId = doCreateUser(cmd);

            log.info("创建用户成功，ID：{}", userId);
            return userId;

        } catch (BusinessException e) {
            // 业务异常，直接向上抛出
            log.warn("创建用户失败，业务异常：{}", e.getMessage());
            throw e;

        } catch (Exception e) {
            // 系统异常，输出错误日志
            log.error("创建用户失败，系统异常，参数：{}", cmd, e);
            throw new SystemException("系统异常", e);
        }
    }
}
```

---

## 异常处理

Service 层抛出业务异常，由全局异常处理器统一处理。

```java
@Service
public class UserServiceImpl implements IUserService {

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        // 业务校验失败，抛出业务异常
        if (userRepo.existsByUsername(cmd.getUsername())) {
            throw new BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS);
        }

        // 业务逻辑...

        return userId;
    }
}
```

---

## 外部服务调用

通过 API 接口调用外部服务（可能是单体内部，也可能是微服务）。

```java
@Service
public class OrderServiceImpl implements IOrderService {

    @Autowired
    private IUserServiceApi userServiceApi;  // API 接口

    @Override
    @Transactional
    public Long createOrder(CreateOrderCommand cmd) {
        // 1. 调用用户服务（外部）
        UserDto user = userServiceApi.getById(cmd.getUserId());
        if (user == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // 2. 创建订单...

        return orderId;
    }
}
```
"""

# ==============================================================================
# 5. DAO 层规范
# ==============================================================================

DAO_STANDARD = """
# Nebula 中台 DAO 层规范

## 职责

DAO 层负责：
- 数据库操作
- 单表查询（使用 MyBatis Plus）
- 复杂查询（自定义 SQL）
- 缓存管理（如果需要）

---

## Mapper 接口

### 基本规则

- 继承 MyBatis Plus 的 `BaseMapper<T>`
- 命名：`{业务名称}Mapper`
- 位置：`core/dao/mapper/`

---

### Mapper 示例

```java
public interface UserMapper extends BaseMapper<UserEntity> {

    /**
     * 根据用户名查询
     */
    UserEntity findByUsername(String username);

    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(String username);

    /**
     * 检查邮箱是否存在
     */
    boolean existsByEmail(String email);

    /**
     * 根据条件查询列表
     */
    List<UserEntity> listByParam(UserQueryParam param);

    /**
     * 根据条件分页查询
     */
    Page<UserEntity> pageByParam(Page<UserEntity> page, UserQueryParam param);

    /**
     * 统计数量
     */
    Long countByStatus(Integer status);
}
```

---

## 返回类型规范

### 单表查询 → Entity

```java
/**
 * 查询单个用户（单表查询）
 */
UserEntity getById(Long id);
```

### 多表联查 → DTO

```java
/**
 * 查询用户详情（包含角色信息，多表联查）
 */
UserDetailDto selectWithRoles(Long userId);
```

### 自定义返回字段 → DTO

```java
/**
 * 统计用户登录信息（自定义字段）
 */
UserLoginStatDto selectLoginStat(LocalDate startDate, LocalDate endDate);
```

---

## 方法命名规范

### Mapper 方法前缀

| 前缀 | 返回类型 | 说明 |
|------|---------|------|
| `find*` | `List<T>` | 查询多个实体 |
| `get*` | `T` | 查询单个实体 |
| `getOpt*` | `Optional<T>` | 查询单个实体（Optional） |
| `page*` | `Page<T>` | 分页查询 |
| `count*` | `Long` | 统计数量 |
| `exists*` | `boolean` | 判断是否存在 |

---

### 示例

```java
List<UserEntity> findByUsername(String username);
UserEntity getById(Long id);
Optional<UserEntity> getOptById(Long id);
Page<UserEntity> pageQuery(Page<UserEntity> page, UserQueryParam param);
Long countByStatus(Integer status);
boolean existsByUsername(String username);
```

---

## Param 类规范

### 使用规则

- 查询参数 > 3 个时，封装为 Param 类
- 命名：`{业务名称}Param`
- 位置：`core/model/param/`
- 继承 `BasePageParam`（如果需要分页）

---

### Param 示例

```java
/**
 * 用户查询参数
 */
public class UserQueryParam extends BasePageParam {

    @Schema(description = "用户名")
    private String username;

    @Schema(description = "邮箱")
    private String email;

    @Schema(description = "状态")
    private Integer status;

    @Schema(description = "开始时间")
    private LocalDate startDate;

    @Schema(description = "结束时间")
    private LocalDate endDate;
}
```

---

### BasePageParam（分页基类）

```java
/**
 * 分页查询基类
 */
public class BasePageParam {

    @Schema(description = "页码", example = "1")
    private Integer pageNum = 1;

    @Schema(description = "每页数量", example = "10")
    private Integer pageSize = 10;

    @Schema(description = "排序字段")
    private String orderBy;

    @Schema(description = "排序方式", example = "asc")
    private String orderDirection = "asc";

    public Integer getPageSize() {
        // 限制每页最大数量
        if (pageSize != null && pageSize > 100) {
            return 100;
        }
        return pageSize;
    }
}
```

---

## MyBatis Plus 使用

### IService 使用

推荐使用 MyBatis Plus 提供的 `IService`：

```java
public interface IUserService extends IService<UserEntity> {
    // 自定义方法...
}

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, UserEntity>
        implements IUserService {
    // 自定义方法...
}
```

---

### 基础 CRUD

使用 MyBatis Plus 提供的方法：

```java
// 插入
userMapper.insert(entity);

// 根据 ID 删除
userMapper.deleteById(id);

// 根据 ID 更新
userMapper.updateById(entity);

// 根据 ID 查询
UserEntity entity = userMapper.selectById(id);

// 查询所有
List<UserEntity> list = userMapper.selectList(null);

// 条件查询
LambdaQueryWrapper<UserEntity> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(UserEntity::getUsername, "zhangsan");
List<UserEntity> list = userMapper.selectList(wrapper);

// 分页查询
Page<UserEntity> page = new Page<>(1, 10);
userMapper.selectPage(page, wrapper);
```

---

## 自定义 SQL

### 复杂查询使用 XML

**Mapper 接口**：
```java
/**
 * 查询用户详情（包含角色）
 */
@Select("<script>" +
        "SELECT u.*, r.role_name " +
        "FROM t_user u " +
        "LEFT JOIN t_user_role ur ON u.id = ur.user_id " +
        "LEFT JOIN t_role r ON ur.role_id = r.id " +
        "WHERE u.id = #{userId} " +
        "</script>")
UserDetailDto selectWithRoles(@Param("userId") Long userId);
```

**XML 文件**（`resources/mapper/UserMapper.xml`）：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.nebula.uaa.core.dao.mapper.UserMapper">

    <select id="selectWithRoles" resultType="com.nebula.uaa.core.model.dto.UserDetailDto">
        SELECT u.*, r.role_name
        FROM t_user u
        LEFT JOIN t_user_role ur ON u.id = ur.user_id
        LEFT JOIN t_role r ON ur.role_id = r.id
        WHERE u.id = #{userId}
    </select>

</mapper>
```

---

## 缓存使用

### 缓存配置

通过配置文件切换缓存实现：
```yaml
nebula:
  cache:
    type: redis  # 或 caffeine
```

---

### @Cacheable 注解

在 Service 层使用缓存：

```java
@Service
public class UserServiceImpl implements IUserService {

    @Cacheable(value = "user", key = "#id", unless = "#result == null")
    public UserDto getById(Long id) {
        // ...
    }
}
```

---

### 缓存 Key 命名

```
user:id:123
user:username:zhangsan
config:system
```

---

## 数据库字段映射

### 驼峰 vs 蛇形

- **数据库字段**：蛇形（`user_name`）
- **Entity 字段**：驼峰（`userName`）
- **自动转换**：MyBatis Plus 开启驼峰自动转换

---

### 配置

```yaml
mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
```
"""

# ==============================================================================
# 6. 数据转换规范
# ==============================================================================

CONVERTER_STANDARD = """
# Nebula 中台数据转换规范

## 转换关系

model 子包内的所有对象都可以相互转换：

```
Req  ↔  Command/Query
Command/Query  ↔  DTO
DTO  ↔  Entity
Entity  ↔  DTO
DTO  ↔  Resp
```

---

## MapStruct 使用

### 基本规则

- 使用 MapStruct 进行对象转换
- 命名：`{业务名称}Converter`
- 位置：`converter/` 包（与 model 包平级）
- 使用静态方法（`INSTANCE`）

---

### Converter 示例

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    UserConverter INSTANCE = Mappers.getMapper(UserConverter.class);

    // Req → Command
    CreateUserCommand toCommand(CreateUserReq req);

    // Command → Req
    CreateUserReq toReq(CreateUserCommand cmd);

    // Query → DTO
    UserDto toDto(GetUserByIdQuery query);

    // Entity → DTO
    UserDto toDto(UserEntity entity);

    // DTO → Entity
    UserEntity toEntity(UserDto dto);

    // DTO → Resp
    UserResp toResp(UserDto dto);

    // List 转换
    List<UserDto> toDtoList(List<UserEntity> entities);
    List<UserResp> toRespList(List<UserDto> dtos);
}
```

---

## 转换场景

### 1. Req → Command

**Controller 层**：
```java
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // 转换 Req → Command
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);

    // 调用 Service
    return userService.createUser(cmd);
}
```

---

### 2. Entity → DTO

**Service 层**：
```java
public UserDto getById(GetUserByIdQuery query) {
    UserEntity entity = userRepo.getById(query.getId());

    // 转换 Entity → DTO
    return UserConverter.INSTANCE.toDto(entity);
}
```

---

### 3. DTO → Resp

**Controller 层**：
```java
@GetMapping("/{id}")
public UserResp getUserById(@PathVariable Long id) {
    GetUserByIdQuery query = new GetUserByIdQuery(id);
    UserDto dto = userService.getById(query);

    // 转换 DTO → Resp
    return UserConverter.INSTANCE.toResp(dto);
}
```

---

## 复杂转换

### 使用 @Mapping 注解

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    @Mapping(target = "userId", source = "id")
    @Mapping(target = "userName", source = "username")
    UserDto toDto(UserEntity entity);

    @Mapping(target = "id", source = "userId")
    @Mapping(target = "username", source = "userName")
    UserEntity toEntity(UserDto dto);
}
```

---

### 使用自定义转换方法

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    @Mapping(target = "status", source = "status", qualifiedByName = "statusToEnum")
    UserDto toDto(UserEntity entity);

    @Named("statusToEnum")
    default UserStatusEnum statusToEnum(Integer status) {
        return UserStatusEnum.of(status);
    }
}
```

---

## 集合转换

### List 转换

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    List<UserDto> toDtoList(List<UserEntity> entities);
    List<UserResp> toRespList(List<UserDto> dtos);
}
```

### Set 转换

```java
Set<UserDto> toDtoSet(Set<UserEntity> entities);
```

---

## 转换器最佳实践

### 1. 保持转换器纯粹

转换器**不包含业务逻辑**，仅进行数据转换。

```java
// ❌ 错误：包含业务逻辑
@Mapper
public interface UserConverter {
    default UserDto toDto(UserEntity entity) {
        UserDto dto = new UserDto();
        dto.setId(entity.getId());

        // 业务逻辑，不应该在这里
        if (entity.getAge() < 18) {
            dto.setAdult(false);
        } else {
            dto.setAdult(true);
        }

        return dto;
    }
}

// ✅ 正确：仅数据转换
@Mapper
public interface UserConverter {
    UserDto toDto(UserEntity entity);
}
```

---

### 2. 使用 @BeanMapping 处理 null 值

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    @BeanMapping(nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE)
    void updateEntityFromDto(UserDto dto, @MappingTarget UserEntity entity);
}
```

---

### 3. 转换器放在合适的位置

- **local/converter/**：local 模块特有的转换器
- **core/converter/**：core 模块共用的转换器

---

## 常见问题

### 1. 字段名不匹配

```java
@Mapping(source = "userId", target = "id")
UserDto toDto(UserEntity entity);
```

---

### 2. 类型转换

```java
@Mapping(source = "createTime", target = "createTime", dateFormat = "yyyy-MM-dd HH:mm:ss")
UserDto toDto(UserEntity entity);
```

---

### 3. 嵌套对象

```java
@Mapping(source = "order.id", target = "orderId")
OrderItemDto toDto(OrderItemEntity entity);
```
"""

# ==============================================================================
# 7. API 设计规范
# ==============================================================================

API_STANDARD = """
# Nebula 中台 API 设计规范

## OpenAPI v3 注解

### Controller 类注解

```java
@RestController
@RequestMapping("/users")
@Tag(name = "用户管理", description = "用户相关接口")
public class UserController {
    // ...
}
```

---

### 方法注解

```java
@Operation(summary = "创建用户", description = "创建新用户")
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // ...
}
```

---

### 参数注解

```java
public class CreateUserReq {

    @Schema(description = "用户名", required = true, example = "zhangsan")
    private String username;

    @Schema(description = "邮箱", required = true, example = "zhangsan@example.com")
    private String email;
}
```

---

## 请求参数规范

### 参数校验注解

#### 基础校验

```java
public class CreateUserReq {

    @NotNull(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度3-20")
    @Schema(description = "用户名", required = true)
    private String username;

    @NotNull(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    @Schema(description = "邮箱", required = true)
    private String email;
}
```

---

#### 复杂校验

```java
public class CreateUserReq {

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    @Schema(description = "手机号")
    private String mobile;

    @Past(message = "生日必须是过去时间")
    @Schema(description = "生日")
    private LocalDate birthday;
}
```

---

### 路径参数

```java
@GetMapping("/{id}")
public UserResp getUserById(
    @PathVariable
    @Min(value = 1, message = "ID 必须大于0")
    Long id) {
    // ...
}
```

---

### 查询参数

```java
@GetMapping
public List<UserResp> listUsers(
    @RequestParam(required = false)
    @Schema(description = "用户名")
    String username,

    @RequestParam(required = false)
    @Schema(description = "状态")
    Integer status) {
    // ...
}
```

---

## 响应体规范

### 统一响应格式

Controller 方法直接返回 data 类型，由 `@RestControllerAdvice` 统一封装。

**格式**：
```json
{
  "code": 200,
  "msg": "success",
  "data": ...
}
```

---

### 忽略统一封装

如果需要自定义 Resp，使用 `@IgnoreResponseAdvice`：

```java
@IgnoreResponseAdvice
@GetMapping("/custom")
public CustomResp customResp() {
    // 直接返回自定义 Resp
}
```

---

## 分页查询规范

### 分页参数

```java
public class UserQueryParam extends BasePageParam {

    @Schema(description = "用户名")
    private String username;

    @Schema(description = "状态")
    private Integer status;
}
```

### 分页返回

```java
@GetMapping("/page")
public PageResp<UserResp> pageUsers(UserQueryParam param) {
    Page<UserDto> page = userService.pageUsers(param);

    PageResp<UserResp> resp = new PageResp<>();
    resp.setRecords(UserConverter.INSTANCE.toRespList(page.getRecords()));
    resp.setTotal(page.getTotal());
    resp.setCurrent(page.getCurrent());
    resp.setSize(page.getSize());

    return resp;
}
```

---

## 接口设计原则

### 1. RESTful 风格

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/users` | 创建用户 |
| `GET` | `/users/{id}` | 查询单个用户 |
| `GET` | `/users` | 查询用户列表 |
| `PUT` | `/users/{id}` | 更新用户 |
| `DELETE` | `/users/{id}` | 删除用户 |

---

### 2. 版本管理

通过 URL 进行版本管理：

```
/v1/users
/v2/users
```

---

### 3. 参数规范

- 使用复数形式（`/users`）
- 使用蛇形命名（`/user-groups`）
- 路径参数使用名词（`/{id}`）
- 查询参数使用名词（`?username=zhangsan`）
"""

# ==============================================================================
# 8. 异常处理规范
# ==============================================================================

EXCEPTION_STANDARD = """
# Nebula 中台异常处理规范

## 异常体系

### 自定义异常

```java
// 基础异常
public class BaseException extends RuntimeException {
    private ErrorCode errorCode;

    public BaseException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }
}

// 业务异常
public class BusinessException extends BaseException {
    public BusinessException(ErrorCode errorCode) {
        super(errorCode);
    }
}

// 系统异常
public class SystemException extends BaseException {
    public SystemException(ErrorCode errorCode, Throwable cause) {
        super(errorCode, cause);
    }
}
```

---

## 错误码规范

### 错误码格式

按模块划分，然后递增：

```
10000-19999: 用户模块
20000-29999: 订单模块
30000-39999: 商品模块
```

---

### 错误码示例

```java
public enum ErrorCode {

    // ========== 用户模块 (10000-19999) ==========
    USERNAME_ALREADY_EXISTS(10001, "用户名已存在"),
    EMAIL_ALREADY_EXISTS(10002, "邮箱已被使用"),
    USER_NOT_FOUND(10003, "用户不存在"),
    USER_LOCKED(10004, "账号已被锁定"),
    USER_QUOTA_EXCEEDED(10005, "用户配额已用尽"),

    // ========== 订单模块 (20000-29999) ==========
    ORDER_NOT_FOUND(20001, "订单不存在"),
    ORDER_STATUS_ERROR(20002, "订单状态异常"),
    ORDER_CANNOT_CANCEL(20003, "订单无法取消"),

    // ========== 商品模块 (30000-39999) ==========
    PRODUCT_NOT_FOUND(30001, "商品不存在"),
    PRODUCT_OUT_OF_STOCK(30002, "商品库存不足");

    private final Integer code;
    private final String message;

    ErrorCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }

    public Integer getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
```

---

### i18n 文件

`resources/i18n/messages_zh_CN.properties`：
```properties
# 用户模块
error.username.already.exists=用户名已存在
error.email.already.used=邮箱已被使用
error.user.not.found=用户不存在
error.user.locked=账号已被锁定

# 订单模块
error.order.not.found=订单不存在
error.order.status.error=订单状态异常

# 商品模块
error.product.not.found=商品不存在
error.product.out.of.stock=商品库存不足
```

---

## 全局异常处理

### RestControllerAdvice

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    /**
     * 业务异常
     */
    @ExceptionHandler(BusinessException.class)
    public Resp<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常：{}", e.getMessage());
        return Resp.error(e.getErrorCode().getCode(), e.getErrorCode().getMessage());
    }

    /**
     * 系统异常
     */
    @ExceptionHandler(SystemException.class)
    public Resp<Void> handleSystemException(SystemException e) {
        log.error("系统异常", e);
        return Resp.error(e.getErrorCode().getCode(), "系统异常，请联系管理员");
    }

    /**
     * 参数校验异常
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Resp<Void> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));
        log.warn("参数校验失败：{}", message);
        return Resp.error(400, message);
    }

    /**
     * 其他异常
     */
    @ExceptionHandler(Exception.class)
    public Resp<Void> handleException(Exception e) {
        log.error("未知异常", e);
        return Resp.error(500, "系统异常，请联系管理员");
    }
}
```

---

## 异常抛出规范

### Controller 层

**不捕获异常**，由全局异常处理器处理：

```java
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    // 不需要 try-catch，异常向上抛出
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);
    return userService.createUser(cmd);
}
```

---

### Service 层

抛出业务异常：

```java
@Service
public class UserServiceImpl implements IUserService {

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        // 业务校验失败，抛出业务异常
        if (userRepo.existsByUsername(cmd.getUsername())) {
            throw new BusinessException(ErrorCode.USERNAME_ALREADY_EXISTS);
        }

        // 业务逻辑...

        return userId;
    }
}
```

---

### catch 异常处理

**catch 异常时必须输出错误日志**，并尽可能添加相关上下文和调用链路：

```java
@Override
@Transactional
public Long createUser(CreateUserCommand cmd) {
    log.info("创建用户开始，参数：{}", cmd);

    try {
        // 业务逻辑...
        Long userId = doCreateUser(cmd);

        log.info("创建用户成功，ID：{}", userId);
        return userId;

    } catch (BusinessException e) {
        // 业务异常，直接向上抛出
        log.warn("创建用户失败，业务异常：{}", e.getMessage());
        throw e;

    } catch (Exception e) {
        // 系统异常，输出错误日志
        log.error("创建用户失败，系统异常，参数：{}", cmd, e);
        throw new SystemException(ErrorCode.SYSTEM_ERROR, e);
    }
}
```

---

## 日志规范

### 日志级别

| 级别 | 使用场景 |
|------|---------|
| `DEBUG` | 详细调试信息 |
| `INFO` | 关键业务操作 |
| `WARN` | 可恢复的异常 |
| `ERROR` | 严重错误 |

---

### 日志示例

```java
@Service
@Slf4j
public class UserServiceImpl implements IUserService {

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        log.info("创建用户开始，参数：{}", cmd);

        try {
            // 业务逻辑...
            Long userId = doCreateUser(cmd);

            log.info("创建用户成功，ID：{}", userId);
            return userId;

        } catch (BusinessException e) {
            log.warn("创建用户失败，业务异常：{}", e.getMessage());
            throw e;

        } catch (Exception e) {
            log.error("创建用户失败，系统异常，参数：{}", cmd, e);
            throw new SystemException(ErrorCode.SYSTEM_ERROR, e);
        }
    }
}
```
"""

# ==============================================================================
# 9. 常量和枚举规范
# ==============================================================================

CONSTANT_ENUM_STANDARD = """
# Nebula 中台常量和枚举规范

## 常量类

### 命名规范

- 命名：`{业务名称}Constant`
- 位置：`constant/` 包（与 service 平级）

---

### 常量类示例

```java
/**
 * 用户常量
 */
public class UserConstant {

    /**
     * 默认用户名
     */
    public static final String DEFAULT_USERNAME = "admin";

    /**
     * 最大用户数量
     */
    public static final Integer MAX_USER_COUNT = 1000;

    /**
     * 用户名最小长度
     */
    public static final Integer USERNAME_MIN_LENGTH = 3;

    /**
     * 用户名最大长度
     */
    public static final Integer USERNAME_MAX_LENGTH = 20;

    /**
     * 缓存过期时间（秒）
     */
    public static final Long CACHE_EXPIRE_TIME = 3600L;

    /**
     * 用户状态枚举值
     */
    public static final Integer STATUS_ACTIVE = 1;
    public static final Integer STATUS_INACTIVE = 0;
    public static final Integer STATUS_LOCKED = -1;
}
```

---

### 使用常量

```java
@Service
public class UserServiceImpl implements IUserService {

    @Override
    public Long createUser(CreateUserCommand cmd) {
        // 校验用户名长度
        if (cmd.getUsername().length() < UserConstant.USERNAME_MIN_LENGTH
                || cmd.getUsername().length() > UserConstant.USERNAME_MAX_LENGTH) {
            throw new BusinessException(ErrorCode.USERNAME_LENGTH_ERROR);
        }

        // 校验用户配额
        Long count = userRepo.countAll();
        if (count >= UserConstant.MAX_USER_COUNT) {
            throw new BusinessException(ErrorCode.USER_QUOTA_EXCEEDED);
        }

        // 业务逻辑...

        return userId;
    }
}
```

---

## 枚举类

### 命名规范

- 命名：`{业务名称}Enum`
- 位置：`enumerate/` 包（与 service 平级）

---

### 枚举类示例

```java
/**
 * 用户状态枚举
 */
public enum UserStatusEnum {

    /**
     * 活跃
     */
    ACTIVE(1, "活跃"),

    /**
     * 非活跃
     */
    INACTIVE(0, "非活跃"),

    /**
     * 锁定
     */
    LOCKED(-1, "锁定"),

    /**
     * 已删除
     */
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

    /**
     * 根据值获取枚举
     */
    public static UserStatusEnum of(Integer code) {
        for (UserStatusEnum item : values()) {
            if (item.getCode().equals(code)) {
                return item;
            }
        }
        return null;
    }

    /**
     * 判断是否是某个状态
     */
    public boolean is(Integer code) {
        return this.getCode().equals(code);
    }
}
```

---

### 枚举使用示例

```java
@Service
public class UserServiceImpl implements IUserService {

    @Override
    public void updateUserStatus(Long userId, Integer status) {
        UserEntity entity = userRepo.getById(userId);
        if (entity == null) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }

        // 检查用户状态
        UserStatusEnum statusEnum = UserStatusEnum.of(status);
        if (statusEnum == null) {
            throw new BusinessException(ErrorCode.USER_STATUS_ERROR);
        }

        // 检查是否可以修改
        if (statusEnum.is(UserStatusEnum.LOCKED.getCode())) {
            throw new BusinessException(ErrorCode.USER_LOCKED);
        }

        entity.setStatus(status);
        userRepo.updateById(entity);
    }
}
```

---

## 常量 vs 枚举

### 使用常量的场景

- 配置值（如最大数量、过期时间）
- 固定的字符串（如默认用户名）
- 不需要扩展的固定值

---

### 使用枚举的场景

- 状态值（如用户状态、订单状态）
- 类型值（如用户类型、商品类型）
- 需要扩展的固定值

---

## MyBatis Plus 枚举处理

### 配置

```yaml
mybatis-plus:
  configuration:
    default-enum-type-handler: com.baomidou.mybatisplus.core.handlers.MybatisEnumTypeHandler
```

### 枚举实现 IEnum 接口

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

    public String getDesc() {
        return desc;
    }
}
```

### 实体类使用枚举

```java
public class UserEntity {

    private Long id;
    private String username;

    /**
     * 用户状态
     */
    private UserStatusEnum status;
}
```
"""

# ==============================================================================
# 10. 其他规范
# ==============================================================================

OTHER_STANDARD = """
# Nebula 中台其他规范

## MyBatis Plus 使用规范

### IService 使用

推荐使用 MyBatis Plus 提供的 `IService`：

```java
public interface IUserService extends IService<UserEntity> {
    // 自定义方法...
}

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, UserEntity>
        implements IUserService {
    // 自定义方法...
}
```

---

### 基础 CRUD

```java
// 插入
userMapper.insert(entity);

// 根据 ID 删除
userMapper.deleteById(id);

// 根据 ID 更新
userMapper.updateById(entity);

// 根据 ID 查询
UserEntity entity = userMapper.selectById(id);

// 查询所有
List<UserEntity> list = userMapper.selectList(null);

// 条件查询
LambdaQueryWrapper<UserEntity> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(UserEntity::getUsername, "zhangsan");
List<UserEntity> list = userMapper.selectList(wrapper);

// 分页查询
Page<UserEntity> page = new Page<>(1, 10);
userMapper.selectPage(page, wrapper);
```

---

## 缓存使用规范

### 缓存配置

通过配置文件切换缓存实现：

```yaml
nebula:
  cache:
    type: redis  # 或 caffeine
```

---

### @Cacheable 注解

```java
@Service
public class UserServiceImpl implements IUserService {

    @Cacheable(value = "user", key = "#id", unless = "#result == null")
    public UserDto getById(Long id) {
        // ...
    }
}
```

---

### 缓存 Key 命名

```
user:id:123
user:username:zhangsan
config:system
```

---

### 自定义缓存过期时间

```java
@Cacheable(value = "user", key = "#id",
           unless = "#result == null",
           cacheResolver = "customCacheResolver")
public UserDto getById(Long id) {
    // ...
}
```

---

## 数据库字段映射

### 驼峰 vs 蛇形

- **数据库字段**：蛇形（`user_name`）
- **Entity 字段**：驼峰（`userName`）
- **自动转换**：MyBatis Plus 开启驼峰自动转换

---

### 配置

```yaml
mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
```

---

## 代码风格规范

### 基本规范

1. **缩进**：使用 4 个空格
2. **行宽**：每行最多 120 个字符
3. **空行**：类之间空 2 行，方法之间空 1 行
4. **编码**：使用 UTF-8 编码

---

### Lombok 使用

推荐使用 Lombok 简化代码：

```java
@Data                      // getter/setter/equals/hashCode/toString
@AllArgsConstructor       // 全参构造器
@NoArgsConstructor        // 无参构造器
@Builder                  // 建造者模式
@Slf4j                    // 日志
public class UserEntity {
    private Long id;
    private String username;
    private String email;
}
```

---

### Optional 使用

推荐使用 `Optional` 处理可能为 null 的值：

```java
public Optional<UserEntity> getUserById(Long id) {
    return Optional.ofNullable(userRepo.selectById(id));
}

public UserDto getUserDtoById(Long id) {
    return getUserById(id)
            .map(entity -> UserConverter.INSTANCE.toDto(entity))
            .orElse(null);
}
```

---

### 注释规范

#### 类注释

```java
/**
 * 用户服务实现
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Service
public class UserServiceImpl implements IUserService {
    // ...
}
```

---

#### 方法注释

```java
/**
 * 创建用户
 *
 * @param cmd 创建用户命令
 * @return 用户 ID
 */
@Override
@Transactional
public Long createUser(CreateUserCommand cmd) {
    // ...
}
```

---

#### 字段注释

```java
/**
 * 用户 ID
 */
private Long id;

/**
 * 用户名
 */
private String username;
```

---

### Model 类 JavaDoc 规范

#### Model 子包分类

| 包路径 | 是否需要 JavaDoc | 说明 |
|--------|---------------|------|
| `model/entity/` | ✅ 必须 | 实体类（对应数据库表） |
| `model/dto/` | ✅ 必须 | 数据传输对象 |
| `model/command/` | ✅ 必须 | 写命令（Service 入参） |
| `model/query/` | ✅ 必须 | 读查询（Service 入参） |
| `model/param/` | ✅ 必须 | DAO 查询参数 |
| `model/req/` | ❌ 不需要 | Controller 请求参数（使用 `@Schema` 注解） |
| `model/resp/` | ❌ 不需要 | Controller 响应参数（使用 `@Schema` 注解） |

---

#### Entity JavaDoc 规范

Entity 类必须包含完整的 JavaDoc，说明类的作用和数据库表对应关系。

**示例**：

```java
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.util.Date;

/**
 * 用户实体类
 *
 * <p>对应数据库表：cx_user</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@TableName("cx_user")
public class UserEntity {

    /**
     * 主键
     */
    private Long id;

    /**
     * 用户名
     */
    private String userName;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 手机号
     */
    private String mobile;

    /**
     * 状态（1：活跃，0：非活跃）
     */
    private Integer status;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除（0：否，1：是）
     */
    private Boolean deleted;
}
```

**规范说明**：
- **类注释**：包含类描述、对应表名、作者、版本信息
- **字段注释**：每个字段都必须有注释，说明字段用途
- **枚举类型**：如果有枚举类型，需要列出所有可选值

---

#### DTO JavaDoc 规范

DTO 类必须包含 JavaDoc，说明数据传输对象的作用。

**示例**：

```java
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.util.Date;

/**
 * 用户数据传输对象
 *
 * <p>用于 Service 层返回用户信息</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@Schema(description = "用户数据传输对象")
public class UserDto {

    /**
     * 用户 ID
     */
    @Schema(description = "用户 ID")
    private Long id;

    /**
     * 用户名
     */
    @Schema(description = "用户名")
    private String userName;

    /**
     * 邮箱
     */
    @Schema(description = "邮箱")
    private String email;

    /**
     * 手机号
     */
    @Schema(description = "手机号")
    private String mobile;

    /**
     * 状态（1：活跃，0：非活跃）
     */
    @Schema(description = "状态（1：活跃，0：非活跃）")
    private Integer status;

    /**
     * 创建时间
     */
    @Schema(description = "创建时间")
    private Date createTime;

    /**
     * 更新时间
     */
    @Schema(description = "更新时间")
    private Date updateTime;
}
```

---

#### Command JavaDoc 规范

Command 类必须包含 JavaDoc，说明写操作的参数含义。

**示例**：

```java
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * 创建用户命令
 *
 * <p>用于创建用户操作</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@Schema(description = "创建用户命令")
public class CreateUserCommand {

    /**
     * 用户名
     *
     * <p>长度：3-20</p>
     * <p>唯一性：必须唯一</p>
     */
    @NotNull(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度3-20")
    @Schema(description = "用户名", required = true, example = "zhangsan")
    private String userName;

    /**
     * 邮箱
     *
     * <p>格式：有效的邮箱地址</p>
     * <p>唯一性：必须唯一</p>
     */
    @NotNull(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    @Schema(description = "邮箱", required = true, example = "zhangsan@example.com")
    private String email;

    /**
     * 手机号
     *
     * <p>格式：11 位手机号</p>
     * <p>可选性：可为空</p>
     */
    @Schema(description = "手机号", example = "13800138000")
    private String mobile;

    /**
     * 状态
     *
     * <p>可选值：1（活跃），0（非活跃）</p>
     * <p>默认值：1</p>
     */
    @Schema(description = "状态（1：活跃，0：非活跃）", example = "1")
    private Integer status = 1;
}
```

---

#### Query JavaDoc 规范

Query 类必须包含 JavaDoc，说明查询条件的含义。

**示例**：

```java
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.time.LocalDate;

/**
 * 获取用户详情查询
 *
 * <p>用于根据用户 ID 查询用户详情</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@Schema(description = "获取用户详情查询")
public class GetUserByIdQuery {

    /**
     * 用户 ID
     *
     * <p>必填性：必填</p>
     * <p>格式：有效的雪花算法 ID</p>
     */
    @NotNull(message = "用户 ID 不能为空")
    @Schema(description = "用户 ID", required = true, example = "1234567890123456789")
    private Long id;
}
```

**批量查询示例**：

```java
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.time.LocalDate;

/**
 * 查询用户列表查询
 *
 * <p>用于根据条件查询用户列表</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@Schema(description = "查询用户列表查询")
public class ListUsersQuery {

    /**
     * 用户名
     *
     * <p>查询类型：模糊匹配</p>
     * <p>可选性：可选</p>
     */
    @Schema(description = "用户名（模糊匹配）", example = "zhang")
    private String userName;

    /**
     * 邮箱
     *
     * <p>查询类型：模糊匹配</p>
     * <p>可选性：可选</p>
     */
    @Schema(description = "邮箱（模糊匹配）", example = "example.com")
    private String email;

    /**
     * 状态
     *
     * <p>查询类型：精确匹配</p>
     * <p>可选性：可选</p>
     * <p>可选值：1（活跃），0（非活跃）</p>
     */
    @Schema(description = "状态（1：活跃，0：非活跃）", example = "1")
    private Integer status;

    /**
     * 开始时间
     *
     * <p>查询类型：范围查询（>=）</p>
     * <p>可选性：可选</p>
     * <p>格式：yyyy-MM-dd</p>
     */
    @Schema(description = "开始时间（yyyy-MM-dd）", example = "2024-01-01")
    private LocalDate startDate;

    /**
     * 结束时间
     *
     * <p>查询类型：范围查询（<=）</p>
     * <p>可选性：可选</p>
     * <p>格式：yyyy-MM-dd</p>
     */
    @Schema(description = "结束时间（yyyy-MM-dd）", example = "2024-12-31")
    private LocalDate endDate;
}
```

---

#### Param JavaDoc 规范

Param 类必须包含 JavaDoc，说明 DAO 查询参数的含义。

**示例**：

```java
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;
import com.nebula.base.mybatis.model.BasePageParam;
import java.time.LocalDate;

/**
 * 用户查询参数
 *
 * <p>用于 DAO 层查询用户</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
@Data
@EqualsAndHashCode(callSuper = true)
@Schema(description = "用户查询参数")
public class UserQueryParam extends BasePageParam {

    /**
     * 用户名
     *
     * <p>查询类型：LIKE 模糊查询</p>
     */
    @Schema(description = "用户名")
    private String userName;

    /**
     * 邮箱
     *
     * <p>查询类型：LIKE 模糊查询</p>
     */
    @Schema(description = "邮箱")
    private String email;

    /**
     * 状态
     *
     * <p>查询类型：= 精确查询</p>
     * <p>可选值：1（活跃），0（非活跃）</p>
     */
    @Schema(description = "状态（1：活跃，0：非活跃）")
    private Integer status;

    /**
     * 开始时间
     *
     * <p>查询类型：>= 范围查询</p>
     */
    @Schema(description = "开始时间")
    private LocalDate startDate;

    /**
     * 结束时间
     *
     * <p>查询类型：<= 范围查询</p>
     */
    @Schema(description = "结束时间")
    private LocalDate endDate;

    /**
     * 用户名列表
     *
     * <p>查询类型：IN 查询</p>
     * <p>使用场景：批量查询多个用户</p>
     */
    @Schema(description = "用户名列表")
    private List<String> userNameList;
}
```

---

#### JavaDoc 规范总结

**类注释规范**：

| 元素 | 必填性 | 说明 | 示例 |
|------|--------|------|------|
| 类描述 | ✅ 必须 | 说明类的作用 | `用户实体类` |
| 对应表名 | ✅ 必须（Entity） | 说明对应的数据库表 | `对应数据库表：cx_user` |
| 用途说明 | ✅ 必须 | 说明类的使用场景 | `用于 Service 层返回用户信息` |
| 作者 | ✅ 必须 | `@author` | `@author zhangsan` |
| 版本 | ✅ 必须 | `@since` | `@since 1.0.0` |

---

**字段注释规范**：

| 元素 | 必填性 | 说明 | 示例 |
|------|--------|------|------|
| 字段描述 | ✅ 必须 | 说明字段的用途 | `用户名` |
| 长度限制 | ⚠️ 建议 | 说明长度限制 | `长度：3-20` |
| 唯一性 | ⚠️ 建议 | 说明是否唯一 | `唯一性：必须唯一` |
| 可选值 | ⚠️ 建议 | 列出可选值 | `可选值：1（活跃），0（非活跃）` |
| 查询类型 | ⚠️ 建议（Query/Param） | 说明查询方式 | `查询类型：LIKE 模糊查询` |
| 使用场景 | ⚠️ 建议 | 说明使用场景 | `使用场景：批量查询多个用户` |

---

**JavaDoc 注解使用**：

```java
/**
 * 用户实体类
 *
 * <p>对应数据库表：cx_user</p>
 * <p>支持用户的基本信息管理</p>
 *
 * @author zhangsan
 * @since 1.0.0
 */
```

- 使用 `<p>` 标签分段
- 多行说明时使用多个 `<p>` 标签
- 注解（`@author`、`@since`）放在最后

---

## 测试规范

### 单元测试

```java
@SpringBootTest
public class UserServiceTest {

    @Autowired
    private IUserService userService;

    @Test
    public void testCreateUser() {
        CreateUserCommand cmd = new CreateUserCommand();
        cmd.setUsername("zhangsan");
        cmd.setEmail("zhangsan@example.com");

        Long userId = userService.createUser(cmd);

        assertNotNull(userId);
    }
}
```

---

### 集成测试

```java
@SpringBootTest
@Transactional
public class UserServiceIntegrationTest {

    @Autowired
    private IUserService userService;

    @Test
    public void testCreateUser() {
        // 测试逻辑...
    }
}
```
"""


# ==============================================================================
# 11. 数据库设计规范
# ==============================================================================

DATABASE_DESIGN_STANDARD = """
# Nebula 中台数据库设计规范

## 表命名规范

### 基本规则

- **表前缀**：所有中台表必须以 `cx_` 为前缀
- **单数形式**：表名使用单数形式，不使用复数
- **命名风格**：使用 snake_case（蛇形命名）
- **业务含义**：表名应清晰表达业务含义

### 表名示例

| 表名 | 说明 | 是否符合规范 |
|------|------|------------|
| `cx_user` | 用户表 | ✅ 符合 |
| `cx_order` | 订单表 | ✅ 符合 |
| `cx_order_item` | 订单明细表 | ✅ 符合 |
| `t_user` | 用户表 | ❌ 不符合（缺少 cx_ 前缀） |
| `cx_users` | 用户表 | ❌ 不符合（使用复数形式） |
| `user` | 用户表 | ❌ 不符合（缺少 cx_ 前缀） |

---

## 字段命名规范

### 基本规则

- **命名风格**：使用 snake_case（蛇形命名）
- **小写字母**：全部使用小写字母
- **下划线分隔**：使用下划线分隔单词
- **业务含义**：字段名应清晰表达业务含义

### 字段示例

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | BIGINT | 主键 |
| `user_name` | VARCHAR | 用户名 |
| `email` | VARCHAR | 邮箱 |
| `mobile` | VARCHAR | 手机号 |
| `create_time` | DATETIME | 创建时间 |
| `update_time` | DATETIME | 更新时间 |
| `is_deleted` | TINYINT(1) | 是否删除 |

---

## 必选字段规范

### 所有表必须包含的字段

所有业务表必须包含以下字段：

#### 1. 主键字段

```sql
`id` BIGINT NOT NULL COMMENT '主键'
```

- **类型**：BIGINT
- **是否为空**：NOT NULL
- **命名**：`id`
- **取值**：使用雪花算法生成
- **说明**：主键，base-mybatis 包中提供雪花算法支持

---

#### 2. 审计字段

```sql
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
`update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
```

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `create_time` | DATETIME | CURRENT_TIMESTAMP | 创建时间，不可为空 |
| `update_time` | DATETIME | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间，不可为空，自动更新 |

---

#### 3. 逻辑删除字段（可选，但建议）

```sql
`is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除（0：否，1：是）'
```

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `is_deleted` | TINYINT(1) | 0 | 是否删除，0 表示未删除，1 表示已删除 |

---

## 完整建表示例

### 标准建表语句

```sql
CREATE TABLE `cx_user` (
  `id` BIGINT NOT NULL COMMENT '主键',
  `user_name` VARCHAR(50) NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `mobile` VARCHAR(20) COMMENT '手机号',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态（1：活跃，0：非活跃）',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除（0：否，1：是）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name` (`user_name`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_mobile` (`mobile`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

## 主键规范

### 使用雪花算法

Nebula 中台使用雪花算法生成主键 ID，由 `base-mybatis` 包提供支持。

#### 雪花算法特点

- 全局唯一
- 趋势递增
- 高性能
- 分布式友好

#### 配置雪花算法

在 `application.yml` 中配置雪花算法的集群 ID 和节点 ID：

```yaml
mybatis-plus:
  global-config:
    db-config:
      id-type: ASSIGN_ID  # 使用雪花算法

nebula:
  snowflake:
    cluster-id: 1        # 集群 ID（1-31）
    node-id: 1           # 节点 ID（1-31）
```

#### 参数说明

| 参数 | 说明 | 取值范围 | 必填 |
|------|------|---------|------|
| `cluster-id` | 集群 ID | 1-31 | 是 |
| `node-id` | 节点 ID | 1-31 | 是 |

**注意**：同一集群内，所有节点的 `cluster-id` 必须相同，但 `node-id` 必须唯一。

---

## 字段类型规范

### 字符串类型

| 类型 | 长度 | 使用场景 | 示例 |
|------|------|---------|------|
| VARCHAR(50) | 50 | 短字符串 | 用户名 |
| VARCHAR(100) | 100 | 中等长度字符串 | 邮箱 |
| VARCHAR(500) | 500 | 长字符串 | 地址 |
| TEXT | 65535 | 超长文本 | 备注信息 |

---

### 数值类型

| 类型 | 说明 | 使用场景 | 示例 |
|------|------|---------|------|
| BIGINT | 大整数 | 主键 ID、金额（分） | `id`、`amount` |
| INT | 整数 | 数量、状态、类型 | `count`、`status` |
| TINYINT | 小整数 | 布尔值、枚举值 | `is_deleted`、`status` |
| DECIMAL(10,2) | 小数 | 金额（元） | `price` |

---

### 日期时间类型

| 类型 | 说明 | 使用场景 | 示例 |
|------|------|---------|------|
| DATETIME | 日期时间 | 时间戳 | `create_time`、`update_time` |
| DATE | 日期 | 日期 | `birthday` |

---

## 索引规范

### 索引命名规范

| 索引类型 | 命名规则 | 示例 |
|---------|---------|------|
| 主键索引 | `PRIMARY` | `PRIMARY KEY (id)` |
| 唯一索引 | `uk_字段名` | `uk_user_name` |
| 普通索引 | `idx_字段名` | `idx_mobile` |
| 联合索引 | `idx_字段1_字段2` | `idx_user_name_status` |

---

### 索引设计原则

1. **主键索引**：所有表必须有主键索引
2. **唯一索引**：需要唯一约束的字段（如用户名、邮箱）
3. **普通索引**：频繁查询的字段
4. **联合索引**：经常一起查询的多个字段（遵循最左前缀原则）
5. **避免过多索引**：索引过多会影响写入性能

---

### 索引示例

```sql
-- 主键索引
PRIMARY KEY (`id`)

-- 唯一索引
UNIQUE KEY `uk_user_name` (`user_name`)
UNIQUE KEY `uk_email` (`email`)

-- 普通索引
KEY `idx_mobile` (`mobile`)
KEY `idx_create_time` (`create_time`)

-- 联合索引
KEY `idx_user_name_status` (`user_name`, `status`)
```

---

## Entity 类规范

### 基本规则

Entity 类名使用 PascalCase，以 `Entity` 结尾。

### Entity 示例

```java
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.util.Date;

@Data
@TableName("cx_user")
public class UserEntity {

    /**
     * 主键（使用雪花算法）
     */
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    /**
     * 用户名
     */
    private String userName;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 手机号
     */
    private String mobile;

    /**
     * 状态（1：活跃，0：非活跃）
     */
    private Integer status;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除（0：否，1：是）
     */
    @TableField("is_deleted")
    private Boolean deleted;
}
```

---

## MyBatis Plus 自动填充配置

### 配置自动填充

在 `config/MyBatisPlusConfig.java` 中配置字段自动填充：

```java
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.stereotype.Component;
import java.util.Date;

@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", Date.class, new Date());
        this.strictInsertFill(metaObject, "updateTime", Date.class, new Date());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", Date.class, new Date());
    }
}
```

---

## 数据库设计最佳实践

### 1. 使用合适的字段类型

```sql
-- ❌ 错误：使用 VARCHAR 存储金额
`price` VARCHAR(20) NOT NULL COMMENT '价格'

-- ✅ 正确：使用 DECIMAL 存储金额
`price` DECIMAL(10,2) NOT NULL COMMENT '价格'
```

---

### 2. 避免使用 NULL

```sql
-- ❌ 错误：允许 NULL
`user_name` VARCHAR(50) NULL COMMENT '用户名'

-- ✅ 正确：设置默认值
`user_name` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '用户名'
```

---

### 3. 使用逻辑删除

```sql
-- ❌ 错误：物理删除
DELETE FROM cx_user WHERE id = 12345;

-- ✅ 正确：逻辑删除
UPDATE cx_user SET is_deleted = 1 WHERE id = 12345;
```

---

### 4. 使用注释

```sql
-- ✅ 正确：所有字段和表都添加注释
CREATE TABLE `cx_user` (
  `id` BIGINT NOT NULL COMMENT '主键',
  `user_name` VARCHAR(50) NOT NULL COMMENT '用户名',
  ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

### 5. 设置字符集

```sql
-- ✅ 正确：使用 utf8mb4 字符集
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```
"""


# ==============================================================================
# 12. 配置管理规范
# ==============================================================================

CONFIGURATION_MANAGEMENT_STANDARD = """
# Nebula 中台配置管理规范

## 配置文件结构

### 目录结构

```
src/main/resources/
├── application.yml              # 通用配置
├── application-dev.yml          # 开发环境配置
├── application-test.yml         # 测试环境配置
├── application-prod.yml         # 生产环境配置
├── logback.xml                  # 日志配置
└── banner.txt                   # 启动横幅
```

---

### 环境配置切换

在 `application.yml` 中激活对应的环境配置：

```yaml
spring:
  profiles:
    active: dev  # dev、test、prod
```

---

## 通用配置（application.yml）

### 基础配置

```yaml
spring:
  application:
    name: nebula-uaa-service

  profiles:
    active: @profiles.active@  # 使用 Maven profile 或环境变量

  jackson:
    time-zone: GMT+8
    date-format: yyyy-MM-dd HH:mm:ss
    default-property-inclusion: non_null

  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 50MB

server:
  port: 8080
  servlet:
    context-path: /api
  tomcat:
    threads:
      max: 200
      min-spare: 10

logging:
  level:
    root: INFO
    com.nebula: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n"
```

---

## 环境配置规范

### 开发环境（application-dev.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/nebula_dev?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

  redis:
    host: localhost
    port: 6379
    password:
    database: 0

nebula:
  snowflake:
    cluster-id: 1
    node-id: 1

logging:
  level:
    com.nebula: DEBUG
    org.springframework: DEBUG
```

---

### 测试环境（application-test.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://test-db.example.com:3306/nebula_test?useUnicode=true&characterEncoding=utf8&useSSL=true&serverTimezone=GMT%2B8
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver

  redis:
    host: test-redis.example.com
    port: 6379
    password: ${REDIS_PASSWORD}
    database: 0

nebula:
  snowflake:
    cluster-id: 2
    node-id: 1

logging:
  level:
    com.nebula: INFO
    org.springframework: WARN
```

---

### 生产环境（application-prod.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://prod-db.example.com:3306/nebula_prod?useUnicode=true&characterEncoding=utf8&useSSL=true&serverTimezone=GMT%2B8
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  redis:
    host: prod-redis.example.com
    port: 6379
    password: ${REDIS_PASSWORD}
    database: 0
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5

nebula:
  snowflake:
    cluster-id: 3
    node-id: 1

logging:
  level:
    com.nebula: WARN
    org.springframework: WARN
  file:
    name: /var/log/nebula/nebula-uaa-service.log
    max-size: 100MB
    max-history: 30
```

---

## 敏感配置管理

### 使用环境变量

生产环境的敏感配置（数据库密码、Redis 密码、第三方密钥等）必须通过环境变量传递，不能硬编码在配置文件中。

#### 环境变量示例

```bash
# 数据库配置
export DB_USERNAME=nebula_prod
export DB_PASSWORD=your_secure_password

# Redis 配置
export REDIS_PASSWORD=your_redis_password

# 第三方密钥
export ALIYUN_ACCESS_KEY=your_access_key
export ALIYUN_ACCESS_SECRET=your_access_secret
```

#### 配置文件中使用环境变量

```yaml
spring:
  datasource:
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

  redis:
    password: ${REDIS_PASSWORD}
```

---

### 使用 Jasypt 加密（可选）

对于必须写入配置文件的敏感信息，使用 Jasypt 加密。

#### 添加依赖

```xml
<dependency>
    <groupId>com.github.ulisesbocchio</groupId>
    <artifactId>jasypt-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

#### 配置加密密码

```yaml
jasypt:
  encryptor:
    password: ${JASYPT_PASSWORD}  # 通过环境变量传递
```

#### 加密敏感信息

使用 Jasypt 工具加密敏感信息：

```bash
java -cp jasypt-1.9.3.jar org.jasypt.intf.cli.JasyptPBEStringEncryptionCLI \
  input="your_password" \
  password=${JASYPT_PASSWORD} \
  algorithm=PBEWithMD5AndDES
```

#### 配置文件中使用加密信息

```yaml
spring:
  datasource:
    password: ENC(加密后的密文)
```

---

## MyBatis Plus 配置规范

### 基础配置

```yaml
mybatis-plus:
  configuration:
    # 驼峰命名自动映射
    map-underscore-to-camel-case: true
    # 日志输出
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
  global-config:
    db-config:
      # 主键类型（雪花算法）
      id-type: ASSIGN_ID
      # 逻辑删除字段
      logic-delete-field: isDeleted
      logic-delete-value: 1
      logic-not-delete-value: 0
    banner: false  # 关闭 MyBatis Plus 的 banner
  # Mapper XML 扫描路径
  mapper-locations: classpath*:/mapper/**/*.xml
```

---

## 雪花算法配置

### 配置示例

```yaml
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```

---

### 参数说明

| 参数 | 说明 | 取值范围 | 必填 |
|------|------|---------|------|
| `cluster-id` | 集群 ID | 1-31 | 是 |
| `node-id` | 节点 ID | 1-31 | 是 |

---

### 集群节点规划示例

| 环境 | 集群 ID | 节点 ID | 节点名称 |
|------|---------|---------|---------|
| 开发环境 | 1 | 1 | dev-node1 |
| 测试环境 | 2 | 1 | test-node1 |
| 测试环境 | 2 | 2 | test-node2 |
| 生产环境 | 3 | 1 | prod-node1 |
| 生产环境 | 3 | 2 | prod-node2 |
| 生产环境 | 3 | 3 | prod-node3 |

**注意**：同一集群内，所有节点的 `cluster-id` 必须相同，但 `node-id` 必须唯一。

---

## 缓存配置规范

### Redis 配置

```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:
    database: 0
    timeout: 3000
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5

nebula:
  cache:
    type: redis  # 或 caffeine
    redis:
      key-prefix: nebula:
      expire-time: 3600  # 默认过期时间（秒）
```

---

### Caffeine 配置

```yaml
nebula:
  cache:
    type: caffeine
    caffeine:
      maximum-size: 1000
      expire-after-write: 3600
```

---

## 日志配置规范

### Logback 配置（logback.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/application.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 日志级别 -->
    <logger name="com.nebula" level="DEBUG"/>
    <logger name="org.springframework" level="WARN"/>
    <logger name="org.hibernate" level="WARN"/>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

---

## 配置管理最佳实践

### 1. 使用 Profile 区分环境

```yaml
spring:
  profiles:
    active: dev  # 使用 Maven profile 或环境变量
```

---

### 2. 敏感信息使用环境变量

```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}  # ✅ 正确
    password: my_password      # ❌ 错误
```

---

### 3. 合理配置连接池

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20      # 最大连接数
      minimum-idle: 5           # 最小空闲连接数
      connection-timeout: 30000  # 连接超时时间（毫秒）
      idle-timeout: 600000       # 空闲连接超时时间（毫秒）
      max-lifetime: 1800000      # 连接最大存活时间（毫秒）
```

---

### 4. 配置雪花算法

```yaml
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```

**注意**：同一集群内，`cluster-id` 必须相同，`node-id` 必须唯一。

---

### 5. 配置日志级别

| 环境 | Root 级别 | Nebula 级别 | Spring 级别 |
|------|---------|------------|------------|
| 开发环境 | DEBUG | DEBUG | DEBUG |
| 测试环境 | INFO | DEBUG | WARN |
| 生产环境 | WARN | WARN | WARN |

---

### 6. 配置文件注释

```yaml
# 应用名称
spring:
  application:
    name: nebula-uaa-service

# 服务端口
server:
  port: 8080

# 雪花算法配置
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```
"""


# ==============================================================================
# MCP 工具函数
# ==============================================================================


async def get_standard(category: str) -> str:
    """
    获取 Nebula 编码规范

    Args:
        category: 规范分类

    Returns:
        规范文档
    """
    category = category.lower().strip()

    standards_map = {
        "architecture": ARCHITECTURE_STANDARD,
        "arch": ARCHITECTURE_STANDARD,
        "naming": NAMING_STANDARD,
        "controller": CONTROLLER_STANDARD,
        "service": SERVICE_STANDARD,
        "dao": DAO_STANDARD,
        "mapper": DAO_STANDARD,
        "converter": CONVERTER_STANDARD,
        "api": API_STANDARD,
        "exception": EXCEPTION_STANDARD,
        "constant": CONSTANT_ENUM_STANDARD,
        "enum": CONSTANT_ENUM_STANDARD,
        "other": OTHER_STANDARD,
        "database": DATABASE_DESIGN_STANDARD,
        "db": DATABASE_DESIGN_STANDARD,
        "config": CONFIGURATION_MANAGEMENT_STANDARD,
        "configuration": CONFIGURATION_MANAGEMENT_STANDARD,
    }

    standard = standards_map.get(category)

    if standard:
        return f"以下是 Nebula 中台 {category.upper()} 规范：\n\n{standard}"
    else:
        available = [
            "architecture (架构设计规范)",
            "naming (命名规范)",
            "controller (Controller 层规范)",
            "service (Service 层规范)",
            "dao/mapper (DAO 层规范)",
            "converter (数据转换规范)",
            "api (API 设计规范)",
            "exception (异常处理规范)",
            "constant/enum (常量和枚举规范)",
            "other (其他规范)",
            "database (数据库设计规范)",
            "config/configuration (配置管理规范)",
        ]
        return f"暂时不支持 '{category}' 规范。\n\n支持的规范：\n" + "\n".join(
            f"- {item}" for item in available
        )


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
