from dotenv import load_dotenv
load_dotenv()


import os, asyncio, requests, datetime

import streamlit as st
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient


# ---------- Tools ----------
def web_search(query: str) -> str:
    """Search the web and return the top results as text."""
    r = requests.post("https://google.serper.dev/search",
                      headers={"X-API-KEY": os.environ["SERPER_API_KEY"]},
                      json={"q": query}, timeout=15)
    items = r.json().get("organic", [])[:5]
    return "\n".join(f"{i['title']}: {i.get('snippet', '')} ({i['link']})" for i in items)


def save_to_file(query: str, answer1: str, answer2: str) -> str:
    """Save the query and both answers to answers.txt."""
    with open("answers.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.datetime.now()} ===\nQUERY: {query}\n"
                f"ASSISTANT ANSWER:\n{answer1}\n\nWEB SEARCH ANSWER:\n{answer2}\n")
    return "Saved to answers.txt"


# ---------- Agents + Team ----------
def build_team():
    client = OpenAIChatCompletionClient(model="gpt-4o-mini")  # reads OPENAI_API_KEY
    assistant = AssistantAgent(
        "Assistant", model_client=client,
        system_message="You are a customer support agent. Answer the user's query directly "
                       "from your own knowledge. Be concise.")
    web = AssistantAgent(
        "Web_Search_Assistant", model_client=client, tools=[web_search],
        reflect_on_tool_use=True,
        system_message="Always call web_search with the user's query, then write a concise "
                       "answer from the results and cite sources.")
    entry = AssistantAgent(
        "Entry_Agent", model_client=client, tools=[save_to_file],
        reflect_on_tool_use=True,
        system_message="Call save_to_file with the original query, the Assistant's answer and "
                       "the Web_Search_Assistant's answer, copied exactly. Then reply briefly "
                       "and end with TERMINATE.")
    stop = TextMentionTermination("TERMINATE") | MaxMessageTermination(8)
    return RoundRobinGroupChat([assistant, web, entry], termination_condition=stop), client


# ---------- Run helpers ----------
async def run_team(query):
    team, client = build_team()
    result = await team.run(task=query)
    await client.close()
    return result


def last_text(result, source):
    msgs = [m for m in result.messages
            if m.source == source and type(m).__name__ == "TextMessage"]
    return msgs[-1].content if msgs else "(no answer)"


# ---------- Streamlit UI ----------
st.title("Multi-Agent Customer Support")
query = st.text_input("Enter your query or task")

if st.button("Ask") and query:
    with st.spinner("Agents are working..."):
        result = asyncio.run(run_team(query))
    col1, col2 = st.columns(2)
    col1.subheader("Assistant answer")
    col1.write(last_text(result, "Assistant"))
    col2.subheader("Web Search answer")
    col2.write(last_text(result, "Web_Search_Assistant"))
    st.success("Saved to answers.txt")
    with st.expander("Full agent conversation"):
        for m in result.messages:
            st.markdown(f"**{m.source}** ({type(m).__name__}): {m.content}")