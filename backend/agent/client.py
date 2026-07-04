import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def get_model_id():
    model_id = os.getenv("MODEL_ID")
    if not model_id:
        raise ValueError("没有找到 MODEL_ID，请在 .env 中配置模型名称。")
    return model_id


def get_client():
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("ANTHROPIC_BASE_URL")

    if not api_key:
        raise ValueError("没有找到 OPENAI_API_KEY，请在 .env 中配置 API Key。")

    if not base_url:
        base_url = "https://api.siliconflow.cn/v1"

    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=120.0,
        max_retries=1,
    )
