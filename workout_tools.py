from __future__ import annotations

from copy import deepcopy
from datetime import date


BODY_PARTS = ["胸部", "背部", "腿部", "臀部", "肩部", "手臂", "核心", "心肺", "灵活性"]
EQUIPMENT_OPTIONS = ["徒手", "弹力带", "哑铃", "壶铃", "杠铃", "固定器械", "引体向上杆", "跑步机", "椭圆机", "瑜伽垫", "健身房"]
EXPERIENCE_LEVELS = ["初级", "中级", "高级"]
GOALS = ["减脂", "增肌", "塑形", "提升力量", "提升心肺", "健康维持"]


EXERCISES = {
    "push_up": {
        "name": "俯卧撑",
        "body_part": "胸部",
        "secondary_parts": ["肩部", "手臂", "核心"],
        "difficulty": "初级",
        "equipment": ["徒手"],
        "sets": 4,
        "reps": "8-15",
        "rest_seconds": 75,
        "tempo": "下放 2 秒，推起 1 秒",
        "training_points": ["身体保持一条直线", "胸部主动靠近地面", "推起时保持肩胛稳定"],
        "common_mistakes": ["塌腰", "手肘过度外展", "只做半程"],
        "tips": ["手掌略宽于肩", "保持自然呼吸", "动作质量下降时及时停止"],
    },
    "incline_push_up": {
        "name": "上斜俯卧撑",
        "body_part": "胸部",
        "secondary_parts": ["肩部", "手臂", "核心"],
        "difficulty": "初级",
        "equipment": ["徒手", "健身房"],
        "sets": 3,
        "reps": "10-15",
        "rest_seconds": 60,
        "tempo": "下放 2 秒，推起 1 秒",
        "training_points": ["选择稳定台面", "胸口靠近支撑面", "保持核心收紧"],
        "common_mistakes": ["耸肩", "腰部下塌", "速度过快"],
        "tips": ["适合俯卧撑基础阶段", "台面越高难度越低"],
    },
    "machine_chest_press": {
        "name": "坐姿推胸",
        "body_part": "胸部",
        "secondary_parts": ["肩部", "手臂"],
        "difficulty": "初级",
        "equipment": ["固定器械", "健身房"],
        "sets": 4,
        "reps": "8-12",
        "rest_seconds": 90,
        "tempo": "推出 1 秒，回放 2 秒",
        "training_points": ["肩胛贴住靠背", "把手高度接近胸中线", "胸部主动发力"],
        "common_mistakes": ["耸肩", "座椅高度不合适", "回放过快"],
        "tips": ["不要锁死肘关节", "新手优先选择能稳定控制的重量"],
    },
    "band_pull_apart": {
        "name": "弹力带拉开",
        "body_part": "背部",
        "secondary_parts": ["肩部"],
        "difficulty": "初级",
        "equipment": ["弹力带"],
        "sets": 3,
        "reps": "12-20",
        "rest_seconds": 45,
        "tempo": "拉开 1 秒，回放 2 秒",
        "training_points": ["肩胛向后下方收紧", "手臂基本伸直", "感受上背发力"],
        "common_mistakes": ["耸肩", "用腰后仰借力", "回放过快"],
        "tips": ["适合作为热身或上背补充训练", "阻力以全程可控为准"],
    },
    "one_arm_row": {
        "name": "单臂哑铃划船",
        "body_part": "背部",
        "secondary_parts": ["手臂", "核心"],
        "difficulty": "初级",
        "equipment": ["哑铃", "健身房"],
        "sets": 4,
        "reps": "10-12/侧",
        "rest_seconds": 90,
        "tempo": "拉起 1 秒，顶峰停 1 秒，下放 2 秒",
        "training_points": ["肩胛先后收再拉肘", "肘部贴近身体向后", "躯干保持稳定"],
        "common_mistakes": ["耸肩", "身体大幅旋转", "只用手臂发力"],
        "tips": ["眼睛看向前下方", "每次下放都让背阔肌充分拉伸"],
    },
    "lat_pulldown": {
        "name": "高位下拉",
        "body_part": "背部",
        "secondary_parts": ["手臂"],
        "difficulty": "初级",
        "equipment": ["固定器械", "健身房"],
        "sets": 4,
        "reps": "10-12",
        "rest_seconds": 90,
        "tempo": "下拉 1 秒，回放 2 秒",
        "training_points": ["先沉肩再拉肘", "胸口微微上挺", "控制回放"],
        "common_mistakes": ["身体后仰过多", "用二头肌硬拉", "下拉到脖子后方"],
        "tips": ["把手拉向锁骨附近", "选择能控制回放的重量"],
    },
    "goblet_squat": {
        "name": "杯式深蹲",
        "body_part": "腿部",
        "secondary_parts": ["臀部", "核心"],
        "difficulty": "初级",
        "equipment": ["哑铃", "壶铃", "健身房"],
        "sets": 4,
        "reps": "10-12",
        "rest_seconds": 90,
        "tempo": "下蹲 2 秒，起身 1 秒",
        "training_points": ["膝盖方向和脚尖一致", "脚跟稳定发力", "背部保持中立"],
        "common_mistakes": ["膝盖内扣", "踮脚", "弯腰塌背"],
        "tips": ["先用轻重量找到深度", "下蹲时保持腹压"],
    },
    "split_squat": {
        "name": "保加利亚分腿蹲",
        "body_part": "腿部",
        "secondary_parts": ["臀部", "核心"],
        "difficulty": "中级",
        "equipment": ["徒手", "哑铃", "健身房"],
        "sets": 3,
        "reps": "8-12/侧",
        "rest_seconds": 90,
        "tempo": "下蹲 2 秒，起身 1 秒",
        "training_points": ["前脚稳定踩地", "躯干略前倾但背部中立", "控制下放深度"],
        "common_mistakes": ["前膝内扣", "后脚借力过多", "身体左右晃动"],
        "tips": ["先徒手掌握平衡", "膝盖不适时改普通分腿蹲"],
    },
    "romanian_deadlift": {
        "name": "罗马尼亚硬拉",
        "body_part": "臀部",
        "secondary_parts": ["腿部", "背部"],
        "difficulty": "中级",
        "equipment": ["哑铃", "杠铃", "健身房"],
        "sets": 4,
        "reps": "8-12",
        "rest_seconds": 120,
        "tempo": "下放 3 秒，起身 1 秒",
        "training_points": ["髋部向后折叠", "背部保持中立", "感受腘绳肌和臀部拉伸"],
        "common_mistakes": ["弯腰硬拉", "膝盖锁死", "重量离身体太远"],
        "tips": ["重量沿腿前侧移动", "不要追求过低的下放幅度"],
    },
    "glute_bridge": {
        "name": "臀桥",
        "body_part": "臀部",
        "secondary_parts": ["腿部", "核心"],
        "difficulty": "初级",
        "equipment": ["徒手", "瑜伽垫"],
        "sets": 4,
        "reps": "12-15",
        "rest_seconds": 60,
        "tempo": "顶起 1 秒，顶峰停 1 秒，下放 2 秒",
        "training_points": ["脚跟发力", "顶峰夹紧臀部", "骨盆保持稳定"],
        "common_mistakes": ["用腰代偿", "脚离身体太远", "顶峰过度挺腰"],
        "tips": ["臀部无感觉时先做弹力带蚌式激活", "可逐步升级为负重臀桥"],
    },
    "overhead_press": {
        "name": "哑铃推举",
        "body_part": "肩部",
        "secondary_parts": ["手臂", "核心"],
        "difficulty": "中级",
        "equipment": ["哑铃", "健身房"],
        "sets": 3,
        "reps": "8-10",
        "rest_seconds": 90,
        "tempo": "推起 1 秒，下放 2 秒",
        "training_points": ["肋骨下沉并收紧核心", "手肘略在身体前方", "顶端稳定而不耸肩"],
        "common_mistakes": ["腰椎过度后仰", "耸肩夹脖子", "左右发力不均"],
        "tips": ["从坐姿或轻重量开始", "肩部不适时改为地雷管推或侧平举"],
    },
    "lateral_raise": {
        "name": "哑铃侧平举",
        "body_part": "肩部",
        "secondary_parts": [],
        "difficulty": "初级",
        "equipment": ["哑铃", "弹力带", "健身房"],
        "sets": 3,
        "reps": "12-15",
        "rest_seconds": 60,
        "tempo": "抬起 1 秒，下放 2 秒",
        "training_points": ["手肘微屈", "抬到肩高附近", "肩部发力而不耸肩"],
        "common_mistakes": ["借力甩起", "重量过大", "手腕高于手肘"],
        "tips": ["轻重量更容易找到中束发力", "最后几次可以缩短幅度但保持控制"],
    },
    "band_curl": {
        "name": "弹力带弯举",
        "body_part": "手臂",
        "secondary_parts": [],
        "difficulty": "初级",
        "equipment": ["弹力带"],
        "sets": 3,
        "reps": "12-15",
        "rest_seconds": 60,
        "tempo": "弯举 1 秒，下放 2 秒",
        "training_points": ["肘部贴近身体", "下放时控制阻力", "手腕保持中立"],
        "common_mistakes": ["身体后仰", "肘部前后摆动", "只做半程"],
        "tips": ["踩带位置越宽阻力越大", "适合居家手臂训练"],
    },
    "plank": {
        "name": "平板支撑",
        "body_part": "核心",
        "secondary_parts": ["肩部"],
        "difficulty": "初级",
        "equipment": ["徒手", "瑜伽垫"],
        "sets": 3,
        "reps": "30-60 秒",
        "rest_seconds": 60,
        "tempo": "静态稳定",
        "training_points": ["肋骨下沉", "骨盆微微后倾", "保持稳定呼吸"],
        "common_mistakes": ["塌腰", "撅臀", "憋气"],
        "tips": ["宁可缩短时间也要保持姿势", "腰酸时先停止并重置"],
    },
    "dead_bug": {
        "name": "死虫式",
        "body_part": "核心",
        "secondary_parts": [],
        "difficulty": "初级",
        "equipment": ["徒手", "瑜伽垫"],
        "sets": 3,
        "reps": "8-12/侧",
        "rest_seconds": 45,
        "tempo": "伸展 2 秒，回收 1 秒",
        "training_points": ["腰背轻贴地面", "动作慢且可控", "保持呼吸"],
        "common_mistakes": ["腰部离地", "动作太快", "颈部紧张"],
        "tips": ["适合初学者建立核心控制", "先做短幅度再逐渐加大"],
    },
    "kettlebell_swing": {
        "name": "壶铃摆动",
        "body_part": "心肺",
        "secondary_parts": ["臀部", "腿部", "核心"],
        "difficulty": "中级",
        "equipment": ["壶铃", "健身房"],
        "sets": 5,
        "reps": "15-20",
        "rest_seconds": 60,
        "tempo": "髋部爆发，手臂放松",
        "training_points": ["髋主导发力", "壶铃贴近身体轨迹", "顶端身体站直"],
        "common_mistakes": ["蹲举壶铃", "用手臂前平举", "腰部代偿"],
        "tips": ["先学会髋铰链", "腰背不适时不要做高次数摆动"],
    },
    "treadmill_intervals": {
        "name": "跑步机间歇",
        "body_part": "心肺",
        "secondary_parts": ["腿部"],
        "difficulty": "中级",
        "equipment": ["跑步机", "健身房"],
        "sets": 8,
        "reps": "快跑 30 秒 + 慢走 60 秒",
        "rest_seconds": 60,
        "tempo": "快慢交替",
        "training_points": ["快段保持可控速度", "慢段主动恢复", "全程保持安全步频"],
        "common_mistakes": ["速度过高失控", "热身不足", "扶着扶手冲刺"],
        "tips": ["先热身 8 分钟", "膝踝不适时改为坡走或椭圆机"],
    },
}


BODY_PART_SPLITS = {
    2: ["全身", "全身"],
    3: ["上肢", "下肢", "全身+核心"],
    4: ["胸部+肩部", "背部+手臂", "腿部+臀部", "核心+心肺"],
    5: ["胸部", "背部", "腿部", "肩部+手臂", "臀部+核心"],
    6: ["胸部", "背部", "腿部", "肩部", "手臂+核心", "心肺+恢复"],
}

PROFILE = {}
TRAINING_PLAN = {}
FEEDBACK_LOG = []


def _resolve_profile(profile=None):
    return PROFILE if profile is None else profile


def _resolve_plan(plan=None):
    return TRAINING_PLAN if plan is None else plan


def _resolve_feedback_log(feedback_log=None):
    return FEEDBACK_LOG if feedback_log is None else feedback_log


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        normalized = value.replace(",", "、").replace("，", "、").replace("/", "、")
        return [item.strip() for item in normalized.split("、") if item.strip()]
    return [str(value)]


def get_reference_data():
    return {
        "success": True,
        "body_parts": BODY_PARTS,
        "equipment_options": EQUIPMENT_OPTIONS,
        "experience_levels": EXPERIENCE_LEVELS,
        "goals": GOALS,
    }


def update_profile(profile=None, **profile_fields):
    active_profile = _resolve_profile(profile)
    allowed_fields = {
        "height_cm",
        "weight_kg",
        "age",
        "sex",
        "goal",
        "training_days_per_week",
        "experience_level",
        "available_equipment",
        "equipment",
        "target_body_parts",
        "injury_notes",
        "preferred_duration_min",
        "rest_days",
    }

    for key, value in profile_fields.items():
        if key not in allowed_fields or value in (None, "", []):
            continue
        if key == "equipment":
            active_profile["available_equipment"] = _as_list(value)
        elif key in {"available_equipment", "target_body_parts", "rest_days"}:
            active_profile[key] = _as_list(value)
        else:
            active_profile[key] = value

    active_profile.setdefault("experience_level", "初级")
    active_profile.setdefault("goal", "塑形")
    active_profile.setdefault("training_days_per_week", 3)
    active_profile.setdefault("available_equipment", ["徒手"])
    active_profile.setdefault("preferred_duration_min", 60)

    return {
        "success": True,
        "profile": active_profile,
        "training_guidance": calculate_training_guidance(active_profile),
        "message": "已更新健身画像。",
    }


def get_profile(profile=None):
    active_profile = _resolve_profile(profile)
    return {
        "success": True,
        "profile": active_profile,
        "training_guidance": calculate_training_guidance(active_profile),
    }


def calculate_training_guidance(profile=None):
    active_profile = _resolve_profile(profile)
    missing = [key for key in ("height_cm", "weight_kg") if key not in active_profile]
    if missing:
        return {
            "ready": False,
            "missing_fields": missing,
            "message": "请先补充身高和体重，计划会更贴合当前状态。",
        }

    height_m = float(active_profile["height_cm"]) / 100
    weight = float(active_profile["weight_kg"])
    bmi = round(weight / (height_m * height_m), 1)
    goal = active_profile.get("goal", "塑形")
    experience = active_profile.get("experience_level", "初级")
    requested_days = int(active_profile.get("training_days_per_week", 3))
    days_per_week = min(max(requested_days, 2), 6)
    duration = int(active_profile.get("preferred_duration_min", 60))

    intensity_by_experience = {
        "初级": "优先建立动作标准、训练习惯和基础容量，暂不追求大重量。",
        "中级": "可以记录重量、次数和主观疲劳，逐步提高训练容量。",
        "高级": "适合使用更明确的周期化安排，并根据恢复表现调整负荷。",
    }
    goal_note = {
        "减脂": "力量训练保留肌肉，心肺训练辅助消耗，饮食仍是能量缺口关键。",
        "增肌": "目标肌群每周建议获得 10-16 个有效训练组，并保证恢复。",
        "塑形": "采用力量训练为主、核心与心肺为辅的均衡安排。",
        "提升力量": "优先复合动作和更长休息，避免每组都练到力竭。",
        "提升心肺": "结合低强度有氧和短间歇，循序增加总时长。",
        "健康维持": "保持规律训练、关节活动度和基础心肺能力。",
    }.get(goal, "保持规律训练，并根据反馈微调强度。")

    return {
        "ready": True,
        "bmi": bmi,
        "goal": goal,
        "experience_level": experience,
        "recommended_days_per_week": days_per_week,
        "recommended_duration_min": min(max(duration, 30), 90),
        "intensity_note": intensity_by_experience.get(experience, intensity_by_experience["初级"]),
        "goal_note": goal_note,
    }


def get_exercise_library(body_part=None, equipment=None, difficulty=None, query=None, profile=None):
    available_equipment = _profile_equipment(profile) if profile is not None else _as_list(equipment)
    results = []

    for exercise_id, exercise in EXERCISES.items():
        if query and query not in exercise["name"] and query.lower() not in exercise_id:
            continue
        if body_part and body_part not in {exercise["body_part"], *exercise["secondary_parts"]}:
            continue
        if difficulty and exercise["difficulty"] != difficulty:
            continue
        if available_equipment and not _exercise_matches_equipment(exercise, available_equipment):
            continue
        results.append({"exercise_id": exercise_id, **deepcopy(exercise)})

    return {
        "success": True,
        "items": results,
        "count": len(results),
    }


def get_exercise_detail(exercise_id=None, name=None):
    resolved_id = _find_exercise_id(exercise_id=exercise_id, name=name)
    if resolved_id is None:
        return {
            "success": False,
            "message": "没有找到对应动作。可以先查看动作库，或提供更准确的动作名称。",
        }

    exercise = deepcopy(EXERCISES[resolved_id])
    return {
        "success": True,
        "exercise_id": resolved_id,
        "exercise": exercise,
        "safety_note": "训练中出现尖锐疼痛、麻木、眩晕或胸闷时，应立即停止训练。",
    }


def generate_weekly_plan(
    days_per_week=None,
    goal=None,
    focus_parts=None,
    available_equipment=None,
    equipment=None,
    experience_level=None,
    preferred_duration_min=None,
    profile=None,
    plan=None,
):
    active_profile = _resolve_profile(profile)
    active_plan = _resolve_plan(plan)
    guidance = calculate_training_guidance(active_profile)
    days = days_per_week or guidance.get("recommended_days_per_week", 3)
    days = min(max(int(days), 2), 6)
    goal = goal or active_profile.get("goal", "塑形")
    experience_level = experience_level or active_profile.get("experience_level", "初级")
    duration = preferred_duration_min or active_profile.get("preferred_duration_min", 60)
    equipment_list = _as_list(available_equipment or equipment) or _profile_equipment(active_profile)
    focus_parts = _as_list(focus_parts) or active_profile.get("target_body_parts") or BODY_PART_SPLITS[days]

    weekly_days = []
    for index in range(days):
        focus = focus_parts[index % len(focus_parts)]
        exercises = _pick_exercises_for_focus(focus, equipment_list, experience_level, goal)
        weekly_days.append(
            {
                "day": f"Day {index + 1}",
                "focus": focus,
                "estimated_duration_min": min(max(int(duration), 30), 90),
                "warmup": _build_warmup(focus),
                "exercises": exercises,
                "cooldown": "训练后 5-8 分钟低强度整理和静态拉伸，重点放松当天训练部位。",
                "status": "planned",
                "adjustments": [],
            }
        )

    active_plan.clear()
    active_plan.update(
        {
            "type": "weekly",
            "goal": goal,
            "days_per_week": days,
            "available_equipment": equipment_list,
            "experience_level": experience_level,
            "days": weekly_days,
            "progression_rule": _build_progression_rule(goal, experience_level),
            "safety_note": "训练中出现尖锐疼痛、眩晕、胸闷或关节异常不适时，应立即停止并考虑咨询专业人士。",
        }
    )

    return {
        "success": True,
        "weekly_plan": active_plan,
        "message": f"已生成每周 {days} 天的{goal}训练计划。",
    }


def generate_monthly_plan(
    days_per_week=None,
    goal=None,
    focus_parts=None,
    available_equipment=None,
    equipment=None,
    experience_level=None,
    profile=None,
    plan=None,
):
    active_profile = _resolve_profile(profile)
    active_plan = _resolve_plan(plan)
    base_plan = {}
    generate_weekly_plan(
        days_per_week=days_per_week,
        goal=goal,
        focus_parts=focus_parts,
        available_equipment=available_equipment or equipment,
        experience_level=experience_level,
        profile=active_profile,
        plan=base_plan,
    )

    phases = [
        ("第 1 周", "适应周", "保留 2-3 次余力，熟悉动作轨迹。", -1),
        ("第 2 周", "标准周", "按计划完成目标组数和次数。", 0),
        ("第 3 周", "进阶周", "状态良好时每个主项增加 1 组或小幅加重。", 1),
        ("第 4 周", "降载周", "总训练量降低约 20%-30%，让身体恢复。", -1),
    ]
    weeks = []
    for week_label, phase, note, set_delta in phases:
        week = deepcopy(base_plan)
        week["week"] = week_label
        week["phase"] = phase
        week["phase_note"] = note
        for day_plan in week["days"]:
            for exercise in day_plan["exercises"]:
                exercise["sets"] = max(2, int(exercise["sets"]) + set_delta)
        weeks.append(week)

    active_plan.clear()
    active_plan.update(
        {
            "type": "monthly",
            "goal": base_plan["goal"],
            "days_per_week": base_plan["days_per_week"],
            "available_equipment": base_plan["available_equipment"],
            "experience_level": base_plan["experience_level"],
            "weeks": weeks,
            "progression_rule": base_plan["progression_rule"],
            "safety_note": base_plan["safety_note"],
        }
    )

    return {
        "success": True,
        "monthly_plan": active_plan,
        "message": f"已生成 4 周、每周 {base_plan['days_per_week']} 天的训练周期。",
    }


def get_training_plan(plan=None):
    active_plan = _resolve_plan(plan)
    return {
        "success": True,
        "training_plan": active_plan,
        "has_plan": bool(active_plan),
    }


def clear_training_plan(plan=None):
    active_plan = _resolve_plan(plan)
    active_plan.clear()
    return {
        "success": True,
        "message": "训练计划已清空。",
    }


def log_workout_feedback(
    day,
    completed=True,
    difficulty_score=None,
    energy_score=None,
    soreness_parts=None,
    pain_parts=None,
    sleep_quality=None,
    note="",
    plan=None,
    feedback_log=None,
):
    active_log = _resolve_feedback_log(feedback_log)
    active_plan = _resolve_plan(plan)
    entry = {
        "date": date.today().isoformat(),
        "day": day,
        "completed": bool(completed),
        "difficulty_score": difficulty_score,
        "energy_score": energy_score,
        "soreness_parts": _as_list(soreness_parts),
        "pain_parts": _as_list(pain_parts),
        "sleep_quality": sleep_quality,
        "note": note,
    }
    entry["advice"] = build_feedback_advice(entry)
    active_log.append(entry)
    adjustment = apply_feedback_adjustment(active_plan, entry) if active_plan else None

    return {
        "success": True,
        "entry": entry,
        "advice": entry["advice"],
        "plan_adjustment": adjustment,
        "summary": get_feedback_summary(active_log)["summary"],
    }


def get_feedback_summary(feedback_log=None):
    active_log = _resolve_feedback_log(feedback_log)
    if not active_log:
        return {
            "success": True,
            "records": [],
            "summary": "还没有训练反馈。完成一次训练后，可以记录完成度、难度、精力、酸痛和疼痛。",
        }

    completed_count = sum(1 for item in active_log if item["completed"])
    pain_count = sum(1 for item in active_log if item.get("pain_parts"))
    latest = active_log[-1]
    return {
        "success": True,
        "records": active_log,
        "summary": (
            f"已记录 {len(active_log)} 次训练反馈，完成 {completed_count} 次，"
            f"疼痛反馈 {pain_count} 次。最近一次建议：{latest['advice']}"
        ),
    }


def build_feedback_advice(entry):
    pain_parts = entry.get("pain_parts") or []
    soreness_parts = entry.get("soreness_parts") or []
    difficulty_score = entry.get("difficulty_score")
    energy_score = entry.get("energy_score")
    sleep_quality = entry.get("sleep_quality")

    if pain_parts:
        return f"{'、'.join(pain_parts)} 出现疼痛，下次应避开该部位的高强度训练，并优先检查动作姿势。"
    if difficulty_score is not None and difficulty_score >= 9:
        return "本次难度偏高，下次建议减少 1-2 组或延长组间休息。"
    if energy_score is not None and energy_score <= 2:
        return "今日精力偏低，下次建议降低训练量 20% 或改为技术练习和恢复训练。"
    if sleep_quality in {"差", "很差"}:
        return "睡眠恢复不足，下次训练保持中低强度，避免冲击个人极限。"
    if soreness_parts:
        return f"{'、'.join(soreness_parts)} 有酸痛，同部位建议至少间隔 48 小时再高强度训练。"
    if entry.get("completed"):
        return "完成情况不错，下次可在动作质量稳定的前提下小幅增加次数、重量或一组训练量。"
    return "本次没有完成，建议降低计划难度，先保证训练习惯稳定。"


def apply_feedback_adjustment(plan, entry):
    if not plan:
        return None

    days = _flatten_plan_days(plan)
    next_day = _find_next_day(days, entry.get("day"))
    if not next_day:
        return {
            "applied": False,
            "message": "已记录反馈，但当前计划没有可调整的下一次训练。",
        }

    message = None
    pain_parts = set(entry.get("pain_parts") or [])
    soreness_parts = set(entry.get("soreness_parts") or [])
    difficulty_score = entry.get("difficulty_score")
    energy_score = entry.get("energy_score")

    if pain_parts:
        _reduce_day_volume(next_day, reduction_sets=1, extra_rest=30, avoid_parts=pain_parts)
        message = f"已将下一次训练降低强度，并标记避开 {'、'.join(pain_parts)} 的高强度动作。"
    elif difficulty_score is not None and difficulty_score >= 9:
        _reduce_day_volume(next_day, reduction_sets=1, extra_rest=30)
        message = "已将下一次训练每个动作减少 1 组，并延长组间休息。"
    elif energy_score is not None and energy_score <= 2:
        _reduce_day_volume(next_day, reduction_sets=1, extra_rest=15)
        next_day["focus"] = f"{next_day['focus']}（低强度）"
        message = "已将下一次训练调整为低强度版本。"
    elif soreness_parts:
        next_day["adjustments"].append(f"{'、'.join(soreness_parts)} 酸痛：同部位动作保留余力，不练到力竭。")
        message = "已添加酸痛部位的恢复提醒。"
    elif entry.get("completed"):
        next_day["adjustments"].append("上次完成良好：主项可小幅加重或每组增加 1-2 次。")
        message = "已添加渐进超负荷提醒。"
    else:
        _reduce_day_volume(next_day, reduction_sets=1, extra_rest=15)
        message = "已降低下一次训练难度，优先保证完成率。"

    next_day["status"] = "adjusted"
    return {
        "applied": True,
        "adjusted_day": next_day["day"],
        "message": message,
    }


def _profile_equipment(profile=None):
    active_profile = _resolve_profile(profile)
    return _as_list(active_profile.get("available_equipment")) or ["徒手"]


def _exercise_matches_equipment(exercise, available_equipment):
    equipment = set(available_equipment)
    if "健身房" in equipment:
        return True
    if not equipment:
        equipment = {"徒手"}
    return bool(set(exercise["equipment"]) & equipment)


def _find_exercise_id(exercise_id=None, name=None):
    if exercise_id in EXERCISES:
        return exercise_id
    if name:
        for current_id, exercise in EXERCISES.items():
            if name == exercise["name"] or name in exercise["name"]:
                return current_id
    return None


def _pick_exercises_for_focus(focus, available_equipment, experience_level, goal):
    focus_parts = _expand_focus(focus)
    candidates = []
    fallback = []

    for exercise_id, exercise in EXERCISES.items():
        item = {"exercise_id": exercise_id, **deepcopy(exercise)}
        if not _difficulty_allowed(exercise["difficulty"], experience_level):
            continue
        if _exercise_matches_equipment(exercise, available_equipment):
            fallback.append(item)
        if exercise["body_part"] not in focus_parts and not set(exercise["secondary_parts"]) & focus_parts:
            continue
        if not _exercise_matches_equipment(exercise, available_equipment):
            continue
        candidates.append(item)

    if goal in {"减脂", "提升心肺"}:
        cardio = [
            {"exercise_id": exercise_id, **deepcopy(exercise)}
            for exercise_id, exercise in EXERCISES.items()
            if exercise["body_part"] == "心肺" and _exercise_matches_equipment(exercise, available_equipment)
        ]
        candidates.extend(cardio)

    picked = _dedupe_exercises(candidates)[:5]
    if not picked:
        picked = _dedupe_exercises(fallback)[:5]
    if not picked:
        picked = [{"exercise_id": exercise_id, **deepcopy(exercise)} for exercise_id, exercise in EXERCISES.items()][:4]
    return picked


def _difficulty_allowed(difficulty, experience_level):
    rank = {"初级": 1, "中级": 2, "高级": 3}
    return rank.get(difficulty, 1) <= rank.get(experience_level, 1)


def _dedupe_exercises(items):
    seen = set()
    result = []
    for item in items:
        if item["exercise_id"] in seen:
            continue
        seen.add(item["exercise_id"])
        result.append(item)
    return result


def _expand_focus(focus):
    mapping = {
        "全身": {"胸部", "背部", "腿部", "臀部", "肩部", "核心"},
        "上肢": {"胸部", "背部", "肩部", "手臂"},
        "下肢": {"腿部", "臀部"},
        "全身+核心": {"胸部", "背部", "腿部", "臀部", "肩部", "核心"},
        "胸部+肩部": {"胸部", "肩部"},
        "背部+手臂": {"背部", "手臂"},
        "腿部+臀部": {"腿部", "臀部"},
        "核心+心肺": {"核心", "心肺"},
        "臀部+核心": {"臀部", "核心"},
        "肩部+手臂": {"肩部", "手臂"},
        "手臂+核心": {"手臂", "核心"},
        "心肺+恢复": {"心肺", "核心", "灵活性"},
    }
    if focus in mapping:
        return mapping[focus]
    parts = set()
    for part in BODY_PARTS:
        if part in focus:
            parts.add(part)
    return parts or {focus}


def _build_warmup(focus):
    if "腿" in focus or "臀" in focus:
        return "动态热身 8-10 分钟：髋关节绕环、徒手深蹲、臀桥、轻重量髋铰链。"
    if "胸" in focus or "背" in focus or "肩" in focus:
        return "动态热身 8-10 分钟：肩绕环、弹力带拉开、俯身 Y-T-W、轻重量推拉。"
    if "心肺" in focus:
        return "动态热身 8-10 分钟：快走、踝膝髋活动、逐步提高心率。"
    return "动态热身 8-10 分钟：关节活动、轻量激活和低强度心肺。"


def _build_progression_rule(goal, experience_level):
    if experience_level == "初级":
        return "当所有动作都能稳定完成目标次数，且主观难度不超过 7/10 时，再小幅增加次数或重量。"
    if goal == "增肌":
        return "优先在目标次数区间内增加次数，达到上限后小幅加重，并记录每周有效训练组。"
    if goal == "提升力量":
        return "主项保留 1-3 次余力，状态良好时每周小幅加重，避免连续多次力竭。"
    return "根据完成度、酸痛和精力反馈调整训练量，保持可持续进步。"


def _flatten_plan_days(plan):
    if plan.get("type") == "monthly":
        days = []
        for week in plan.get("weeks", []):
            days.extend(week.get("days", []))
        return days
    return plan.get("days", [])


def _find_next_day(days, current_day):
    if not days:
        return None
    current_index = None
    for index, day_plan in enumerate(days):
        if day_plan.get("day") == current_day:
            current_index = index
            break
    if current_index is None:
        return days[0]
    return days[(current_index + 1) % len(days)]


def _reduce_day_volume(day_plan, reduction_sets=1, extra_rest=0, avoid_parts=None):
    avoid_parts = avoid_parts or set()
    day_plan["adjustments"].append("根据反馈降低训练量，保持动作质量优先。")
    for exercise in day_plan.get("exercises", []):
        exercise["sets"] = max(2, int(exercise["sets"]) - reduction_sets)
        exercise["rest_seconds"] = int(exercise["rest_seconds"]) + extra_rest
        if exercise["body_part"] in avoid_parts or set(exercise["secondary_parts"]) & avoid_parts:
            exercise["note"] = "今日仅做轻重量技术练习，或替换为无痛动作。"
