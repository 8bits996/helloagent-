# 🚀 快速上手指南

> **AI Agent Engineering L3-L8 层级：从理论到实践的 30 分钟快速入门**

---

## 📖 目录

1. [5 分钟快速开始](#5-分钟快速开始)
2. [选择你的起点](#选择你的起点)
3. [分层级快速上手](#分层级快速上手)
4. [常用命令速查表](#常用命令速查表)
5. [故障排查](#故障排查)
6. [进阶资源](#进阶资源)

---

## 5 分钟快速开始

### 步骤 1: 准备项目上下文 (1 分钟)

```bash
# 复制模板文件到你的项目根目录
cp templates/claude-md-template.md YOUR_PROJECT/CLAUDE.md
cp templates/cursorrules-template.md YOUR_PROJECT/.cursorrules

# 编辑 CLAUDE.md，填写你的项目信息
nano YOUR_PROJECT/CLAUDE.md
```

### 步骤 2: 创建文档索引 (1 分钟)

```bash
# 在项目根目录创建 AGENTS.md
cat > YOUR_PROJECT/AGENTS.md << 'EOF'
# Quick Navigation

## Getting Started
- [Setup Guide](./docs/setup.md)
- [Architecture](./docs/architecture.md)

## Development
- [API Guide](./docs/api-guide.md)
- [Testing](./docs/testing.md)

## Best Practices
- [Code Style](./docs/code-style.md)
- [Security](./docs/security.md)
EOF
```

### 步骤 3: 配置 MCP Server (2 分钟)

```bash
# 安装常用 MCP Servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github

# 配置 Claude Desktop (如果使用)
mkdir -p ~/Library/Application\ Support/Claude
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/your/project"
      ]
    }
  }
}
EOF
```

### 步骤 4: 验证设置 (1 分钟)

```bash
# 在 Cursor 或 Claude Code 中打开你的项目
# 确认 AI 能访问 CLAUDE.md 和 .cursorrules

# 测试命令
# 在 AI 对话中输入: "请根据 CLAUDE.md 的规则，帮我创建一个新的 API 端点"
```

---

## 选择你的起点

### 🟢 如果你是初学者 (从 L3 开始)

**你已经掌握**: 基本的 AI 编程助手使用（如 ChatGPT、GitHub Copilot）

**下一步**: 学习上下文工程

**行动计划**:
1. 完整阅读 `AI_Agent_Engineering_Levels_Research_Report.md` 的 L3 章节
2. 使用模板创建你的第一个 `CLAUDE.md`
3. 练习"计划-委托-评估"循环
4. 完成检查清单中的所有项目

**预期时间**: 1-2 周

### 🟡 如果你有经验 (从 L4 开始)

**你已经掌握**: 使用 AI 工具完成日常开发任务

**下一步**: 建立知识固化机制

**行动计划**:
1. 实现"学习点捕获系统"
2. 设置 Git hooks 自动化
3. 创建 CI/CD 知识同步
4. 建立团队共享的知识库

**预期时间**: 1 周

### 🔴 如果你是高级用户 (从 L5 开始)

**你已经掌握**: 自定义 AI 工作流，有明确的编码规范

**下一步**: 扩展 AI 能力边界

**行动计划**:
1. 开发自定义 MCP Server
2. 创建技能注册表
3. 实现 AI 驱动的自动化测试
4. 探索后台代理

**预期时间**: 2-3 周

---

## 分层级快速上手

### L3: Context Engineering

#### 核心任务: 创建项目上下文系统

**快速实现**:

```bash
# 1. 创建必要的文件
touch CLAUDE.md AGENTS.md .cursorrules

# 2. 使用模板填充
cp templates/claude-md-template.md CLAUDE.md
cp templates/cursorrules-template.md .cursorrules

# 3. 编辑文件，填写你的项目信息
```

**关键检查点**:
- [ ] CLAUDE.md 包含技术栈说明
- [ ] AGENTS.md 有清晰的文档导航
- [ ] .cursorrules 定义了编码规范
- [ ] 文件已提交到 Git

**测试方法**:
```
在 AI 对话中问: "根据 CLAUDE.md，我们项目的技术栈是什么？"
AI 应该能正确回答
```

**常见问题**:

Q: CLAUDE.md 应该多大？  
A: 建议 100-200 行，使用 AGENTS.md 指向详细文档

Q: 如何更新上下文？  
A: 每次会话结束后，更新 CLAUDE.md 中的"常见问题"部分

---

### L4: Compounding Engineering

#### 核心任务: 建立知识固化循环

**快速实现**:

```bash
# 1. 创建学习点记录模板
cat > .claude/learning-template.md << 'EOF'
## Learning Record

### Date: [YYYY-MM-DD]
### Context: [What were you trying to do?]
### Issue: [What went wrong?]
### Solution: [How did you fix it?]
### Category: [pattern/anti-pattern/gotcha/best-practice]
EOF

# 2. 创建自动化脚本
cat > scripts/record-learning.sh << 'EOF'
#!/bin/bash
# 记录学习点并更新 CLAUDE.md
echo "Recording learning point..."
# 你的实现
EOF

chmod +x scripts/record-learning.sh
```

**关键检查点**:
- [ ] 有学习点记录系统
- [ ] Git hooks 能自动触发记录
- [ ] CLAUDE.md 定期更新
- [ ] 团队能访问共享知识库

**测试方法**:
```
故意让 AI 犯一个错误，然后记录解决方案。
下次会话时，AI 应该不再犯同样的错误。
```

---

### L5: MCP & Skills

#### 核心任务: 开发自定义 MCP Server

**快速实现**:

```bash
# 1. 初始化 MCP Server 项目
npx @modelcontextprotocol/create-server my-custom-server

# 2. 编辑服务器代码
cd my-custom-server
nano src/index.ts

# 3. 添加工具定义
# 参考报告中的示例代码

# 4. 测试服务器
npm run dev
```

**关键检查点**:
- [ ] MCP Server 能启动
- [ ] 工具定义正确
- [ ] Claude Desktop 能连接
- [ ] 工具能正常调用

**测试方法**:
```
在 Claude Desktop 中问: "使用我的自定义工具，执行 [某个操作]"
AI 应该能调用你的 MCP Server
```

**常用 MCP Servers**:
- `@modelcontextprotocol/server-filesystem`: 文件系统访问
- `@modelcontextprotocol/server-github`: GitHub API 集成
- `@modelcontextprotocol/server-postgres`: PostgreSQL 操作

---

### L6: Harness Engineering

#### 核心任务: 构建自动化反馈回路

**快速实现**:

```bash
# 1. 配置测试框架
npm install -D vitest @vitest/ui @testing-library/react

# 2. 创建 vitest.config.ts
cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
  },
});
EOF

# 3. 设置 pre-commit hook
npx husky install
npx husky add .husky/pre-commit "npm test"

# 4. 测试反馈回路
npm test
```

**关键检查点**:
- [ ] 测试套件配置完成
- [ ] Pre-commit hooks 生效
- [ ] 测试覆盖率 > 80%
- [ ] CI/CD 集成测试

**测试方法**:
```
提交一个故意有 bug 的代码，观察 pre-commit hook 是否阻止提交。
```

---

### L7: Background Agents

#### 核心任务: 实现后台自动化

**快速实现**:

```bash
# 1. 安装依赖
pip install langgraph
# 或
npm install langchain @langchain/core

# 2. 创建代理配置
cat > config/background-agents.yml << 'EOF'
agents:
  refactor:
    enabled: true
    schedule: "0 2 * * *"
    model: opus
    maxTasks: 3
EOF

# 3. 实现代理逻辑
# 参考报告中的 BackgroundAgent 类
```

**关键检查点**:
- [ ] 代理能异步运行
- [ ] 多模型协作正常
- [ ] 有监控面板
- [ ] 能处理长时间任务

**测试方法**:
```
调度一个后台任务，关闭终端。
一段时间后检查任务是否完成。
```

---

### L8: Agent Teams

#### 核心任务: 构建多智能体协作系统

**快速实现**:

```bash
# 1. 安装框架
pip install crewai
# 或
pip install langgraph

# 2. 定义代理角色
cat > agents/roles.py << 'EOF'
from crewai import Agent

developer = Agent(
    role='Developer',
    goal='Write clean code',
    backstory='Expert programmer',
)

reviewer = Agent(
    role='Reviewer',
    goal='Ensure code quality',
    backstory='Detail-oriented',
)
EOF

# 3. 编排工作流
# 参考报告中的完整示例
```

**关键检查点**:
- [ ] 多个代理能协同工作
- [ ] 任务认领机制正常
- [ ] 冲突能自动解决
- [ ] 有性能监控

**测试方法**:
```
提交一个复杂任务，观察多个代理如何分工协作。
```

---

## 常用命令速查表

### Context Engineering

```bash
# 创建上下文文件
cp templates/claude-md-template.md CLAUDE.md

# 检查 token 数量
python -c "import tiktoken; print(len(tiktoken.get_encoding('cl100k_base').encode(open('CLAUDE.md').read())))"

# 更新上下文
git add CLAUDE.md .cursorrules AGENTS.md
git commit -m "docs: update project context"
```

### MCP Server

```bash
# 创建新服务器
npx @modelcontextprotocol/create-server my-server

# 运行服务器
npm run dev

# 测试服务器
curl http://localhost:3000/health

# 安装到 Claude Desktop
# 编辑 ~/Library/Application Support/Claude/claude_desktop_config.json
```

### Testing

```bash
# 运行所有测试
npm test

# 运行特定测试
npm test -- --grep "UserService"

# 生成覆盖率报告
npm run test:coverage

# 运行 E2E 测试
npm run test:e2e

# 调试模式
npm run test:ui
```

### Background Agents

```bash
# 启动后台代理
npm run agent:start

# 查看代理状态
npm run agent:status

# 停止代理
npm run agent:stop

# 查看日志
tail -f logs/agent.log
```

---

## 故障排查

### 问题 1: AI 不遵循 CLAUDE.md 规则

**可能原因**:
- CLAUDE.md 文件不在项目根目录
- 文件格式不正确
- 上下文窗口太小，AI 看不到完整内容

**解决方案**:
```bash
# 确认文件位置
ls -la CLAUDE.md

# 检查文件格式
head -20 CLAUDE.md

# 精简内容，保留关键信息
wc -l CLAUDE.md  # 应该 < 300 行
```

### 问题 2: MCP Server 连接失败

**可能原因**:
- 配置文件路径错误
- 端口被占用
- 权限问题

**解决方案**:
```bash
# 检查配置
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 检查端口
lsof -i :3000

# 检查权限
chmod +x /path/to/mcp-server

# 重启 Claude Desktop
```

### 问题 3: 测试无法运行

**可能原因**:
- 依赖未安装
- 配置错误
- 环境变量缺失

**解决方案**:
```bash
# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查配置
cat vitest.config.ts

# 设置环境变量
export DATABASE_URL="your-db-url"
npm test
```

### 问题 4: 后台代理崩溃

**可能原因**:
- 内存不足
- 超时
- 错误处理不当

**解决方案**:
```bash
# 检查日志
tail -100 logs/agent.log

# 增加超时时间
# 在配置文件中设置 timeout: 3600000  # 1 小时

# 监控内存
ps aux | grep node

# 限制并发任务
# 在配置中设置 maxConcurrency: 1
```

---

## 进阶资源

### 官方文档

- **MCP 协议**: https://modelcontextprotocol.io
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **CrewAI**: https://docs.crewai.com/
- **Cursor**: https://docs.cursor.sh/
- **Claude Code**: https://docs.anthropic.com/claude/docs/claude-code

### 开源项目

- **MCP Servers**: https://github.com/modelcontextprotocol/servers
- **LangGraph Examples**: https://github.com/langchain-ai/langgraph/tree/main/examples
- **CrewAI Examples**: https://github.com/joaomdmoura/crewAI-examples

### 社区资源

- **Cursor Rules Collection**: https://github.com/PatrickJS/awesome-cursorrules
- **MCP Server Registry**: https://github.com/punkpeye/awesome-mcp-servers
- **AI Agent Patterns**: https://github.com/e2b-dev/awesome-ai-agents

### 学习路径

1. **Week 1-2**: L3 Context Engineering
   - 创建项目上下文
   - 管理对话历史
   - 优化 token 使用

2. **Week 3-4**: L4 Compounding Engineering
   - 建立知识固化系统
   - 自动化学习点捕获
   - 团队知识共享

3. **Week 5-6**: L5 MCP & Skills
   - 开发自定义 MCP Server
   - 集成外部工具
   - 创建技能库

4. **Week 7-8**: L6 Harness Engineering
   - 自动化测试
   - 反馈回路
   - 自我修复系统

5. **Week 9-10**: L7 Background Agents
   - 后台任务
   - 多模型协作
   - 长时间运行任务

6. **Week 11-12**: L8 Agent Teams
   - 多智能体协调
   - 冲突解决
   - 复杂工作流

---

## 📝 总结

这份快速上手指南提供了：

✅ **5 分钟快速开始** - 立即可用的配置步骤  
✅ **分层级指南** - 针对不同水平的定制路径  
✅ **命令速查表** - 常用操作的快速参考  
✅ **故障排查** - 常见问题的解决方案  
✅ **进阶资源** - 深入学习的方向

**下一步行动**:

1. 选择适合你的起点层级
2. 按照快速实现步骤操作
3. 完成关键检查点
4. 遇到问题参考故障排查
5. 准备好后进入下一层级

**记住**: 稳扎稳打，每一步都要有实际产出。不要跳级，每一级都是下一级的基础。

---

**版本**: 1.0.0  
**创建日期**: 2025-03-19  
**维护者**: AI Agent Engineering Team
