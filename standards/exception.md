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
