"""
Source Attribution Tracking System

Tracks the provenance of every fact with:
- Full evidence chains from source to extracted fact
- Citation generation for reports
- Source quality scoring
- Audit trail for compliance

Usage:
    from company_researcher.quality.source_attribution import (
        SourceTracker,
        EvidenceChain,
        Citation
    )

    tracker = SourceTracker()
    tracker.add_source(url, content, metadata)
    tracker.attribute_fact(fact, source_id, evidence)
    citations = tracker.generate_citations()
"""

import hashlib
import json
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of evidence supporting a fact."""
    DIRECT_QUOTE = "direct_quote"       # Exact text from source
    PARAPHRASE = "paraphrase"           # Reworded information
    INFERENCE = "inference"             # Derived from multiple facts
    CALCULATION = "calculation"         # Computed from source data
    AGGREGATION = "aggregation"         # Combined from multiple sources


class CitationStyle(Enum):
    """Citation formatting styles."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    SIMPLE = "simple"
    MARKDOWN = "markdown"


@dataclass
class SourceDocument:
    """A source document with full metadata."""
    id: str
    url: str
    title: str
    content: str
    content_hash: str
    domain: str
    retrieved_at: datetime
    publication_date: Optional[datetime] = None
    author: Optional[str] = None
    organization: Optional[str] = None
    document_type: str = "web_page"
    language: str = "en"
    word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, url: str, title: str, content: str, **kwargs) -> "SourceDocument":
        """Create a source document with auto-generated ID and hash."""
        from urllib.parse import urlparse

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        doc_id = hashlib.md5(f"{url}:{content_hash}".encode()).hexdigest()[:12]
        domain = urlparse(url).netloc.replace("www.", "")

        return cls(
            id=doc_id,
            url=url,
            title=title,
            content=content,
            content_hash=content_hash,
            domain=domain,
            retrieved_at=datetime.now(),
            word_count=len(content.split()),
            **kwargs
        )


@dataclass
class Evidence:
    """Evidence supporting a fact."""
    id: str
    source_id: str
    evidence_type: EvidenceType
    text: str                          # The actual evidence text
    location: Optional[str] = None     # Where in source (paragraph, section)
    confidence: float = 0.8
    extracted_at: datetime = field(default_factory=datetime.now)
    extraction_method: str = "llm"


@dataclass
class EvidenceChain:
    """Complete chain of evidence for a fact."""
    fact_id: str
    fact_text: str
    fact_value: Any
    evidences: List[Evidence]
    source_documents: List[SourceDocument]
    chain_confidence: float
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def primary_source(self) -> Optional[SourceDocument]:
        """Get the most authoritative source in the chain."""
        if not self.source_documents:
            return None
        # Return source with highest tier evidence
        direct_sources = [
            doc for doc, ev in zip(self.source_documents, self.evidences)
            if ev.evidence_type == EvidenceType.DIRECT_QUOTE
        ]
        return direct_sources[0] if direct_sources else self.source_documents[0]

    @property
    def source_count(self) -> int:
        """Number of unique sources."""
        return len(set(doc.id for doc in self.source_documents))


@dataclass
class Citation:
    """A formatted citation."""
    source: SourceDocument
    style: CitationStyle
    formatted: str
    inline: str              # Short inline reference
    footnote: str            # Footnote format


class SourceTracker:
    """
    Tracks sources and attributions throughout the research process.

    Maintains a complete audit trail of where every fact came from.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sources: Dict[str, SourceDocument] = {}
        self.evidences: Dict[str, List[Evidence]] = defaultdict(list)
        self.fact_chains: Dict[str, EvidenceChain] = {}
        self.source_usage: Dict[str, int] = defaultdict(int)

    def add_source(
        self,
        url: str,
        title: str,
        content: str,
        publication_date: Optional[datetime] = None,
        author: Optional[str] = None,
        **metadata
    ) -> str:
        """
        Add a source document to the tracker.

        Returns:
            Source ID for attribution
        """
        doc = SourceDocument.create(
            url=url,
            title=title,
            content=content,
            publication_date=publication_date,
            author=author,
            metadata=metadata
        )

        self.sources[doc.id] = doc
        logger.info(f"Added source: {doc.id} ({doc.domain})")

        return doc.id

    def add_source_from_search_result(self, result: Dict[str, Any]) -> str:
        """Add source from a search API result."""
        return self.add_source(
            url=result.get("url", ""),
            title=result.get("title", "Untitled"),
            content=result.get("content", result.get("snippet", "")),
            score=result.get("score"),
            search_query=result.get("query")
        )

    def attribute_fact(
        self,
        fact_id: str,
        fact_text: str,
        fact_value: Any,
        source_id: str,
        evidence_text: str,
        evidence_type: EvidenceType = EvidenceType.PARAPHRASE,
        confidence: float = 0.8,
        location: Optional[str] = None
    ) -> EvidenceChain:
        """
        Attribute a fact to a source with evidence.

        Args:
            fact_id: Unique identifier for the fact
            fact_text: Human-readable fact description
            fact_value: The actual value (number, string, etc.)
            source_id: ID of the source document
            evidence_text: The text that supports this fact
            evidence_type: Type of evidence
            confidence: Confidence in the attribution
            location: Where in the source the evidence was found

        Returns:
            EvidenceChain for this fact
        """
        if source_id not in self.sources:
            logger.warning(f"Source {source_id} not found, creating placeholder")
            self.sources[source_id] = SourceDocument(
                id=source_id,
                url="unknown",
                title="Unknown Source",
                content="",
                content_hash="",
                domain="unknown",
                retrieved_at=datetime.now()
            )

        # Create evidence
        evidence = Evidence(
            id=f"{fact_id}_{source_id}_{len(self.evidences[fact_id])}",
            source_id=source_id,
            evidence_type=evidence_type,
            text=evidence_text,
            location=location,
            confidence=confidence
        )

        self.evidences[fact_id].append(evidence)
        self.source_usage[source_id] += 1

        # Create or update evidence chain
        chain = self._build_evidence_chain(fact_id, fact_text, fact_value)
        self.fact_chains[fact_id] = chain

        return chain

    def add_corroborating_evidence(
        self,
        fact_id: str,
        source_id: str,
        evidence_text: str,
        evidence_type: EvidenceType = EvidenceType.PARAPHRASE,
        confidence: float = 0.8
    ):
        """Add additional evidence to an existing fact."""
        if fact_id not in self.fact_chains:
            logger.warning(f"Fact {fact_id} not found, cannot add corroborating evidence")
            return

        evidence = Evidence(
            id=f"{fact_id}_{source_id}_{len(self.evidences[fact_id])}",
            source_id=source_id,
            evidence_type=evidence_type,
            text=evidence_text,
            confidence=confidence
        )

        self.evidences[fact_id].append(evidence)
        self.source_usage[source_id] += 1

        # Rebuild chain with new evidence
        chain = self.fact_chains[fact_id]
        chain = self._build_evidence_chain(
            fact_id,
            chain.fact_text,
            chain.fact_value
        )
        self.fact_chains[fact_id] = chain

    def _build_evidence_chain(
        self,
        fact_id: str,
        fact_text: str,
        fact_value: Any
    ) -> EvidenceChain:
        """Build complete evidence chain for a fact."""
        evidences = self.evidences.get(fact_id, [])
        source_docs = []

        for ev in evidences:
            if ev.source_id in self.sources:
                source_docs.append(self.sources[ev.source_id])

        # Calculate chain confidence
        if evidences:
            # Higher confidence with more corroborating sources
            base_confidence = sum(e.confidence for e in evidences) / len(evidences)
            source_bonus = min(len(set(e.source_id for e in evidences)) * 0.05, 0.2)
            direct_quote_bonus = 0.1 if any(
                e.evidence_type == EvidenceType.DIRECT_QUOTE for e in evidences
            ) else 0
            chain_confidence = min(base_confidence + source_bonus + direct_quote_bonus, 0.99)
        else:
            chain_confidence = 0.0

        return EvidenceChain(
            fact_id=fact_id,
            fact_text=fact_text,
            fact_value=fact_value,
            evidences=evidences,
            source_documents=source_docs,
            chain_confidence=chain_confidence
        )

    def get_evidence_chain(self, fact_id: str) -> Optional[EvidenceChain]:
        """Get evidence chain for a fact."""
        return self.fact_chains.get(fact_id)

    def generate_citation(
        self,
        source_id: str,
        style: CitationStyle = CitationStyle.SIMPLE
    ) -> Citation:
        """Generate a formatted citation for a source."""
        source = self.sources.get(source_id)
        if not source:
            return Citation(
                source=SourceDocument(
                    id=source_id, url="", title="Unknown", content="",
                    content_hash="", domain="", retrieved_at=datetime.now()
                ),
                style=style,
                formatted="[Source not found]",
                inline="[?]",
                footnote="Source not found"
            )

        if style == CitationStyle.APA:
            formatted = self._format_apa(source)
        elif style == CitationStyle.MLA:
            formatted = self._format_mla(source)
        elif style == CitationStyle.CHICAGO:
            formatted = self._format_chicago(source)
        elif style == CitationStyle.MARKDOWN:
            formatted = self._format_markdown(source)
        else:
            formatted = self._format_simple(source)

        # Generate inline reference
        inline = f"[{source.domain}]"
        if source.author:
            inline = f"[{source.author.split()[0]}]"

        # Generate footnote
        footnote = f"{source.title}. {source.url}"
        if source.publication_date:
            footnote = f"{source.title} ({source.publication_date.strftime('%Y')}). {source.url}"

        return Citation(
            source=source,
            style=style,
            formatted=formatted,
            inline=inline,
            footnote=footnote
        )

    def _format_apa(self, source: SourceDocument) -> str:
        """Format citation in APA style."""
        author = source.author or source.organization or source.domain
        year = source.publication_date.year if source.publication_date else "n.d."
        title = source.title

        return f"{author}. ({year}). {title}. Retrieved from {source.url}"

    def _format_mla(self, source: SourceDocument) -> str:
        """Format citation in MLA style."""
        author = source.author or source.domain
        title = f'"{source.title}"'
        site = source.organization or source.domain
        date = source.publication_date.strftime("%d %b. %Y") if source.publication_date else ""
        access_date = source.retrieved_at.strftime("%d %b. %Y")

        return f'{author}. {title}. {site}, {date}. Web. {access_date}.'

    def _format_chicago(self, source: SourceDocument) -> str:
        """Format citation in Chicago style."""
        author = source.author or source.domain
        title = f'"{source.title}"'
        date = source.publication_date.strftime("%B %d, %Y") if source.publication_date else ""
        access_date = source.retrieved_at.strftime("%B %d, %Y")

        return f'{author}. {title}. {date}. Accessed {access_date}. {source.url}.'

    def _format_markdown(self, source: SourceDocument) -> str:
        """Format citation in Markdown link style."""
        return f'[{source.title}]({source.url})'

    def _format_simple(self, source: SourceDocument) -> str:
        """Format simple citation."""
        date_str = ""
        if source.publication_date:
            date_str = f" ({source.publication_date.strftime('%Y-%m-%d')})"
        return f"{source.title}{date_str} - {source.url}"

    def generate_all_citations(
        self,
        style: CitationStyle = CitationStyle.SIMPLE,
        sort_by: str = "usage"
    ) -> List[Citation]:
        """Generate citations for all sources used."""
        if sort_by == "usage":
            sorted_ids = sorted(
                self.source_usage.keys(),
                key=lambda x: self.source_usage[x],
                reverse=True
            )
        elif sort_by == "domain":
            sorted_ids = sorted(
                self.sources.keys(),
                key=lambda x: self.sources[x].domain
            )
        else:
            sorted_ids = list(self.sources.keys())

        return [self.generate_citation(sid, style) for sid in sorted_ids]

    def get_fact_with_citations(
        self,
        fact_id: str,
        style: CitationStyle = CitationStyle.MARKDOWN
    ) -> Tuple[str, List[str]]:
        """Get fact text with inline citations."""
        chain = self.fact_chains.get(fact_id)
        if not chain:
            return "", []

        citations = []
        for ev in chain.evidences:
            citation = self.generate_citation(ev.source_id, style)
            citations.append(citation.formatted)

        # Format fact with inline citations
        cite_refs = ", ".join(f"[{i+1}]" for i in range(len(citations)))
        fact_with_cite = f"{chain.fact_text} {cite_refs}"

        return fact_with_cite, citations

    def generate_source_summary(self) -> Dict[str, Any]:
        """Generate summary of all sources used."""
        summary = {
            "total_sources": len(self.sources),
            "total_facts": len(self.fact_chains),
            "total_evidences": sum(len(evs) for evs in self.evidences.values()),
            "by_domain": defaultdict(int),
            "by_evidence_type": defaultdict(int),
            "source_reliability": {},
            "most_cited": []
        }

        for source in self.sources.values():
            summary["by_domain"][source.domain] += 1

        for fact_id, evidences in self.evidences.items():
            for ev in evidences:
                summary["by_evidence_type"][ev.evidence_type.value] += 1

        # Most cited sources
        most_cited = sorted(
            self.source_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        summary["most_cited"] = [
            {
                "source_id": sid,
                "domain": self.sources[sid].domain if sid in self.sources else "unknown",
                "title": self.sources[sid].title if sid in self.sources else "Unknown",
                "citations": count
            }
            for sid, count in most_cited
        ]

        return summary

    def export_for_report(self) -> Dict[str, Any]:
        """Export attribution data for inclusion in reports."""
        return {
            "project_id": self.project_id,
            "generated_at": datetime.now().isoformat(),
            "summary": self.generate_source_summary(),
            "facts": [
                {
                    "id": chain.fact_id,
                    "text": chain.fact_text,
                    "value": chain.fact_value,
                    "confidence": chain.chain_confidence,
                    "source_count": chain.source_count,
                    "primary_source": chain.primary_source.url if chain.primary_source else None
                }
                for chain in self.fact_chains.values()
            ],
            "sources": [
                {
                    "id": source.id,
                    "url": source.url,
                    "title": source.title,
                    "domain": source.domain,
                    "citations": self.source_usage.get(source.id, 0)
                }
                for source in self.sources.values()
            ]
        }

    def to_json(self) -> str:
        """Export tracker data as JSON."""
        return json.dumps(self.export_for_report(), indent=2, default=str)


def create_tracker_for_research(company_name: str) -> SourceTracker:
    """Create a source tracker for a company research project."""
    project_id = f"{company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
    return SourceTracker(project_id=project_id)
