---
name: teko-comment
description: |
  This skill automates commenting on Teko AI Agent competition entries. 
  It should be used when the user wants to batch comment on multiple AI Agent works on teko.woa.com, 
  including navigating to entries, scrolling to comment sections, and submitting comments with promotional text.
  Triggers: "评论teko作品", "给teko投票", "teko批量评论", "AI Agent评论"
---

# Teko AI Agent 评论技能

## 概述

本技能用于在腾讯Teko平台(teko.woa.com)的AI Agent大赛作品页面进行批量评论，支持自动导航、评论输入和提交。

## 前置条件

- 需要已登录teko.woa.com
- 需要chrome-devtools MCP工具可用
- 用户需要提供评论内容或使用默认推广语

## 核心工作流程

### 1. 获取作品列表

导航到AI Agent作品列表页面：

```
URL: https://teko.woa.com/event/ai-agent/list
```

使用 `navigate_page` 工具访问列表页，然后用 `take_snapshot` 获取页面元素。

### 2. 进入作品详情页

作品详情页URL格式：
```
https://teko.woa.com/event/ai-agent/{作品ID}
```

直接使用 `navigate_page` 导航到具体作品页面，比直接点击更可靠。

### 3. 定位评论区

进入作品页面后，执行以下步骤定位评论区：

1. 等待页面加载完成：
   ```
   wait_for: "评论" 或 "发表评论"
   ```

2. 滚动到页面底部：
   ```
   press_key: "End"
   ```

3. 获取页面快照确认评论区可见：
   ```
   take_snapshot
   ```

### 4. 输入评论

找到评论输入框（通常是textarea元素），使用 `fill` 工具输入评论内容。

**默认推广语模板**：
```
{针对作品的评价内容}

智能新航海，合规不触礁！也欢迎体验扬帆出海合规助手并提出建议或评论：https://teko.woa.com/event/ai-agent/1697
```

### 5. 提交评论

**重要**：使用回车键提交评论，而非点击提交按钮：

```
press_key: "Enter"
```

### 6. 处理频率限制

评论提交可能有频率限制，建议：
- 每次评论后等待3-5秒
- 如遇到限制提示，暂停一段时间后继续
- 可使用 `wait_for` 等待页面响应

## 评论内容建议

根据作品类型生成个性化评论：

| 作品类型 | 评论角度 |
|---------|---------|
| 工具类 | 实用性、效率提升 |
| 娱乐类 | 趣味性、创意 |
| 教育类 | 知识传递、学习体验 |
| 效率类 | 时间节省、流程优化 |

## 批量评论流程

执行批量评论时，按以下顺序操作：

1. 获取作品列表，记录待评论作品ID
2. 依次访问每个作品页面
3. 滚动到评论区
4. 根据作品内容生成评论
5. 使用回车键提交
6. 等待适当时间后继续下一个

## 常见问题处理

### 页面加载不完整

如果 `take_snapshot` 返回空白或不完整内容：
1. 使用 `take_screenshot` 查看实际页面
2. 尝试 `press_key: "F5"` 刷新页面
3. 重新导航到目标页面

### 评论区不可见

1. 多次按 `End` 键滚动
2. 使用 `evaluate_script` 执行 `window.scrollTo(0, document.body.scrollHeight)`
3. 查找评论相关元素的uid并点击

### 提交失败

1. 检查是否有频率限制提示
2. 确认评论内容不为空
3. 尝试点击提交按钮作为备选方案

## 示例会话

用户: "帮我给teko上的AI Agent作品评论"

执行步骤:
1. `list_pages` - 查看当前页面
2. `navigate_page` 到作品列表或具体作品
3. `take_snapshot` - 获取页面状态
4. `press_key: "End"` - 滚动到评论区
5. `fill` - 输入评论内容
6. `press_key: "Enter"` - 提交评论
