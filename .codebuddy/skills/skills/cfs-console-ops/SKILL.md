---
name: cfs-console-ops
description: |
  此 skill 用于在 yfm4 控制台中管理 Cloud File Storage（CFS），包括在指定地域下检查或创建 VPC 与子网、创建 CFS 文件系统（以最小必填参数为主）、查看和汇总文件系统及其挂载信息。
  应在用户提到"开通 CFS"、"创建/查看 CFS 文件系统"、"获取 CFS 挂载信息"等需求时触发。
allowed-tools:
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__fill
  - mcp__chrome-devtools__press_key
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__wait_for
---

# CFS 控制台操作 Skill

## 目的与适用场景

管理 yfm4 平台上的 CFS 文件系统资源：
- 在控制台中以"只填必填 + 合理默认可选"的方式，快速创建可用的 CFS 文件系统
- 查看并汇总现有 CFS 文件系统及其挂载信息、基础规格等

### 典型触发语句
- "帮我在 yfm4 上开通一个 CFS 文件系统"
- "按最小必填参数创建一个 CFS 文件系统"
- "查看当前账号下有哪些 CFS 文件系统"
- "查看我刚创建的 cfs-fs-xxx 的详情和挂载方式"

## 总体原则

1. **不在工作区任何文件中写入具体登录账号或密码**
2. 默认假设用户已在浏览器中完成 yfm4 登录；如检测到登录页，则提示用户在浏览器里手工登录成功后再继续
3. 通过 chrome-devtools MCP 工具在浏览器中执行交互操作
4. 始终优先使用"最小必填 + 安全默认值"的配置

## 关键页面与入口

| 页面 | URL |
|------|-----|
| CFS 概览页 | http://console.yfm4.fsphere.cn/cfs |
| CFS 文件系统列表页 | http://console.yfm4.fsphere.cn/cfs/list |
| CFS 权限管理页 | http://console.yfm4.fsphere.cn/cfs/permission |
| CFS 监控页 | http://console.yfm4.fsphere.cn/cfs/monitor |
| VPC 控制台 | http://console.yfm4.fsphere.cn/vpc |

## 使用的 MCP 工具

此 skill 依赖 `chrome-devtools` MCP 服务器提供的浏览器自动化能力：

| 工具 | 用途 |
|------|------|
| `navigate_page` | 在当前页面中打开指定 URL |
| `take_snapshot` | 获取当前页面的无障碍结构快照，利用其中的 uid + 文本定位元素 |
| `wait_for` | 等待页面出现特定文本，用于同步页面状态 |
| `click` | 对指定 uid 的元素进行点击 |
| `fill` / `fill_form` | 在简单输入框中直接写入值 |
| `press_key` | 在复杂或对自动赋值敏感的输入框中模拟键盘逐字输入 |
| `evaluate_script` | 在页面中执行小段脚本 |

### 基本策略

- 通过 `take_snapshot` 查找包含特定文案的元素，再使用对应 uid 调用 `click` / `press_key`
- 对带有前端校验的输入框（如"名称"、"子网名称"），优先通过 `press_key` 模拟真实键盘输入

## 工作流 A：检查或创建用于 CFS 的 VPC

当需要创建 CFS 文件系统且当前地域下尚无合适 VPC 时，执行此工作流。

### 步骤

1. **导航到 VPC 控制台**
   - 使用 `navigate_page` 打开 `http://console.yfm4.fsphere.cn/vpc`
   - 使用 `wait_for` 等待页面出现 "VPC" 或 "私有网络"

2. **检查当前地域是否已有 VPC**
   - 使用 `take_snapshot` 获取列表区域结构
   - 如果列表中已有符合条件的 VPC，记录该 VPC 信息
   - 如果列表为空，执行"最小必填参数创建 VPC"

3. **最小必填参数创建 VPC**
   - 点击"新建"按钮打开弹窗
   - 填写字段：
     - 地域：保持当前地域（如"重庆"）
     - 名称：`cfs-vpc-YYYYMMDD-1`
     - VPC CIDR：保持默认值（如 `10.0.0.0/8`）
     - 子网名称：`cfs-subnet-YYYYMMDD-1`
     - 子网 CIDR：保持默认值（如 `10.0.0.0/24`）
     - 可用区：保持默认
   - 点击"创建"按钮
   - 等待 VPC 列表中出现该名称的记录

## 工作流 B：以最小必填参数创建 CFS 文件系统

### 前置条件
调用工作流 A，在目标地域获取一个可用 VPC

### 步骤

1. **打开 CFS 文件系统列表**
   - 使用 `navigate_page` 打开 `http://console.yfm4.fsphere.cn/cfs/list`
   - 使用 `wait_for` 等待页面出现"文件系统列表"

2. **打开"创建文件系统"弹窗**
   - 查找并点击"新建"按钮
   - 使用 `take_snapshot` 确认弹窗已出现

3. **填写最小必填字段**

   | 字段 | 建议值 | 说明 |
   |------|--------|------|
   | 名称 | `cfs-fs-YYYYMMDD-1` | 通过 `press_key` 输入 |
   | 地域 | 保持当前地域 | 如"重庆" |
   | 可用区 | 保持默认 | 如"可用区一" |
   | 存储类型 | 通用标准型 | 展开下拉选择 |
   | 文件服务协议 | NFS | 展开下拉选择 |
   | 选择网络 | 工作流 A 中的 VPC | 展开下拉选择 |
   | 权限组 | 默认权限组 | 保持默认 |

4. **提交创建**
   - 点击"确定"按钮
   - 等待文件系统列表中出现新记录
   - 记录新文件系统的 ID、名称、状态等

### 输出结构
```json
{
  "filesystemName": "cfs-fs-20251130-1",
  "filesystemId": "cfs-xxxxx",
  "region": "chongqing",
  "zone": "az",
  "storageType": "Standard",
  "protocol": "NFS",
  "vpcId": "vpc-xxxxx",
  "subnetId": "subnet-xxxxx",
  "status": "创建中"
}
```

## 工作流 C：查看与汇总 CFS 文件系统

### 步骤

1. **打开 CFS 文件系统列表**
   - 使用 `navigate_page` 打开 `http://console.yfm4.fsphere.cn/cfs/list`

2. **过滤或定位目标文件系统**
   - 如果用户提供名称，在搜索框中输入关键字
   - 否则遍历列表

3. **读取列表中的基础信息**
   - 名称 / ID
   - 存储类型、协议
   - 使用量 / 总容量
   - 吞吐上限、状态
   - 地域 / 可用区

4. **获取挂载信息**
   - 点击"挂载"或"详情"按钮
   - 从弹窗中提取：
     - 挂载点地址
     - 推荐的 mount 命令
     - 协议版本、加密、权限等

## 基于 DOM selector 操作 Tea 下拉框（高级技巧）

当 `take_snapshot` + uid 难以稳定控制 Tea UI 的下拉框时，使用 `evaluate_script`：

```javascript
() => {
  const dialog = document.querySelector('.tea-dialog');
  if (!dialog) return 'no-dialog';

  // 找到目标表单项
  const protocolItem = Array.from(
    dialog.querySelectorAll('.tea-form__item')
  ).find(item => item.textContent && item.textContent.includes('文件服务协议'));
  if (!protocolItem) return 'no-item';

  // 展开下拉框
  const header = protocolItem.querySelector('.tea-dropdown__header, .tea-select');
  if (!header) return 'no-header';
  header.click();

  // 在 overlay 中选择选项
  const overlayRoot = document.querySelector('#tea-overlay-root') || document.body;
  const option = Array.from(overlayRoot.querySelectorAll('*')).find(
    node => node.textContent && node.textContent.trim().includes('NFS')
  );
  if (!option) return 'no-nfs';
  option.click();

  return 'clicked-nfs';
}
```

## 错误处理与降级策略

1. **页面结构变动**
   - 再次调用 `take_snapshot`，改用更通用的文本或层级关系定位元素
   - 若仍无法定位，向用户说明并给出人工操作步骤

2. **自动填值无法通过前端校验**
   - 停止反复尝试
   - 说明已完成的字段和推荐值
   - 明确指出需要用户手动补齐的字段

3. **创建操作超时**
   - 使用列表视图轮询检查是否已出现新文件系统
   - 超时后向用户说明可能原因，建议在控制台中人工确认

## 登录信息参考

当需要访问 yfm4 平台时，可参考以下信息：
- 登录地址：`http://console.yfm4.fsphere.cn/`
- 用户名：`brc_resource`
- 密码：`Tencent@1234`

**安全注意事项**：不要将账号密码写入项目源代码或公共配置文件中。
