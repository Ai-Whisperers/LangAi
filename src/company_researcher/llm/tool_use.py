"""
Tool Use for Structured Data Extraction.

Uses Claude's tool use (function calling) capability for reliable
structured data extraction with validated schemas.

Usage:
    from company_researcher.llm.tool_use import get_structured_extractor

    extractor = get_structured_extractor()

    # Extract financial data
    data = extractor.extract_financial_data(
        content="Tesla reported $96.8B in revenue...",
        company_name="Tesla"
    )

    # Custom schema extraction
    data = extractor.extract_with_schema(
        content="...",
        schema={...},
        tool_name="extract_metrics"
    )
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from threading import Lock

from anthropic import Anthropic

from .client_factory import get_anthropic_client


# =============================================================================
# Tool Definitions
# =============================================================================

FINANCIAL_EXTRACTION_TOOLS = [
    {
        "name": "extract_revenue",
        "description": "Extract revenue figures and growth data from research content",
        "input_schema": {
            "type": "object",
            "properties": {
                "annual_revenue": {
                    "type": "number",
                    "description": "Annual revenue in USD (use billions format, e.g., 96.8 for $96.8B)"
                },
                "revenue_year": {
                    "type": "integer",
                    "description": "Year of the revenue figure"
                },
                "revenue_unit": {
                    "type": "string",
                    "enum": ["millions", "billions"],
                    "description": "Unit of revenue figure"
                },
                "yoy_growth_rate": {
                    "type": "number",
                    "description": "Year-over-year growth rate as percentage"
                },
                "quarterly_revenues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "quarter": {"type": "string"},
                            "amount": {"type": "number"},
                            "year": {"type": "integer"}
                        }
                    },
                    "description": "Quarterly revenue figures if available"
                },
                "revenue_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources for revenue data"
                }
            },
            "required": ["annual_revenue", "revenue_year"]
        }
    },
    {
        "name": "extract_funding",
        "description": "Extract funding and valuation information for private companies",
        "input_schema": {
            "type": "object",
            "properties": {
                "total_funding": {
                    "type": "number",
                    "description": "Total funding raised in USD"
                },
                "funding_unit": {
                    "type": "string",
                    "enum": ["millions", "billions"],
                    "description": "Unit of funding figure"
                },
                "latest_round": {
                    "type": "string",
                    "description": "Latest funding round (e.g., Series A, B, C)"
                },
                "latest_round_amount": {
                    "type": "number",
                    "description": "Amount raised in latest round"
                },
                "latest_round_date": {
                    "type": "string",
                    "description": "Date of latest round (YYYY-MM format)"
                },
                "valuation": {
                    "type": "number",
                    "description": "Latest valuation in USD"
                },
                "valuation_unit": {
                    "type": "string",
                    "enum": ["millions", "billions"]
                },
                "key_investors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key investors"
                }
            }
        }
    },
    {
        "name": "extract_market_position",
        "description": "Extract market position and competitive data",
        "input_schema": {
            "type": "object",
            "properties": {
                "market_share": {
                    "type": "number",
                    "description": "Market share as percentage"
                },
                "market_rank": {
                    "type": "integer",
                    "description": "Rank in the market (1 = leader)"
                },
                "total_addressable_market": {
                    "type": "number",
                    "description": "TAM in USD billions"
                },
                "competitors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "market_share": {"type": "number"},
                            "is_direct": {"type": "boolean"}
                        }
                    },
                    "description": "List of competitors"
                },
                "competitive_advantages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key competitive advantages"
                }
            }
        }
    },
    {
        "name": "extract_products",
        "description": "Extract product and service information",
        "input_schema": {
            "type": "object",
            "properties": {
                "main_products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "revenue_contribution": {"type": "number"}
                        }
                    },
                    "description": "Main products/services"
                },
                "target_customers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Target customer segments"
                },
                "pricing_model": {
                    "type": "string",
                    "description": "Business/pricing model"
                },
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key product features"
                }
            }
        }
    },
    {
        "name": "extract_company_overview",
        "description": "Extract general company information",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "founded_year": {"type": "integer"},
                "headquarters": {"type": "string"},
                "employee_count": {"type": "integer"},
                "employee_count_approximate": {"type": "boolean"},
                "industry": {"type": "string"},
                "sub_industry": {"type": "string"},
                "company_type": {
                    "type": "string",
                    "enum": ["public", "private", "startup", "subsidiary"]
                },
                "stock_ticker": {"type": "string"},
                "stock_exchange": {"type": "string"},
                "website": {"type": "string"},
                "description": {
                    "type": "string",
                    "description": "Brief company description"
                }
            },
            "required": ["company_name"]
        }
    }
]


@dataclass
class ExtractionResult:
    """Result from structured extraction."""
    tool_name: str
    data: Dict[str, Any]
    model: str
    input_tokens: int
    output_tokens: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "data": self.data,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens
        }


class StructuredExtractor:
    """
    Extract structured data using Claude's tool use capability.

    Tool use provides more reliable structured output than asking
    for JSON in a prompt, with built-in schema validation.
    """

    def __init__(self, client: Optional[Anthropic] = None):
        """
        Initialize the extractor.

        Args:
            client: Optional Anthropic client
        """
        self.client = client or get_anthropic_client()

    def extract_financial_data(
        self,
        content: str,
        company_name: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Extract structured financial data from text.

        Uses all financial extraction tools to pull out:
        - Revenue figures
        - Funding information
        - Market position
        - Company overview

        Args:
            content: Text content to extract from
            company_name: Company being analyzed
            model: Model to use
            max_tokens: Maximum tokens

        Returns:
            Dictionary with extracted data by tool name
        """
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=FINANCIAL_EXTRACTION_TOOLS,
            messages=[{
                "role": "user",
                "content": f"""Extract financial and company information for {company_name} from the following content.
Use the available tools to extract structured data for any information you find.
Call multiple tools if different types of information are present.

Content:
{content}"""
            }]
        )

        # Process all tool calls
        extracted_data = {}
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                extracted_data[tool_name] = block.input

        return {
            "company_name": company_name,
            "extracted": extracted_data,
            "tools_used": list(extracted_data.keys()),
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    def extract_with_schema(
        self,
        content: str,
        schema: Dict[str, Any],
        tool_name: str,
        description: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1000,
        force_tool: bool = True
    ) -> ExtractionResult:
        """
        Extract data using a custom schema.

        Args:
            content: Content to extract from
            schema: JSON Schema for the data
            tool_name: Name for the extraction tool
            description: Description of what to extract
            model: Model to use
            max_tokens: Maximum tokens
            force_tool: Whether to force tool use

        Returns:
            ExtractionResult object
        """
        tool = {
            "name": tool_name,
            "description": description,
            "input_schema": schema
        }

        params = {
            "model": model,
            "max_tokens": max_tokens,
            "tools": [tool],
            "messages": [{
                "role": "user",
                "content": f"Extract the requested information from:\n\n{content}"
            }]
        }

        if force_tool:
            params["tool_choice"] = {"type": "tool", "name": tool_name}

        response = self.client.messages.create(**params)

        # Find tool use in response
        for block in response.content:
            if block.type == "tool_use":
                return ExtractionResult(
                    tool_name=block.name,
                    data=block.input,
                    model=model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens
                )

        # No tool use found
        return ExtractionResult(
            tool_name=tool_name,
            data={},
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

    def extract_entities(
        self,
        content: str,
        entity_types: List[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, List[str]]:
        """
        Extract named entities from text.

        Args:
            content: Text to extract from
            entity_types: Types to extract (default: companies, people, locations)
            model: Model to use

        Returns:
            Dictionary of entity types to lists of entities
        """
        if entity_types is None:
            entity_types = ["companies", "people", "locations", "products", "dates"]

        schema = {
            "type": "object",
            "properties": {
                entity_type: {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": f"List of {entity_type} mentioned"
                }
                for entity_type in entity_types
            }
        }

        result = self.extract_with_schema(
            content=content,
            schema=schema,
            tool_name="extract_entities",
            description="Extract named entities from the text",
            model=model
        )

        return result.data

    def extract_key_metrics(
        self,
        content: str,
        metric_types: List[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ) -> List[Dict[str, Any]]:
        """
        Extract key metrics with values and context.

        Args:
            content: Text to extract from
            metric_types: Types of metrics to look for
            model: Model to use

        Returns:
            List of extracted metrics
        """
        if metric_types is None:
            metric_types = [
                "revenue", "profit", "growth_rate", "market_share",
                "employee_count", "customer_count", "valuation"
            ]

        schema = {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "metric_type": {
                                "type": "string",
                                "enum": metric_types
                            },
                            "value": {"type": "number"},
                            "unit": {"type": "string"},
                            "time_period": {"type": "string"},
                            "context": {"type": "string"},
                            "source_text": {"type": "string"}
                        },
                        "required": ["metric_type", "value"]
                    }
                }
            }
        }

        result = self.extract_with_schema(
            content=content,
            schema=schema,
            tool_name="extract_metrics",
            description="Extract numerical metrics with their values and context",
            model=model
        )

        return result.data.get("metrics", [])

    def extract_competitive_intel(
        self,
        content: str,
        company_name: str,
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Extract competitive intelligence data.

        Args:
            content: Text to extract from
            company_name: Focus company
            model: Model to use

        Returns:
            Competitive intelligence data
        """
        schema = {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "weaknesses": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "opportunities": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "threats": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "competitive_position": {
                    "type": "string",
                    "enum": ["leader", "challenger", "follower", "niche"]
                },
                "key_differentiators": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }

        result = self.extract_with_schema(
            content=content,
            schema=schema,
            tool_name="extract_competitive_intel",
            description=f"Extract competitive intelligence for {company_name}",
            model=model
        )

        return result.data


# Singleton instance
_structured_extractor: Optional[StructuredExtractor] = None
_extractor_lock = Lock()


def get_structured_extractor() -> StructuredExtractor:
    """
    Get singleton structured extractor instance.

    Returns:
        StructuredExtractor instance
    """
    global _structured_extractor
    if _structured_extractor is None:
        with _extractor_lock:
            if _structured_extractor is None:
                _structured_extractor = StructuredExtractor()
    return _structured_extractor


def reset_structured_extractor() -> None:
    """Reset extractor instance (for testing)."""
    global _structured_extractor
    _structured_extractor = None
