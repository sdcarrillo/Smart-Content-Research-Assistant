import re
from typing import List, Dict
from .state import Subtopic

def parse_ids(segment: str) -> List[int]:
    ids = []
    for part in segment.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            ids.extend(range(int(a), int(b)+1))
        else:
            ids.append(int(part))
    return ids

def apply_human_commands(commands: str, current: List[Subtopic]) -> List[Subtopic]:
    by_id = {s["id"]: s for s in current}
    approved, rejected = set(), set()
    modified, additions = {}, []
    chunks = [c.strip() for c in commands.split(";") if c.strip()]

    # print(f"[supervisor] comandos del usuario: {commands}")

    for chunk in chunks:
        lower = chunk.lower()
        if lower.startswith(("approve", "aprobar")):
            for i in parse_ids(chunk.split(" ", 1)[1]):
                approved.add(i)
        elif lower.startswith(("reject", "rechazar")):
            for i in parse_ids(chunk.split(" ", 1)[1]):
                rejected.add(i)
        elif lower.startswith(("modify", "modificar")):
            m = re.match(r".*?(\d+)\s+to\s+(.+)", chunk)
            if m:
                modified[int(m.group(1))] = m.group(2).strip('"').strip("'")
        elif lower.startswith(("add", "agregar")):
            label = chunk.split(" ", 1)[1].strip('"').strip("'")
            additions.append(label)

    result = []

    if approved:
        ids_to_keep = approved
    else:
        # si no hay approve, toma todos excepto los rechazados
        ids_to_keep = set(by_id.keys()) - rejected

    for sid, s in by_id.items():
        if sid not in ids_to_keep:
            continue
        title = modified.get(sid, s["title"])
        result.append({"id": len(result) + 1, "title": title, "rationale": s["rationale"]})

    for label in additions:
        result.append({"id": len(result) + 1, "title": label, "rationale": "Añadido manualmente."})

    #print(f"[supervisor] subtemas finales:\n{result}")

    return result
