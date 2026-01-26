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
public List<UserResp> listUsers(ListUsersReq req) {
    ListUsersQuery query = UserConverter.INSTANCE.toQuery(req);
    List<UserDto> dtos = userService.listUsers(query);

    return UserConverter.INSTANCE.toRespList(dtos);
}
```

---

### 6. 分页查询
```java
@Operation(summary = "分页查询用户", description = "分页查询用户列表")
@GetMapping("/page")
public PageResp<UserResp> pageUsers(PageUsersReq req) {
    PageUsersQuery query = UserConverter.INSTANCE.toQuery(req);
    Page<UserDto> page = userService.pageUsers(query);

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
