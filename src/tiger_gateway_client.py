from langchain_openai import ChatOpenAI

from src.config import (
    TIGER_AI_GATEWAY_API_KEY,
    TIGER_AI_GATEWAY_MODEL,
    TIGER_AI_GATEWAY_URL,
)


def create_tiger_gateway_client(
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> ChatOpenAI:
    api_key = api_key or TIGER_AI_GATEWAY_API_KEY
    base_url = base_url or TIGER_AI_GATEWAY_URL
    model = model or TIGER_AI_GATEWAY_MODEL

    if not api_key:
        raise ValueError(
            "TIGER_AI_GATEWAY_API_KEY is required to create the Tiger gateway LLM client."
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0,
    )
