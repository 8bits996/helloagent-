# 🧠 项目记忆：外卖平台端到端测试

> 项目域标识：`e2e-testing`
> 创建时间：2026-03-12（估计）
> 最后更新：2026-03-21

---

## 📋 项目概述

外卖平台项目的端到端测试配置与用例编写。

## 🔑 关键配置

- 测试框架：Playwright
- 测试文件位置：`e2e/api/` 和 `e2e/ui/`
- 配置：4 个测试项目（api, chromium, firefox, webkit）

## 📊 测试覆盖

- API 测试：29 个用例（健康检查、商家列表/详情、菜品详情等）
- UI 测试：6 个用例（页面加载测试）
- 集成测试：3 个用例
- **合计：38 个测试用例**

## 🛠️ 运行命令

- `npm run test:e2e` — 运行全部测试
- `npm run test:e2e:api` — 仅 API 测试
- `npm run test:e2e:ui` — 可视化调试

## 📌 备注

- OpenSpec 已全局安装 v1.2.0（@fission-ai/openspec）
- 可通过 `openspec init` 初始化
