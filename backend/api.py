from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.store import create_session_store
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


app = FastAPI(title="AI Fitness Coach Agent", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = create_session_store()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=40)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileRequest(BaseModel):
    height_cm: Optional[float] = Field(default=None, ge=120, le=230)
    weight_kg: Optional[float] = Field(default=None, ge=35, le=220)
    age: Optional[int] = Field(default=None, ge=12, le=90)
    sex: Optional[str] = None
    goal: Optional[str] = None
    training_days_per_week: Optional[int] = Field(default=None, ge=0, le=7)
    experience_level: Optional[str] = None
    available_equipment: Optional[list[str]] = None
    target_body_parts: Optional[list[str]] = None
    injury_notes: Optional[str] = None
    preferred_duration_min: Optional[int] = Field(default=None, ge=15, le=150)
    rest_days: Optional[list[str]] = None


class PlanRequest(BaseModel):
    days_per_week: Optional[int] = Field(default=None, ge=2, le=6)
    goal: Optional[str] = None
    focus_parts: Optional[list[str]] = None
    available_equipment: Optional[list[str]] = None
    experience_level: Optional[str] = None
    preferred_duration_min: Optional[int] = Field(default=None, ge=15, le=150)


class FeedbackRequest(BaseModel):
    day: str
    completed: bool = True
    difficulty_score: Optional[int] = Field(default=None, ge=1, le=10)
    energy_score: Optional[int] = Field(default=None, ge=1, le=5)
    soreness_parts: Optional[list[str]] = None
    pain_parts: Optional[list[str]] = None
    sleep_quality: Optional[str] = None
    note: str = ""


class ChatRequest(BaseModel):
    message: str


def _token_from_header(authorization: Optional[str]):
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_current_user(authorization: Optional[str] = Header(default=None)):
    token = _token_from_header(authorization)
    user = store.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录。")
    return user


def get_current_token(authorization: Optional[str] = Header(default=None)):
    token = _token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="请先登录。")
    return token


def _save_all(user_id: int, messages=None, training_plan=None, profile=None, feedback_log=None):
    if messages is not None or training_plan is not None:
        store.save_session(
            user_id,
            messages if messages is not None else store.get_messages(user_id),
            training_plan if training_plan is not None else store.get_training_plan(user_id),
        )
    if profile is not None or feedback_log is not None:
        store.save_fitness_state(
            user_id,
            profile if profile is not None else store.get_profile(user_id),
            feedback_log if feedback_log is not None else store.get_feedback_log(user_id),
        )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/auth/register")
def register(payload: RegisterRequest):
    try:
        user = store.create_user(payload.username, payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    token = store.create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = store.authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="邮箱或密码不正确。")
    token = store.create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/auth/logout")
def logout(token: str = Depends(get_current_token)):
    store.revoke_token(token)
    return {"success": True}


@app.get("/api/me")
def me(current_user=Depends(get_current_user)):
    return {"user": current_user}


@app.get("/api/reference-data")
def reference_data():
    return get_reference_data()


@app.get("/api/profile")
def read_profile(current_user=Depends(get_current_user)):
    profile = store.get_profile(current_user["id"])
    return get_profile(profile=profile)


@app.post("/api/profile")
def save_profile(payload: ProfileRequest, current_user=Depends(get_current_user)):
    profile = store.get_profile(current_user["id"])
    result = update_profile(profile=profile, **payload.model_dump())
    _save_all(current_user["id"], profile=profile)
    result["user"] = current_user
    return result


@app.get("/api/exercises")
def exercises(
    body_part: Optional[str] = None,
    equipment: Optional[str] = None,
    difficulty: Optional[str] = None,
    query: Optional[str] = None,
    current_user=Depends(get_current_user),
):
    profile = store.get_profile(current_user["id"])
    return get_exercise_library(
        body_part=body_part,
        equipment=equipment,
        difficulty=difficulty,
        query=query,
        profile=profile,
    )


@app.get("/api/exercises/{exercise_id}")
def exercise_detail(exercise_id: str, current_user=Depends(get_current_user)):
    _ = current_user
    result = get_exercise_detail(exercise_id=exercise_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.get("/api/training-plan")
def read_training_plan(current_user=Depends(get_current_user)):
    return get_training_plan(plan=store.get_training_plan(current_user["id"]))


@app.post("/api/weekly-plan")
def weekly_plan(payload: PlanRequest, current_user=Depends(get_current_user)):
    profile = store.get_profile(current_user["id"])
    plan = store.get_training_plan(current_user["id"])
    result = generate_weekly_plan(
        days_per_week=payload.days_per_week,
        goal=payload.goal,
        focus_parts=payload.focus_parts,
        available_equipment=payload.available_equipment,
        experience_level=payload.experience_level,
        preferred_duration_min=payload.preferred_duration_min,
        profile=profile,
        plan=plan,
    )
    _save_all(current_user["id"], training_plan=plan)
    return result


@app.post("/api/monthly-plan")
def monthly_plan(payload: PlanRequest, current_user=Depends(get_current_user)):
    profile = store.get_profile(current_user["id"])
    plan = store.get_training_plan(current_user["id"])
    result = generate_monthly_plan(
        days_per_week=payload.days_per_week,
        goal=payload.goal,
        focus_parts=payload.focus_parts,
        available_equipment=payload.available_equipment,
        experience_level=payload.experience_level,
        profile=profile,
        plan=plan,
    )
    _save_all(current_user["id"], training_plan=plan)
    return result


@app.delete("/api/training-plan")
def delete_training_plan(current_user=Depends(get_current_user)):
    plan = store.get_training_plan(current_user["id"])
    result = clear_training_plan(plan=plan)
    store.clear_training_plan(current_user["id"])
    return result


@app.get("/api/feedback")
def feedback_summary(current_user=Depends(get_current_user)):
    return get_feedback_summary(feedback_log=store.get_feedback_log(current_user["id"]))


@app.post("/api/feedback")
def save_feedback(payload: FeedbackRequest, current_user=Depends(get_current_user)):
    plan = store.get_training_plan(current_user["id"])
    feedback_log = store.get_feedback_log(current_user["id"])
    result = log_workout_feedback(
        day=payload.day,
        completed=payload.completed,
        difficulty_score=payload.difficulty_score,
        energy_score=payload.energy_score,
        soreness_parts=payload.soreness_parts,
        pain_parts=payload.pain_parts,
        sleep_quality=payload.sleep_quality,
        note=payload.note,
        plan=plan,
        feedback_log=feedback_log,
    )
    _save_all(current_user["id"], training_plan=plan, feedback_log=feedback_log)
    return result


@app.post("/api/chat")
def chat(payload: ChatRequest, current_user=Depends(get_current_user)):
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        return {
            "reply": "还没有配置模型 API Key。你仍然可以使用画像、动作库、计划生成和反馈调整这些本地功能。",
            "tool_calls": [],
        }

    messages = store.get_messages(current_user["id"])
    plan = store.get_training_plan(current_user["id"])
    profile = store.get_profile(current_user["id"])
    feedback_log = store.get_feedback_log(current_user["id"])

    try:
        from backend.agent.loop import run_agent

        result = run_agent(
            messages=messages,
            user_message=payload.message,
            training_plan=plan,
            profile=profile,
            feedback_log=feedback_log,
        )
    except Exception as error:
        return {
            "reply": f"模型调用失败：{type(error).__name__}: {error}",
            "tool_calls": [],
        }

    _save_all(current_user["id"], messages=messages, training_plan=plan, profile=profile, feedback_log=feedback_log)
    return {
        "reply": result["reply"],
        "tool_calls": result["tool_calls"],
    }
