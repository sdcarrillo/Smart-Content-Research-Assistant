import uuid
from langgraph.types import Command
from graph.research_graph import build_graph

def run_console():
    graph = build_graph()
    topic = input("Ingresá el tema: ").strip()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.invoke({"topic": topic}, config=config)
    while "__interrupt__" in state:
        payload = state["__interrupt__"][0].value
        print("\n--- Subtemas ---")
        for s in payload["subtopics"]:
            print(f"{s['id']}. {s['title']} — {s['rationale']}")
        print(payload["message"])
        cmd = input("\nComandos: ").strip()
        state = graph.invoke(Command(resume=cmd), config=config)

    print("\n\n=== INFORME FINAL ===\n")
    print(state["final_report"])
