from workout_tools import clear_training_plan


def main():
    print("AI 健身教练")
    print("输入 exit 退出。")
    print("输入 reset 开始新的计划。\n")

    conversation_history = []
    training_plan = {}
    profile = {}
    feedback_log = []

    while True:
        user_input = input("你：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            break

        if user_input.lower() == "reset":
            conversation_history.clear()
            training_plan.clear()
            profile.clear()
            feedback_log.clear()
            clear_training_plan(training_plan)
            print("\n对话、画像、反馈和训练计划已清空。\n")
            continue

        if not user_input:
            continue

        try:
            from backend.agent.loop import run_agent

            result = run_agent(
                messages=conversation_history,
                user_message=user_input,
                training_plan=training_plan,
                profile=profile,
                feedback_log=feedback_log,
            )
        except Exception as error:
            print(f"\n模型请求失败：{type(error).__name__}: {error}")
            continue

        print(f"\n教练：{result['reply']}\n")

        if result["tool_calls"]:
            print("工具调用：")
            for tool_call in result["tool_calls"]:
                print(f"- {tool_call['tool_name']}：{tool_call['tool_input']}")
            print()


if __name__ == "__main__":
    main()
