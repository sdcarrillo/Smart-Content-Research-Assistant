from typing import TypedDict, List

class Subtopic(TypedDict):
    id: int
    title: str
    rationale: str

class CuratedSection(TypedDict):
    subtopic_title: str
    key_points: str
    synthesis: str
    recommended_sources: List[str]

class ResearchState(TypedDict, total=False):
    topic: str
    initial_subtopics: List[Subtopic]
    approved_subtopics: List[Subtopic]
    curated_sections: List[CuratedSection]
    final_report: str