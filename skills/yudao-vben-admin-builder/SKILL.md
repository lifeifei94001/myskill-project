---
name: yudao-vben-admin-builder
description: "Use when building or extending Java enterprise management systems with Yudao (ruoyi-vue-pro / yudao-boot-mini) and Vben 5 or Vue3 Element Plus frontend. Triggers on: '芋道', 'yudao', 'ruoyi-vue-pro', 'yudao-boot-mini', 'Vben', '若依', or when designing Java SaaS, multi-tenant backends, complex RBAC, BPM approval workflows, ERP, CRM, or tenant management systems even without framework names. Do NOT trigger for lightweight internal tools, single-table scripts, or Python/Node stacks. Communicates in plain business language for non-technical users."
---

# 芋道后台系统搭建技能 (Yudao & Vben Admin Builder)

本技能用于全流程指导基于**芋道开源 (ruoyi-vue-pro / yudao-boot-mini)** 与 **Vben 5 / Vue3 Element Plus 前端** 构建 Java 企业级大型中后台系统（如 SaaS 多租户、BPM 审批流、ERP、CRM 等）。

---

## 一、 四大核心铁律 (最高优先级)

1. **先搜后写，严禁凭空造码**：
   在动笔编写任何 Java、`.vue` 或 `data.ts` 代码前，**必须先在当前仓库使用 grep/glob 搜索同模块已有文件作为唯一模板**照着仿写。包路径、基类、工具类方法、前端组件 API 必须在仓库中已存在，严禁凭记忆臆造。
2. **能用代码生成器出的 CRUD，绝不手写**：
   表单、表格、增删改查全部由后台「基础设施 → 代码生成」产出基础骨架。AI 的核心精力**仅用于增量逻辑**：复杂业务校验、状态流转机、聚合统计、报表导出、特殊数据权限。
3. **改完必验证，不盲猜报错**：
   每次修改代码后必须执行编译或启动验证。遇到报错必须调出完整错误日志定位根因再修复，绝不凭感觉猜测。
4. **大白话业务沟通**：
   用户通常不懂底层代码，只懂业务。沟通时避免倾倒技术术语，每一步操作需提供三要素：
   - **你要做什么**（清晰简短的动作）
   - **你会看到什么**（预期的界面变化或反馈）
   - **如果不对怎么办**（常见排错要点）
   验收时给出结构化业务清单，指导用户在界面按业务流程完整点选验证。

---

## 二、 项目选型与前端决策

### 1. 官方资源矩阵

| 组成部分 | 官方项目地址 / 分支 | 说明 |
| :--- | :--- | :--- |
| **后端完整版 (首选)** | `https://github.com/YunaiV/ruoyi-vue-pro`<br>（JDK 17/21 + Spring Boot 3 请用 `master-jdk17` 分支） | 包含系统基础设施、工作流 (BPM)、CRM、ERP、商城等全套功能，满足复杂企业级需求。 |
| **后端精简版** | `https://github.com/yudaocode/yudao-boot-mini` | 仅保留系统与基础设施模块，剔除工作流与大型业务模块。仅适合轻量人员/租户管理。 |
| **前端 Vue3 + Element Plus** | `https://github.com/yudaocode/yudao-ui-admin-vue3` | 结构成熟固定，组件生态极其稳定，AI 生成代码的准确率最高。 |
| **前端 Vben 5** | `https://github.com/yudaocode/yudao-ui-admin-vben` | 现代化设计、高颜值、交互精致。因迭代较快，AI 容易误混入旧版写法，需严格对照仓库模板。 |

- **官方文档**：[https://doc.iocoder.cn/quick-start/](https://doc.iocoder.cn/quick-start/)
- **视频教程**：[https://doc.iocoder.cn/video/](https://doc.iocoder.cn/video/)
- **国内镜像**：访问 GitHub 缓慢时可切换 Gitee 同名组织（`yudaocode` 组织）。

### 2. 前端选型决策指南 (让用户先看演示)
1. **引导用户查看官方演示**：
   - Vue3 版：[http://dashboard-vue3.yudao.iocoder.cn](http://dashboard-vue3.yudao.iocoder.cn)
   - Vben 版：[http://dashboard-vben.yudao.iocoder.cn](http://dashboard-vben.yudao.iocoder.cn)
2. **选择逻辑**：
   - 用户认可 Vue3 版视觉风格 → **直接选 Vue3 版（最稳健）**。
   - 用户对界面质感有极高要求，且确认所需业务模块在 Vben 演示中已有完整实现 → **选 Vben 版**。
   - *两套前端接口完全对齐通用，后续可随时根据需要平滑切换。*

### 3. 后端选型决策指南
- 需要审批流 (BPM)、ERP、CRM 或完整多租户企业级系统 → **必须选完整版**。
- 仅需要账号、角色、基础租户隔离的小型管理端 → **可选精简版**（提示用户：未来若需补充工作流需手动迁移相关模块）。

---

## 三、 标准开发流程 (8 步落地法)

```
① 需求访谈 ➔ ② 运行环境 ➔ ③ 规范建表 ➔ ④ 代码生成 ➔ ⑤ 安全落盘 ➔ ⑥ AI 增量 ➔ ⑦ 业务验收 ➔ ⑧ 上线自检
```

### 1. 需求访谈 (大白话调研)
向用户确认核心业务要素：
- 系统中有哪几种角色？各自管什么事？
- 核心管理对象是什么（客户、线索、员工、订单、合同）？每个对象有哪些字段和流转状态？
- 谁能看、谁能改、谁能审？
- 是否需要多租户独立隔离？是否需要工作流审批？

### 2. 环境搭建与首跑验证
- **依赖设施**：使用 Docker 启动 MySQL (8.0+) 与 Redis (6.0+)。
- **开发工具**：后端需 JDK 17/21 + Maven 3.8+；前端需 Node.js ≥ 20（Vben 版强制使用 `pnpm` 包管理器）。
- **首跑验证**：先跑通官方默认代码与演示页面，让用户确认初始系统功能正常且视觉符合预期。

### 3. 数据库设计规范
- 表名统一使用小写下划线：`模块_业务对象`（例如 `crm_customer`、`trade_order`）。
- 每张业务表必须带有芋道标准字段（详见 `references/yudao_backend_conventions.md`）：
  - 审计字段：`creator`, `create_time`, `updater`, `update_time`, `deleted`
  - 多租户表必带：`tenant_id`
- **辅助生成**：使用内置脚本快速生成标准 DDL：
  ```bash
  python scripts/generate_yudao_ddl.py --table <表名> --comment <业务说明>
  ```

### 4. 代码生成器出骨架
1. 登录管理后台，进入 **「基础设施」 -> 「代码生成」**。
2. 点击「基于 DB 导入」，搜索并勾选目标表。
3. 编辑生成信息（模块名、业务名、前端模板选 Vue3 或 Vben、指定上级挂载菜单）。
4. 点击「生成代码」，下载压缩包（详细配置见 [code_generator_workflow.md](references/code_generator_workflow.md)）。

### 5. 代码落盘与执行安全
- **在具备文件与执行能力的环境（如 Claude Code / 本地智能代理）**：
  1. 解压生成包，将 Java 代码与前端 Vue/TS 文件准确移动至对应模块目录。
  2. 检查 `sql/sql.sql` 中的父级菜单编号（`parent_id`），确认与目标位置匹配。
  3. **仅在本地开发数据库执行 SQL**；**在执行前务必对开发数据库进行备份**。
  4. 清理 Redis 菜单与权限缓存（或直接重启后端服务）。
  5. 引导用户完成关键一步：进入后台 **「系统管理」 -> 「角色管理」**，给角色勾选新菜单权限并保存。
  - **生产环境绝对严禁自动执行任何 SQL！**
- **在纯对话环境（无法操作文件与数据库）**：
  - 输出明确的文件存放清单、路径映射以及 SQL 执行指导，由用户确认后自行执行。

### 6. AI 增量业务开发
- 严格遵循四大铁律第 1 条，以同模块已有业务代码为模板进行扩展。
- 业务校验写在 Service 层，错误通过 `ErrorCodeConstants` 抛出 `ServiceException`。

### 7. 用户验收清单
向用户提供清晰的界面点选测试步骤：
- **新增**：填入测试数据保存，检查必填提示是否友好。
- **列表与搜索**：多维度筛选、重置、分页是否生效。
- **编辑与删除**：修改后数据是否即时更新；删除后列表是否不再展示。
- **权限与隔离**：切换不同角色或不同租户账号，验证数据是否真正隔离。

### 8. 上线与安全复核
上线前向用户提示核心安全检查项：
- 更改默认管理员密码与 Redis 密码。
- 检查后端端口与 Swagger 接口文档是否禁止外网裸露访问。
- 确认自动化数据库备份任务与 HTTPS 证书配置完毕。

---

## 四、 核心代码约束 (规避常见陷阱)

### 1. 后端约束
- **多租户继承**：多租户实体必须继承 `TenantBaseDO`，MyBatis-Plus 插件会自动追加租户过滤，**严禁在业务代码中手写租户过滤条件**。
- **持久层封装**：Mapper 继承 `BaseMapperX<T>`，使用 `LambdaQueryWrapperX<T>` 构建带 `IfPresent` 的动态查询。
- **控制层接口**：统一返回 `CommonResult<T>`；接口鉴权使用 `@PreAuthorize("@ss.hasPermission('模块:对象:动作')")`。
- **错误码管理**：错误码统一定义在当前模块的 `ErrorCodeConstants` 中，避免硬编码中文异常文本。
- **DO 与 VO 转换**：**严格遵循当前模块已有的转换风格**（新模块大多采用 `BeanUtils.toBean()`，部分已有模块使用 MapStruct），不要在同一模块内杂糅混用。
- **业务流水号生成**：**严禁使用「日期 + 随机数」**，必须使用 Redis 自增生成器或数据库自增序列。
- **主键策略**：`@KeySequence` 仅在 Oracle、达梦等依赖 Sequence 的数据库中使用，**MySQL 项目坚决不加**。

### 2. 前端约束
- **Vben 5 防踩坑**：**严禁使用 Vben 2.x 的废弃 API**（如 `BasicTable`, `BasicForm`, `useTable`, `useForm` 等）。必须以当前仓库已有的页面和 `data.ts` 为唯一蓝本。
- **时间格式一致性**：前后端时间类型需严格对应（如前端组件指定 `value-format="x"` 对应 Unix 时间戳，不要直接传原生 Date 对象）。
- **字典通用性**：状态类字段展示统一采用字典标签组件，不要在前端页面散落大量三元表达式。

---

## 五、 与用户的沟通与答疑原则

1. **纠正“AI 零幻觉一键搞定”的误区**：
   若用户提及“AI 能够一键全自动生成无 Bug 系统”，应如实说明：复杂业务系统的稳定性依赖于成熟的代码生成器骨架、规范的既有代码仿写、以及严格的编译验证闭环。
2. **纯聊天场景提醒**：
   如果当前环境无法直接操作本地文件，应主动提醒用户手动复制粘贴代码、手动执行 SQL 的潜在遗漏风险，并给出分步定位排错方案。

---

## 模块参考文档与实用工具

- [yudao_backend_conventions.md](references/yudao_backend_conventions.md)：后端核心类、DO/VO 转换、MapperX 查询与错误码规范。
- [vben5_frontend_conventions.md](references/vben5_frontend_conventions.md)：Vben 5 与 Vue3 Element Plus 选型指南、组件范式与避坑对照表。
- [code_generator_workflow.md](references/code_generator_workflow.md)：代码生成器配置全流程与开发库安全落盘准则。
- `scripts/generate_yudao_ddl.py`：标准建表 DDL 生成工具。
