import json

from backend.agent.client import get_client, get_model_id
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tools import TOOLS, execute_tool, parse_tool_arguments


def run_agent(
    messages,
    user_message,
    training_plan=None,
    profile=None,
    feedback_log=None,
):
    """
    执行一轮 Agent 对话。

    messages 是当前会话历史，user_message 是用户最新输入。
    """
    client = get_client()
    model_id = get_model_id()

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    tool_call_logs = []

    while True:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *messages,
            ],
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1400,
        )

        message = response.choices[0].message

        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
        }

        if message.tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ]

        messages.append(assistant_message)

        if not message.tool_calls:
            return {
                "reply": message.content or "",
                "tool_calls": tool_call_logs,
            }

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = parse_tool_arguments(tool_call.function.arguments)

            result = execute_tool(
                tool_name,
                tool_input,
                plan=training_plan,
                profile=profile,
                feedback_log=feedback_log,
            )

            tool_call_logs.append(
                {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "tool_result": result,
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
