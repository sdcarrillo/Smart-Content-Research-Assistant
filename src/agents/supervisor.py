from langgraph.types import interrupt

from shared.state import ResearchState, Subtopic
from shared.parser import apply_human_commands


def approval_node(state: ResearchState) -> ResearchState:
    """
    Nodo Supervisor 
    Su función es:
    - Tomar los subtemas iniciales del Investigator.
    - Pausar la ejecución del grafo y exponer esos subtemas al usuario.
    - Recibir un único comando del usuario (via Command(resume=...)).
    - Aplicar ese comando (approve/reject/modify/add) usando apply_human_commands.
    - Guardar la lista final en approved_subtopics.
    """

    initial = state.get("initial_subtopics", [])

    if not initial:
        raise ValueError("Supervisor: no hay subtemas iniciales para aprobar.")

    # Preparamos el payload para el runner de consola.
    payload = {
        "subtopics": initial,
        "message": (
            "Revisá los subtemas propuestos y definí el plan con un solo comando.\n"
            "Formato sugerido (podés combinar con ';'):\n"
            "  approve 1,3\n"
            "  reject 2\n"
            "  modify 1 to \"Nuevo título\"\n"
            "  add \"Nuevo subtema\"\n"
            "Si no usás 'approve', se asume que todo lo no 'reject' se mantiene."
        ),
    }

    # Pausamos el grafo
    user_command: str = interrupt(payload)

    # Procesamos el comando
    approved = apply_human_commands(user_command, initial)

    if not approved:

        raise ValueError(
            "Supervisor: ningún subtema aprobado después del comando. "
            "Revisá la instrucción ingresada."
        )

    # Normalizamos IDs para el resto del flujo.
    normalized: list[Subtopic] = []
    for i, sub in enumerate(approved, start=1):
        normalized.append(
            Subtopic(
                id=i,
                title=sub["title"],
                rationale=sub.get("rationale", ""),
            )
        )

    return {"approved_subtopics": normalized}
