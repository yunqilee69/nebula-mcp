# Nebula 中台配置管理规范

## 配置文件结构

### 目录结构

```
src/main/resources/
├── application.yml              # 通用配置
├── application-dev.yml          # 开发环境配置
├── application-test.yml         # 测试环境配置
├── application-prod.yml         # 生产环境配置
├── logback.xml                  # 日志配置
└── banner.txt                   # 启动横幅
```

---

### 环境配置切换

在 `application.yml` 中激活对应的环境配置：

```yaml
spring:
  profiles:
    active: dev  # dev、test、prod
```

---

## 通用配置（application.yml）

### 基础配置

```yaml
spring:
  application:
    name: nebula-uaa-service

  profiles:
    active: @profiles.active@  # 使用 Maven profile 或环境变量

  jackson:
    time-zone: GMT+8
    date-format: yyyy-MM-dd HH:mm:ss
    default-property-inclusion: non_null

  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 50MB

server:
  port: 8080
  servlet:
    context-path: /api
  tomcat:
    threads:
      max: 200
      min-spare: 10

logging:
  level:
    root: INFO
    com.nebula: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n"
```

---

## 环境配置规范

### 开发环境（application-dev.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/nebula_dev?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver

  redis:
    host: localhost
    port: 6379
    password:
    database: 0

nebula:
  snowflake:
    cluster-id: 1
    node-id: 1

logging:
  level:
    com.nebula: DEBUG
    org.springframework: DEBUG
```

---

### 测试环境（application-test.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://test-db.example.com:3306/nebula_test?useUnicode=true&characterEncoding=utf8&useSSL=true&serverTimezone=GMT%2B8
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver

  redis:
    host: test-redis.example.com
    port: 6379
    password: ${REDIS_PASSWORD}
    database: 0

nebula:
  snowflake:
    cluster-id: 2
    node-id: 1

logging:
  level:
    com.nebula: INFO
    org.springframework: WARN
```

---

### 生产环境（application-prod.yml）

```yaml
spring:
  datasource:
    url: jdbc:mysql://prod-db.example.com:3306/nebula_prod?useUnicode=true&characterEncoding=utf8&useSSL=true&serverTimezone=GMT%2B8
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  redis:
    host: prod-redis.example.com
    port: 6379
    password: ${REDIS_PASSWORD}
    database: 0
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5

nebula:
  snowflake:
    cluster-id: 3
    node-id: 1

logging:
  level:
    com.nebula: WARN
    org.springframework: WARN
  file:
    name: /var/log/nebula/nebula-uaa-service.log
    max-size: 100MB
    max-history: 30
```

---

## 敏感配置管理

### 使用环境变量

生产环境的敏感配置（数据库密码、Redis 密码、第三方密钥等）必须通过环境变量传递，不能硬编码在配置文件中。

#### 环境变量示例

```bash
# 数据库配置
export DB_USERNAME=nebula_prod
export DB_PASSWORD=your_secure_password

# Redis 配置
export REDIS_PASSWORD=your_redis_password

# 第三方密钥
export ALIYUN_ACCESS_KEY=your_access_key
export ALIYUN_ACCESS_SECRET=your_access_secret
```

#### 配置文件中使用环境变量

```yaml
spring:
  datasource:
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

  redis:
    password: ${REDIS_PASSWORD}
```

---

### 使用 Jasypt 加密（可选）

对于必须写入配置文件的敏感信息，使用 Jasypt 加密。

#### 添加依赖

```xml
<dependency>
    <groupId>com.github.ulisesbocchio</groupId>
    <artifactId>jasypt-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

#### 配置加密密码

```yaml
jasypt:
  encryptor:
    password: ${JASYPT_PASSWORD}  # 通过环境变量传递
```

#### 加密敏感信息

使用 Jasypt 工具加密敏感信息：

```bash
java -cp jasypt-1.9.3.jar org.jasypt.intf.cli.JasyptPBEStringEncryptionCLI \
  input="your_password" \
  password=${JASYPT_PASSWORD} \
  algorithm=PBEWithMD5AndDES
```

#### 配置文件中使用加密信息

```yaml
spring:
  datasource:
    password: ENC(加密后的密文)
```

---

## MyBatis Plus 配置规范

### 基础配置

```yaml
mybatis-plus:
  configuration:
    # 驼峰命名自动映射
    map-underscore-to-camel-case: true
    # 日志输出
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
  global-config:
    db-config:
      # 主键类型（雪花算法）
      id-type: ASSIGN_ID
      # 逻辑删除字段
      logic-delete-field: isDeleted
      logic-delete-value: 1
      logic-not-delete-value: 0
    banner: false  # 关闭 MyBatis Plus 的 banner
  # Mapper XML 扫描路径
  mapper-locations: classpath*:/mapper/**/*.xml
```

---

## 雪花算法配置

### 配置示例

```yaml
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```

---

### 参数说明

| 参数 | 说明 | 取值范围 | 必填 |
|------|------|---------|------|
| `cluster-id` | 集群 ID | 1-31 | 是 |
| `node-id` | 节点 ID | 1-31 | 是 |

---

### 集群节点规划示例

| 环境 | 集群 ID | 节点 ID | 节点名称 |
|------|---------|---------|---------|
| 开发环境 | 1 | 1 | dev-node1 |
| 测试环境 | 2 | 1 | test-node1 |
| 测试环境 | 2 | 2 | test-node2 |
| 生产环境 | 3 | 1 | prod-node1 |
| 生产环境 | 3 | 2 | prod-node2 |
| 生产环境 | 3 | 3 | prod-node3 |

**注意**：同一集群内，所有节点的 `cluster-id` 必须相同，但 `node-id` 必须唯一。

---

## 缓存配置规范

### Redis 配置

```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:
    database: 0
    timeout: 3000
    lettuce:
      pool:
        max-active: 20
        max-idle: 10
        min-idle: 5

nebula:
  cache:
    type: redis  # 或 caffeine
    redis:
      key-prefix: nebula:
      expire-time: 3600  # 默认过期时间（秒）
```

---

### Caffeine 配置

```yaml
nebula:
  cache:
    type: caffeine
    caffeine:
      maximum-size: 1000
      expire-after-write: 3600
```

---

## 日志配置规范

### Logback 配置（logback.xml）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/application.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 日志级别 -->
    <logger name="com.nebula" level="DEBUG"/>
    <logger name="org.springframework" level="WARN"/>
    <logger name="org.hibernate" level="WARN"/>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

---

## 配置管理最佳实践

### 1. 使用 Profile 区分环境

```yaml
spring:
  profiles:
    active: dev  # 使用 Maven profile 或环境变量
```

---

### 2. 敏感信息使用环境变量

```yaml
spring:
  datasource:
    password: ${DB_PASSWORD}  # ✅ 正确
    password: my_password      # ❌ 错误
```

---

### 3. 合理配置连接池

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20      # 最大连接数
      minimum-idle: 5           # 最小空闲连接数
      connection-timeout: 30000  # 连接超时时间（毫秒）
      idle-timeout: 600000       # 空闲连接超时时间（毫秒）
      max-lifetime: 1800000      # 连接最大存活时间（毫秒）
```

---

### 4. 配置雪花算法

```yaml
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```

**注意**：同一集群内，`cluster-id` 必须相同，`node-id` 必须唯一。

---

### 5. 配置日志级别

| 环境 | Root 级别 | Nebula 级别 | Spring 级别 |
|------|---------|------------|------------|
| 开发环境 | DEBUG | DEBUG | DEBUG |
| 测试环境 | INFO | DEBUG | WARN |
| 生产环境 | WARN | WARN | WARN |

---

### 6. 配置文件注释

```yaml
# 应用名称
spring:
  application:
    name: nebula-uaa-service

# 服务端口
server:
  port: 8080

# 雪花算法配置
nebula:
  snowflake:
    cluster-id: 1  # 集群 ID（1-31）
    node-id: 1     # 节点 ID（1-31）
```
