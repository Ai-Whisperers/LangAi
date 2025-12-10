"""
Hugging Face Inference API Client.

Free tier: Limited requests, rate-limited
Provides: ML model inference for NLP tasks

Documentation: https://huggingface.co/docs/api-inference
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    label: str
    score: float

    @classmethod
    def from_dict(cls, data: Dict) -> "SentimentResult":
        return cls(
            label=data.get("label", ""),
            score=data.get("score", 0.0)
        )


@dataclass
class EntityResult:
    """Named entity recognition result."""
    entity: str
    word: str
    score: float
    start: int
    end: int

    @classmethod
    def from_dict(cls, data: Dict) -> "EntityResult":
        return cls(
            entity=data.get("entity", data.get("entity_group", "")),
            word=data.get("word", ""),
            score=data.get("score", 0.0),
            start=data.get("start", 0),
            end=data.get("end", 0)
        )


@dataclass
class ClassificationResult:
    """Zero-shot classification result."""
    labels: List[str]
    scores: List[float]
    sequence: str

    @classmethod
    def from_dict(cls, data: Dict) -> "ClassificationResult":
        return cls(
            labels=data.get("labels", []),
            scores=data.get("scores", []),
            sequence=data.get("sequence", "")
        )


class HuggingFaceClient(BaseAPIClient):
    """
    Hugging Face Inference API Client.

    Free tier: Rate-limited, queue-based
    Pro: $9/mo (20x credits, priority)

    Features:
    - Sentiment analysis
    - Named entity recognition
    - Text summarization
    - Zero-shot classification
    - Text generation
    - Many more models available
    """

    BASE_URL = "https://api-inference.huggingface.co/models"

    # Default models for various tasks
    MODELS = {
        "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
        "ner": "dbmdz/bert-large-cased-finetuned-conll03-english",
        "summarization": "facebook/bart-large-cnn",
        "zero_shot": "facebook/bart-large-mnli",
        "text_generation": "gpt2",
        "financial_sentiment": "ProsusAI/finbert"
    }

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="HUGGINGFACE_API_KEY",
            cache_ttl=3600,
            rate_limit_calls=30,
            rate_limit_period=60.0
        )

    def _get_headers(self) -> Dict[str, str]:
        """Add authorization header."""
        headers = super()._get_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def _inference(
        self,
        model: str,
        inputs: Any,
        parameters: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> Any:
        """
        Make inference request to a model.

        Args:
            model: Model ID
            inputs: Input text or data
            parameters: Model-specific parameters
            options: Request options (wait_for_model, etc.)

        Returns:
            Model output
        """
        payload = {"inputs": inputs}
        if parameters:
            payload["parameters"] = parameters
        if options:
            payload["options"] = options

        # Use model-specific endpoint
        url = f"{self.BASE_URL}/{model}"

        return await self._request(
            url,
            method="POST",
            json_data=payload,
            use_cache=False  # Inference results shouldn't be cached
        )

    async def sentiment_analysis(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[SentimentResult]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze
            model: Model ID (defaults to DistilBERT SST-2)

        Returns:
            List of SentimentResult with POSITIVE/NEGATIVE scores
        """
        model = model or self.MODELS["sentiment"]
        result = await self._inference(
            model,
            text,
            options={"wait_for_model": True}
        )

        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                return [SentimentResult.from_dict(r) for r in result[0]]
            return [SentimentResult.from_dict(r) for r in result]
        return []

    async def financial_sentiment(
        self,
        text: str
    ) -> List[SentimentResult]:
        """
        Analyze financial sentiment using FinBERT.

        Args:
            text: Financial text to analyze

        Returns:
            List of SentimentResult (positive/negative/neutral)
        """
        return await self.sentiment_analysis(text, self.MODELS["financial_sentiment"])

    async def named_entity_recognition(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[EntityResult]:
        """
        Extract named entities from text.

        Args:
            text: Text to analyze
            model: Model ID (defaults to BERT CoNLL03)

        Returns:
            List of EntityResult with entity types:
            - PER (person)
            - ORG (organization)
            - LOC (location)
            - MISC (miscellaneous)
        """
        model = model or self.MODELS["ner"]
        result = await self._inference(
            model,
            text,
            options={"wait_for_model": True}
        )

        if isinstance(result, list):
            return [EntityResult.from_dict(r) for r in result]
        return []

    async def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 30,
        model: Optional[str] = None
    ) -> str:
        """
        Summarize long text.

        Args:
            text: Text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            model: Model ID (defaults to BART CNN)

        Returns:
            Summary text
        """
        model = model or self.MODELS["summarization"]
        result = await self._inference(
            model,
            text,
            parameters={
                "max_length": max_length,
                "min_length": min_length
            },
            options={"wait_for_model": True}
        )

        if isinstance(result, list) and len(result) > 0:
            return result[0].get("summary_text", "")
        return ""

    async def zero_shot_classification(
        self,
        text: str,
        labels: List[str],
        model: Optional[str] = None,
        multi_label: bool = False
    ) -> ClassificationResult:
        """
        Classify text into custom categories.

        Args:
            text: Text to classify
            labels: Candidate labels
            model: Model ID (defaults to BART MNLI)
            multi_label: Allow multiple labels

        Returns:
            ClassificationResult with labels and scores

        Example:
            labels = ["positive outlook", "negative outlook", "neutral"]
            result = await client.zero_shot_classification(
                "Company reported strong Q4 earnings",
                labels
            )
        """
        model = model or self.MODELS["zero_shot"]
        result = await self._inference(
            model,
            {
                "text": text,
                "candidate_labels": labels,
                "multi_label": multi_label
            },
            options={"wait_for_model": True}
        )

        if isinstance(result, dict):
            return ClassificationResult.from_dict(result)
        return ClassificationResult(labels=[], scores=[], sequence=text)

    async def analyze_company_news(
        self,
        articles: List[str],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze company news sentiment and categories.

        Args:
            articles: List of news article texts
            categories: Custom categories for classification

        Returns:
            Dict with sentiment breakdown and category scores
        """
        categories = categories or [
            "growth potential",
            "financial risk",
            "market opportunity",
            "competitive threat",
            "regulatory concern"
        ]

        results = {
            "sentiment": {"positive": 0, "negative": 0, "neutral": 0},
            "category_scores": {cat: [] for cat in categories},
            "entities": [],
            "article_count": len(articles)
        }

        for article in articles[:10]:  # Limit to avoid rate limits
            # Sentiment
            sentiment = await self.financial_sentiment(article[:512])
            for s in sentiment:
                label = s.label.lower()
                if label in results["sentiment"]:
                    results["sentiment"][label] += 1

            # Categories
            classification = await self.zero_shot_classification(article[:512], categories)
            for label, score in zip(classification.labels, classification.scores):
                if label in results["category_scores"]:
                    results["category_scores"][label].append(score)

            # Entities
            entities = await self.named_entity_recognition(article[:512])
            for entity in entities:
                if entity.entity in ["ORG", "PER"] and entity.score > 0.9:
                    results["entities"].append(entity.word)

        # Calculate averages
        for cat in categories:
            scores = results["category_scores"][cat]
            results["category_scores"][cat] = sum(scores) / len(scores) if scores else 0

        # Deduplicate entities
        results["entities"] = list(set(results["entities"]))[:20]

        return results
