import json
from typing import List
from shared.state import ResearchState, CuratedSection, Subtopic
from config.models import llm_invoke

ADVANCED_KEYWORDS = [
    "teoría", "cuántic", "bayes", "bayesiano", "medición causal",
    "identificación causal", "ecuaciones diferenciales", "análisis funcional",
    "topología", "complejidad computacional", "optimización convexa",
    "teoría de juegos", "redes neuronales profundas", "transformer",
    "modelos fundacionales", "procesos estocásticos", "método numérico",
    "macro dinámic", "econometría avanzada", "inferencia causal",
]

def estimate_curator_tier(topic: str, subtopics: List[Subtopic]) -> str:
    """
    - cheap: temas descriptivos / introductorios
    - standard: mezcla o duda razonable
    - premium: muchos subtemas + señales fuertes de complejidad técnica

    Mira señales semánticas básicas
    """
    text = (topic + " " + " ".join(s["title"] for s in subtopics)).lower()

    advanced_hits = sum(1 for kw in ADVANCED_KEYWORDS if kw in text)

    n = len(subtopics)

    if advanced_hits >= 3:
        return "premium"

    # Si hay alguna señal avanzada y varios subtemas --> premium
    if advanced_hits >= 1 and n >= 5:
        return "premium"
    
    if advanced_hits >= 1:
        return "standard"

    # Sin señales avanzadas
    if n <= 4:
        return "cheap"
    if n <= 8:
        return "standard"
    
    return "premium"


def curator_node(state: ResearchState) -> ResearchState:
    """
    Nodo del Agente Curador.

    Entrada:
    - state["topic"]: tema principal.
    - state["approved_subtopics"]: subtemas ya validados/modificados por el humano.

    Salida:
    - state["curated_sections"]: lista de CuratedSection, una por subtema aprobado.

    Rol:
    Toma los subtemas aprobados y, usando un modelo elegido según la complejidad,
    genera para cada uno:
        - Puntos clave estructurados.
        - Una síntesis corta.
        - Fuentes recomendadas.
    Esto alimenta al reporter, que arma el informe final. 
    """

    topic = state["topic"]
    approved: List[Subtopic] = state.get("approved_subtopics", [])

    if not approved:
        raise ValueError("CuratorNode: no hay subtemas aprobados para analizar.")

    # Selección de tier en base al contenido
    tier = estimate_curator_tier(topic, approved)

    #print(f"[curator] recibió {len(approved)} subtemas aprobados")
    #print(f"[curator] modelo usado: {tier}")

    curated_sections: List[CuratedSection] = []

    system_prompt = (
        "Eres el Agente Curador dentro de un sistema de investigación multi-agente.\n"
        "Recibes un subtema validado por un humano y debes profundizarlo.\n"
        "Tu salida DEBE ser un JSON ESTRICTO con el siguiente formato:\n"
        "{\n"
        "  \"key_points\": [\"punto 1\", \"punto 2\", \"punto 3\"],\n"
        "  \"synthesis\": \"párrafo breve integrando los puntos clave\",\n"
        "  \"recommended_sources\": [\"Fuente 1\", \"Fuente 2\", \"Fuente 3\"]\n"
        "}\n"
        "Reglas:\n"
        "- 3 a 6 key_points, concretos, específicos del subtema.\n"
        "- La synthesis debe ser clara, accionable y referida al subtema, no genérica.\n"
        "- Las recommended_sources son sugerencias (autores, papers, libros, reportes, instituciones), sin links obligatorios.\n"
        "- NO incluyas texto fuera del JSON. No uses markdown, ni explicaciones adicionales.\n"
    )

    for sub in approved:
        subtopic_title = sub["title"]
        rationale = sub.get("rationale", "").strip()

        user_prompt = (
            f"Tema principal: \"{topic}\"\n"
            f"Subtema: \"{subtopic_title}\"\n"
            f"Justificación original: \"{rationale}\"\n"
            "Genera SOLO el JSON indicado."
        )

        raw = llm_invoke(tier, system_prompt, user_prompt)

        # Intentamos parsear el JSON devuelto por el modelo
        key_points: List[str] = []
        synthesis: str = ""
        recommended_sources: List[str] = []

        try:
            data = json.loads(raw)

            if not isinstance(data, dict):
                raise ValueError("La respuesta no es un objeto JSON.")

            # key_points
            raw_kp = data.get("key_points", [])
            if isinstance(raw_kp, list):
                key_points = [
                    str(p).strip()
                    for p in raw_kp
                    if str(p).strip()
                ]

            synthesis = str(data.get("synthesis", "")).strip()

            # recommended_sources
            raw_src = data.get("recommended_sources", [])
            if isinstance(raw_src, list):
                recommended_sources = [
                    str(s).strip()
                    for s in raw_src
                    if str(s).strip()
                ]

            # para no dejar nada vacío
            if not key_points:
                key_points = [
                    f"Aspectos relevantes a profundizar sobre {subtopic_title} en el contexto de {topic}.",
                ]
            if not synthesis:
                synthesis = (
                    f"Síntesis preliminar sobre {subtopic_title}, destacando los puntos clave "
                    f"y su relación con el tema general {topic}."
                )
            if not recommended_sources:
                recommended_sources = [
                    f"Referencias especializadas sobre {subtopic_title} relacionadas con {topic}.",
                ]

        except Exception:
            # en caso que no devuelva nada parseable dejamos que se encargue el reporter
            key_points = [
                f"Analizar el rol de {subtopic_title} dentro de {topic}.",
                "Identificar evidencia empírica o casos de estudio relevantes.",
                "Explorar implicancias técnicas, éticas, económicas o regulatorias (según corresponda).",
            ]
            synthesis = (
                f"Análisis preliminar de {subtopic_title} como componente clave de {topic}, "
                "proponiendo líneas claras para el informe final."
            )
            recommended_sources = [
                f"Artículos académicos y reportes técnicos sobre {subtopic_title}.",
            ]

        curated_sections.append(
            CuratedSection(
                subtopic_title=subtopic_title,
                key_points="\n".join(f"- {kp}" for kp in key_points),
                synthesis=synthesis,
                recommended_sources=recommended_sources,
            )
        )

    return {"curated_sections": curated_sections}