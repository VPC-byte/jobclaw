# 🦞 JobClaw — Master Plan

## Vision

**成为 AI Agent 时代的招聘基础设施。**

不是又一个招聘网站。是一个 **协议层** — 让任何 AI agent 都能代表求职者或招聘方，在标准化的框架下完成匹配。

---

## 核心洞察

### 为什么现在？

1. **AI Agent 爆发** — OpenClaw, Claude Code, Codex, Devin... 每个人都在部署 agent
2. **招聘是最大的信息不对称市场** — 全球 $500B+ 人力资源市场
3. **没人在做 agent-to-agent** — 所有 AI 招聘工具还在"帮 HR 筛简历"的 Web2 思维
4. **Z 世代反感传统招聘** — 不想写 cover letter，不想刷 LinkedIn，想要更高效的方式

### 为什么能赢？

- **先发优势**: Agent-to-agent hiring 这个品类还不存在
- **技术壁垒**: 需要深度理解 AI agent 协议，不是套个 API 就行
- **网络效应**: 双边市场一旦形成，后来者很难追
- **OpenClaw 生态**: 自带分发渠道

---

## Product Design

### 三层架构

```
┌─────────────────────────────────────────────┐
│           JobClaw Platform (Web)            │  ← 人类界面
│  Dashboard · Analytics · Final Decisions    │
├─────────────────────────────────────────────┤
│        JobClaw Protocol (API/MCP)           │  ← Agent 协议层
│  Matching · Negotiation · Scheduling        │
├─────────────────────────────────────────────┤
│         Agent Runtime (OpenClaw)            │  ← Agent 执行层
│  Seeker Agent · Recruiter Agent · Eval      │
└─────────────────────────────────────────────┘
```

### 求职者侧 (Seeker Agent)

1. **Profile Ingestion** — Agent 读取你的 GitHub、LinkedIn、简历、项目，构建 Skill Graph
2. **Preference Engine** — 通过对话了解你的底线（薪资、远程、行业、文化偏好）
3. **Auto-Apply** — Agent 主动出击，和匹配的 Recruiter Agent 发起对话
4. **Interview Prep** — Agent 帮你准备面试，模拟技术问题
5. **Negotiation** — Agent 在你设定的范围内自动谈薪资

### 招聘方侧 (Recruiter Agent)

1. **JD Intelligence** — Agent 分析 JD，提取真正重要的技能和特质（不是关键词堆砌）
2. **Candidate Scoring** — 多维度评分：技术匹配、文化匹配、成长潜力
3. **Technical Screening** — Agent 出题、评估代码、分析 GitHub 贡献
4. **Pipeline Management** — 自动排序、跟进、安排面试
5. **Market Intelligence** — 薪资基准、人才供需、竞对分析

### Agent-to-Agent 协议

```
Seeker Agent                    Recruiter Agent
     │                                │
     ├──── Discovery Request ────────►│
     │                                │
     │◄───── Match Score + JD ────────┤
     │                                │
     ├──── Skill Proof + Portfolio ──►│
     │                                │
     │◄───── Technical Challenge ─────┤
     │                                │
     ├──── Solution + Discussion ────►│
     │                                │
     │◄───── Evaluation Result ───────┤
     │                                │
     ├──── Salary Expectation ───────►│
     │                                │
     │◄───── Offer / Counter ─────────┤
     │                                │
     │◄───── Schedule Interview ──────┤  ← 人类介入点
     │                                │
```

---

## Go-to-Market Strategy

### Phase 0: Protocol + Demo (Month 1-2) 🎯 CURRENT

**目标**: 证明概念，做出 wow moment

- [ ] 定义 JobClaw Protocol spec (JSON-RPC / MCP based)
- [ ] 实现 Seeker Agent skill (OpenClaw skill)
- [ ] 实现 Recruiter Agent skill (OpenClaw skill)
- [ ] Demo: 两个 agent 完成一次完整的匹配+筛选+安排面试
- [ ] Landing page: jobclaw.org
- [ ] 录制 demo 视频

**关键指标**: 一个完整的 agent-to-agent hiring flow 跑通

### Phase 1: Closed Beta (Month 3-4)

**目标**: 真实用户验证

- [ ] 找 10 个 OpenClaw 用户做 beta tester（先从 Discord 社区招）
- [ ] 找 5 个小公司/startup 做招聘方 beta
- [ ] 聚焦 **Tech Hiring** — 工程师招工程师，最容易自动化
- [ ] Skill 评估准确率 > 80%
- [ ] 收集反馈，迭代协议

**关键指标**: 至少 3 次成功匹配（agent 推荐 → 人类面试 → offer）

### Phase 2: Product-Market Fit (Month 5-8)

**目标**: 找到 PMF，建立双边网络

- [ ] 开放注册（waitlist 制）
- [ ] Seeker Agent 一键部署（不需要自己搭 OpenClaw）
- [ ] Recruiter Dashboard (Web UI)
- [ ] 集成主流 ATS (Greenhouse, Lever, Workday)
- [ ] 支持更多岗位类型（Design, PM, Marketing）

**关键指标**: 100+ 活跃求职者，20+ 招聘方，周匹配 50+

### Phase 3: Growth (Month 9-12)

**目标**: 规模化

- [ ] Freemium 模型上线
- [ ] Agent Marketplace — 第三方开发专业领域 agent
- [ ] 企业版（on-prem agent，数据不出企业）
- [ ] 国际化（先英语市场，再中文）
- [ ] 融资 or 自营？根据数据决定

---

## Revenue Model

### 对求职者 — 免费 + Premium

| Tier | 价格 | 功能 |
|------|------|------|
| Free | $0 | 基础 profile，每月 10 次 agent 匹配 |
| Pro | $29/月 | 无限匹配，高级谈判，面试准备 |
| Elite | $99/月 | 专属 agent 调优，优先展示，猎头模式 |

### 对招聘方 — SaaS + Success Fee

| Tier | 价格 | 功能 |
|------|------|------|
| Starter | $199/月 | 3 个活跃岗位，基础筛选 |
| Growth | $599/月 | 无限岗位，技术评估，pipeline 管理 |
| Enterprise | Custom | On-prem，定制 agent，API 全开 |
| Success Fee | 首年薪资 8% | 可选，按成功入职收费（vs 猎头 20-30%） |

### 为什么 8% 而不是免费？

- 猎头收 20-30%，JobClaw 收 8%，省了一大半
- Agent 做了猎头 80% 的工作（搜索、筛选、初面、谈判）
- 人类只做最后 20%（终面、文化判断）
- **对标**: LinkedIn Recruiter $10k/年/seat，猎头一个 senior hire 收 $30-50k

---

## 竞争分析

| 对手 | 模式 | 弱点 |
|------|------|------|
| LinkedIn | 社交+招聘，卖 InMail | Web2 思维，AI 只是 feature 不是 core |
| Indeed | 流量+广告 | 简历黑洞，候选人体验差 |
| HireVue | AI 面试 | 只做筛选一个环节，不做全流程 |
| Moonhub | AI 猎头 | 只做招聘方，没有求职者 agent |
| Mercor | AI 匹配 | 中心化平台，不是 agent-to-agent |

**JobClaw 差异化**: 唯一一个让 **双方都有 agent** 的平台。不是中心化 AI 替你选，是你的 AI 和他的 AI 直接对话。

---

## Tech Stack (Proposed)

### Backend
- **Runtime**: Node.js / Bun
- **API**: Hono (lightweight, edge-ready)
- **Database**: PostgreSQL + pgvector (skill matching)
- **Queue**: BullMQ / Redis
- **Agent Protocol**: MCP (Model Context Protocol) based

### Frontend
- **Framework**: Next.js 15 / Nuxt 4
- **UI**: Tailwind + shadcn/ui
- **Real-time**: WebSocket for agent activity feed

### Agent Layer
- **OpenClaw Skills**: seeker-agent, recruiter-agent, evaluator-agent
- **LLM**: Claude Sonnet (主力) + Gemini Flash (批量任务)
- **Embeddings**: text-embedding-3-large (skill graph)
- **Eval**: Code execution sandbox for technical assessment

### Infrastructure
- **Hosting**: GCP (free credits phase) → Vercel/Fly.io (scale phase)
- **Domain**: jobclaw.org (Cloud DNS)
- **CI/CD**: GitHub Actions
- **Monitoring**: Grafana + Prometheus

---

## 🔥 Viral Mechanics — 怎么让它爆

### 1. "My Agent Got Me a Job" 社交货币
- 求职者成功入职后，自动生成分享卡片："我的 AI agent 帮我在 3 天内拿到了 offer"
- Twitter/LinkedIn viral loop
- 每个成功案例都是免费广告

### 2. Agent Battle — 公开技术评估
- 允许求职者 agent 公开展示技术评估结果（类似 LeetCode 分数）
- "我的 agent 在 JobClaw 评分 95/100" — 新的社交证明
- 招聘方可以直接按分数搜索

### 3. Open Protocol — 第三方 Agent 接入
- 开放协议，任何 AI agent 框架都能接入（不只 OpenClaw）
- AutoGPT, CrewAI, LangGraph agents 都能用
- **生态 > 平台** — 成为招聘领域的 "HTTP"

### 4. "Fire Your Recruiter" Campaign
- 挑衅性营销："你的猎头收 $30k，我们的 agent 收 $3k"
- 计算器工具：输入你的招聘预算，显示用 JobClaw 能省多少
- PR 话题性极强

### 5. Developer-First
- 先攻占 tech hiring（最容易自动化，用户最 tech-savvy）
- 在 Hacker News, Reddit r/cscareer, Twitter tech 圈传播
- 开源 Protocol spec，让开发者贡献

### 6. "Agent Resume" — 新简历格式
- 不再是 PDF 简历，而是一个活的 Agent Profile
- Agent 可以实时回答招聘方问题、展示项目、跑代码
- "发我你的 agent link" 取代 "发我你的简历"

---

## Risks & Mitigations

| 风险 | 严重程度 | 缓解 |
|------|----------|------|
| Agent 匹配质量差 | 🔴 High | 人工反馈 loop，持续训练 |
| 法律合规（就业歧视）| 🔴 High | 审计 agent 决策，透明评分 |
| 冷启动（双边市场）| 🟡 Medium | 先做单边（帮求职者），再拉招聘方 |
| 大厂抄袭 | 🟡 Medium | 速度 + 协议标准 + 社区 |
| LLM 成本 | 🟢 Low | Gemini Flash 便宜，且成本持续下降 |

---

## Immediate Next Steps (This Week)

1. ✅ Register jobclaw.org
2. ✅ Create GitHub repo
3. [ ] Design JobClaw Protocol v0.1 spec
4. [ ] Build seeker-agent OpenClaw skill (MVP)
5. [ ] Build recruiter-agent OpenClaw skill (MVP)
6. [ ] Set up project structure (monorepo)
7. [ ] Landing page draft

---

*Last updated: 2026-03-05*
*Authors: Joe + Nyx 🌙*
