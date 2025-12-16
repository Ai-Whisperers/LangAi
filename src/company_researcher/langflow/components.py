"""
Custom LangFlow Components for Company Researcher.

These components wrap the existing research agents for use in LangFlow's
visual workflow builder. Each component exposes the agent's functionality
through LangFlow's component interface.

Components follow LangFlow's custom component pattern:
- Inherit from langflow.custom.CustomComponent
- Define inputs/outputs with proper typing
- Implement build() method for component logic
"""

from typing import Any, Dict, Optional

from ..utils import get_logger

logger = get_logger(__name__)

# Check if LangFlow is available
try:
    from langflow.custom import CustomComponent
    from langflow.field_typing import Data

    LANGFLOW_AVAILABLE = True
except ImportError:
    LANGFLOW_AVAILABLE = False

    # Create stub classes for when LangFlow is not installed
    class CustomComponent:
        """Stub CustomComponent when LangFlow not installed."""

        def __init__(self):
            self.display_name = ""
            self.description = ""

        def build(self, *args, **kwargs):
            raise NotImplementedError("LangFlow not installed")

    Data = Dict[str, Any]


class ResearcherAgentComponent(CustomComponent):
    """
    LangFlow component for the Researcher Agent.

    Performs initial company research using web search and LLM analysis.
    This is typically the first node in a research workflow.
    """

    display_name = "Researcher Agent"
    description = "Initial company research and information gathering"
    icon = "search"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company to research",
                "required": True,
            },
            "search_depth": {
                "display_name": "Search Depth",
                "info": "Number of search queries to generate",
                "value": 5,
                "advanced": True,
            },
            "max_results": {
                "display_name": "Max Results",
                "info": "Maximum search results per query",
                "value": 3,
                "advanced": True,
            },
        }

    def build(
        self,
        company_name: str,
        search_depth: int = 5,
        max_results: int = 3,
    ) -> Data:
        """
        Execute the researcher agent.

        Args:
            company_name: Company to research
            search_depth: Number of search queries
            max_results: Results per query

        Returns:
            Research results including company overview and sources
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import researcher_agent_node
            from ..state import create_initial_state

            # Create initial state
            state = create_initial_state(company_name)

            # Run researcher agent
            result = researcher_agent_node(state)

            return {
                "company_name": company_name,
                "company_overview": result.get("company_overview", ""),
                "sources": result.get("sources", []),
                "search_results": result.get("search_results", ""),
                "tokens": result.get("total_tokens", {}),
                "cost": result.get("total_cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Researcher agent error: {e}")
            return {"error": str(e)}


class FinancialAgentComponent(CustomComponent):
    """
    LangFlow component for the Financial Agent.

    Performs comprehensive financial analysis including revenue,
    profitability, and financial health metrics.
    """

    display_name = "Financial Agent"
    description = "Financial analysis: revenue, profitability, health"
    icon = "dollar-sign"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company to analyze",
                "required": True,
            },
            "research_context": {
                "display_name": "Research Context",
                "info": "Previous research results (from Researcher Agent)",
                "required": False,
            },
            "use_alpha_vantage": {
                "display_name": "Use Alpha Vantage",
                "info": "Fetch real-time stock data",
                "value": True,
                "advanced": True,
            },
            "use_sec_edgar": {
                "display_name": "Use SEC EDGAR",
                "info": "Fetch official SEC filings",
                "value": True,
                "advanced": True,
            },
        }

    def build(
        self,
        company_name: str,
        research_context: Optional[Dict] = None,
        use_alpha_vantage: bool = True,
        use_sec_edgar: bool = True,
    ) -> Data:
        """
        Execute the financial agent.

        Args:
            company_name: Company to analyze
            research_context: Previous research data
            use_alpha_vantage: Use stock data API
            use_sec_edgar: Use SEC filings

        Returns:
            Financial analysis results
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import financial_agent_node
            from ..state import OverallState

            # Build state from context
            state: OverallState = {
                "company_name": company_name,
                "company_overview": (
                    research_context.get("company_overview", "") if research_context else ""
                ),
                "search_results": (
                    research_context.get("search_results", "") if research_context else ""
                ),
                "sources": research_context.get("sources", []) if research_context else [],
            }

            # Run financial agent
            result = financial_agent_node(state)

            return {
                "company_name": company_name,
                "financial_analysis": result.get("financial_analysis", ""),
                "tokens": result.get("total_tokens", {}),
                "cost": result.get("total_cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Financial agent error: {e}")
            return {"error": str(e)}


class MarketAgentComponent(CustomComponent):
    """
    LangFlow component for the Market Agent.

    Performs market analysis including TAM/SAM/SOM sizing,
    industry trends, and competitive dynamics.
    """

    display_name = "Market Agent"
    description = "Market analysis: TAM/SAM/SOM, trends, competition"
    icon = "trending-up"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company to analyze",
                "required": True,
            },
            "research_context": {
                "display_name": "Research Context",
                "info": "Previous research results",
                "required": False,
            },
            "include_tam_sam_som": {
                "display_name": "Include TAM/SAM/SOM",
                "info": "Calculate market sizing",
                "value": True,
            },
            "include_trends": {
                "display_name": "Include Trends",
                "info": "Analyze industry trends",
                "value": True,
            },
        }

    def build(
        self,
        company_name: str,
        research_context: Optional[Dict] = None,
        include_tam_sam_som: bool = True,
        include_trends: bool = True,
    ) -> Data:
        """
        Execute the market agent.

        Args:
            company_name: Company to analyze
            research_context: Previous research data
            include_tam_sam_som: Include market sizing
            include_trends: Include trend analysis

        Returns:
            Market analysis results
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import market_agent_node
            from ..state import OverallState

            state: OverallState = {
                "company_name": company_name,
                "company_overview": (
                    research_context.get("company_overview", "") if research_context else ""
                ),
                "search_results": (
                    research_context.get("search_results", "") if research_context else ""
                ),
                "sources": research_context.get("sources", []) if research_context else [],
            }

            result = market_agent_node(state)

            return {
                "company_name": company_name,
                "market_analysis": result.get("market_analysis", ""),
                "tokens": result.get("total_tokens", {}),
                "cost": result.get("total_cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Market agent error: {e}")
            return {"error": str(e)}


class ProductAgentComponent(CustomComponent):
    """
    LangFlow component for the Product Agent.

    Analyzes product offerings, technology stack, and roadmap.
    """

    display_name = "Product Agent"
    description = "Product analysis: offerings, technology, roadmap"
    icon = "package"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company to analyze",
                "required": True,
            },
            "research_context": {
                "display_name": "Research Context",
                "info": "Previous research results",
                "required": False,
            },
        }

    def build(
        self,
        company_name: str,
        research_context: Optional[Dict] = None,
    ) -> Data:
        """
        Execute the product agent.

        Args:
            company_name: Company to analyze
            research_context: Previous research data

        Returns:
            Product analysis results
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import product_agent_node
            from ..state import OverallState

            state: OverallState = {
                "company_name": company_name,
                "company_overview": (
                    research_context.get("company_overview", "") if research_context else ""
                ),
                "search_results": (
                    research_context.get("search_results", "") if research_context else ""
                ),
                "sources": research_context.get("sources", []) if research_context else [],
            }

            result = product_agent_node(state)

            return {
                "company_name": company_name,
                "product_analysis": result.get("product_analysis", ""),
                "tokens": result.get("total_tokens", {}),
                "cost": result.get("total_cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Product agent error: {e}")
            return {"error": str(e)}


class SynthesizerAgentComponent(CustomComponent):
    """
    LangFlow component for the Synthesizer Agent.

    Combines all specialist analyses into a comprehensive report.
    """

    display_name = "Synthesizer Agent"
    description = "Synthesize all analyses into comprehensive report"
    icon = "file-text"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company",
                "required": True,
            },
            "financial_analysis": {
                "display_name": "Financial Analysis",
                "info": "Results from Financial Agent",
                "required": True,
            },
            "market_analysis": {
                "display_name": "Market Analysis",
                "info": "Results from Market Agent",
                "required": True,
            },
            "product_analysis": {
                "display_name": "Product Analysis",
                "info": "Results from Product Agent",
                "required": True,
            },
        }

    def build(
        self,
        company_name: str,
        financial_analysis: str,
        market_analysis: str,
        product_analysis: str,
    ) -> Data:
        """
        Execute the synthesizer agent.

        Args:
            company_name: Company name
            financial_analysis: Financial agent output
            market_analysis: Market agent output
            product_analysis: Product agent output

        Returns:
            Comprehensive synthesized report
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import synthesizer_agent_node
            from ..state import OverallState

            state: OverallState = {
                "company_name": company_name,
                "financial_analysis": financial_analysis,
                "market_analysis": market_analysis,
                "product_analysis": product_analysis,
            }

            result = synthesizer_agent_node(state)

            return {
                "company_name": company_name,
                "final_report": result.get("final_report", ""),
                "tokens": result.get("total_tokens", {}),
                "cost": result.get("total_cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Synthesizer agent error: {e}")
            return {"error": str(e)}


class CompetitorScoutComponent(CustomComponent):
    """
    LangFlow component for the Competitor Scout Agent (Phase 9).

    Provides comprehensive competitive intelligence including:
    - Competitor identification and classification
    - Tech stack analysis
    - Threat level assessment
    - Competitive positioning
    """

    display_name = "Competitor Scout"
    description = "Competitive intelligence: competitors, threats, positioning"
    icon = "users"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company to analyze competitors for",
                "required": True,
            },
            "research_context": {
                "display_name": "Research Context",
                "info": "Previous research results",
                "required": False,
            },
            "include_tech_stack": {
                "display_name": "Include Tech Stack",
                "info": "Analyze competitor technology stacks",
                "value": True,
            },
            "include_threat_assessment": {
                "display_name": "Include Threat Assessment",
                "info": "Assess competitive threat levels",
                "value": True,
            },
        }

    def build(
        self,
        company_name: str,
        research_context: Optional[Dict] = None,
        include_tech_stack: bool = True,
        include_threat_assessment: bool = True,
    ) -> Data:
        """
        Execute the competitor scout agent.

        Args:
            company_name: Company to analyze competitors for
            research_context: Previous research data
            include_tech_stack: Include tech stack analysis
            include_threat_assessment: Include threat assessments

        Returns:
            Competitive intelligence analysis
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..agents import competitor_scout_agent_node
            from ..state import OverallState

            state: OverallState = {
                "company_name": company_name,
                "company_overview": (
                    research_context.get("company_overview", "") if research_context else ""
                ),
                "search_results": (
                    research_context.get("search_results", "") if research_context else ""
                ),
                "sources": research_context.get("sources", []) if research_context else [],
            }

            result = competitor_scout_agent_node(state)
            agent_output = result.get("agent_outputs", {}).get("competitor", {})

            return {
                "company_name": company_name,
                "competitor_analysis": agent_output.get("analysis", ""),
                "competitors_found": agent_output.get("competitors_found", 0),
                "threat_summary": agent_output.get("threat_summary", {}),
                "competitive_intensity": agent_output.get("competitive_intensity", "unknown"),
                "tokens": agent_output.get("tokens", {}),
                "cost": agent_output.get("cost", 0.0),
            }
        except Exception as e:
            logger.error(f"Competitor scout agent error: {e}")
            return {"error": str(e)}


class QualityCheckerComponent(CustomComponent):
    """
    LangFlow component for Quality Checking.

    Validates research quality and determines if iteration is needed.
    """

    display_name = "Quality Checker"
    description = "Validate research quality and check thresholds"
    icon = "check-circle"

    def build_config(self) -> Dict[str, Any]:
        """Define component configuration."""
        return {
            "company_name": {
                "display_name": "Company Name",
                "info": "Name of the company",
                "required": True,
            },
            "research_data": {
                "display_name": "Research Data",
                "info": "Combined research results to validate",
                "required": True,
            },
            "quality_threshold": {
                "display_name": "Quality Threshold",
                "info": "Minimum quality score (0-100)",
                "value": 85.0,
            },
        }

    def build(
        self,
        company_name: str,
        research_data: Dict[str, Any],
        quality_threshold: float = 85.0,
    ) -> Data:
        """
        Execute quality check.

        Args:
            company_name: Company name
            research_data: Research results to validate
            quality_threshold: Minimum acceptable quality

        Returns:
            Quality assessment including score and pass/fail
        """
        if not LANGFLOW_AVAILABLE:
            return {"error": "LangFlow not installed"}

        try:
            from ..quality import check_research_quality

            result = check_research_quality(
                company_name=company_name,
                extracted_data=str(research_data),
                sources=research_data.get("sources", []),
            )

            quality_score = result["quality_score"]
            passed = quality_score >= quality_threshold

            return {
                "company_name": company_name,
                "quality_score": quality_score,
                "threshold": quality_threshold,
                "passed": passed,
                "missing_information": result.get("missing_information", []),
                "recommendation": "APPROVE" if passed else "ITERATE",
            }
        except Exception as e:
            logger.error(f"Quality checker error: {e}")
            return {"error": str(e)}


# Component registry for LangFlow discovery
COMPONENT_REGISTRY = {
    "ResearcherAgent": ResearcherAgentComponent,
    "FinancialAgent": FinancialAgentComponent,
    "MarketAgent": MarketAgentComponent,
    "ProductAgent": ProductAgentComponent,
    "CompetitorScout": CompetitorScoutComponent,  # Phase 9
    "SynthesizerAgent": SynthesizerAgentComponent,
    "QualityChecker": QualityCheckerComponent,
}


def get_all_components() -> Dict[str, type]:
    """Get all available LangFlow components."""
    return COMPONENT_REGISTRY.copy()
