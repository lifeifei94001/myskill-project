# 芋道后端开发规范与最佳实践 (Yudao Backend Conventions)

本手册基于 `ruoyi-vue-pro` (Spring Boot 3 + JDK 17/21 `master-jdk17` 分支与微服务/单体架构) 编写，用于指导 AI 代理在进行增量代码编写时保持与框架标准高度一致。

---

## 1. 核心铁律：读已有模板再写

> **永远不要从零凭空编写 Controller、Service、Mapper 或 DO。**
> 在开始动笔前，使用 `find_by_name` 或 `grep_search` 查找当前模块内现有的实体与接口（例如 `system`、`infra`、`crm` 或 `erp` 模块），严格遵循其包名、导入、基类与命名风格。

---

## 2. 数据实体规范 (DO)

### 2.1 基类选择
芋道提供两种标准基类：
- **普通业务表**：继承 `BaseDO`（包含 `creator`, `createTime`, `updater`, `updateTime`, `deleted`）。
- **多租户业务表**（90% 以上的企业级业务表）：继承 `TenantBaseDO`（继承自 `BaseDO` 并附加 `tenantId` 字段）。

```java
package cn.iocoder.yudao.module.crm.dal.dataobject.customer;

import cn.iocoder.yudao.framework.mybatis.core.dataobject.TenantBaseDO;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.*;

@TableName("crm_customer")
@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CrmCustomerDO extends TenantBaseDO {

    @TableId
    private Long id;

    private String name;

    private Integer status;

    private String remark;
}
```

> **注意：**
> 1. 多租户数据隔离由 MyBatis-Plus 租户插件自动拦截注入，**严禁在业务 SQL / QueryWrapper 中手动追加 `eq(tenant_id)` 过滤条件**。
> 2. `@KeySequence` 注解仅用于 Oracle、达梦等依赖 DB Sequence 的数据库，**MySQL 项目严禁添加**。

---

## 3. 持久层规范 (Mapper)

继承 `BaseMapperX<T>`，使用 `LambdaQueryWrapperX<T>` 构造条件查询：

```java
package cn.iocoder.yudao.module.crm.dal.mysql.customer;

import cn.iocoder.yudao.framework.common.pojo.PageResult;
import cn.iocoder.yudao.framework.mybatis.core.mapper.BaseMapperX;
import cn.iocoder.yudao.framework.mybatis.core.query.LambdaQueryWrapperX;
import cn.iocoder.yudao.module.crm.controller.admin.customer.vo.CrmCustomerPageReqVO;
import cn.iocoder.yudao.module.crm.dal.dataobject.customer.CrmCustomerDO;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface CrmCustomerMapper extends BaseMapperX<CrmCustomerDO> {

    default PageResult<CrmCustomerDO> selectPage(CrmCustomerPageReqVO reqVO) {
        return selectPage(reqVO, new LambdaQueryWrapperX<CrmCustomerDO>()
                .likeIfPresent(CrmCustomerDO::getName, reqVO.getName())
                .eqIfPresent(CrmCustomerDO::getStatus, reqVO.getStatus())
                .betweenIfPresent(CrmCustomerDO::getCreateTime, reqVO.getCreateTime())
                .orderByDesc(CrmCustomerDO::getId));
    }
}
```

> **方法要点：**
> - 使用 `likeIfPresent`、`eqIfPresent`、`betweenIfPresent`，当参数为 null 或空字符串时自动忽略，避免手写大量 `if (reqVO.getName() != null)`。

---

## 4. 控制层规范 (Controller)

- 接口返回统一使用 `CommonResult<T>`。
- 权限注解统一使用 `@PreAuthorize("@ss.hasPermission('模块:对象:动作')")`。
- 操作日志统一使用 `@OperateLog(type = ...)`。

```java
@Tag(name = "管理后台 - 客户管理")
@RestController
@RequestMapping("/crm/customer")
@Validated
public class CrmCustomerController {

    @Resource
    private CrmCustomerService customerService;

    @PostMapping("/create")
    @Operation(summary = "创建客户")
    @PreAuthorize("@ss.hasPermission('crm:customer:create')")
    public CommonResult<Long> createCustomer(@Valid @RequestBody CrmCustomerSaveReqVO createReqVO) {
        return success(customerService.createCustomer(createReqVO));
    }

    @GetMapping("/page")
    @Operation(summary = "获得客户分页")
    @PreAuthorize("@ss.hasPermission('crm:customer:query')")
    public CommonResult<PageResult<CrmCustomerRespVO>> getCustomerPage(@Valid CrmCustomerPageReqVO pageReqVO) {
        PageResult<CrmCustomerDO> pageResult = customerService.getCustomerPage(pageReqVO);
        return success(BeanUtils.toBean(pageResult, CrmCustomerRespVO.class));
    }
}
```

---

## 5. 对象转换 (DO 与 VO 转换)

**严格遵循当前模块已有模式：**
1. **主流新版本规范**：使用芋道框架封装的 `cn.iocoder.yudao.framework.common.util.object.BeanUtils`：
   ```java
   CrmCustomerDO customer = BeanUtils.toBean(createReqVO, CrmCustomerDO.class);
   return BeanUtils.toBean(pageResult, CrmCustomerRespVO.class);
   ```
2. **遗留模块或部分复杂模块**：使用 MapStruct `XxxConvert.INSTANCE.convert(...)`。
3. **禁止混合**：同一个业务模块内部保持统一，不要一半写 MapStruct 一半写 BeanUtils。

---

## 6. 异常与错误码规范

- 错误码统一定义在当前模块的 `ErrorCodeConstants` 中：
  ```java
  ErrorCode CUSTOMER_NOT_EXISTS = new ErrorCode(1_002_001_000, "客户不存在");
  ErrorCode CUSTOMER_NAME_DUPLICATE = new ErrorCode(1_002_001_001, "客户名称已经存在");
  ```
- 业务校验失败直接抛出 `ServiceExceptionUtil.exception(CUSTOMER_NOT_EXISTS)`。
- 错误码段需遵循芋道模块分配规则（每模块分配不同千分位前缀），避免跨模块冲突。

---

## 7. 唯一业务编码生成

- **严禁使用 `日期 + 随机数`**（高并发或重置时必现重复 Bug）。
- **标准方案**：
  1. 使用 Redis 自增编号生成器（如 `RedisIdUtils` 或 `RedisSequence`）。
  2. 或使用模块内的流水号规则引擎生成连续编号。
