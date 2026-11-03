# 芋道前端选型与编码规范 (Vben5 与 Vue3 版)

本文档指导 AI 代理在处理芋道官方提供的两套前端框架时的选型策略与编码约束。

---

## 1. 前端选型与演示对比流程

在开始写前端前，**必须引导非技术用户先看官方演示并体验业务操作**：

| 前端方案 | 官方演示地址 | 核心特点 | 适用建议 |
| :--- | :--- | :--- | :--- |
| **Vue3 + Element Plus** | [http://dashboard-vue3.yudao.iocoder.cn](http://dashboard-vue3.yudao.iocoder.cn) | 经典中后台风格，组件生态成熟，AI 生成准确率极高 | **首选推荐**。如果用户追求稳定、低维护成本、业务功能完整，选此版 |
| **Vben 5 (Vue 3 + Tailwind/Shadcn UI)** | [http://dashboard-vben.yudao.iocoder.cn](http://dashboard-vben.yudao.iocoder.cn) | 颜值高、现代化设计、动效精致，但版本演进快 | 用户对颜值有硬性要求，且确认所需业务模块在演示中已有完整实现时选此版 |

> **关键提醒：**
> 两套前端与芋道后端 RESTful API 完全通用。如果在项目中期用户对界面有更换需求，可以直接无缝对接另一套前端。

---

## 2. Vben 5 编码铁律与避坑清单

### 2.1 严禁混入 Vben 2.x 废弃 API
AI 极易受历史语料污染生成已经淘汰的 Vben 2.x 语法。**在当前项目中绝对禁止出现以下写法**：
- ❌ **严禁**：`import { BasicTable, useTable } from '@/components/Table'`
- ❌ **严禁**：`import { BasicForm, useForm } from '@/components/Form'`
- ❌ **严禁**：`import { BasicModal, useModal } from '@/components/Modal'`
- ❌ **严禁**：`createConfirm`, `useMessage` 的旧式写法

### 2.2 遵循仓库内已有业务模块结构
Vben 5 的业务模块标准结构通常为：
```text
views/crm/customer/
├── index.vue        # 列表主页面
├── data.ts          # 表格列定义、表单搜索项定义
├── customer-form.vue# 新增/修改抽屉或弹窗
└── api.ts           # 对应模块接口请求 (或统一放在 api/crm/customer.ts)
```

**操作前必做：**
先打开仓库中现有的成熟模块（如 `views/system/user/` 或 `views/infra/codegen/`），检查其：
1. `data.ts` 中的 `columns`、`formSchema` 结构声明。
2. 表格与弹窗的组合机制（查看是使用 `useVbenDrawer` 还是 `useVbenModal`）。
3. 严格拷贝导入路径与组件命名，切勿凭空编造。

---

## 3. Vue3 + Element Plus 版编码规范 (`yudao-ui-admin-vue3`)

### 3.1 页面典型范式
Vue3 版通常基于 `element-plus`，搭配芋道封装的通用 CRUD 工具（如 `useCrudSchemas`、`ContentWrap`、`Dialog` 等）：
- 检查同级目录下现有的 `[entity].data.ts` 和 `index.vue`。
- 搜索表单使用统一封装或 `el-form` + `el-row` / `el-col` 栅格。
- 按钮权限通过 `v-hasPermi="['module:entity:action']"` 指令控制。

---

## 4. 前后端数据交互关键约束

### 4.1 日期与时间格式一致性
- 后端 Spring Boot 默认接收和返回 Unix 毫秒时间戳或 `LocalDateTime`（格式为 `yyyy-MM-dd HH:mm:ss`）。
- 前端日期选择器组件（`el-date-picker` 或 Vben 日期选择框）：
  - 若传时间戳，必须指定 `value-format="x"`。
  - 若传格式化字符串，必须指定 `value-format="YYYY-MM-DD HH:mm:ss"`。
  - **严禁直接传递 JavaScript 原生 `Date` 对象给后端**，避免反序列化异常。

### 4.2 字典项绑定
- 芋道提供了全局字典缓存机制。
- 状态字段在列表展示时，优先使用字典标签组件（例如 `<dict-tag :type="DICT_TYPE.COMMON_STATUS" :value="row.status" />`）。
- 不要手写 `status === 0 ? '正常' : '关闭'` 散落在各个页面中。
