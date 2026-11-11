# 🌱 Lume Studio · 小白学习指南

> **Your First Step into Anything.**
> 输入你想学的科目，自动生成一份「听得懂、学得会、不放弃」的学习目标和路径。
> 全程大白话，零基础也能上手；卡住了右下角直接问，像有个朋友在旁边陪你学。

🔗 **在线体验**：https://chengyi-mountain.github.io/Lume/

📣 **宣传文案见 [PROMO.md](./PROMO.md)**（含中英文一句话 / 短 / 长文案、朋友圈口语版、话题标签、SEO 关键词，可直接复制转发）。

---

## ✨ 功能特性

| 功能 | 说明 |
|---|---|
| 🎯 双模式计划 | 每个科目内置「小白 / 进阶」两套完整学习目标 + 分阶段路径 + 避坑提醒 + 学习资源 |
| 🤖 智能兜底 | 输入任意科目名（哪怕没收录），本地规则引擎即时生成一份结构完整的方案，离线可用 |
| 💬 学习助手 | 悬浮在右下角，知识库 / AI 智能体 / 外链三通道答疑，卡住随时问 |
| 🧭 上下文感知 | 在科目页提问，助手自动带上当前科目 + 当前模式，回答更贴合 |
| 🎯 打卡进度 | 目标 / 阶段可勾选打卡，数据存在本地浏览器，可看总览、导出 / 导入备份 |
| 🌗 明/暗主题 | 自动跟随系统偏好，可手动切换，选择会记住 |
| 📱 响应式 | PC / 手机自适应，圆角卡片 + 微交互 |
| ⚖️ 免责声明 | 内置完整的免责声明与开源协议，高敏领域有明确提醒 |
| 📦 零依赖 | 单文件 `index.html`，双击即开，扔到 GitHub Pages 即成公网网站 |

内置 **31** 个热门科目，覆盖编程技术、AI 与智能、职业技能、语言学习、学科与考试、办公与效率、音乐与艺术、数据与 AI、个人成长、理财与生活、设计与创作、兴趣生活等方向；未收录的科目也能由本地规则引擎即时生成方案。

---

## 🚀 快速开始

### 方式一：本地直接打开

下载 `index.html`，双击用浏览器打开即可，无需联网、无需安装任何东西。

### 方式二：部署到 GitHub Pages（推荐，免费）

1. 在 GitHub 新建仓库（命名 `Lume`），把 `index.html` 上传到仓库根目录；
2. 仓库 **Settings → Pages**，Source 选 `Deploy from a branch`，分支选 `main`，目录选 `/ (root)`；
3. 保存后等待 1–2 分钟，访问 `https://<你的用户名>.github.io/Lume/` 即可。

### 替换仓库地址（仅 fork 自建时需要）

本仓库的「提 issue / 请求收录科目」链接已指向 `chengyi-mountain/Lume`。如果你 fork 后自建部署，需要改成你自己的仓库：打开 `index.html`，搜索 `chengyi-mountain/Lume`，替换成 `用户名/仓库名`；也可以在 `index.html` 的 `</body>` 前显式声明，优先级更高：

```html
<script>
  window.LUME_REPO = "你的用户名/Lume";
</script>
```

---

## 🤖 接入 AI 智能体（可选）

不配置也完全可用，助手会自动走「内置知识库」通道，离线即答。

### 方式一：页面设置弹窗

打开网站 → 点右下角 💬 → 通道下拉选「AI 智能体」→ 按提示填入接口信息。

> 默认建议用额度 / 限速的 Key，避免烧钱。

### 方式二：写进代码（适合自建部署）

在 `index.html` 的 `</body>` 前加一段：

```html
<script>
  window.LUME_STUDIO_CONFIG = {
    api: "https://你的接口地址",
    model: "模型名",
    format: "openai",                // 是否为 OpenAI 兼容格式
    headers: { Authorization: "Bearer 你的Key" }
  };
</script>
```

支持的供应商（改 `api` / `model` / `headers` 即可）：

| 供应商 | api 示例 | format |
|---|---|---|
| 混元（腾讯云） | `https://hunyuan.tencentcloudapi.com/v1/chat/completions` | `openai` |
| DeepSeek | `https://api.deepseek.com/v1/chat/completions` | `openai` |
| OpenAI 兼容 | 任意兼容 `/v1/chat/completions` 的地址 | `openai` |
| 自定义接口 | 你的服务端地址 | 不填，提供 `bodyBuilder` 自行组装请求体 |

更灵活的自定义请求体：

```html
<script>
  window.LUME_STUDIO_CONFIG = {
    api: "https://你的接口地址",
    bodyBuilder: (name, prompt, cfg) => JSON.stringify({
      model: cfg.model,
      system: "你是学习助手",
      input: prompt
    })
  };
</script>
```

> ⚠️ 安全提醒：自建部署时不要把 Key 硬编码进公开仓库；如果一定要提交，请使用受限 / 低额度 Key，或用环境变量在构建时注入。**Key 只存在用户本地浏览器，本项目不会上传、不会收集。**

---

## 📚 贡献新科目

科目计划是纯数据，加一个科目只要往 `index.html` 的 `SUBJECTS` 数组里塞一条：

```javascript
{
  id: "guitar", icon: "🎸", name: "吉他", cat: "音乐与艺术", hot: false,
  intro: "一句话说清它是什么、学了能干嘛",
  goals: {
    beginner: ["能弹唱 3 首完整歌曲", "..."],
    advanced: ["能即兴伴奏、扒谱", "..."]
  },
  phases: {
    beginner: [
      { title: "阶段名", meta:{ time:"1-2 周", out:"阶段产出" },
        quote: "一句大白话解释这阶段在干啥",
        items: ["具体知识点 1", "具体知识点 2", "..."] }
    ],
    advanced: [ /* 同上结构 */ ]
  },
  tips: { beginner: ["避坑 1", "..."], advanced: ["避坑 1", "..."] },
  resources: [ { t: "资源名", d: "一句话说明" }, ... ]
}
```

**字段约定**

- `id` 全小写英文，全局唯一；`icon` 用 emoji；
- `cat` 建议从现有方向中选：编程技术 / AI与智能 / 职业技能 / 语言学习 / 学科与考试 / 兴趣生活 / 办公与效率 / 音乐与艺术 / 数据与 AI / 理财与生活 / 个人成长 / 设计与创作；
- 每个阶段 **必须** 有 `quote`（大白话解释），这是本项目「不劝退」的核心；
- 未内置科目会走本地规则引擎，但收录到 `SUBJECTS` 后能提供质量更高的专属方案。

你也可以在网站上：输入科目 → 等本地方案生成 → 点「复制为 JSON」→ 去 GitHub 提 PR，作者审核后即可合并。

扩充内置知识库同理：在 `KB` 数组里加 `{q:"问题", a:"回答"}` 即可。

---

## ⚖️ 免责声明（精简版）

1. 本站内容为经验性学习建议，**不构成学习成果、就业、考试通过率或收益承诺**；
2. 第三方资源（书籍 / 课程 / 视频）的内容、价格、版权由各平台负责，本站不作担保；
3. **AI 回答可能出错**，涉及医疗、法律、金融投资、税务等高敏领域，**务必咨询持证专业人士**；
4. 打卡进度 / API Key 仅存本地浏览器，不上传、不收集，但清空浏览器数据会丢失；
5. 实践类操作（健身 / 烹饪 / 编程 / 财务）请在安全合规前提下进行。

完整版见网站右下角工具栏 ⚖️。

---

## 📜 开源协议

[MIT](./LICENSE) —— 可自由使用、修改、分发，包括商业用途。使用即视为同意免责声明。

---

## 🙌 如何贡献

1. Fork 本仓库，新建分支：`git checkout -b feat/new-subject`
2. 在 `SUBJECTS`（或 `KB`）里加入你的内容
3. 提交并推送：`git commit -m "feat: 新增吉他科目" && git push`
4. 提 Pull Request，等待审核合并 🎉

也欢迎提交 Issue 反馈 bug、提出新科目请求或改进建议。
