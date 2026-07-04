# AI Fitness Coach Agent

面向健身人群的 AI 健身教练实践项目，支持登录注册、SQLite 数据库存储、用户画像、器械匹配、动作库查询、一周训练计划、一个月训练周期，以及根据当天训练反馈自动调整下一次训练。

## 功能亮点

- 登录注册：支持邮箱注册、登录、Bearer Token 鉴权和退出登录。
- SQLite 持久化：保存用户、访问令牌、对话历史、用户画像、训练计划和训练反馈日志。
- 用户画像：记录身高、体重、年龄、性别、训练目标、经验等级、训练频率、可用器械、重点部位和伤病限制。
- 动作库：按训练部位、器械、难度和关键词筛选动作，并查看单一动作的训练要点、常见错误、节奏、休息和安全提示。
- 训练计划：根据目标、训练天数、器械和重点部位生成一周计划或 4 周周期化计划。
- 反馈调整：根据完成度、主观难度、精力、睡眠、酸痛和疼痛自动调整下一次训练。
- AI 对话：通过 OpenAI-compatible Function Calling 调用画像、动作库、计划和反馈工具。

## 技术栈

- Python 3.11+
- FastAPI
- Streamlit
- SQLite
- OpenAI-compatible Chat Completions API
- pip

## 项目结构

```text
backend/
  api.py              # FastAPI API、登录注册和鉴权
  store.py            # SQLite 用户、Token 和训练状态存储
  agent/
    client.py         # LLM 客户端配置
    loop.py           # Agent 工具调用循环
    prompts.py        # 健身教练系统提示词
    tools.py          # Function Calling schema 和工具执行
frontend/
  app.py              # Streamlit 登录页和健身教练工作台
workout_tools.py      # 动作库、画像、计划生成和反馈调整核心逻辑
main.py               # 命令行对话入口
requirements.txt      # pip 依赖
```

## 快速开始

创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

如需 AI 对话，在 `.env` 中填写：

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
MODEL_ID=your_model_id_here
DATABASE_PATH=fitness_coach.db
```

不配置模型 Key 时，登录注册、画像、动作库、计划生成和反馈调整这些本地功能仍可使用。

启动后端：

```bash
python -m uvicorn backend.api:app --reload
```

启动前端：

```bash
streamlit run frontend/app.py
```

默认前端连接 `http://127.0.0.1:8000`。如需修改：

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
streamlit run frontend/app.py
```

## 数据库说明

默认数据库文件是 `fitness_coach.db`，可以通过 `.env` 中的 `DATABASE_PATH` 修改。应用启动时会自动建表：

- `users`：用户账号和密码哈希
- `access_tokens`：登录令牌
- `messages`：AI 对话历史
- `profiles`：用户健身画像
- `training_plans`：当前训练计划
- `feedback_logs`：训练反馈日志

密码使用 PBKDF2-HMAC-SHA256 加盐哈希存储，不保存明文密码。

## 示例对话

```text
我男，28 岁，175cm，72kg，每周练 4 天，目标增肌。家里有哑铃、弹力带和瑜伽垫，肩部偶尔不舒服，帮我建立画像。
根据我的器械生成一周训练计划，重点练胸背腿和核心。
杯式深蹲有哪些训练要点、常见错误和注意事项？
今天 Day 1 完成了，难度 9 分，腿部酸痛，睡眠一般，帮我记录并调整下一次训练。
给我生成一个 4 周的训练周期。
```
