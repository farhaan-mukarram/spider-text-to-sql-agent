import csv
import json

from langchain.messages import AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from tqdm import tqdm

from utils.database import query_table, tools


class AgentState(MessagesState):
    db_id: str


model = ChatOllama(model="gemma4:e4b", temperature=0)


list_tables_tool = next(tool for tool in tools if tool.name == "list_tables")


generate_query_system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to build_agent. You MUST ensure that the query generated is
relevant to the question.

Here are the provided tools:
    - list_tables: returns a list of tables in the database

""".format(
    dialect="sqlite",
)


# Example: create a predetermined tool call
def list_tables(state: AgentState):
    db_id = state["db_id"]

    tool_call = {
        "name": "list_tables",
        "args": {"table": db_id},
        "id": "abc123",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="TABLE LIST: ", tool_calls=[tool_call])

    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(tool_message.content)

    return {"messages": [tool_call_message, tool_message, response]}


def generate_query(state: MessagesState):
    system_message = {
        "role": "system",
        "content": generate_query_system_prompt,
    }
    # We do not force a tool call here, to allow the model to
    # respond naturally when it obtains the solution.
    response = model.invoke([system_message] + state["messages"])

    return {"messages": [response]}


check_query_system_prompt = """
You are a SQL expert with a strong attention to detail.
Double check the {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes,
just reproduce the original query. You must return the query as plain text as your final answer.
""".format(dialect="sqlite")


def check_query(state: MessagesState):
    response = model.invoke([AIMessage(check_query_system_prompt)] + state["messages"])

    return {"messages": [response]}


def build_agent(db_id: str):
    builder = StateGraph(AgentState)
    builder.add_node(list_tables)
    builder.add_node(generate_query)
    builder.add_node(check_query)

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "generate_query")
    builder.add_edge("generate_query", "check_query")
    builder.add_edge("check_query", END)

    agent = builder.compile()

    return agent


def main():
    with open("./data/dev.json") as f:
        data = json.loads(f.read())

    correct_count = 0

    csv_path = "./results.csv"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        # Save results incrementally to CSV
        writer = csv.DictWriter(
            f, fieldnames=["gold_query", "gold_results", "agent_query", "agent_results"]
        )
        writer.writeheader()

        for item in tqdm(data, desc="Evaluating"):
            table, question, gold_query = item["db_id"], item["question"], item["query"]
            agent = build_agent(table)
            result = agent.invoke(
                {
                    "db_id": table,
                    "messages": [{"role": "user", "content": question}],
                }
            )

            agent_query = result["messages"][-1].content
            gold_results = query_table(table, gold_query)
            agent_results = query_table(table, agent_query)

            if gold_results == agent_results:
                correct_count += 1

            # Convert results to string representation
            gold_results_str = str(gold_results) if gold_results else "[]"
            agent_results_str = str(agent_results) if agent_results else "[]"
            row = {
                "gold_query": gold_query,
                "gold_results": gold_results_str,
                "agent_query": agent_query,
                "agent_results": agent_results_str,
            }
            writer.writerow(row)
            f.flush()

    print(f"Correct queries: {correct_count}")
    print(f"Results saved to {csv_path}")


if __name__ == "__main__":
    main()
