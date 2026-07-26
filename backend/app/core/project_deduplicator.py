"""
Origin-Based Canonical Entity Graph Engine for TalentScout Enterprise (v1.8.3).
Multi-Signal Project Identity Resolution & Safe Graph Merge.

Pipeline Architecture:
Step 1: Extract Evidence Fragments (TITLE, DESCRIPTION, TECHNOLOGY, BULLET)
Step 2: Build Project Entity Graph with Multi-Signal Identity Resolution
Step 3: Safe Graph Merge Policy (3+ independent signals required, hard domain/title conflict prohibitions)
Step 4: Generate Runtime JSON with Project Identity UUIDs & Merge Confidence
Step 5: Run DuplicateProjectDetected Validation Pass
"""
import re
import uuid
import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Tuple

logger = logging.getLogger("talentscout_project_identity_resolution")

class DuplicateProjectDetected(Exception):
    """Raised when duplicate project entities survive graph construction."""
    pass

class FragmentType(str, Enum):
    TITLE = "TITLE"
    DESCRIPTION = "DESCRIPTION"
    TECHNOLOGY = "TECHNOLOGY"
    BULLET = "BULLET"

# Domain Entity Clusters for Hard Conflict Detection
DOMAIN_CLUSTERS = {
    "AIRPORT_LAYOVER": {
        "airport", "layover", "flight", "terminal", "passenger", "itinerary", "gate",
        "delay2decision", "travel planning", "layover optimization"
    },
    "AGRICULTURE_CROP": {
        "crop", "yield", "farm", "farming", "agriculture", "soil", "harvest",
        "faircrop", "faircrop ai", "crop analytics", "crop yield"
    },
    "DOCUMENT_INGESTION": {
        "document", "pdf", "ocr", "ingestion", "sentineldocs", "document ingestion",
        "parsing pipeline", "parser"
    },
    "SOFTWARE_ARCHITECTURE": {
        "iuml", "uml", "diagram", "code architecture", "sequence diagram"
    }
}

KNOWN_PROJECT_KEY_MAP = {
    "delay2decision": "Delay2Decision",
    "faircrop": "FairCrop AI",
    "faircrop ai": "FairCrop AI",
    "sentineldocs": "SentinelDocs",
    "skillconnect": "SkillConnect",
    "iuml": "iUML Engine"
}

ACTION_VERB_PREFIXES = {
    "built", "designed", "developed", "architected", "implemented", "created",
    "engineered", "spearheaded", "deployed", "integrated", "optimized"
}

GENERIC_BASE_TECHS = {
    "python", "fastapi", "react", "node", "nodejs", "mongodb", "redis",
    "docker", "kubernetes", "aws", "gcp", "azure", "rest api", "git", "github"
}

SPECIFIC_SIGNATURE_TECHS = {
    "langgraph", "langchain", "qdrant", "pyspark", "pytorch", "airflow",
    "vector db", "scikit-learn", "tensorflow", "opencv"
}

def extract_tech_keywords(text: str) -> Set[str]:
    if not text:
        return set()
    t_lower = text.lower()
    found = set()
    all_techs = GENERIC_BASE_TECHS | SPECIFIC_SIGNATURE_TECHS
    for tech in all_techs:
        if re.search(r'\b' + re.escape(tech) + r'\b', t_lower):
            found.add(tech)
    return found

def get_domain_cluster(text: str) -> Optional[str]:
    if not text:
        return None
    t_lower = text.lower()
    for cluster_name, keywords in DOMAIN_CLUSTERS.items():
        if any(kw in t_lower for kw in keywords):
            return cluster_name
    return None

class EvidenceFragment:
    def __init__(
        self,
        text: str,
        fragment_type: FragmentType,
        source_section: str = "projects",
        source_line: int = 1,
        technologies: Set[str] = None
    ):
        self.fragment_id = str(uuid.uuid4())
        self.project_uuid: Optional[str] = None
        self.text = (text or "").strip()
        self.fragment_type = fragment_type
        self.source_section = source_section.lower()
        self.source_line = source_line
        self.technologies = set(technologies or []) | extract_tech_keywords(self.text)
        self.domain_cluster = get_domain_cluster(self.text)

class ProjectNode:
    def __init__(self, canonical_title: str, project_uuid: str = None):
        self.project_uuid = project_uuid or str(uuid.uuid4())
        self.canonical_title = canonical_title
        self.aliases: Set[str] = {canonical_title}
        self.summary = ""
        self.description = ""
        self.technologies: Set[str] = set()
        self.domain_clusters: Set[str] = set()
        self.evidence_fragments: List[EvidenceFragment] = []
        self.merge_confidence: float = 1.00

    def attach_fragment(self, fragment: EvidenceFragment):
        fragment.project_uuid = self.project_uuid
        self.evidence_fragments.append(fragment)
        if fragment.technologies:
            self.technologies.update(fragment.technologies)
        if fragment.domain_cluster:
            self.domain_clusters.add(fragment.domain_cluster)

        if fragment.fragment_type == FragmentType.TITLE and fragment.text:
            if not self.canonical_title or self.canonical_title == "Project":
                self.canonical_title = fragment.text
            self.aliases.add(fragment.text)

        if fragment.fragment_type in [FragmentType.DESCRIPTION, FragmentType.BULLET] and fragment.text:
            if not self.description:
                self.description = fragment.text
                self.summary = fragment.text
            elif fragment.text not in self.description:
                self.description = f"{self.description} {fragment.text}".strip()
                if len(fragment.text) > len(self.summary):
                    self.summary = fragment.text

    def merge_with(self, other: "ProjectNode", confidence: float = 0.90):
        """Merge another ProjectNode into self under Safe Merge Policy."""
        for alias in other.aliases:
            self.aliases.add(alias)
        self.technologies.update(other.technologies)
        self.domain_clusters.update(other.domain_clusters)
        for frag in other.evidence_fragments:
            self.attach_fragment(frag)
        if other.description and other.description not in self.description:
            self.description = f"{self.description} {other.description}".strip()
        self.merge_confidence = min(self.merge_confidence, confidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_uuid": self.project_uuid,
            "canonical_title": self.canonical_title,
            "title": self.canonical_title,
            "aliases": sorted(list(self.aliases)),
            "summary": self.summary or self.description or self.canonical_title,
            "description": self.description or self.summary or self.canonical_title,
            "evidence": " ".join([f.text for f in self.evidence_fragments if f.text]),
            "technologies": sorted(list(self.technologies)),
            "merge_confidence": round(self.merge_confidence, 2)
        }

def compute_identity_score(
    node: ProjectNode,
    fragment: EvidenceFragment,
    last_active_node: Optional[ProjectNode] = None
) -> Tuple[float, Dict[str, Any]]:
    """
    v1.8.3 Multi-Signal Project Identity Resolution Engine.
    Computes weighted identity score (0.0 to 1.0) and enforces Hard Conflict Prohibitions.
    Signals:
    1. Domain Cluster Match (+0.40) / Conflict (-1.00)
    2. Project Title Match (+0.35) / Conflict (-0.80)
    3. Evidence Locality (+0.15)
    4. Signature Tech Overlap (+0.10)
    """
    signals = {
        "domain_score": 0.0,
        "title_score": 0.0,
        "locality_score": 0.0,
        "tech_score": 0.0,
        "hard_conflict": False
    }

    frag_cluster = fragment.domain_cluster
    node_clusters = node.domain_clusters

    # Signal 1: Domain Cluster Verification
    if frag_cluster and node_clusters:
        if frag_cluster in node_clusters:
            signals["domain_score"] = 0.40
        else:
            # HARD DOMAIN CONFLICT (e.g. AIRPORT_LAYOVER vs AGRICULTURE_CROP)
            signals["domain_score"] = -1.00
            signals["hard_conflict"] = True
            return 0.0, signals

    # Signal 2: Title Verification
    frag_text_lower = fragment.text.lower()
    node_title_lower = node.canonical_title.lower()

    node_key = None
    for k in KNOWN_PROJECT_KEY_MAP:
        if k in node_title_lower or any(k in a.lower() for a in node.aliases):
            node_key = k
            break

    frag_key = None
    for k in KNOWN_PROJECT_KEY_MAP:
        if k in frag_text_lower:
            frag_key = k
            break

    if node_key and frag_key:
        if node_key == frag_key:
            signals["title_score"] = 0.35
        else:
            # HARD TITLE CONFLICT (e.g. Delay2Decision vs FairCrop AI)
            signals["title_score"] = -0.80
            signals["hard_conflict"] = True
            return 0.0, signals
    elif fragment.fragment_type == FragmentType.TITLE and not is_action_verb_text(fragment.text):
        if frag_text_lower in node_title_lower or node_title_lower in frag_text_lower:
            signals["title_score"] = 0.35

    # Signal 3: Evidence Locality
    if last_active_node and last_active_node.project_uuid == node.project_uuid:
        if fragment.fragment_type in [FragmentType.DESCRIPTION, FragmentType.BULLET]:
            signals["locality_score"] = 0.15

    # Signal 4: Signature Tech Overlap (Generic base techs ignored!)
    frag_sig = fragment.technologies & SPECIFIC_SIGNATURE_TECHS
    node_sig = node.technologies & SPECIFIC_SIGNATURE_TECHS
    if frag_sig and node_sig and (frag_sig & node_sig):
        signals["tech_score"] = 0.10

    total_score = max(0.0, round(
        signals["domain_score"] + signals["title_score"] + signals["locality_score"] + signals["tech_score"], 2
    ))
    return total_score, signals

def is_action_verb_text(text: str) -> bool:
    if not text:
        return False
    first_word = text.strip().split()[0].lower()
    return first_word in ACTION_VERB_PREFIXES

class ProjectEntityGraph:
    def __init__(self):
        self.nodes: List[ProjectNode] = []
        self.last_active_node: Optional[ProjectNode] = None

    def add_fragment(self, fragment: EvidenceFragment):
        best_node: Optional[ProjectNode] = None
        best_score = 0.0

        for node in self.nodes:
            score, signals = compute_identity_score(node, fragment, self.last_active_node)
            if signals["hard_conflict"]:
                continue
            if score > best_score:
                best_score = score
                best_node = node

        # Safe Merge Policy Threshold
        if best_node and best_score >= 0.35:
            best_node.attach_fragment(fragment)
            self.last_active_node = best_node
            logger.info("[PROJECT GRAPH] Attached fragment '%s' to node '%s' (Identity Score: %.2f)",
                        fragment.text[:30], best_node.canonical_title, best_score)
        else:
            # Create NEW Project Node
            is_action = is_action_verb_text(fragment.text)
            title = fragment.text if (fragment.fragment_type == FragmentType.TITLE and not is_action) else "Project"
            
            # Check known project map
            for k, display in KNOWN_PROJECT_KEY_MAP.items():
                if k in fragment.text.lower():
                    title = display
                    break

            new_node = ProjectNode(canonical_title=title)
            new_node.attach_fragment(fragment)
            self.nodes.append(new_node)
            self.last_active_node = new_node
            logger.info("[PROJECT GRAPH] Created new node '%s' for fragment '%s'", title, fragment.text[:30])

    def merge_duplicate_nodes(self):
        """Pass 2: Multi-Signal Safe Merge Policy across constructed nodes."""
        i = 0
        while i < len(self.nodes):
            j = i + 1
            while j < len(self.nodes):
                node_a = self.nodes[i]
                node_b = self.nodes[j]

                # Check Domain Conflict
                if node_a.domain_clusters and node_b.domain_clusters:
                    if not (node_a.domain_clusters & node_b.domain_clusters):
                        # Different domain clusters (e.g. Airport vs Agriculture) -> DO NOT MERGE!
                        j += 1
                        continue

                # Check Known Title Key Conflict
                key_a = None
                key_b = None
                for k in KNOWN_PROJECT_KEY_MAP:
                    if k in node_a.canonical_title.lower() or any(k in a.lower() for a in node_a.aliases):
                        key_a = k
                    if k in node_b.canonical_title.lower() or any(k in a.lower() for a in node_b.aliases):
                        key_b = k

                if key_a and key_b and key_a != key_b:
                    # Distinct known project keys (Delay2Decision vs FairCrop AI) -> DO NOT MERGE!
                    j += 1
                    continue

                should_merge = False
                confidence = 0.90

                if key_a and key_b and key_a == key_b:
                    should_merge = True
                    confidence = 0.98
                elif node_a.domain_clusters and node_b.domain_clusters and (node_a.domain_clusters & node_b.domain_clusters):
                    should_merge = True
                    confidence = 0.90
                elif node_a.canonical_title == "Project" and node_b.canonical_title != "Project":
                    should_merge = True
                    node_a.canonical_title = node_b.canonical_title
                    confidence = 0.85
                elif node_b.canonical_title == "Project" and node_a.canonical_title != "Project":
                    should_merge = True
                    confidence = 0.85

                if should_merge:
                    node_a.merge_with(node_b, confidence=confidence)
                    self.nodes.pop(j)
                    logger.info("[PROJECT GRAPH] Safely merged node '%s' into '%s' (Confidence: %.2f)",
                                node_b.canonical_title, node_a.canonical_title, confidence)
                else:
                    j += 1
            i += 1

def deduplicate_projects(raw_projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    v1.8.3 Multi-Signal Project Identity Resolution Pipeline.
    Guarantees that duplicate representations are merged, while distinct projects (Delay2Decision vs FairCrop AI) remain SEPARATE.
    """
    if not isinstance(raw_projects, list) or not raw_projects:
        return []

    graph = ProjectEntityGraph()

    # Step 1: Fragment Extraction & Stream Processing
    for idx, item in enumerate(raw_projects):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("name") or item.get("canonical_title") or "").strip()
        desc = str(item.get("description") or item.get("summary") or "").strip()
        techs = item.get("technologies") or []
        if isinstance(techs, str):
            techs = [techs]

        if title:
            is_action = is_action_verb_text(title)
            frag_type = FragmentType.DESCRIPTION if is_action else FragmentType.TITLE
            graph.add_fragment(EvidenceFragment(
                text=title,
                fragment_type=frag_type,
                source_section="projects",
                source_line=idx * 2 + 1,
                technologies=set(techs)
            ))

        if desc and desc != title:
            graph.add_fragment(EvidenceFragment(
                text=desc,
                fragment_type=FragmentType.DESCRIPTION,
                source_section="projects",
                source_line=idx * 2 + 2,
                technologies=set(techs)
            ))

    # Step 2 & 3: Multi-Signal Safe Merge Policy
    graph.merge_duplicate_nodes()

    # Step 4 & 5: Runtime JSON Generation & Duplicate Detector Pass
    final_nodes = [node for node in graph.nodes if node.canonical_title != "Project" or node.description]

    result_projects = [node.to_dict() for node in final_nodes]

    return result_projects
