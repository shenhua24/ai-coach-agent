import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI 健身教练", page_icon="AI", layout="wide")

st.markdown(
    """
    <style>
    .block-container { max-width: 1480px; padding-top: 1.2rem; padding-left: 1.8rem; padding-right: 1.8rem; }
    [data-testid="stMetricValue"] { font-size: 1.45rem; }
    .app-header { padding: 1rem 1.1rem; border: 1px solid #d7dee8; background: #f7f9fb; border-radius: 8px; margin-bottom: 1rem; }
    .app-header h1 { margin: 0 0 0.25rem 0; font-size: 2rem; letter-spacing: 0; }
    .app-header p { color: #4b5563; margin: 0; line-height: 1.65; }
    .tag { display: inline-block; background: #e9f5ef; color: #17613a; padding: 3px 8px; border-radius: 6px; margin: 2px 4px 2px 0; font-size: 0.78rem; }
    .warning-note { border-left: 4px solid #b45309; background: #fff8ed; color: #5f3b08; padding: 0.75rem 0.9rem; border-radius: 6px; margin: 0.5rem 0 1rem 0; line-height: 1.55; }
    </style>
    """,
    unsafe_allow_html=True,
)


def auth_headers():
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path, params=None, auth=True):
    response = requests.get(f"{API_BASE_URL}{path}", params=params, headers=auth_headers() if auth else None, timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path, payload=None, auth=True):
    response = requests.post(f"{API_BASE_URL}{path}", json=payload or {}, headers=auth_headers() if auth else None, timeout=120)
    response.raise_for_status()
    return response.json()


def api_delete(path):
    response = requests.delete(f"{API_BASE_URL}{path}", headers=auth_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def init_state():
    defaults = {
        "access_token": None,
        "user": None,
        "reference": {},
        "profile": {},
        "guidance": {},
        "training_plan": {},
        "feedback_records": [],
        "feedback_summary": "",
        "messages": [],
        "tool_calls": [],
        "exercises": [],
        "knowledge_results": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_reference():
    st.session_state.reference = api_get("/api/reference-data", auth=False)


def load_profile():
    data = api_get("/api/profile")
    st.session_state.profile = data["profile"]
    st.session_state.guidance = data["training_guidance"]


def load_plan():
    data = api_get("/api/training-plan")
    st.session_state.training_plan = data["training_plan"]


def load_feedback():
    data = api_get("/api/feedback")
    st.session_state.feedback_records = data["records"]
    st.session_state.feedback_summary = data["summary"]


def load_exercises(body_part=None, equipment=None, difficulty=None, query=None):
    data = api_get("/api/exercises", {"body_part": body_part or None, "equipment": equipment or None, "difficulty": difficulty or None, "query": query or None})
    st.session_state.exercises = data["items"]


def load_all():
    load_profile()
    load_plan()
    load_feedback()
    load_exercises()


def split_tags(value):
    return [item.strip() for item in value.replace(",", "、").replace("，", "、").split("、") if item.strip()]


def error_message(error):
    try:
        return error.response.json().get("detail") or str(error)
    except Exception:
        return str(error)


def render_header():
    st.markdown(
        """
        <div class="app-header">
            <h1>AI 健身教练</h1>
            <p>基于 RAG + Agent 的个性化健身助手。系统结合本地健身知识库、用户画像、器械约束和训练反馈，生成更可解释的训练建议。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth():
    render_header()
    st.subheader("登录后开始训练计划")
    login_tab, register_tab = st.tabs(["登录", "注册"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("邮箱", key="login_email")
            password = st.text_input("密码", type="password", key="login_password")
            submitted = st.form_submit_button("登录", width="stretch")
        if submitted:
            try:
                data = api_post("/api/auth/login", {"email": email, "password": password}, auth=False)
            except requests.HTTPError as error:
                st.error(error_message(error))
            else:
                st.session_state.access_token = data["access_token"]
                st.session_state.user = data["user"]
                load_all()
                st.rerun()
    with register_tab:
        with st.form("register_form"):
            username = st.text_input("用户名")
            register_email = st.text_input("邮箱")
            register_password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("注册并登录", width="stretch")
        if submitted:
            try:
                data = api_post("/api/auth/register", {"username": username, "email": register_email, "password": register_password}, auth=False)
            except requests.HTTPError as error:
                st.error(error_message(error))
            else:
                st.session_state.access_token = data["access_token"]
                st.session_state.user = data["user"]
                load_all()
                st.rerun()


def render_top_bar():
    user = st.session_state.user or {}
    col1, col2 = st.columns([1, 0.18])
    col1.caption(f"当前用户：{user.get('username', '-')} · {user.get('email', '-')}")
    if col2.button("退出登录", width="stretch"):
        try:
            api_post("/api/auth/logout")
        except requests.RequestException:
            pass
        for key in ["access_token", "user", "profile", "guidance", "training_plan", "feedback_records", "messages", "tool_calls", "exercises", "knowledge_results"]:
            st.session_state[key] = None if key in {"access_token", "user"} else [] if key in {"feedback_records", "messages", "tool_calls", "exercises", "knowledge_results"} else {}
        st.rerun()


def render_profile_form():
    reference = st.session_state.reference
    profile = st.session_state.profile
    goals = reference.get("goals", ["塑形"])
    levels = reference.get("experience_levels", ["初级"])
    equipment_options = reference.get("equipment_options", ["徒手"])
    body_parts = reference.get("body_parts", [])
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            height_cm = st.number_input("身高 cm", 120.0, 230.0, float(profile.get("height_cm", 175.0)))
            weight_kg = st.number_input("体重 kg", 35.0, 220.0, float(profile.get("weight_kg", 72.0)))
            age = st.number_input("年龄", 12, 90, int(profile.get("age", 28)))
            sex_options = ["男", "女", "其他"]
            sex = st.selectbox("性别", sex_options, index=sex_options.index(profile.get("sex", "男")) if profile.get("sex") in sex_options else 0)
        with col2:
            goal = st.selectbox("训练目标", goals, index=goals.index(profile.get("goal", "塑形")) if profile.get("goal") in goals else 0)
            experience_level = st.selectbox("经验等级", levels, index=levels.index(profile.get("experience_level", "初级")) if profile.get("experience_level") in levels else 0)
            training_days = st.slider("每周训练天数", 2, 6, int(profile.get("training_days_per_week", 3)))
            duration = st.slider("单次训练时长", 30, 90, int(profile.get("preferred_duration_min", 60)), step=5)
        selected_equipment = st.multiselect("当前拥有的器械", equipment_options, default=profile.get("available_equipment", ["徒手"]))
        selected_parts = st.multiselect("重点训练部位", body_parts, default=profile.get("target_body_parts", []))
        injury_notes = st.text_area("伤病或限制", value=profile.get("injury_notes", ""), height=80)
        submitted = st.form_submit_button("保存画像", width="stretch")
    if submitted:
        data = api_post("/api/profile", {"height_cm": height_cm, "weight_kg": weight_kg, "age": age, "sex": sex, "goal": goal, "training_days_per_week": training_days, "experience_level": experience_level, "available_equipment": selected_equipment or ["徒手"], "target_body_parts": selected_parts, "injury_notes": injury_notes, "preferred_duration_min": duration})
        st.session_state.profile = data["profile"]
        st.session_state.guidance = data["training_guidance"]
        load_exercises()
        st.success("画像已保存")


def render_guidance():
    guidance = st.session_state.guidance
    st.subheader("训练基线")
    if not guidance.get("ready"):
        st.info(guidance.get("message", "保存画像后显示训练基线。"))
        return
    col1, col2 = st.columns(2)
    with col1:
        st.metric("BMI", guidance["bmi"])
        st.metric("建议天数", f"{guidance['recommended_days_per_week']} 天/周")
    with col2:
        st.metric("单次时长", f"{guidance['recommended_duration_min']} 分钟")
        st.metric("经验等级", guidance["experience_level"])
    st.caption(guidance["goal_note"])
    st.caption(guidance["intensity_note"])


def render_plan_actions():
    reference = st.session_state.reference
    profile = st.session_state.profile
    st.subheader("计划生成")
    with st.form("plan_form"):
        days = st.slider("每周训练天数", 2, 6, int(profile.get("training_days_per_week", 3)))
        plan_goal = st.selectbox("目标", reference.get("goals", ["塑形"]), index=reference.get("goals", ["塑形"]).index(profile.get("goal", "塑形")) if profile.get("goal") in reference.get("goals", []) else 0)
        plan_parts = st.multiselect("优先部位", reference.get("body_parts", []), default=profile.get("target_body_parts", []))
        plan_equipment = st.multiselect("可用器械", reference.get("equipment_options", []), default=profile.get("available_equipment", ["徒手"]))
        col1, col2 = st.columns(2)
        weekly = col1.form_submit_button("生成一周计划", width="stretch")
        monthly = col2.form_submit_button("生成一月计划", width="stretch")
    payload = {"days_per_week": days, "goal": plan_goal, "focus_parts": plan_parts, "available_equipment": plan_equipment or ["徒手"], "experience_level": profile.get("experience_level", "初级"), "preferred_duration_min": profile.get("preferred_duration_min", 60)}
    if weekly or monthly:
        endpoint = "/api/weekly-plan" if weekly else "/api/monthly-plan"
        data = api_post(endpoint, payload)
        load_plan()
        st.success(data["message"])
        if data.get("knowledge_sources"):
            with st.expander("本次计划参考依据", expanded=True):
                render_knowledge_items(data["knowledge_sources"])
    if st.button("清空当前计划", width="stretch"):
        api_delete("/api/training-plan")
        load_plan()
        st.rerun()


def render_exercise(exercise):
    with st.container(border=True):
        top = st.columns([1.4, 1])
        with top[0]:
            st.markdown(f"#### {exercise['name']}")
            st.caption(f"{exercise['body_part']} | {exercise['difficulty']} | {exercise['sets']} 组 x {exercise['reps']} | 休息 {exercise['rest_seconds']} 秒")
        with top[1]:
            tags = "".join(f'<span class="tag">{item}</span>' for item in exercise.get("equipment", []))
            st.markdown(tags, unsafe_allow_html=True)
        st.write("训练要点：" + "；".join(exercise.get("training_points", [])))
        if exercise.get("note"):
            st.info(exercise["note"])


def iter_plan_days(plan):
    if plan.get("type") == "monthly":
        for week in plan.get("weeks", []):
            for day in week.get("days", []):
                yield week, day
    else:
        for day in plan.get("days", []):
            yield None, day


def render_plan():
    plan = st.session_state.training_plan
    st.subheader("当前训练计划")
    if not plan:
        st.info("还没有训练计划。先保存画像，再生成一周或一个月计划。")
        return
    col1, col2, col3 = st.columns(3)
    col1.metric("计划类型", "一月" if plan.get("type") == "monthly" else "一周")
    col2.metric("目标", plan.get("goal", "-"))
    col3.metric("训练频率", f"{plan.get('days_per_week', 0)} 天/周")
    st.markdown(f"<div class='warning-note'>{plan.get('safety_note', '')}</div>", unsafe_allow_html=True)
    st.caption("进阶规则：" + plan.get("progression_rule", ""))
    for week, day in iter_plan_days(plan):
        title = f"{week['week']} · {week['phase']} · {day['day']}：{day['focus']}" if week else f"{day['day']}：{day['focus']}"
        with st.expander(title, expanded=week is None):
            if week:
                st.caption(week["phase_note"])
            st.write("热身：" + day["warmup"])
            for adjustment in day.get("adjustments", []):
                st.info(adjustment)
            for exercise in day.get("exercises", []):
                render_exercise(exercise)
            st.write("整理：" + day["cooldown"])


def render_feedback():
    plan = st.session_state.training_plan
    st.subheader("当天反馈与调整")
    day_options = [day["day"] for _, day in iter_plan_days(plan)] or ["Day 1"]
    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            day = st.selectbox("训练日", day_options)
            completed = st.checkbox("已完成训练", value=True)
            difficulty = st.slider("主观难度", 1, 10, 7)
        with col2:
            energy = st.slider("精力状态", 1, 5, 3)
            sleep = st.selectbox("睡眠质量", ["好", "一般", "差", "很差"], index=1)
            soreness = st.text_input("酸痛部位", placeholder="例如 胸部、腿部")
        pain = st.text_input("疼痛部位", placeholder="如果有尖锐疼痛，请写具体部位")
        note = st.text_area("备注", height=70)
        submitted = st.form_submit_button("记录反馈并调整计划", width="stretch")
    if submitted:
        data = api_post("/api/feedback", {"day": day, "completed": completed, "difficulty_score": difficulty, "energy_score": energy, "soreness_parts": split_tags(soreness), "pain_parts": split_tags(pain), "sleep_quality": sleep, "note": note})
        st.success(data["advice"])
        if data.get("plan_adjustment"):
            st.info(data["plan_adjustment"]["message"])
        if data.get("knowledge_sources"):
            with st.expander("恢复与安全依据", expanded=True):
                render_knowledge_items(data["knowledge_sources"])
        load_plan()
        load_feedback()
    st.caption(st.session_state.feedback_summary)
    if st.session_state.feedback_records:
        st.dataframe(st.session_state.feedback_records, width="stretch", hide_index=True)


def render_exercise_library():
    reference = st.session_state.reference
    st.subheader("动作库")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])
    body_part = col1.selectbox("部位", [""] + reference.get("body_parts", []))
    equipment = col2.selectbox("器械", [""] + reference.get("equipment_options", []))
    difficulty = col3.selectbox("难度", [""] + reference.get("experience_levels", []))
    query = col4.text_input("搜索动作")
    if st.button("筛选动作", width="stretch"):
        load_exercises(body_part, equipment, difficulty, query)
    if not st.session_state.exercises:
        st.info("没有匹配动作。可以放宽器械、部位或难度条件。")
        return
    cols = st.columns(3)
    for index, exercise in enumerate(st.session_state.exercises):
        with cols[index % 3]:
            render_exercise(exercise)


def render_knowledge_items(items):
    if not items:
        st.info("没有检索到匹配依据。")
        return
    for item in items:
        with st.container(border=True):
            st.markdown(f"#### {item['title']}")
            st.caption(f"来源：{item['source']} | 相关度：{item.get('score', '-')}")
            st.write(item["snippet"])


def render_knowledge_search():
    st.subheader("RAG 健身知识库")
    col1, col2 = st.columns([1, 0.18])
    query = col1.text_input("检索训练原则、恢复、安全和目标相关知识", value="增肌训练频率和恢复原则")
    top_k = col2.number_input("条数", min_value=1, max_value=8, value=3)
    if st.button("检索知识库", width="stretch"):
        data = api_post("/api/knowledge/search", {"query": query, "top_k": int(top_k)})
        st.session_state.knowledge_results = data["items"]
    render_knowledge_items(st.session_state.knowledge_results)


def send_message(user_message):
    st.session_state.messages.append({"role": "user", "content": user_message})
    data = api_post("/api/chat", {"message": user_message})
    st.session_state.messages.append({"role": "assistant", "content": data["reply"]})
    st.session_state.tool_calls.extend(data.get("tool_calls", []))
    load_all()


def render_chat():
    st.subheader("AI 教练对话")
    prompt_cols = st.columns(3)
    if prompt_cols[0].button("按科学原则做周计划", width="stretch"):
        send_message("先检索训练原则，再根据我的画像和器械生成一周训练计划。")
    if prompt_cols[1].button("解释一个动作", width="stretch"):
        send_message("检索依据后告诉我杯式深蹲的训练要点、常见错误和注意事项。")
    if prompt_cols[2].button("根据反馈调整", width="stretch"):
        send_message("我今天 Day 1 完成了，但难度 9 分，腿部很酸，帮我记录并结合恢复原则调整下一次训练。")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_input = st.chat_input("输入你的训练需求、器械情况或当天反馈")
    if user_input:
        send_message(user_input)
        st.rerun()
    if st.session_state.tool_calls:
        with st.expander("工具调用记录"):
            st.json(st.session_state.tool_calls)


init_state()
try:
    if not st.session_state.reference:
        load_reference()
except requests.RequestException:
    st.error("无法连接后端服务。请先启动：python -m uvicorn backend.api:app --reload")
    st.stop()

if not st.session_state.access_token:
    render_auth()
    st.stop()

try:
    if not st.session_state.profile:
        load_all()
except requests.HTTPError as error:
    if error.response.status_code == 401:
        st.session_state.access_token = None
        st.session_state.user = None
        st.warning("登录已失效，请重新登录。")
        st.rerun()
    st.error(error_message(error))
    st.stop()
except requests.RequestException:
    st.error("无法连接后端服务。请先启动：python -m uvicorn backend.api:app --reload")
    st.stop()

render_header()
render_top_bar()
left_col, main_col, right_col = st.columns([1.05, 1.75, 1.05], gap="large")
with left_col:
    with st.expander("用户画像", expanded=True):
        render_profile_form()
    render_guidance()
    st.divider()
    render_plan_actions()
with main_col:
    render_plan()
with right_col:
    render_feedback()
st.divider()
tabs = st.tabs(["动作库", "知识库", "AI 对话"])
with tabs[0]:
    render_exercise_library()
with tabs[1]:
    render_knowledge_search()
with tabs[2]:
    render_chat()
