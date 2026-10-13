from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import config

_llm = ChatOpenAI(
    model=config.OPENROUTER_MODEL,
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_BASE_URL,
    temperature=0.7,
)


def _to_langchain_messages(history: list[tuple[str, str]], user_message: str):
    messages = [SystemMessage(content=config.SYSTEM_PROMPT)]
    for role, content in history:
        if role == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=user_message))
    return messages


async def get_bot_reply(history: list[tuple[str, str]], user_message: str) -> str:
    messages = _to_langchain_messages(history, user_message)
    response = await _llm.ainvoke(messages)
    return response.content
