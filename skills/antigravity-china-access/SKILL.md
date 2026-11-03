---
name: antigravity-china-access
description: Google Antigravity 中国大陆网络连接解决方案。为 Google Antigravity 提供进程级局部代理配置与无黑框快捷启动，用于解决中国大陆网络环境下 Antigravity 无法登录、模型超时、Agent 连接中断、Language Server 无法拉取等问题，无需开启全局代理或 TUN 模式。
---

# Antigravity China Access (Google Antigravity 中国大陆网络连接解决方案)

本 Skill 基于 [Molly1116/Antigravity-China-Access](https://github.com/Molly1116/Antigravity-China-Access)，为 Windows 平台下的 Google Antigravity 提供**仅针对 Antigravity 进程树**的局部代理启动与快捷方式管理方案。

## 适用场景

- 处于中国大陆网络环境，使用 Google Antigravity 遇到连接超时、网络中断或 403 错误。
- Antigravity 界面可打开，但登录、模型调用、Agent 会话或 Language Server 无法连通。
- 不希望开启全局代理模式（Global Mode），也不希望开启虚拟网卡 TUN 模式接管整机流量。
- 避免使用 `setx` 修改 Windows 全局系统环境变量或修改注册表。

---

## 核心机制与原理

```text
桌面快捷方式 (Antigravity (Proxy).lnk)
    ↓
wscript.exe (后台静默，无黑色终端弹窗)
    ↓
Start-Antigravity-Proxy.vbs
    ↓
Start-Antigravity-Proxy.ps1 (读取 proxy-config.psd1，仅在当前进程注入环境变量)
    ├── HTTP_PROXY / HTTPS_PROXY
    ├── http_proxy / https_proxy
    └── NO_PROXY / no_proxy
    ↓
启动官方 Antigravity.exe (继承父进程局部代理变量)
    ├── Electron 界面
    ├── Language Server
    └── 捆绑 Agent 进程
```

> **注意**：局部环境变量仅作用于 Antigravity 及其派生的子进程，不会写入系统的 User/System Environment 变量，关闭或使用原生快捷方式启动时完全恢复默认网络。

---

## 文件结构

- [SKILL.md](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/SKILL.md)：Skill 说明与操作指南。
- [proxy-config.example.psd1](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/proxy-config.example.psd1)：代理配置文件模板。
- [proxy-config.psd1](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/proxy-config.psd1)：实际生效的本地代理配置。
- [Start-Antigravity-Proxy.ps1](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/Start-Antigravity-Proxy.ps1)：核心 PowerShell 启动脚本。
- [Start-Antigravity-Proxy.vbs](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/Start-Antigravity-Proxy.vbs)：静默无窗口 VBS 启动引导。
- [New-Antigravity-ProxyShortcut.ps1](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/New-Antigravity-ProxyShortcut.ps1)：桌面代理启动快捷方式生成脚本。
- [README.md](file:///d:/APP/development_projects/.agents/skills/antigravity-china-access/README.md)：原项目完整中文说明文档。

---

## 常用操作

### 1. 配置本地代理地址与端口

编辑 `proxy-config.psd1`，填入你的本地代理客户端监听的 HTTP/Mixed 端口：

```powershell
@{
    # 支持 CONNECT 请求的 HTTP 代理端口
    # 示例：v2rayN 默认为 http://127.0.0.1:10808，Clash/Mihomo 默认为 http://127.0.0.1:7890
    ProxyUrl = 'http://127.0.0.1:10808'

    # 本地旁路规则
    NoProxy = 'localhost,127.0.0.1,::1'
}
```

> **提示**：必须填写 HTTP 协议端点（如 `http://127.0.0.1:端口`），若代理工具仅有纯 SOCKS5 端口，请开启客户端的 HTTP/Mixed 监听端口。

### 2. 生成桌面启动快捷方式

在当前目录运行以下命令生成桌面无黑框快捷方式 `Antigravity (Proxy).lnk`：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\New-Antigravity-ProxyShortcut.ps1
```

执行后桌面将生成带 Antigravity 官方图标的快捷方式，双击即可直接带代理静默启动。

### 3. 直接通过命令行/后台启动

#### 静默无黑框启动
```powershell
wscript.exe //B //NoLogo .\Start-Antigravity-Proxy.vbs
```

#### PowerShell 命令行启动（带调试输出）
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-Antigravity-Proxy.ps1
```

### 4. 恢复默认启动

- 若需普通无代理模式，直接从开始菜单或官方快捷方式启动 Antigravity 即可。
- 卸载时仅需删除桌面 `Antigravity (Proxy).lnk` 及本 skill 目录，系统无任何残留。
