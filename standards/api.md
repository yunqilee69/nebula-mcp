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
