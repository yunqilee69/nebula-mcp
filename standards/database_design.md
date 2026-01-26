# Nebula 中台数据库设计规范

## 表命名规范

### 基本规则

- **表前缀**：所有中台表必须以 `cx_` 为前缀
- **单数形式**：表名使用单数形式，不使用复数
- **命名风格**：使用 snake_case（蛇形命名）
- **业务含义**：表名应清晰表达业务含义

### 表名示例

| 表名 | 说明 | 是否符合规范 |
|------|------|------------|
| `cx_user` | 用户表 | ✅ 符合 |
| `cx_order` | 订单表 | ✅ 符合 |
| `cx_order_item` | 订单明细表 | ✅ 符合 |
| `t_user` | 用户表 | ❌ 不符合（缺少 cx_ 前缀） |
| `cx_users` | 用户表 | ❌ 不符合（使用复数形式） |
| `user` | 用户表 | ❌ 不符合（缺少 cx_ 前缀） |

---

## 字段命名规范

### 基本规则

- **命名风格**：使用 snake_case（蛇形命名）
- **小写字母**：全部使用小写字母
- **下划线分隔**：使用下划线分隔单词
- **业务含义**：字段名应清晰表达业务含义

### 字段示例

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | BIGINT | 主键 |
| `user_name` | VARCHAR | 用户名 |
| `email` | VARCHAR | 邮箱 |
| `mobile` | VARCHAR | 手机号 |
| `create_time` | DATETIME | 创建时间 |
| `update_time` | DATETIME | 更新时间 |
| `is_deleted` | TINYINT(1) | 是否删除 |

---

## 必选字段规范

### 所有表必须包含的字段

所有业务表必须包含以下字段：

#### 1. 主键字段

```sql
`id` BIGINT NOT NULL COMMENT '主键'
```

- **类型**：BIGINT
- **是否为空**：NOT NULL
- **命名**：`id`
- **取值**：使用雪花算法生成
- **说明**：主键，base-mybatis 包中提供雪花算法支持

---

#### 2. 审计字段

```sql
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
`update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
```

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `create_time` | DATETIME | CURRENT_TIMESTAMP | 创建时间，不可为空 |
| `update_time` | DATETIME | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间，不可为空，自动更新 |

---

#### 3. 逻辑删除字段（可选，但建议）

```sql
`is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除（0：否，1：是）'
```

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `is_deleted` | TINYINT(1) | 0 | 是否删除，0 表示未删除，1 表示已删除 |

---

## 完整建表示例

### 标准建表语句

```sql
CREATE TABLE `cx_user` (
  `id` BIGINT NOT NULL COMMENT '主键',
  `user_name` VARCHAR(50) NOT NULL COMMENT '用户名',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `mobile` VARCHAR(20) COMMENT '手机号',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态（1：活跃，0：非活跃）',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除（0：否，1：是）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name` (`user_name`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_mobile` (`mobile`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

## 主键规范

### 使用雪花算法

Nebula 中台使用雪花算法生成主键 ID，由 `base-mybatis` 包提供支持。

#### 雪花算法特点

- 全局唯一
- 趋势递增
- 高性能
- 分布式友好

#### 配置雪花算法

在 `application.yml` 中配置雪花算法的集群 ID 和节点 ID：

```yaml
mybatis-plus:
  global-config:
    db-config:
      id-type: ASSIGN_ID  # 使用雪花算法

nebula:
  snowflake:
    cluster-id: 1        # 集群 ID（1-31）
    node-id: 1           # 节点 ID（1-31）
```

#### 参数说明

| 参数 | 说明 | 取值范围 | 必填 |
|------|------|---------|------|
| `cluster-id` | 集群 ID | 1-31 | 是 |
| `node-id` | 节点 ID | 1-31 | 是 |

**注意**：同一集群内，所有节点的 `cluster-id` 必须相同，但 `node-id` 必须唯一。

---

## 字段类型规范

### 字符串类型

| 类型 | 长度 | 使用场景 | 示例 |
|------|------|---------|------|
| VARCHAR(50) | 50 | 短字符串 | 用户名 |
| VARCHAR(100) | 100 | 中等长度字符串 | 邮箱 |
| VARCHAR(500) | 500 | 长字符串 | 地址 |
| TEXT | 65535 | 超长文本 | 备注信息 |

---

### 数值类型

| 类型 | 说明 | 使用场景 | 示例 |
|------|------|---------|------|
| BIGINT | 大整数 | 主键 ID、金额（分） | `id`、`amount` |
| INT | 整数 | 数量、状态、类型 | `count`、`status` |
| TINYINT | 小整数 | 布尔值、枚举值 | `is_deleted`、`status` |
| DECIMAL(10,2) | 小数 | 金额（元） | `price` |

---

### 日期时间类型

| 类型 | 说明 | 使用场景 | 示例 |
|------|------|---------|------|
| DATETIME | 日期时间 | 时间戳 | `create_time`、`update_time` |
| DATE | 日期 | 日期 | `birthday` |

---

## 索引规范

### 索引命名规范

| 索引类型 | 命名规则 | 示例 |
|---------|---------|------|
| 主键索引 | `PRIMARY` | `PRIMARY KEY (id)` |
| 唯一索引 | `uk_字段名` | `uk_user_name` |
| 普通索引 | `idx_字段名` | `idx_mobile` |
| 联合索引 | `idx_字段1_字段2` | `idx_user_name_status` |

---

### 索引设计原则

1. **主键索引**：所有表必须有主键索引
2. **唯一索引**：需要唯一约束的字段（如用户名、邮箱）
3. **普通索引**：频繁查询的字段
4. **联合索引**：经常一起查询的多个字段（遵循最左前缀原则）
5. **避免过多索引**：索引过多会影响写入性能

---

### 索引示例

```sql
-- 主键索引
PRIMARY KEY (`id`)

-- 唯一索引
UNIQUE KEY `uk_user_name` (`user_name`)
UNIQUE KEY `uk_email` (`email`)

-- 普通索引
KEY `idx_mobile` (`mobile`)
KEY `idx_create_time` (`create_time`)

-- 联合索引
KEY `idx_user_name_status` (`user_name`, `status`)
```

---

## Entity 类规范

### 基本规则

Entity 类名使用 PascalCase，以 `Entity` 结尾。

### Entity 示例

```java
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.util.Date;

@Data
@TableName("cx_user")
public class UserEntity {

    /**
     * 主键（使用雪花算法）
     */
    @TableId(type = IdType.ASSIGN_ID)
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
    @TableField("is_deleted")
    private Boolean deleted;
}
```

---

## MyBatis Plus 自动填充配置

### 配置自动填充

在 `config/MyBatisPlusConfig.java` 中配置字段自动填充：

```java
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
import org.springframework.stereotype.Component;
import java.util.Date;

@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", Date.class, new Date());
        this.strictInsertFill(metaObject, "updateTime", Date.class, new Date());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", Date.class, new Date());
    }
}
```

---

## 数据库设计最佳实践

### 1. 使用合适的字段类型

```sql
-- ❌ 错误：使用 VARCHAR 存储金额
`price` VARCHAR(20) NOT NULL COMMENT '价格'

-- ✅ 正确：使用 DECIMAL 存储金额
`price` DECIMAL(10,2) NOT NULL COMMENT '价格'
```

---

### 2. 避免使用 NULL

```sql
-- ❌ 错误：允许 NULL
`user_name` VARCHAR(50) NULL COMMENT '用户名'

-- ✅ 正确：设置默认值
`user_name` VARCHAR(50) NOT NULL DEFAULT '' COMMENT '用户名'
```

---

### 3. 使用逻辑删除

```sql
-- ❌ 错误：物理删除
DELETE FROM cx_user WHERE id = 12345;

-- ✅ 正确：逻辑删除
UPDATE cx_user SET is_deleted = 1 WHERE id = 12345;
```

---

### 4. 使用注释

```sql
-- ✅ 正确：所有字段和表都添加注释
CREATE TABLE `cx_user` (
  `id` BIGINT NOT NULL COMMENT '主键',
  `user_name` VARCHAR(50) NOT NULL COMMENT '用户名',
  ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

---

### 5. 设置字符集

```sql
-- ✅ 正确：使用 utf8mb4 字符集
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```
