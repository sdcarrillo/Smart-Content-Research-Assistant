import json
from typing import List

from shared.state import ResearchState, Subtopic
from config.models import llm_invoke


def investigator_node(state: ResearchState) -> ResearchState:
    """
    Nodo del Agente Investigador.
    Usa el modelo cheap para proponer subtemas según el tópico.
    Devuelve entre 5 y 8 subtemas en formato estructurado.
    """

    topic = state["topic"]

    system_prompt = (
        "Eres el Agente Investigador de un sistema de investigación multi-agente.\n"
        "Tu tarea es, dado un tema general, proponer entre 5 y 8 subtemas concretos, no redundantes, "
        "cada uno con una breve justificación (2-3 líneas máximo).\n"
        "La salida debe ser JSON ESTRICTO, sin texto adicional ni explicaciones.\n"
        "Formato esperado:\n"
        "[\n"
        "  {\"id\": 1, \"title\": \"...\", \"rationale\": \"...\"},\n"
        "  {\"id\": 2, \"title\": \"...\", \"rationale\": \"...\"}\n"
        "]\n"
        "Condiciones:\n"
        "- Los IDs deben ser enteros consecutivos empezando en 1.\n"
        "- 'title' debe ser claro y accionable.\n"
        "- 'rationale' explica por qué ese subtema es relevante para el análisis del tema.\n"
    )

    user_prompt = f'Tema: "{topic}"\nGenera la lista JSON ahora.'

    #print(f"[investigator] topic recibido: {topic}")

    raw = llm_invoke("cheap", system_prompt, user_prompt)


    subs: List[Subtopic] = []
    try:
        data = json.loads(raw)

        if not isinstance(data, list):
            raise ValueError("La respuesta no es una lista JSON.")

        for i, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            rationale = str(item.get("rationale", "")).strip()
            if not title:
                continue

            subs.append(
                Subtopic(
                    id=i,
                    title=title,
                    rationale=rationale or "Subtema relevante para el análisis del tema."
                )
            )

        if not subs:
            raise ValueError("Lista de subtemas vacía.")

    except Exception:
        # por si falla el nodo, que no se rompa el grafo 
        subs = [
            Subtopic(id=1, title=f"Fundamentos de {topic}", rationale="Conceptos base y contexto general."),
            Subtopic(id=2, title=f"Aplicaciones de {topic}", rationale="Casos de uso y ejemplos prácticos."),
            Subtopic(id=3, title=f"Desafíos y riesgos en {topic}", rationale="Limitaciones técnicas, éticas o económicas."),
            Subtopic(id=4, title=f"Perspectivas futuras de {topic}", rationale="Tendencias probables y líneas de evolución."),
        ]

    return {"initial_subtopics": subs}