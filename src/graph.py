from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from src.memory import create_memory_connection
from src.sql_tools import execute_sql, get_schema
from src.safety import validate_sql
from src.tiger_gateway_client import create_tiger_gateway_client


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    sql: str
    rows: list
    answer: str
    error: str


def get_last_user_question(state: AgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return message.content
    return ""


llm = create_tiger_gateway_client()

# Tools used by the workflow
schema_tool = get_schema
execute_tool = execute_sql
validate_tool = validate_sql

# Bind the tools so the model can call them when needed.
tools = [schema_tool, execute_tool, validate_tool]
llm_with_tools = llm.bind_tools(tools)


def generate_mysql_select(state: AgentState) -> AgentState:
    if state.get("error"):
        return state

    schema = schema_tool.invoke({})
    prompt = [
        SystemMessage(
            content=(
                "You are a SQL assistant for a retail MySQL database. "
                "Using the schema below, write ONE safe MySQL SELECT statement for the user's latest question. "
                "The query must use actual tables and columns from the schema, include a FROM clause, "
                "and must not return only a string literal or constant expression. "
                "Return only the SQL query, with no explanation.\n\nSchema:\n"
                f"{schema}"
            )
        ),
        *state["messages"],
    ]
    response = llm_with_tools.invoke(prompt)
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    return {**state, "question": get_last_user_question(state), "sql": sql}


def validate_mysql_select(state: AgentState) -> AgentState:
    sql = state.get("sql", "")
    if not sql:
        return {**state, "error": "No SQL generated."}
    try:
        cleaned = validate_tool.invoke({"sql": sql})
        return {**state, "sql": cleaned, "error": ""}
    except Exception as exc:
        return {**state, "sql": "", "error": f"Validation failed: {exc}"}


def execute_mysql_select(state: AgentState) -> AgentState:
    sql = state.get("sql", "")
    if not sql:
        return {**state, "rows": [], "error": "No valid SQL to execute."}
    try:
        result = execute_tool.invoke({"query": sql})
        return {**state, "rows": result, "error": ""}
    except Exception as exc:
        return {**state, "rows": [], "error": f"Execution failed: {exc}"}


def summarize_query_result(state: AgentState) -> AgentState:
    if state.get("error"):
        friendly_error = (
            "I couldn't generate a safe SQL query for that request. "
            "Please ask for a safe data lookup such as a SELECT query on the available tables."
        )
        return {**state, "answer": friendly_error}

    question = state.get("question") or get_last_user_question(state)
    prompt = [
        SystemMessage(content="You are a helpful assistant. Summarize the SQL result into a concise, user-facing answer."),
        HumanMessage(content=f"User question: {question}\nSQL: {state.get('sql', '')}\nResult: {state.get('rows', [])}"),
    ]
    response = llm_with_tools.invoke(prompt)
    return {**state, "answer": response.content}


def final_response(state: AgentState) -> AgentState:
    return {**state, "messages": [AIMessage(content=state.get("answer", ""))]}


builder = StateGraph(AgentState)
builder.add_node("generate_mysql_select", generate_mysql_select)
builder.add_node("validate_mysql_select", validate_mysql_select)
builder.add_node("execute_mysql_select", execute_mysql_select)
builder.add_node("summarize_query_result", summarize_query_result)
builder.add_node("final_response", final_response)

builder.add_edge(START, "generate_mysql_select")
builder.add_edge("generate_mysql_select", "validate_mysql_select")
builder.add_edge("validate_mysql_select", "execute_mysql_select")
builder.add_edge("execute_mysql_select", "summarize_query_result")
builder.add_edge("summarize_query_result", "final_response")
builder.add_edge("final_response", END)

memory_db_path = "sql_agent_memory.db"
memory_conn = create_memory_connection(memory_db_path)
memory = SqliteSaver(memory_conn)

app = builder.compile(checkpointer=memory)
