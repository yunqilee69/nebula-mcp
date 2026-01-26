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
    List<UserDto> listUsers(ListUsersQuery query);
    Page<UserDto> pageUsers(PageUsersQuery query);
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
    public List<UserDto> listUsers(ListUsersQuery query) {
        // 将 Query 转换为 Param 传给 DAO 层
        UserQueryParam param = UserConverter.INSTANCE.toParam(query);
        List<UserEntity> entities = userRepo.listByParam(param);

        return UserConverter.INSTANCE.toDtoList(entities);
    }

    @Override
    public IPage<UserDto> pageUsers(PageUsersQuery query) {
        // 将 Query 转换为 Param 传给 DAO 层
        UserQueryParam param = UserConverter.INSTANCE.toParam(query);
        IPage<UserEntity> page = userRepo.pageByParam(param);

        List<UserDto> dtos = UserConverter.INSTANCE.toDtoList(page.getRecords());

        IPage<UserDto> result = new Page<>(page.getCurrent(), page.getSize(), page.getTotal());
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

## 方法签名规范

### 基本规则

**Service 层方法签名中不能使用 Entity，只能使用 DTO、Command、Query 类。**

---

### 原因说明

1. **解耦数据模型**：Entity 是数据库映射对象，属于 DAO 层内部实现，不应暴露到 Service 层
2. **清晰的职责边界**：Service 层应关注业务对象（DTO/Command/Query），而非持久化对象（Entity）
3. **便于维护和扩展**：当数据库表结构变更时，仅需修改 Entity，不影响 Service 层接口
4. **避免数据泄露**：Entity 可能包含敏感字段或内部字段，不应直接暴露给上层

---

### 正确示例

```java
public interface IUserService {
    // ✅ 正确：使用 Command 作为入参
    Long createUser(CreateUserCommand cmd);

    // ✅ 正确：使用 Query 作为入参
    UserDto getById(GetUserByIdQuery query);

    // ✅ 正确：使用 Query 作为查询参数
    List<UserDto> listUsers(ListUsersQuery query);

    // ✅ 正确：使用 Query 作为查询参数
    IPage<UserDto> pageUsers(PageUsersQuery query);
}
```

---

### 错误示例

```java
public interface IUserService {
    // ❌ 错误：方法参数不能使用 Entity
    Long createUser(UserEntity entity);

    // ❌ 错误：方法返回值不能使用 Entity
    UserEntity getById(Long id);

    // ❌ 错误：方法参数不能使用 Entity
    void updateUser(UserEntity entity);

    // ❌ 错误：方法返回值不能使用 Entity
    List<UserEntity> listUsers();
}
```

---

### Internal Service 可以使用 Entity

Internal Service（内部服务）是 Service 层内部的辅助类，可以使用 Entity：

```java
@Service
public class UserInternalService {

    /**
     * 校验用户状态
     */
    public void validateUserStatus(Long userId) {
        // ✅ Internal Service 内部可以使用 Entity
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

### 数据转换规范

| 层 | 入参类型 | 返回类型 |
|----|---------|---------|
| **Controller** | Req (local/model/req/) | Resp (local/model/resp/) |
| **Service** | Command/Query (core/model/) | DTO (core/model/dto/) |
| **DAO** | Entity/Param (core/model/) | Entity/DTO (core/model/) |

**数据流转**：
```
Controller: Req → Command/Query → Service
Service: Command/Query → Entity (内部) → DTO → Controller
DAO: Entity/Param ↔ 数据库
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

---

## 数据库查询规范

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
