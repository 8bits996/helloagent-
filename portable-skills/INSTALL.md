# AI Assisted Coding 技能安装指南

## 技能来源
- 仓库地址: https://git.woa.com/cloud-mt/ai-assisted-coding.git

## 手动下载步骤

### 方法一：通过 Git 克隆（推荐）

1. 打开终端，进入技能目录：
   ```bash
   cd c:/Users/frankechen/CodeBuddy/chrome/portable-skills/ai-assisted-coding
   ```

2. 克隆仓库（需要内网访问权限）：
   ```bash
   git clone https://git.woa.com/cloud-mt/ai-assisted-coding.git .
   ```
   
   或使用 SSH：
   ```bash
   git clone git@git.woa.com:cloud-mt/ai-assisted-coding.git .
   ```

### 方法二：通过网页下载

1. 访问 https://git.woa.com/cloud-mt/ai-assisted-coding
2. 登录 OA 账号
3. 点击 "下载 ZIP" 或 "Download"
4. 解压到 `portable-skills/ai-assisted-coding/` 目录

## 安装到 CodeBuddy

### 方法一：复制到全局技能目录

将技能文件夹复制到 CodeBuddy 全局技能目录：

```powershell
# Windows
xcopy /E /I "c:\Users\frankechen\CodeBuddy\chrome\portable-skills\ai-assisted-coding" "%USERPROFILE%\.codebuddy\skills\ai-assisted-coding"
```

### 方法二：复制到项目技能目录

将技能文件夹复制到当前项目的 `.codebuddy/skills/` 目录：

```powershell
xcopy /E /I "c:\Users\frankechen\CodeBuddy\chrome\portable-skills\ai-assisted-coding" ".codebuddy\skills\ai-assisted-coding"
```

## 分享给他人

将整个 `portable-skills/ai-assisted-coding` 文件夹打包分享即可：

```powershell
# 打包为 ZIP
Compress-Archive -Path "c:\Users\frankechen\CodeBuddy\chrome\portable-skills\ai-assisted-coding" -DestinationPath "c:\Users\frankechen\CodeBuddy\chrome\ai-assisted-coding-skill.zip"
```

接收者解压后，按照上述安装步骤操作即可使用。

## 技能文件结构说明

标准的 CodeBuddy 技能文件夹结构：

```
ai-assisted-coding/
├── SKILL.md          # 技能说明文件（必需）
├── scripts/          # 脚本文件（可选）
├── references/       # 参考文档（可选）
├── assets/           # 资源文件（可选）
└── ...
```

## 验证安装

1. 重启 CodeBuddy 或刷新技能列表
2. 在对话中输入 `/skills` 查看已安装的技能
3. 应该能看到 `ai-assisted-coding` 技能

## 常见问题

### Q: 克隆时提示权限不足
A: 确保你已登录腾讯内网，且有该仓库的访问权限。可以联系仓库管理员申请权限。

### Q: 技能不生效
A: 检查技能目录中是否有 `SKILL.md` 文件，这是 CodeBuddy 识别技能的必需文件。

### Q: 如何更新技能
A: 进入技能目录执行 `git pull`，或重新下载最新版本。
