from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from shared.state import ResearchState
from agents.investigator import investigator_node
from agents.curator import curator_node
from agents.reporter import reporter_node
from agents.supervisor import approval_node

def build_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("investigator", investigator_node)
    builder.add_node("approval", approval_node)
    builder.add_node("curator", curator_node)
    builder.add_node("reporter", reporter_node)
    builder.add_edge(START, "investigator")
    builder.add_edge("investigator", "approval")
    builder.add_edge("approval", "curator")
    builder.add_edge("curator", "reporter")
    builder.add_edge("reporter", END)
    return builder.compile(checkpointer=MemorySaver())