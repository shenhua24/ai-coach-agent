import json

from workout_tools import (
    clear_training_plan,
    generate_monthly_plan,
    generate_weekly_plan,
    get_exercise_detail,
    get_exercise_library,
    get_feedback_summary,
    get_profile,
    get_reference_data,
    get_training_plan,
    log_workout_feedback,
    update_profile,
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_reference_data",
            "description": "获取可选训练目标、身体部位、经验等级和器械选项。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": "更新健身用户画像，包括目标、训练频率、经验、器械、目标部位和伤病限制。",
            "parameters": {
                "type": "object",
                "properties": {
                    "height_cm": {"type": "number"},
                    "weight_kg": {"type": "number"},
                    "age": {"type": "integer"},
                    "sex": {"type": "string"},
                    "goal": {"type": "string", "description": "例如 减脂、增肌、塑形、提升力量、提升心肺"},
                    "training_days_per_week": {"type": "integer"},
                    "experience_level": {"type": "string", "description": "初级、中级或高级"},
                    "available_equipment": {"type": "array", "items": {"type": "string"}},
                    "target_body_parts": {"type": "array", "items": {"type": "string"}},
                    "injury_notes": {"type": "string"},
                    "preferred_duration_min": {"type": "integer"},
                    "rest_days": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "查看当前用户画像和训练建议摘要。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exercise_library",
            "description": "按部位、器械、难度或关键词查询动作库。",
            "parameters": {
                "type": "object",
                "properties": {
                    "body_part": {"type": "string"},
                    "equipment": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "query": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exercise_detail",
            "description": "查看单一运动的注意事项、训练要点、常见错误和安全提示。",
            "parameters": {
                "type": "object",
                "properties": {
                    "exercise_id": {"type": "string"},
                    "name": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_weekly_plan",
            "description": "根据画像、器械、目标部位和训练天数生成一周训练计划。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_per_week": {"type": "integer"},
                    "goal": {"type": "string"},
                    "focus_parts": {"type": "array", "items": {"type": "string"}},
                    "available_equipment": {"type": "array", "items": {"type": "string"}},
                    "experience_level": {"type": "string"},
                    "preferred_duration_min": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_monthly_plan",
            "description": "生成 4 周训练周期，包含适应、标准、进阶和降载安排。",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_per_week": {"type": "integer"},
                    "goal": {"type": "string"},
                    "focus_parts": {"type": "array", "items": {"type": "string"}},
                    "available_equipment": {"type": "array", "items": {"type": "string"}},
                    "experience_level": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_training_plan",
            "description": "查看当前一周或一个月训练计划。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_training_plan",
            "description": "清空当前训练计划。只有用户明确要求清空时才调用。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_workout_feedback",
            "description": "记录当天训练反馈，并根据完成度、难度、酸痛、疼痛和精力调整下一次训练。",
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {"type": "string", "description": "例如 Day 1"},
                    "completed": {"type": "boolean"},
                    "difficulty_score": {"type": "integer", "description": "1-10，越高越难"},
                    "energy_score": {"type": "integer", "description": "1-5，越高精力越好"},
                    "soreness_parts": {"type": "array", "items": {"type": "string"}},
                    "pain_parts": {"type": "array", "items": {"type": "string"}},
                    "sleep_quality": {"type": "string", "description": "好、一般、差、很差"},
                    "note": {"type": "string"},
                },
                "required": ["day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_feedback_summary",
            "description": "查看训练反馈历史和最近一次调整建议。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


TOOL_HANDLERS = {
    "get_reference_data": get_reference_data,
    "update_profile": update_profile,
    "get_profile": get_profile,
    "get_exercise_library": get_exercise_library,
    "get_exercise_detail": get_exercise_detail,
    "generate_weekly_plan": generate_weekly_plan,
    "generate_monthly_plan": generate_monthly_plan,
    "get_training_plan": get_training_plan,
    "clear_training_plan": clear_training_plan,
    "log_workout_feedback": log_workout_feedback,
    "get_feedback_summary": get_feedback_summary,
}

PROFILE_TOOL_NAMES = {"update_profile", "get_profile"}
PLAN_TOOL_NAMES = {"generate_weekly_plan", "generate_monthly_plan", "get_training_plan", "clear_training_plan"}


def execute_tool(tool_name, tool_input, plan=None, profile=None, feedback_log=None, **_legacy_kwargs):
    handler = TOOL_HANDLERS.get(tool_name)

    if handler is None:
        return {
            "success": False,
            "message": f"未知工具：{tool_name}",
        }

    try:
        if tool_name in PROFILE_TOOL_NAMES:
            return handler(**tool_input, profile=profile)

        if tool_name in PLAN_TOOL_NAMES:
            if tool_name in {"generate_weekly_plan", "generate_monthly_plan"}:
                return handler(**tool_input, profile=profile, plan=plan)
            return handler(**tool_input, plan=plan)

        if tool_name == "log_workout_feedback":
            return handler(**tool_input, plan=plan, feedback_log=feedback_log)

        if tool_name == "get_feedback_summary":
            return handler(**tool_input, feedback_log=feedback_log)

        if tool_name == "get_exercise_library" and profile is not None and not tool_input.get("equipment"):
            return handler(**tool_input, profile=profile)

        return handler(**tool_input)
    except Exception as error:
        return {
            "success": False,
            "message": str(error),
        }


def parse_tool_arguments(arguments):
    if not arguments:
        return {}

    try:
        return json.loads(arguments)
    except json.JSONDecodeError:
        return {}
