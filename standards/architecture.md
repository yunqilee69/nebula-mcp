# Nebula 中台 Java 后端架构设计规范

## 整体架构

采用传统 MVC 三层架构 + 轻量级 DDD 设计思想

```
Controller 层（local/）
  ↓
Service 层（core/service/ + internal service）
  ↓
DAO 层（core/dao/mapper/）
```

---

## 模块结构

Nebula 中台采用按业务域划分的模块化设计，支持构建单体项目和微服务项目。

### 模块类型

#### 1. API 模块（api/）
**职责**：定义基础契约（接口定义）

**包结构**：
```
nebula-uaa-api/
└── com/nebula/uaa/api/
    ├── service/               # 服务接口
    ├── model/                 # 数据模型
    │   ├── dto/               # 数据传输对象
    │   ├── command/           # 写命令
    │   └── query/             # 读查询
    ├── constant/              # 常量
    └── enumerate/             # 枚举
```

**特点**：
- 纯接口定义，无实现
- 可被 core、local、remote 模块依赖
- 包含跨模块使用的常量和枚举

---

#### 2. Core 模块（core/）
**职责**：服务实现 + 数据访问（无 Controller）

**包结构**：
```
nebula-uaa-core/
└── com/nebula/uaa/core/
    ├── service/               # Service 层
    │   └── impl/              # Service 实现
    ├── dao/
    │   └── mapper/            # MyBatis Mapper 接口
    ├── model/                 # 数据模型
    │   ├── entity/            # 实体类（对应数据库表）
    │   ├── dto/               # 数据传输对象
    │   ├── command/           # 写命令（Service 入参）
    │   ├── query/             # 读查询（Service 入参）
    │   └── param/             # DAO 查询参数（>3 参数时）
    └── config/               # 配置类
```

**特点**：
- 包含完整的业务逻辑实现
- 无 Controller 层
- 可被 local 和 remote 模块依赖

---

#### 3. Local 模块（local/）
**职责**：封装 Controller 层（单体应用使用）

**包结构**：
```
nebula-uaa-local/
└── com/nebula/uaa/local/
    ├── controller/            # Controller 层
    ├── model/
    │   ├── req/               # 请求参数（Controller 入参）
    │   └── resp/              # 响应参数（Controller 返回）
    ├── converter/             # MapStruct 转换器
    └── config/               # 配置类
```

**特点**：
- 封装 Controller 层
- 负责 HTTP 请求/响应处理
- 进行 Req/Resp → Command/Query 的转换
- 可被 service 模块依赖

---

#### 4. Remote 模块（remote/）
**职责**：远程调用客户端（微服务使用）

**包结构**：
```
nebula-uaa-remote/
└── com/nebula/uaa/remote/
    ├── feign/                 # Feign 客户端
    └── config/               # 配置类
```

**特点**：
- 引入 base-cloud 和 api 模块
- 提供 Feign 客户端
- 其他服务通过 remote 模块调用

---

#### 5. Service 模块（service/）
**职责**：独立应用（包含 local 模块）

**包结构**：
```
nebula-uaa-service/
└── com/nebula/uaa/service/
    ├── application/           # 启动类
    └── resources/            # 配置文件
```

**特点**：
- 独立部署的应用
- 包含 local 模块
- 其他服务通过 remote 模块调用本服务

---

#### 6. Base 基础模块
**职责**：提供通用能力

**子模块**：
```
base/
├── base-model/               # 基础数据模型
├── base-mybatis/             # MyBatis 配置和转换
├── base-web/                 # Web 基础配置
└── base-cloud/               # 微服务基础配置
```

---

## 分层职责

### Controller 层（local/controller/）

**职责**：
- 处理 HTTP 请求和响应
- 参数校验（使用 Jakarta Validation）
- 将 Req 转换为 Command/Query
- 调用 Service 层
- 返回 Resp

**不包含**：
- 业务逻辑
- 数据访问
- 复杂计算

---

### Service 层（core/service/）

**职责**：
- 编排业务流程
- 封装核心业务逻辑
- 事务管理
- 调用 DAO 层
- 调用外部服务（通过 API 接口）

**轻量级 DDD**：
- 可拆分 Internal Service（内部服务）
- Internal Service 封装可复用的业务逻辑
- 避免过度设计，保持简单

**示例**：
```java
// 对外接口（编排业务流程）
@Service
public class UserServiceImpl implements IUserService {
    @Autowired
    private UserInternalService userInternalService;

    @Transactional
    public Long createUser(CreateUserCommand cmd) {
        // 调用内部服务进行业务校验
        userInternalService.validateUsername(cmd.getUsername());
        userInternalService.validateEmail(cmd.getEmail());

        // 创建用户
        User user = new User();
        // ...

        // 保存
        return userRepo.save(user);
    }
}

// 内部服务（封装可复用的业务逻辑）
@Service
public class UserInternalService {
    public void validateUsername(String username) {
        if (userRepo.existsByUsername(username)) {
            throw new BusinessException("用户名已存在");
        }
    }
}
```

---

### DAO 层（core/dao/mapper/）

**职责**：
- 数据库操作
- 单表查询（使用 MyBatis Plus）
- 复杂查询（自定义 SQL）
- 缓存管理（如果需要）

**返回类型规则**：
- 单表查询：返回 Entity
- 多表联查：返回 DTO
- 只读查询：返回 DTO

---

## 数据流转

```
HTTP 请求
  ↓
Controller 入参
  ↓
Req (local/model/req/)
  ↓
MapStruct 转换
  ↓
Command/Query (core/model/command|query/)
  ↓
Service 层
  ↓
DTO/Entity (core/model/dto|entity/)
  ↓
Mapper
  ↓
数据库
```

返回流程相反。

---

## 架构优势

### 1. 灵活性
- 同一套代码可构建单体应用或微服务
- 通过包组合实现不同部署方式

### 2. 可维护性
- 按业务域划分，职责清晰
- 模块间低耦合，易于修改

### 3. 可扩展性
- 新增业务模块只需遵循现有规范
- 可独立开发和部署

### 4. 复用性
- API 模块可被多个模块依赖
- Base 模块提供通用能力
