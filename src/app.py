import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.graph import app as agent_app


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql: str
    answer: str
    error: str | None = None
    no_data: bool = False
    rows: list[dict] = []
    messages: list[str] = []

    class Config:
        arbitrary_types_allowed = True


def make_input_state(question: str, prior_state: dict | None = None) -> dict:
    previous_messages = []
    if prior_state and prior_state.get("messages"):
        previous_messages = list(prior_state["messages"])

    return {
        "messages": [
            SystemMessage(content="You are a helpful SQL assistant for a retail database."),
            *previous_messages,
            HumanMessage(content=question),
        ],
        "question": question,
        "sql": "",
        "rows": [],
        "answer": "",
        "error": "",
    }


def format_messages(messages: list) -> list[str]:
    formatted = []
    for message in messages:
        content = getattr(message, "content", str(message))
        message_type = getattr(message, "type", type(message).__name__)
        formatted.append(f"{message_type}: {content}")
    return formatted


app = FastAPI()


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    state = make_input_state(request.question)
    result = agent_app.invoke(state, config={"configurable": {"thread_id": "uv"}})

    rows = result.get("rows", []) or []
    error = result.get("error") or None
    no_data = not bool(rows) and error is None

    ai_message = f"AIMessage: {result.get('answer', '')}" if result.get('answer') else "AIMessage: "
    return QueryResponse(
        sql=result.get("sql", ""),
        answer=result.get("answer", ""),
        error=error,
        no_data=no_data,
        rows=rows,
        messages=format_messages(state["messages"]) + [ai_message],
    )


def run_cli() -> None:
    print("SQL assistant CLI. Type a question or 'quit' to exit.")
    prior_state = None
    while True:
        question = input("ask> ").strip()
        if not question or question.lower() in {"quit", "exit"}:
            break

        state = make_input_state(question, prior_state=prior_state)
        result = agent_app.invoke(state, config={"configurable": {"thread_id": "cli"}})
        prior_state = result

        print("\n=== Messages ===")
        for message in state["messages"]:
            if hasattr(message, "pretty_print"):
                message.pretty_print()
            else:
                print(f"{type(message).__name__}: {getattr(message, 'content', message)}")

        print("================================== AI Message ==================================")
        print(result.get('answer', ""))

        print("\n" + "=" * 80)
        print(f"SQL: {result.get('sql', '')}")

        if result.get("error"):
            print(f"Safety/Error: {result['error']}")
        elif not result.get("rows"):
            print("No data returned from the query.")

        print(f"Rows: {result.get('rows', [])}")
        print("==============\n")


if __name__ == "__main__":
    run_cli()
