"""
Evaluation Dataset - Test data generation and management.

Provides:
- Dataset creation for research evaluations
- Test case management
- Dataset persistence
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EvalCase:
    """Single evaluation test case."""
    id: str
    name: str
    input: Dict[str, Any]
    expected_output: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Optional fields for specific test types
    company_name: Optional[str] = None
    expected_facts: List[str] = field(default_factory=list)
    expected_sources: List[str] = field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "input": self.input,
            "expected_output": self.expected_output,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "company_name": self.company_name,
            "expected_facts": self.expected_facts,
            "expected_sources": self.expected_sources,
            "difficulty": self.difficulty
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvalCase":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.utcnow()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            input=data.get("input", {}),
            expected_output=data.get("expected_output", {}),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            company_name=data.get("company_name"),
            expected_facts=data.get("expected_facts", []),
            expected_sources=data.get("expected_sources", []),
            difficulty=data.get("difficulty", "medium")
        )


@dataclass
class EvalResult:
    """Result of evaluating a single test case."""
    case_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    actual_output: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "score": self.score,
            "actual_output": self.actual_output,
            "errors": self.errors,
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat()
        }


class EvalDataset:
    """
    Evaluation dataset for testing research workflows.

    Usage:
        dataset = EvalDataset("research-eval-v1")

        # Add test cases
        dataset.add_case(EvalCase(
            id="test-1",
            name="Tesla Research",
            input={"company_name": "Tesla"},
            expected_output={"has_financials": True}
        ))

        # Save dataset
        dataset.save("datasets/research-eval.json")

        # Load dataset
        loaded = EvalDataset.load("datasets/research-eval.json")
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.cases: List[EvalCase] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.version = "1.0"

    def add_case(self, case: EvalCase) -> None:
        """Add a test case to the dataset."""
        self.cases.append(case)

    def add_cases(self, cases: List[EvalCase]) -> None:
        """Add multiple test cases."""
        self.cases.extend(cases)

    def get_case(self, case_id: str) -> Optional[EvalCase]:
        """Get case by ID."""
        for case in self.cases:
            if case.id == case_id:
                return case
        return None

    def get_cases_by_tag(self, tag: str) -> List[EvalCase]:
        """Get all cases with a specific tag."""
        return [c for c in self.cases if tag in c.tags]

    def get_cases_by_difficulty(self, difficulty: str) -> List[EvalCase]:
        """Get all cases with a specific difficulty."""
        return [c for c in self.cases if c.difficulty == difficulty]

    def remove_case(self, case_id: str) -> bool:
        """Remove a case by ID."""
        for i, case in enumerate(self.cases):
            if case.id == case_id:
                del self.cases[i]
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataset to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "cases": [c.to_dict() for c in self.cases]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvalDataset":
        """Create dataset from dictionary."""
        dataset = cls(
            name=data.get("name", "unnamed"),
            description=data.get("description", "")
        )
        dataset.version = data.get("version", "1.0")
        dataset.metadata = data.get("metadata", {})

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            dataset.created_at = datetime.fromisoformat(created_at)

        for case_data in data.get("cases", []):
            dataset.add_case(EvalCase.from_dict(case_data))

        return dataset

    def save(self, path: str) -> None:
        """Save dataset to JSON file."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    @classmethod
    def load(cls, path: str) -> "EvalDataset":
        """Load dataset from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __len__(self) -> int:
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)


def create_research_dataset(
    name: str = "research-eval",
    include_companies: Optional[List[str]] = None
) -> EvalDataset:
    """
    Create a standard research evaluation dataset.

    Args:
        name: Dataset name
        include_companies: List of companies to include

    Returns:
        EvalDataset with pre-defined test cases
    """
    companies = include_companies or [
        "Apple", "Tesla", "Microsoft", "Google", "Amazon"
    ]

    dataset = EvalDataset(
        name=name,
        description="Standard research evaluation dataset"
    )

    for company in companies:
        # Basic research test
        dataset.add_case(EvalCase(
            id=f"basic-{company.lower()}",
            name=f"Basic {company} Research",
            input={"company_name": company, "depth": "basic"},
            expected_output={"has_overview": True},
            tags=["basic", "company-research"],
            company_name=company,
            difficulty="easy"
        ))

        # Comprehensive research test
        dataset.add_case(EvalCase(
            id=f"comprehensive-{company.lower()}",
            name=f"Comprehensive {company} Research",
            input={"company_name": company, "depth": "comprehensive"},
            expected_output={
                "has_overview": True,
                "has_financials": True,
                "has_competitors": True
            },
            tags=["comprehensive", "company-research"],
            company_name=company,
            difficulty="hard"
        ))

    return dataset


def load_dataset(path: str) -> EvalDataset:
    """Load dataset from file."""
    return EvalDataset.load(path)


def save_dataset(dataset: EvalDataset, path: str) -> None:
    """Save dataset to file."""
    dataset.save(path)
