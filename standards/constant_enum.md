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

---

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

---

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
