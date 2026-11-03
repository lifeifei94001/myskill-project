# RuoYi Backend Conventions & API Standards

This reference documents the code patterns and conventions expected from RuoYi (Spring Boot 2.x/3.x) when pairing with modern React / Shadcn Admin frontends.

---

## 1. Standard API Response Structures

### 1.1 Single Object / Mutation Response (`AjaxResult`)
RuoYi standard wrapper for commands, updates, deletes, and single-item fetches:

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "id": 1,
    "name": "王福荣"
  }
}
```

* **`code: 200`** — Success.
* **`code: 401`** — Unauthorized / Token expired.
* **`code: 403`** — Forbidden / Insufficient permissions.
* **`code: 500`** — Business or server error (`msg` contains the user-facing message).

### 1.2 Paginated Table Query Response (`TableDataInfo`)
When querying lists for data tables (using RuoYi `startPage()`):

```json
{
  "total": 1428,
  "rows": [
    {
      "id": 101,
      "name": "王福荣",
      "idCard": "330106194803152819",
      "phone": "13857129081",
      "status": "0",
      "createTime": "2026-01-10 12:30:00"
    }
  ],
  "code": 200,
  "msg": "查询成功"
}
```

---

## 2. Standard Spring Boot Controller Template

```java
package com.ruoyi.project.village.controller;

import java.util.List;
import javax.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import com.ruoyi.framework.web.controller.BaseController;
import com.ruoyi.framework.web.domain.AjaxResult;
import com.ruoyi.framework.web.page.TableDataInfo;
import com.ruoyi.framework.aspectj.lang.annotation.Log;
import com.ruoyi.framework.aspectj.lang.enums.BusinessType;
import com.ruoyi.project.village.domain.VillageVillager;
import com.ruoyi.project.village.service.IVillageVillagerService;

@RestController
@RequestMapping("/village/villager")
public class VillageVillagerController extends BaseController {

    @Autowired
    private IVillageVillagerService villagerService;

    /**
     * 分页查询村民列表
     */
    @PreAuthorize("@ss.hasPermi('village:villager:list')")
    @GetMapping("/list")
    public TableDataInfo list(VillageVillager query) {
        startPage(); // 自动拦截 pageNum 与 pageSize 参数
        List<VillageVillager> list = villagerService.selectVillagerList(query);
        return getDataTable(list);
    }

    /**
     * 获取单个村民详细信息
     */
    @PreAuthorize("@ss.hasPermi('village:villager:query')")
    @GetMapping("/{id}")
    public AjaxResult getInfo(@PathVariable("id") Long id) {
        return success(villagerService.selectVillagerById(id));
    }

    /**
     * 新增村民
     */
    @PreAuthorize("@ss.hasPermi('village:villager:add')")
    @Log(title = "村民档案", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody VillageVillager villager) {
        villager.setCreateBy(getUsername());
        return toAjax(villagerService.insertVillager(villager));
    }

    /**
     * 修改村民
     */
    @PreAuthorize("@ss.hasPermi('village:villager:edit')")
    @Log(title = "村民档案", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody VillageVillager villager) {
        villager.setUpdateBy(getUsername());
        return toAjax(villagerService.updateVillager(villager));
    }

    /**
     * 删除村民 (支持批量: id1,id2,id3)
     */
    @PreAuthorize("@ss.hasPermi('village:villager:remove')")
    @Log(title = "村民档案", businessType = BusinessType.DELETE)
    @DeleteMapping("/{ids}")
    public AjaxResult remove(@PathVariable Long[] ids) {
        return toAjax(villagerService.deleteVillagerByIds(ids));
    }
}
```

---

## 3. RuoYi BaseEntity Standard Fields

All domain entity classes in RuoYi should extend `BaseEntity`:

```java
public class BaseEntity implements Serializable {
    private String searchDate;
    private String createBy;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createTime;
    private String updateBy;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updateTime;
    private String remark;
    private Map<String, Object> params;
    // getters & setters
}
```

---

## 4. CORS Configuration for Local Development

When developing with Vite on `http://localhost:5173` and RuoYi on `http://localhost:8080`, either:

### Method A: Vite Reverse Proxy (Recommended, zero Java changes)
In `vite.config.ts`:
```ts
server: {
  port: 5173,
  proxy: {
    '/dev-api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/dev-api/, ''),
    },
  },
}
```

### Method B: RuoYi `ResourcesConfig.java` Global CORS Filter
```java
@Configuration
public class ResourcesConfig implements WebMvcConfigurer {
    @Bean
    public CorsFilter corsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowCredentials(true);
        config.addAllowedOriginPattern("*");
        config.addAllowedHeader("*");
        config.addAllowedMethod("*");
        config.setMaxAge(1800L);
        source.registerCorsConfiguration("/**", config);
        return new CorsFilter(source);
    }
}
```
