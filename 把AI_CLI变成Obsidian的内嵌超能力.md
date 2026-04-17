# 把 AI CLI 变成 Obsidian 的"内嵌超能力"

**作者：** hongyuzheng(郑泓宇)  
**来源：** https://iwiki.woa.com/p/4017404064?from=iSearch  
**保存时间：** 2026-03-15

---

## 1、为什么值得做

早些时候，我们想用 AI 操作笔记，往往是打开一个黑乎乎的命令行窗口（CLI），指向 Obsidian 的文件库。

**虽然功能强大，但体验很割裂**：写笔记在 Obsidian，跑指令在命令行，两边来回切换，选择文件也很麻烦。

理想中的状态是这样的：

- **就在手边**：在笔记里写着写着，鼠标右边一拉就能问它；
- **自由切换**：今天想用 Claude Code 写代码，明天想用 Minimax 润色文案，后天想用 Gemini 画图，不需要换工具，只需要换"脑子"；
- **懂上下文**：能直接把当前这篇笔记甩给它，让它基于现有内容干活。

---

## 2、三步走配置AI CLI

**核心思路：** 用Obsidian Agent Client插件把AI CLI接进来

插件地址：https://github.com/RAIT-09/obsidian-agent-client

### 第一步：安装node

### 第二步：安装Obsidian Agent Client插件

安装渠道有两种：
- 通过BRAT插件拉github地址加载
- 手动安装

### 第三步：配置AI CLI

这里用codex进行演示

配置下node地址和codex地址

然后就可以开始愉快的使用了

---

## 3、skills使用示例

### 官方skills
https://github.com/kepano/obsidian-skills#

### 画图skills
https://github.com/axtonliu/axton-obsidian-visual-skills

针对codex而言，需复制至对应的skills文件夹

### 3.1、给文档增加标签

自动调用obsidian-markdown skills

### 3.2、excalidraw图绘制

---

## 配置步骤总结

1. **安装 Node.js**：确保系统已安装 Node.js
2. **安装 Obsidian Agent Client 插件**：
   - 方法一：通过 BRAT 插件从 GitHub 加载
   - 方法二：手动安装
3. **配置 AI CLI**：
   - 配置 node 地址
   - 配置 codex 地址
4. **使用 Skills**：
   - 官方 skills：https://github.com/kepano/obsidian-skills#
   - 画图 skills：https://github.com/axtonliu/axton-obsidian-visual-skills
   - 将 skills 复制到对应的文件夹

---

**标签：** #AI #Obsidian #CLI #工具配置 #效率提升
