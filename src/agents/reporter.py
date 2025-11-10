from typing import List

from shared.state import ResearchState, CuratedSection
from config.models import llm_invoke


def reporter_node(state: ResearchState) -> ResearchState:
    """
    Nodo del Agente Reportero.

    Entrada:
    - state["topic"]: tema principal.
    - state["curated_sections"]: lista de secciones curadas por el Curator.

    Salida:
    - state["final_report"]: string en formato Markdown con el informe final.

    Rol:
    - Transformar el contenido curado en un informe coherente, claro y presentable.
    - No investiga desde cero ni decide subtemas: solo organiza y redacta.
    - Usa siempre un modelo de mayor calidad (tier 'premium'), dado que es la capa de output final.
    """

    topic = state.get("topic", "").strip()
    sections: List[CuratedSection] = state.get("curated_sections", [])

    if not topic:
        raise ValueError("ReporterNode: falta el tema principal en el estado.")

    if not sections:
        raise ValueError("ReporterNode: no hay secciones curadas para construir el informe.")
    
    #print(f"[reporter] generando informe final con {len(sections)} secciones")

    # Preparamos un resumen estructurado de lo que ya hizo el Curator
    outline_parts = []
    for sec in sections:
        title = sec["subtopic_title"]
        key_points = sec.get("key_points", "").strip()
        synthesis = sec.get("synthesis", "").strip()
        sources = sec.get("recommended_sources", [])

        outline_parts.append(
            f"SUBTEMA: {title}\n"
            f"PUNTOS CLAVE:\n{key_points}\n\n"
            f"SINTESIS:\n{synthesis}\n\n"
            f"FUENTES SUGERIDAS:\n- " + "\n- ".join(sources)
        )

    outline = "\n\n---\n\n".join(outline_parts)

    system_prompt = (
        "Eres el Agente Reportero de un sistema de investigación multi-agente.\n"
        "Tu tarea es escribir un INFORME FINAL en ESPAÑOL, en formato MARKDOWN, "
        "a partir del contenido curado que recibes.\n"
        "No introduzcas subtemas completamente nuevos; podés profundizar o descomponer los aprobados.\n"
        "Requisitos del informe:\n"
        "- Título principal claro.\n"
        "- Resumen ejecutivo breve (5-8 líneas) al inicio.\n"
        "- Una sección por cada subtema, con encabezado '## ...'.\n"
        "- En cada sección, integrar los puntos clave y la síntesis de forma fluida.\n"
        "- Mencionar o listar fuentes sugeridas cuando aporten claridad (sin necesidad de links reales).\n"
        "- Conclusión final corta, resaltando hallazgos clave y posibles líneas futuras.\n"
        "- Estilo: claro, profesional, directo, sin relleno innecesario.\n"
        "- No inventes datos específicos ni números si no están sugeridos.\n"
        "- Respeta la estructura, pero podés mejorar el orden lógico.\n"
    )

    user_prompt = (
        f"Tema principal del informe: \"{topic}\"\n\n"
        "A continuación tienes el material curado generado por otro agente.\n"
        "Úsalo como base para redactar el informe final en Markdown:\n\n"
        f"{outline}\n"
    )

    report_md = llm_invoke("premium", system_prompt, user_prompt).strip()

    # En caso de respuesta vacía o rota
    if not report_md:
        # No debería pasar, pero así no se rompe el grafo
        sections_titles = "\n".join(f"- {sec['subtopic_title']}" for sec in sections)
        report_md = (
            f"# Informe sobre {topic}\n\n"
            "## Resumen ejecutivo\n"
            "Este informe presenta una síntesis estructurada del tema a partir de subtemas clave.\n\n"
            "## Subtemas abordados\n"
            f"{sections_titles}\n\n"
            "## Conclusión\n"
            "Se recomienda revisar en detalle las secciones anteriores y complementar con fuentes específicas.\n"
        )

    return {"final_report": report_md}
