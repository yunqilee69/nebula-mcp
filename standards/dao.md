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
    IPage<UserEntity> pageByParam(IPage<UserEntity> page, UserQueryParam param);

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
| `page*` | `IPage<T>` | 分页查询 |
| `count*` | `Long` | 统计数量 |
| `exists*` | `boolean` | 判断是否存在 |

---

### 示例

```java
List<UserEntity> findByUsername(String username);
UserEntity getById(Long id);
Optional<UserEntity> getOptById(Long id);
IPage<UserEntity> pageQuery(IPage<UserEntity> page, UserQueryParam param);
Long countByStatus(Integer status);
boolean existsByUsername(String username);
```

---

### 分页查询返回类型规范

**DAO层分页查询必须返回 `IPage<T>` 类型**：

- **T的类型**：根据业务场景确定，通常为 Entity 或 DTO
- **常见场景**：
  - 单表查询：`IPage<Entity>`（返回实体）
  - 多表联查：`IPage<Dto>`（返回数据传输对象）
  - 自定义字段：`IPage<Dto>`（返回包含自定义字段的数据传输对象）

**示例**：
```java
// 单表分页查询，返回 Entity
IPage<UserEntity> pageByCondition(IPage<UserEntity> page, UserQueryParam param);

// 多表联查分页，返回 DTO
IPage<UserDetailDto> pageWithRoles(IPage<UserDetailDto> page, UserQueryParam param);

// 自定义字段分页，返回 DTO
IPage<UserStatDto> pageStatistics(IPage<UserStatDto> page, UserStatQueryParam param);
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

### Service 层禁止使用 LambdaQueryWrapper

**规则**：Service 层**禁止**使用 `LambdaQueryWrapper` 拼接查询条件，所有数据库查询必须通过 DAO 层提供的方法进行。

---

### 原因说明

1. **代码重复**：如果在 Service 层使用 `LambdaQueryWrapper`，相同的查询逻辑会在多个 Service 类中重复出现
2. **不利于复用**：查询逻辑封装在 Service 层，其他 Service 无法复用
3. **职责不清**：数据库查询属于 DAO 层职责，Service 层应关注业务逻辑
4. **测试困难**：查询条件分散在 Service 层，难以进行单元测试和集成测试
5. **维护成本高**：查询条件变更时需要修改多处 Service 代码

---

### 错误示例（Service 层使用 LambdaQueryWrapper）

```java
@Service
public class UserServiceImpl implements IUserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public List<UserDto> listUsers(ListUsersQuery query) {
        // ❌ 错误：在 Service 层直接使用 LambdaQueryWrapper
        LambdaQueryWrapper<UserEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserEntity::getStatus, query.getStatus());
        wrapper.like(UserEntity::getUsername, query.getUsername());
        wrapper.ge(UserEntity::getCreateTime, query.getStartDate());
        wrapper.le(UserEntity::getCreateTime, query.getEndDate());
        List<UserEntity> list = userMapper.selectList(wrapper);

        return UserConverter.INSTANCE.toDtoList(list);
    }

    @Override
    public UserDto getByUsername(String username) {
        // ❌ 错误：在 Service 层直接使用 LambdaQueryWrapper
        LambdaQueryWrapper<UserEntity> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserEntity::getUsername, username);
        UserEntity entity = userMapper.selectOne(wrapper);

        return UserConverter.INSTANCE.toDto(entity);
    }
}
```

**问题**：
- 查询逻辑写在 Service 层，其他 Service 无法复用
- 相同的查询条件可能在多处重复编写
- 违反分层架构原则

---

### 正确示例（调用 DAO 层提供的方法）

```java
// DAO 层：提供查询方法
public interface UserMapper extends BaseMapper<UserEntity> {

    /**
     * 根据条件查询用户列表
     */
    List<UserEntity> listByParam(UserQueryParam param);

    /**
     * 根据用户名查询
     */
    UserEntity findByUsername(String username);
}
```

```java
// Service 层：调用 DAO 层方法
@Service
public class UserServiceImpl implements IUserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public List<UserDto> listUsers(ListUsersQuery query) {
        // ✅ 正确：调用 DAO 层提供的方法
        UserQueryParam param = UserConverter.INSTANCE.toParam(query);
        List<UserEntity> list = userMapper.listByParam(param);

        return UserConverter.INSTANCE.toDtoList(list);
    }

    @Override
    public UserDto getByUsername(String username) {
        // ✅ 正确：调用 DAO 层提供的方法
        UserEntity entity = userMapper.findByUsername(username);

        return UserConverter.INSTANCE.toDto(entity);
    }
}
```

**优势**：
- 查询逻辑封装在 DAO 层，可被多个 Service 复用
- 职责清晰：DAO 负责查询，Service 负责业务逻辑
- 易于测试和维护
- 查询条件变更时只需修改 DAO 层

---

### 特殊情况说明

**MyBatis Plus 提供的通用方法（可直接调用）**：

以下 MyBatis Plus 提供的基础 CRUD 方法，Service 层可以直接调用：

```java
@Service
public class UserServiceImpl implements IUserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public UserDto getById(GetUserByIdQuery query) {
        // ✅ 正确：调用 MyBatis Plus 基础方法
        UserEntity entity = userMapper.selectById(query.getId());
        return UserConverter.INSTANCE.toDto(entity);
    }

    @Override
    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        // ✅ 正确：调用 MyBatis Plus 基础方法
        UserEntity entity = new UserEntity();
        entity.setUsername(cmd.getUsername());
        entity.setEmail(cmd.getEmail());
        userMapper.insert(entity);

        return entity.getId();
    }
}
```

**允许直接调用的基础方法**：
- `selectById(id)` - 根据 ID 查询
- `insert(entity)` - 插入
- `updateById(entity)` - 根据 ID 更新
- `deleteById(id)` - 根据 ID 删除
- `selectList(null)` - 查询所有

**禁止在 Service 层使用的方法**：
- `selectList(LambdaQueryWrapper)` - 条件查询
- `selectOne(LambdaQueryWrapper)` - 单个条件查询
- `selectPage(IPage, LambdaQueryWrapper)` - 分页条件查询
- `selectCount(LambdaQueryWrapper)` - 统计数量
- 其他任何使用 `LambdaQueryWrapper` 的方法

---

### DAO 层查询方法封装建议

**常见查询方法命名模式**：

| 场景 | 方法名 | 返回类型 | 示例 |
|-------|---------|---------|------|
| 单个条件查询 | `findBy{Field}` | `Entity` | `findByUsername(String username)` |
| 多个条件查询 | `listByParam(Param)` | `List<Entity>` | `listByParam(UserQueryParam param)` |
| 条件分页查询 | `pageByParam(Page, Param)` | `IPage<Entity>` | `pageByParam(IPage page, UserQueryParam param)` |
| 存在性检查 | `existsBy{Field}` | `boolean` | `existsByUsername(String username)` |
| 统计查询 | `countBy{Condition}` | `Long` | `countByStatus(Integer status)` |

**实现建议**：

```java
public interface UserMapper extends BaseMapper<UserEntity> {

    // 1. 简单条件查询（参数 <= 3 个）
    UserEntity findByUsername(String username);
    boolean existsByUsername(String username);

    // 2. 复杂条件查询（参数 > 3 个，封装为 Param）
    List<UserEntity> listByParam(UserQueryParam param);
    IPage<UserEntity> pageByParam(IPage<UserEntity> page, UserQueryParam param);

    // 3. 统计查询
    Long countByStatus(Integer status);
}
```

---

### 最佳实践总结

1. **Service 层不拼接查询条件**：所有查询条件封装通过 Param 传递给 DAO 层
2. **DAO 层提供完整查询方法**：包括简单查询、复杂查询、分页查询、统计查询
3. **使用 Param 类传递查询参数**：查询参数超过 3 个时，封装为 Param 类
4. **复用 DAO 层方法**：相同的查询逻辑在 DAO 层实现一次，多个 Service 共享
5. **保持分层清晰**：Service 层专注业务逻辑，DAO 层专注数据访问

---

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
```

**注意**：条件查询必须在 DAO 层封装，Service 层禁止使用 `LambdaQueryWrapper`。

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

    @Cacheable(value = "user", key = "#query.id", unless = "#result == null")
    public UserDto getById(GetUserByIdQuery query) {
        // ...
    }
}
```

---

### 缓存 Key 命名

```java
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
