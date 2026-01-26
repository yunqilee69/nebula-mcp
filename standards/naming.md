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
UserDto getById(GetUserByIdQuery query);
List<UserDto> listUsers(ListUsersQuery query);
IPage<UserDto> pageUsers(PageUsersQuery query);
```

---

### 分页查询返回类型规范

**Service层分页查询必须返回 `IPage<T>` 类型**：

- **T的类型**：根据业务场景确定，通常为 DTO 或 Entity
- **常见场景**：
  - 单表查询：`IPage<Entity>`（直接返回实体）
  - 多表联查：`IPage<Dto>`（返回数据传输对象）
  - 自定义字段：`IPage<Dto>`（返回包含自定义字段的数据传输对象）

**示例**：
```java
// 单表查询，返回 Entity
IPage<UserEntity> pageUsersByCondition(UserPageParam param);

// 多表联查，返回 DTO
IPage<UserDetailDto> pageUsersWithRoles(UserPageParam param);

// 自定义字段统计，返回 DTO
IPage<UserStatDto> pageUserStatistics(UserStatPageParam param);
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
