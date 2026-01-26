# Nebula 中台其他规范

## 工具类使用规范

### 基本原则

1. **优先使用 Apache Commons 工具类**
   - 避免重复造轮子
   - Apache Commons 工具类经过充分测试，稳定可靠
   - 提高代码可读性和维护性

2. **常见的 Apache Commons 工具库**
   - `org.apache.commons.collections4` - 集合工具类
   - `org.apache.commons.lang3` - 字符串和对象工具类
   - `org.apache.commons.io` - IO 工具类

---

## 类型转换规范

### 基本原则

**严格禁止使用 BeanUtils**

**原因**：
- BeanUtils 使用反射，性能低下
- 无法在编译期发现类型转换错误
- 类型安全性差，容易引发运行时异常
- 代码可读性差，难以维护

---

## MapStruct 转换器（首选）

### 规范要求

1. **优先使用 MapStruct 转换器**进行对象类型转换
2. **命名规则**：`{业务名称}Converter`
3. **位置**：`converter/` 包（与 model 包平级）
4. **使用方式**：通过静态方法 `INSTANCE` 调用

### 使用示例

#### ✅ 推荐用法

```java
import org.mapstruct.Mapper;
import org.mapstruct.factory.Mappers;

@Mapper(componentModel = "spring")
public interface UserConverter {

    UserConverter INSTANCE = Mappers.getMapper(UserConverter.class);

    // Entity → DTO
    UserDto toDto(UserEntity entity);

    // DTO → Entity
    UserEntity toEntity(UserDto dto);

    // List 转换
    List<UserDto> toDtoList(List<UserEntity> entities);
}

// 使用转换器
public UserDto getUserById(Long id) {
    UserEntity entity = userMapper.selectById(id);
    return UserConverter.INSTANCE.toDto(entity);
}

// List 转换
public List<UserDto> listUsers() {
    List<UserEntity> entities = userMapper.selectList(null);
    return UserConverter.INSTANCE.toDtoList(entities);
}
```

#### ❌ 不推荐用法

```java
import org.springframework.beans.BeanUtils;

// 禁止使用 BeanUtils
public UserDto getUserById(Long id) {
    UserEntity entity = userMapper.selectById(id);

    // ❌ 危险！禁止使用 BeanUtils
    UserDto dto = new UserDto();
    BeanUtils.copyProperties(entity, dto);

    return dto;
}
```

### 复杂字段映射

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    UserConverter INSTANCE = Mappers.getMapper(UserConverter.class);

    // 字段名不匹配时使用 @Mapping
    @Mapping(source = "id", target = "userId")
    @Mapping(source = "name", target = "userName")
    @Mapping(source = "createTime", target = "createTime", dateFormat = "yyyy-MM-dd HH:mm:ss")
    UserDto toDto(UserEntity entity);

    // 忽略某些字段
    @Mapping(target = "password", ignore = true)
    @Mapping(target = "deleted", ignore = true)
    UserDto toDtoForResponse(UserEntity entity);

    // 嵌套对象
    @Mapping(source = "order.id", target = "orderId")
    OrderItemDto toDto(OrderItemEntity entity);
}
```

### 自定义转换方法

```java
@Mapper(componentModel = "spring")
public interface UserConverter {

    UserConverter INSTANCE = Mappers.getMapper(UserConverter.class);

    // 使用自定义转换方法
    @Mapping(target = "status", source = "status", qualifiedByName = "intToEnum")
    UserDto toDto(UserEntity entity);

    // 自定义转换方法
    @Named("intToEnum")
    default UserStatusEnum intToEnum(Integer status) {
        return UserStatusEnum.of(status);
    }

    // 枚举转整数
    @Named("enumToInt")
    default Integer enumToInt(UserStatusEnum status) {
        return status != null ? status.getCode() : null;
    }
}
```

---

## 手动转换方法（备选）

### 适用场景

当转换逻辑复杂，不适合用 MapStruct 时，使用手动转换方法。

### 使用示例

#### ✅ 推荐用法

```java
// Converter 类中提供手动转换方法
public class OrderConverter {

    // 手动转换方法
    public static OrderDto toDto(OrderEntity entity) {
        if (entity == null) {
            return null;
        }

        OrderDto dto = new OrderDto();
        dto.setId(entity.getId());
        dto.setOrderNo(entity.getOrderNo());
        dto.setAmount(entity.getAmount());

        // 复杂逻辑
        if (entity.getStatus() == 1) {
            dto.setStatusText("待支付");
        } else if (entity.getStatus() == 2) {
            dto.setStatusText("已支付");
        } else {
            dto.setStatusText("已完成");
        }

        return dto;
    }

    // 手动转换 List
    public static List<OrderDto> toDtoList(List<OrderEntity> entities) {
        if (CollectionUtils.isEmpty(entities)) {
            return Collections.emptyList();
        }

        return entities.stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }
}
```

#### ❌ 不推荐用法

```java
// 禁止使用 BeanUtils
public OrderDto toDto(OrderEntity entity) {
    OrderDto dto = new OrderDto();
    // ❌ 禁止使用 BeanUtils
    BeanUtils.copyProperties(entity, dto);

    // 复杂逻辑
    if (dto.getStatus() == 1) {
        dto.setStatusText("待支付");
    }
    // ...

    return dto;
}
```

---

## 转换选择优先级

| 优先级 | 转换方式 | 适用场景 |
|--------|---------|---------|
| **1** | MapStruct 转换器 | 标准的对象转换，字段映射简单或中等复杂度 |
| **2** | 手动转换方法 | 复杂的转换逻辑，需要特殊处理 |
| **❌** | BeanUtils | 禁止使用 |

---

## 常见转换场景

### 1. Entity → DTO

```java
// 使用 MapStruct
@Mapper
public interface UserConverter {
    UserDto toDto(UserEntity entity);
    List<UserDto> toDtoList(List<UserEntity> entities);
}

// Service 层使用
public UserDto getById(Long id) {
    UserEntity entity = userMapper.selectById(id);
    return UserConverter.INSTANCE.toDto(entity);
}
```

---

### 2. DTO → Entity

```java
// 使用 MapStruct
@Mapper
public interface UserConverter {
    UserEntity toEntity(UserDto dto);
}

// Service 层使用
public void updateUser(UserDto dto) {
    UserEntity entity = UserConverter.INSTANCE.toEntity(dto);
    userMapper.updateById(entity);
}
```

---

### 3. Req → Command

```java
// 使用 MapStruct
@Mapper(componentModel = "spring")
public interface UserConverter {
    CreateUserCommand toCommand(CreateUserReq req);
}

// Controller 层使用
@PostMapping
public Long createUser(@Valid @RequestBody CreateUserReq req) {
    CreateUserCommand cmd = UserConverter.INSTANCE.toCommand(req);
    return userService.createUser(cmd);
}
```

---

### 4. DTO → Resp

```java
// 使用 MapStruct
@Mapper(componentModel = "spring")
public interface UserConverter {
    UserResp toResp(UserDto dto);
    List<UserResp> toRespList(List<UserDto> dtos);
}

// Controller 层使用
@GetMapping("/{id}")
public UserResp getUserById(@PathVariable Long id) {
    UserDto dto = userService.getById(id);
    return UserConverter.INSTANCE.toResp(dto);
}
```

---

## 性能对比

| 转换方式 | 性能 | 类型安全 | 可读性 | 维护性 |
|---------|------|---------|--------|--------|
| MapStruct | ⭐⭐⭐⭐⭐ 高 | ✅ 编译期检查 | ✅ 清晰 | ✅ 易维护 |
| 手动转换 | ⭐⭐⭐⭐ 高 | ✅ 编译期检查 | ✅ 清晰 | ✅ 易维护 |
| BeanUtils | ⭐ 低 | ❌ 运行时检查 | ❌ 不清晰 | ❌ 难维护 |

---

## 禁止使用的转换方式

### ❌ 完全禁止 BeanUtils

```java
// ❌ 禁止使用任何形式的 BeanUtils
import org.springframework.beans.BeanUtils;
import org.apache.commons.beanutils.BeanUtils;

// 任何这些用法都是禁止的：
BeanUtils.copyProperties(source, target);
BeanUtils.copyProperties(target, source);
BeanUtils.populate(bean, properties);
```

### ❌ 禁止原因

1. **性能差**：使用反射，性能开销大
2. **不安全**：无法在编译期发现错误
3. **不透明**：无法清楚知道哪些字段被复制
4. **维护难**：字段变更时难以追踪影响范围

---

## MapUtils 使用规范

### 从 Map 中获取值

**规范要求**：使用 `MapUtils.getXXX` 方法从 Map 中获取值，必须提供默认值。

**原因**：
- 强迫使用者考虑 key 不存在时的默认行为
- 避免 NullPointerException
- 代码更健壮，更易维护

### 使用示例

#### ✅ 推荐用法

```java
import org.apache.commons.collections4.MapUtils;

// 获取 String 类型值
String username = MapUtils.getString(map, "username", "default");
String email = MapUtils.getString(userMap, "email", "");

// 获取 Integer 类型值
Integer age = MapUtils.getInteger(map, "age", 0);
Integer status = MapUtils.getInteger(userMap, "status", 1);

// 获取 Long 类型值
Long userId = MapUtils.getLong(map, "userId", 0L);
Long timestamp = MapUtils.getLong(dataMap, "timestamp", System.currentTimeMillis());

// 获取 Boolean 类型值
Boolean isAdmin = MapUtils.getBoolean(map, "isAdmin", false);
Boolean active = MapUtils.getBoolean(userMap, "active", true);

// 获取 Double 类型值
Double price = MapUtils.getDouble(map, "price", 0.0);
Double rate = MapUtils.getDouble(configMap, "rate", 1.0);
```

#### ❌ 不推荐用法

```java
// 直接使用 map.get()，可能返回 null
String username = (String) map.get("username"); // 危险！可能为 null

// 手动判断 null，代码冗余
String username = map.get("username");
if (username == null) {
    username = "default";
}
```

### 适用场景

| 场景 | 推荐方法 | 说明 |
|------|---------|------|
| 从配置 Map 读取值 | `MapUtils.getString/Integer/Long` | 必须提供默认值 |
| 从请求参数 Map 获取值 | `MapUtils.getString` | 提供合理的默认值 |
| 从缓存 Map 获取值 | `MapUtils.getXXX` | 默认值表示未命中 |
| 从结果集 Map 读取值 | `MapUtils.getXXX` | 避免 NPE |

### 方法列表

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `getString(Map, key, defaultValue)` | `String` | 获取 String 值 |
| `getInteger(Map, key, defaultValue)` | `Integer` | 获取 Integer 值 |
| `getLong(Map, key, defaultValue)` | `Long` | 获取 Long 值 |
| `getBoolean(Map, key, defaultValue)` | `Boolean` | 获取 Boolean 值 |
| `getDouble(Map, key, defaultValue)` | `Double` | 获取 Double 值 |
| `getObject(Map, key, defaultValue)` | `Object` | 获取任意对象 |

---

## CollectionUtils 使用规范

### 判断集合是否为空

**规范要求**：使用 `CollectionUtils.isEmpty()` 判断集合是否为空。

**原因**：
- 同时处理 `null` 和 `empty` 的情况
- 避免 NullPointerException
- 代码简洁，语义清晰

### 使用示例

#### ✅ 推荐用法

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.List;
import java.util.Set;
import java.util.Map;

// 判断 List 是否为空
if (CollectionUtils.isEmpty(userList)) {
    // 处理空集合或 null 的情况
    return Collections.emptyList();
}

// 判断 Set 是否为空
if (CollectionUtils.isEmpty(roleSet)) {
    throw new BusinessException("用户角色不能为空");
}

// 判断 Map 是否为空（MapUtils）
import org.apache.commons.collections4.MapUtils;
if (MapUtils.isEmpty(configMap)) {
    log.warn("配置为空，使用默认配置");
}

// 集合为空时返回空集合
public List<UserDto> listUsers(ListUsersQuery query) {
    List<UserEntity> entities = userMapper.selectList(query);
    return CollectionUtils.isEmpty(entities)
        ? Collections.emptyList()
        : UserConverter.INSTANCE.toDtoList(entities);
}
```

#### ❌ 不推荐用法

```java
// 先判断 null，再判断 empty，代码冗余
if (userList == null || userList.isEmpty()) {
    // ...
}

// 只判断 empty，可能抛出 NullPointerException
if (userList.isEmpty()) { // 危险！如果 userList 为 null 会抛出 NPE
    // ...
}
```

### 常用方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `isEmpty(Collection)` | `boolean` | 判断集合是否为空（null 或 empty） |
| `isNotEmpty(Collection)` | `boolean` | 判断集合是否不为空 |
| `size(Collection)` | `int` | 安全获取集合大小（null 返回 0） |
| `addAll(Collection, Collection)` | `boolean` | 将一个集合的所有元素添加到另一个集合 |
| `containsAll(Collection, Collection)` | `boolean` | 判断集合是否包含另一个集合的所有元素 |

### 适用场景

| 场景 | 推荐方法 | 说明 |
|------|---------|------|
| 判断查询结果是否为空 | `CollectionUtils.isEmpty()` | 处理 null 和 empty |
| 判断参数集合是否有效 | `CollectionUtils.isNotEmpty()` | 参数校验 |
| 判断返回值是否需要处理 | `CollectionUtils.isEmpty()` | 避免不必要的处理 |
| 获取集合大小 | `CollectionUtils.size()` | 避免空指针异常 |

---

## StringUtils 使用规范

### 字符串操作

**规范要求**：使用 Apache Commons Lang3 的 `StringUtils` 进行字符串操作。

### 使用示例

#### ✅ 推荐用法

```java
import org.apache.commons.lang3.StringUtils;

// 判断字符串是否为空
if (StringUtils.isBlank(username)) {
    throw new BusinessException("用户名不能为空");
}

// 判断字符串是否不为空
if (StringUtils.isNotBlank(email)) {
    // 发送邮件逻辑
}

// 字符串判空
if (StringUtils.isEmpty(mobile)) {
    mobile = "未知";
}

// 字符串非空
if (StringUtils.isNotEmpty(address)) {
    // 处理地址
}

// 字符串比较（安全）
if (StringUtils.equals(str1, str2)) {
    // 相等
}

// 字符串忽略大小写比较
if (StringUtils.equalsIgnoreCase(str1, str2)) {
    // 忽略大小写相等
}

// 字符串拼接
String result = StringUtils.join(userIds, ",");

// 字符串分割
String[] parts = StringUtils.split(str, ",");

// 去除空格
String trimmed = StringUtils.trim(str);

// 字符串缩略
String summary = StringUtils.abbreviate(longText, 50);
```

### 常用方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `isEmpty(String)` | `boolean` | 判断字符串是否为空（null 或 ""） |
| `isNotEmpty(String)` | `boolean` | 判断字符串是否不为空 |
| `isBlank(String)` | `boolean` | 判断字符串是否为空白（null、"" 或纯空格） |
| `isNotBlank(String)` | `boolean` | 判断字符串是否不为空白 |
| `equals(String, String)` | `boolean` | 字符串相等比较（null 安全） |
| `equalsIgnoreCase(String, String)` | `boolean` | 忽略大小写比较（null 安全） |
| `join(Iterable, String)` | `String` | 集合元素拼接为字符串 |
| `split(String, String)` | `String[]` | 字符串分割 |
| `trim(String)` | `String` | 去除字符串首尾空格 |
| `abbreviate(String, int)` | `String` | 字符串缩略 |

---

## ObjectUtils 使用规范

### 对象操作

**规范要求**：使用 Apache Commons Lang3 的 `ObjectUtils` 进行对象操作。

### 使用示例

#### ✅ 推荐用法

```java
import org.apache.commons.lang3.ObjectUtils;

// 对象判空
if (ObjectUtils.isEmpty(user)) {
    return null;
}

// 对象比较（null 安全）
if (ObjectUtils.equals(obj1, obj2)) {
    // 相等
}

// 获取默认值
String name = ObjectUtils.firstNonNull(inputName, "default");

// 判断是否为 null
if (ObjectUtils.isNull(obj)) {
    // 处理 null
}

// 判断是否不为 null
if (ObjectUtils.notNull(obj)) {
    // 处理非 null
}
```

### 常用方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `isEmpty(Object)` | `boolean` | 判断对象是否为空（null、空集合、空字符串等） |
| `isNotEmpty(Object)` | `boolean` | 判断对象是否不为空 |
| `equals(Object, Object)` | `boolean` | 对象相等比较（null 安全） |
| `firstNonNull(Object, Object...)` | `T` | 返回第一个非 null 对象 |
| `isNull(Object)` | `boolean` | 判断对象是否为 null |
| `notNull(Object)` | `boolean` | 判断对象是否不为 null |

---

## 最佳实践

### 1. 默认值的选择

**原则**：
- String 类型的默认值通常使用空字符串 `""`
- 数值类型的默认值通常使用 `0`、`0L`、`0.0`
- Boolean 类型的默认值根据业务场景选择 `true` 或 `false`

```java
// String 类型
String username = MapUtils.getString(map, "username", "");

// 数值类型
Integer count = MapUtils.getInteger(map, "count", 0);
Long timestamp = MapUtils.getLong(map, "timestamp", 0L);

// Boolean 类型
Boolean enabled = MapUtils.getBoolean(map, "enabled", true); // 默认启用
Boolean isAdmin = MapUtils.getBoolean(map, "isAdmin", false); // 默认不是管理员
```

### 2. 集合判空的返回

**原则**：
- 返回空集合而不是 `null`
- 使用 `Collections.emptyList()`、`Collections.emptySet()`、`Collections.emptyMap()`

```java
public List<UserDto> listUsers(ListUsersQuery query) {
    List<UserEntity> entities = userMapper.selectList(query);
    
    return CollectionUtils.isEmpty(entities)
        ? Collections.emptyList()
        : UserConverter.INSTANCE.toDtoList(entities);
}
```

### 3. 工具类的静态导入

**推荐使用静态导入**：减少代码前缀，提高可读性

```java
import static org.apache.commons.collections4.CollectionUtils.isEmpty;
import static org.apache.commons.collections4.MapUtils.getInteger;
import static org.apache.commons.lang3.StringUtils.isNotBlank;

// 使用时更简洁
if (isEmpty(userList)) {
    return Collections.emptyList();
}

Integer age = getInteger(map, "age", 0);

if (isNotBlank(username)) {
    // 处理逻辑
}
```

### 4. 性能考虑

**注意**：虽然 Apache Commons 工具类很方便，但在性能敏感的场景下需要注意：

```java
// 在高频调用的场景，可以缓存结果
private static final String DEFAULT_USERNAME = "";

public String getUsername(Map<String, Object> map) {
    // 避免每次都创建新的空字符串
    return MapUtils.getString(map, "username", DEFAULT_USERNAME);
}
```

---

## 禁止使用的代码模式

### ❌ 直接使用 map.get() 没有空检查

```java
// 危险！可能抛出 NullPointerException
String username = (String) map.get("username");
```

### ❌ 手动判空和获取默认值

```java
// 代码冗余，不推荐
String username = map.get("username");
if (username == null) {
    username = "default";
}
```

### ❌ 直接判断集合的 isEmpty()

```java
// 危险！如果集合为 null 会抛出 NullPointerException
if (userList.isEmpty()) {
    // ...
}
```

### ❌ 字符串判空只使用 null 判断

```java
// 不完整，没有处理空字符串
if (str == null) {
    // ...
}
```

---

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
