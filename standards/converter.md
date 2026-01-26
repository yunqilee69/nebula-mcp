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
