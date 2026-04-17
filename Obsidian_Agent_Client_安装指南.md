# Obsidian Agent Client 插件安装配置指南

## 前置要求

✅ Node.js v20.19.0 已安装  
✅ npm 10.8.2 已安装

---

## 方法一：通过 BRAT 插件安装（推荐）

### 步骤 1：安装 BRAT 插件

1. 打开 Obsidian
2. 进入 **设置** → **社区插件**
3. 关闭"安全模式"
4. 点击"浏览"按钮
5. 搜索 "BRAT"
6. 找到 **"Obsidian42 - BRAT"** 并安装
7. 安装完成后点击"启用"

### 步骤 2：使用 BRAT 安装 Agent Client

1. 在 **设置** → **社区插件** 中找到 "BRAT"
2. 点击 BRAT 的设置图标
3. 在 "Beta Plugin List" 部分点击 "Add Beta Plugin"
4. 输入仓库地址：`https://github.com/RAIT-09/obsidian-agent-client`
5. 点击确定，等待安装完成
6. 在社区插件列表中找到 "Agent Client" 并启用

---

## 方法二：手动安装

### 步骤 1：下载插件

```bash
# 进入 Obsidian 插件目录
cd <你的Obsidian文件库路径>/.obsidian/plugins

# 克隆插件仓库
git clone https://github.com/RAIT-09/obsidian-agent-client.git

# 进入插件目录
cd obsidian-agent-client

# 安装依赖
npm install

# 构建插件
npm run build
```

### 步骤 2：启用插件

1. 打开 Obsidian
2. 进入 **设置** → **社区插件**
3. 在插件列表中找到 "Agent Client"
4. 点击启用

---

## 配置 AI CLI（以 Codex 为例）

### 步骤 1：配置 Node.js 路径

1. 打开 Obsidian 设置
2. 找到 "Agent Client" 插件设置
3. 在 "Node Path" 字段中输入 Node.js 的路径
   - Windows: `C:\Program Files\nodejs\node.exe` 或 `C:\Program Files (x86)\nodejs\node.exe`
   - 或使用命令查找：`where node`

### 步骤 2：配置 AI CLI 路径

1. 在 "CLI Path" 字段中输入你的 AI CLI 工具路径
   - 例如：`codex`（如果已全局安装）
   - 或完整路径：`C:\Users\<用户名>\AppData\Roaming\npm\codex.cmd`

### 步骤 3：测试配置

1. 在 Obsidian 中打开任意笔记
2. 使用快捷键或命令面板打开 Agent Client
3. 尝试与 AI 交互

---

## Skills 配置

### 官方 Skills

仓库地址：https://github.com/kepano/obsidian-skills

```bash
# 克隆到你的 skills 文件夹
cd <你的Obsidian文件库路径>/.obsidian/skills
git clone https://github.com/kepano/obsidian-skills.git
```

### 画图 Skills

仓库地址：https://github.com/axtonliu/axton-obsidian-visual-skills

```bash
# 克隆到你的 skills 文件夹
cd <你的Obsidian文件库路径>/.obsidian/skills
git clone https://github.com/axtonliu/axton-obsidian-visual-skills.git
```

---

## 使用示例

### 1. 给文档增加标签

- Agent Client 会自动调用 `obsidian-markdown` skills
- 在聊天中输入："给这篇笔记添加标签 #AI #工具"

### 2. 绘制 Excalidraw 图

- 使用画图 skills
- 在聊天中描述你想要的图表

---

## 常见问题

### Q: 找不到 Node.js 路径？

```bash
# 在命令行中运行
where node
```

### Q: 插件无法加载？

1. 检查 `.obsidian/plugins/obsidian-agent-client` 目录是否存在
2. 检查 `main.js` 和 `manifest.json` 文件是否存在
3. 重启 Obsidian

### Q: CLI 命令无法执行？

1. 确认 CLI 工具已正确安装
2. 在命令行中测试 CLI 命令是否可用
3. 检查路径配置是否正确

---

## 下一步

请告诉我您的 Obsidian 文件库路径，我将帮您：
1. 移动保存的文章到 Obsidian
2. 协助完成插件安装
3. 配置 AI CLI 工具
