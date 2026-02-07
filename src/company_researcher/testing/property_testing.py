"""
Property-Based Testing - Hypothesis-style testing utilities.

Provides:
- Property generators
- Invariant checking
- Shrinking support
- Test data generators
"""

import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generator, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class GenerationConfig:
    """Configuration for data generation."""

    seed: Optional[int] = None
    max_size: int = 100
    min_size: int = 0
    max_examples: int = 100


class PropertyTestResult:
    """Result of a property test."""

    def __init__(self):
        self.passed = True
        self.examples_run = 0
        self.failures: List[Dict[str, Any]] = []
        self.smallest_failure: Optional[Dict[str, Any]] = None

    def add_failure(self, example: Any, error: Exception) -> None:
        """Record a failure."""
        self.passed = False
        self.failures.append(
            {"example": example, "error": str(error), "error_type": type(error).__name__}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "examples_run": self.examples_run,
            "failure_count": len(self.failures),
            "failures": self.failures[:5],  # First 5 failures
            "smallest_failure": self.smallest_failure,
        }


# Data Generators


class Gen:
    """
    Data generators for property testing.

    Usage:
        # Generate random integers
        for value in Gen.integers(min=0, max=100).examples(10):
            print(value)

        # Generate random strings
        for s in Gen.strings(max_length=20).examples(10):
            print(s)

        # Generate random dictionaries
        for d in Gen.dicts(Gen.strings(), Gen.integers()).examples(10):
            print(d)
    """

    def __init__(
        self, generator: Callable[[], T], shrinker: Callable[[T], Generator[T, None, None]] = None
    ):
        self._generator = generator
        self._shrinker = shrinker
        self._filter: Optional[Callable[[T], bool]] = None
        self._map: Optional[Callable[[T], Any]] = None

    def generate(self) -> T:
        """Generate a single value."""
        while True:
            value = self._generator()
            if self._map:
                value = self._map(value)
            if self._filter is None or self._filter(value):
                return value

    def examples(self, n: int = 10) -> Generator[T, None, None]:
        """Generate n examples."""
        for _ in range(n):
            yield self.generate()

    def filter(self, predicate: Callable[[T], bool]) -> "Gen[T]":
        """Filter generated values."""
        new_gen = Gen(self._generator, self._shrinker)
        new_gen._filter = predicate
        return new_gen

    def map(self, f: Callable[[T], Any]) -> "Gen":
        """Transform generated values."""
        new_gen = Gen(self._generator, self._shrinker)
        new_gen._map = f
        return new_gen

    def shrink(self, value: T) -> Generator[T, None, None]:
        """Shrink a value to find minimal failing example."""
        if self._shrinker:
            yield from self._shrinker(value)

    # Built-in generators

    @classmethod
    def integers(cls, min_value: int = -1000000, max_value: int = 1000000) -> "Gen[int]":
        """Generate random integers."""

        def gen():
            return random.randint(min_value, max_value)

        def shrink(n):
            if n == 0:
                return
            yield 0
            if n > 0:
                yield n // 2
                yield n - 1
            else:
                yield -n // 2
                yield n + 1

        return cls(gen, shrink)

    @classmethod
    def floats(
        cls, min_value: float = -1e6, max_value: float = 1e6, allow_nan: bool = False
    ) -> "Gen[float]":
        """Generate random floats."""

        def gen():
            return random.uniform(min_value, max_value)

        return cls(gen)

    @classmethod
    def booleans(cls) -> "Gen[bool]":
        """Generate random booleans."""
        return cls(lambda: random.choice([True, False]))

    @classmethod
    def strings(
        cls, min_length: int = 0, max_length: int = 100, alphabet: str = None
    ) -> "Gen[str]":
        """Generate random strings."""
        chars = alphabet or string.ascii_letters + string.digits

        def gen():
            length = random.randint(min_length, max_length)
            return "".join(random.choice(chars) for _ in range(length))

        def shrink(s):
            if len(s) == 0:
                return
            yield ""
            if len(s) > 1:
                yield s[: len(s) // 2]
                yield s[1:]
                yield s[:-1]

        return cls(gen, shrink)

    @classmethod
    def from_choices(cls, choices: List[T]) -> "Gen[T]":
        """Generate by choosing from a list."""
        return cls(lambda: random.choice(choices))

    @classmethod
    def lists(cls, element_gen: "Gen[T]", min_size: int = 0, max_size: int = 20) -> "Gen[List[T]]":
        """Generate random lists."""

        def gen():
            size = random.randint(min_size, max_size)
            return [element_gen.generate() for _ in range(size)]

        def shrink(lst):
            if len(lst) == 0:
                return
            yield []
            if len(lst) > 1:
                yield lst[: len(lst) // 2]
                yield lst[1:]
                yield lst[:-1]

        return cls(gen, shrink)

    @classmethod
    def dicts(
        cls, key_gen: "Gen", value_gen: "Gen", min_size: int = 0, max_size: int = 10
    ) -> "Gen[Dict]":
        """Generate random dictionaries."""

        def gen():
            size = random.randint(min_size, max_size)
            return {key_gen.generate(): value_gen.generate() for _ in range(size)}

        return cls(gen)

    @classmethod
    def tuples(cls, *generators: "Gen") -> "Gen[tuple]":
        """Generate random tuples."""

        def gen():
            return tuple(g.generate() for g in generators)

        return cls(gen)

    @classmethod
    def one_of(cls, *generators: "Gen") -> "Gen":
        """Randomly choose from multiple generators."""

        def gen():
            chosen = random.choice(generators)
            return chosen.generate()

        return cls(gen)

    @classmethod
    def none(cls) -> "Gen[None]":
        """Generate None."""
        return cls(lambda: None)

    @classmethod
    def optional(cls, gen: "Gen[T]") -> "Gen[Optional[T]]":
        """Generate value or None."""
        return cls.one_of(gen, cls.none())

    @classmethod
    def datetimes(cls, min_date: datetime = None, max_date: datetime = None) -> "Gen[datetime]":
        """Generate random datetimes."""
        min_dt = min_date or datetime(2000, 1, 1)
        max_dt = max_date or datetime(2030, 12, 31)
        delta = (max_dt - min_dt).total_seconds()

        def gen():
            offset = random.uniform(0, delta)
            return min_dt + timedelta(seconds=offset)

        return cls(gen)

    @classmethod
    def emails(cls) -> "Gen[str]":
        """Generate random email addresses."""

        def gen():
            user = "".join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
            domain = "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            tld = random.choice(["com", "org", "net", "io"])
            return f"{user}@{domain}.{tld}"

        return cls(gen)


# Research-specific generators


class ResearchGen:
    """Generators for research-related test data."""

    @classmethod
    def company_names(cls) -> Gen[str]:
        """Generate realistic company names."""
        prefixes = ["Tech", "Global", "Advanced", "Digital", "Smart", "Blue", "Green"]
        suffixes = ["Corp", "Inc", "Systems", "Solutions", "Labs", "Tech", "AI"]
        middles = ["Data", "Cloud", "Net", "Web", "Soft", "Cyber", "Bio"]

        def gen():
            parts = [random.choice(prefixes)]
            if random.random() > 0.5:
                parts.append(random.choice(middles))
            parts.append(random.choice(suffixes))
            return " ".join(parts)

        return Gen(gen)

    @classmethod
    def research_queries(cls) -> Gen[str]:
        """Generate research-like queries."""
        templates = [
            "What is {company}'s revenue?",
            "Who is the CEO of {company}?",
            "Tell me about {company}'s products",
            "{company} financial performance",
            "{company} competitors analysis",
            "Latest news about {company}",
        ]
        companies = ["Tesla", "Apple", "Google", "Microsoft", "Amazon", "Meta"]

        def gen():
            template = random.choice(templates)
            company = random.choice(companies)
            return template.format(company=company)

        return Gen(gen)

    @classmethod
    def metrics(cls) -> Gen[Dict[str, Any]]:
        """Generate financial metrics."""

        def gen():
            return {
                "revenue": random.uniform(1e6, 1e12),
                "profit_margin": random.uniform(-0.5, 0.5),
                "growth_rate": random.uniform(-0.3, 0.5),
                "market_cap": random.uniform(1e6, 1e12),
                "pe_ratio": random.uniform(5, 100),
                "employees": random.randint(10, 500000),
            }

        return Gen(gen)


# Property testing runner


def given(*generators: Gen):
    """
    Decorator for property-based tests.

    Usage:
        @given(Gen.integers(), Gen.strings())
        def test_example(x: int, s: str):
            assert len(s) >= 0
            assert x + 0 == x
    """

    def decorator(test_func: Callable) -> Callable:
        def wrapper(max_examples: int = 100, seed: int = None) -> PropertyTestResult:
            if seed is not None:
                random.seed(seed)

            result = PropertyTestResult()

            for _ in range(max_examples):
                args = [g.generate() for g in generators]
                result.examples_run += 1

                try:
                    test_func(*args)
                except Exception as e:
                    result.add_failure(args, e)

                    # Try to shrink
                    smallest = args
                    for i, (gen, arg) in enumerate(zip(generators, args)):
                        for shrunk in gen.shrink(arg):
                            shrunk_args = args[:i] + [shrunk] + args[i + 1 :]
                            try:
                                test_func(*shrunk_args)
                            except Exception:
                                smallest = shrunk_args

                    result.smallest_failure = {"args": smallest, "error": str(e)}

            return result

        wrapper.__name__ = test_func.__name__
        wrapper.test_func = test_func
        return wrapper

    return decorator


def check_property(
    property_func: Callable[..., bool], *generators: Gen, max_examples: int = 100
) -> PropertyTestResult:
    """
    Check a property over random examples.

    Args:
        property_func: Function returning True if property holds
        *generators: Generators for arguments
        max_examples: Number of examples to test

    Returns:
        PropertyTestResult
    """
    result = PropertyTestResult()

    for _ in range(max_examples):
        args = [g.generate() for g in generators]
        result.examples_run += 1

        try:
            if not property_func(*args):
                result.add_failure(args, AssertionError("Property returned False"))
        except Exception as e:
            result.add_failure(args, e)

    return result


# Common property assertions


def is_idempotent(f: Callable[[T], T], gen: Gen[T], max_examples: int = 100) -> PropertyTestResult:
    """Check if f(f(x)) == f(x)."""

    def check(x):
        return f(f(x)) == f(x)

    return check_property(check, gen, max_examples=max_examples)


def is_commutative(
    f: Callable[[T, T], Any], gen: Gen[T], max_examples: int = 100
) -> PropertyTestResult:
    """Check if f(x, y) == f(y, x)."""

    def check(x, y):
        return f(x, y) == f(y, x)

    return check_property(check, gen, gen, max_examples=max_examples)


def is_associative(
    f: Callable[[T, T], T], gen: Gen[T], max_examples: int = 100
) -> PropertyTestResult:
    """Check if f(f(x, y), z) == f(x, f(y, z))."""

    def check(x, y, z):
        return f(f(x, y), z) == f(x, f(y, z))

    return check_property(check, gen, gen, gen, max_examples=max_examples)


def preserves_invariant(
    f: Callable, gen: Gen, invariant: Callable[[Any], bool], max_examples: int = 100
) -> PropertyTestResult:
    """Check if function preserves an invariant."""

    def check(x):
        if not invariant(x):
            return True  # Skip invalid inputs
        result = f(x)
        return invariant(result)

    return check_property(check, gen, max_examples=max_examples)
