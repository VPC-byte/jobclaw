# JobClaw

JobClaw 是一个开源的 AI 求职代理, 帮助你自动化「搜岗位 -> 匹配 -> 投递 -> 通知」流程。

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

## 为什么做 JobClaw

求职过程常见痛点:
- 多平台重复搜索, 时间成本高
- 职位与简历匹配靠人工判断, 效率低
- 投递状态分散, 跟进困难

JobClaw 通过可扩展流水线解决这些问题:
- 抓取 Boss直聘、LinkedIn 职位
- 使用 LLM 对职位和用户画像进行评分匹配
- 自动投递高匹配岗位
- 通过 Telegram/Discord 发送匹配结果与投递状态

## 快速开始

```bash
pip install -e .
playwright install chromium
cp .env.example .env
cp profiles/example.yaml profiles/me.yaml
jobclaw run --profile profiles/me.yaml --query "Python 工程师"
```

## 架构总览

```text
用户画像(Profile) -> 抓取器(Scraper) -> 匹配器(Matcher) -> 自动投递(Applier) -> 通知(Notifier)
```

详细架构请看 [docs/architecture.md](./docs/architecture.md)。

## 支持平台

| 平台 | 状态 | 说明 |
| --- | --- | --- |
| Boss直聘 | ✅ | 已提供抓取和投递适配 |
| LinkedIn | ✅ | 已提供抓取和投递适配 |
| 拉勾 | 🔜 | 计划中 |
| 前程无忧 | 🔜 | 计划中 |

## 常用命令

```bash
jobclaw validate-profile --profile profiles/example.yaml
jobclaw scrape --platform all --query "后端工程师" --limit 20
jobclaw run --platform all --profile profiles/example.yaml --query "AI 工程师"
```

## 参与贡献

欢迎提交 PR, 包括但不限于:
- 新平台适配器
- 更好的匹配策略和提示词
- 稳定性与可观测性改进
- 新通知渠道

开发:

```bash
pip install -e .[dev]
pytest -q
```

## 合规说明

自动化操作可能受平台条款和当地法律约束。请在合法合规、授权范围内使用。

## 许可证

MIT, 见 [LICENSE](./LICENSE)。
