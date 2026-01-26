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

    @Cacheable(value = "user", key = "#query.id", unless = "#result == null")
    public UserDto getById(GetUserByIdQuery query) {
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
@Cacheable(value = "user", key = "#query.id",
           unless = "#result == null",
           cacheResolver = "customCacheResolver")
public UserDto getById(GetUserByIdQuery query) {
    // ...
}
```

---

## 数据库字段映射

### 鼓峰 vs 蛇形

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
