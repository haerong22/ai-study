history = []

def add_to_conversation(user_message, bot_response):
    history.append(
        {"user": user_message, "bot": bot_response, "timestamp": str(len(history) + 1)}
    )

    if len(history) > 10:
        history.pop(0)


def get_conversation_context():
    if not history:
        return "이전 대화 없음"

    context = "=== 최근 대화 기록 ===\n"
    for i, chat in enumerate(history, 1):
        context += f"{i}. 사용자: {chat["user"]}\n"
        context += f"     봇: {chat["bot"]}\n\n"

    return context