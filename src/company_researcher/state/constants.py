"""
State Constants Module

Provides constants for state dictionary keys and configuration values.

Using constants instead of strings:
- Prevents typos
- Enables IDE auto-completion
- Makes refactoring easier
- Documents all state fields

Usage:
    from company_researcher.state.constants import StateKey, DefaultValue

    # Instead of: state["company_name"]
    # Use: state[StateKey.COMPANY_NAME]

    # Check defaults
    quality_threshold = DefaultValue.MIN_QUALITY_SCORE
"""


class StateKey:
    """
    Constants for state dictionary keys.

    Organized by category for easy navigation.
    """

    # ========================================
    # Input Fields
    # ========================================
    COMPANY_NAME = "company_name"

    # ========================================
    # Query Generation
    # ========================================
    SEARCH_QUERIES = "search_queries"
    QUERY_LANGUAGE = "query_language"
    DETECTED_REGION = "detected_region"
    DETECTED_LANGUAGE = "detected_language"

    # ========================================
    # Search Results
    # ========================================
    SEARCH_RESULTS = "search_results"
    SOURCES = "sources"

    # ========================================
    # Company Classification
    # ========================================
    COMPANY_CLASSIFICATION = "company_classification"
    IS_PUBLIC_COMPANY = "is_public_company"
    STOCK_TICKER = "stock_ticker"
    EXCHANGE = "exchange"
    AVAILABLE_DATA_SOURCES = "available_data_sources"
    COMPANY_TYPE = "company_type"

    # ========================================
    # Data Collection
    # ========================================
    SEC_DATA = "sec_data"
    SCRAPED_CONTENT = "scraped_content"
    NEWS_DATA = "news_data"
    FINANCIAL_DATA = "financial_data"

    # ========================================
    # Analysis
    # ========================================
    NOTES = "notes"
    COMPANY_OVERVIEW = "company_overview"
    KEY_METRICS = "key_metrics"
    PRODUCTS_SERVICES = "products_services"
    COMPETITORS = "competitors"
    KEY_INSIGHTS = "key_insights"

    # ========================================
    # Enhanced Analysis
    # ========================================
    COMPETITIVE_MATRIX = "competitive_matrix"
    RISK_PROFILE = "risk_profile"
    INVESTMENT_THESIS = "investment_thesis"
    NEWS_SENTIMENT = "news_sentiment"
    ESG_ANALYSIS = "esg_analysis"
    BRAND_ANALYSIS = "brand_analysis"

    # ========================================
    # Agent Outputs
    # ========================================
    AGENT_OUTPUTS = "agent_outputs"
    RESEARCHER = "researcher"
    FINANCIAL = "financial"
    MARKET = "market"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    SYNTHESIZER = "synthesizer"
    LOGIC_CRITIC = "logic_critic"

    # ========================================
    # Quality
    # ========================================
    QUALITY_SCORE = "quality_score"
    QUALITY_BREAKDOWN = "quality_breakdown"
    EXTRACTED_FACTS = "extracted_facts"
    CONTRADICTIONS = "contradictions"
    GAPS = "gaps"
    MISSING_INFO = "missing_info"

    # ========================================
    # Iteration
    # ========================================
    ITERATION_COUNT = "iteration_count"
    SHOULD_ITERATE = "should_iterate"
    ITERATION_REASON = "iteration_reason"
    MAX_ITERATIONS = "max_iterations"

    # ========================================
    # Metrics
    # ========================================
    TOTAL_COST = "total_cost"
    TOTAL_TOKENS = "total_tokens"
    START_TIME = "start_time"
    DURATION_SECONDS = "duration_seconds"

    # ========================================
    # Output
    # ========================================
    REPORT_PATH = "report_path"
    OUTPUT_FILES = "output_files"
    MARKDOWN_CONTENT = "markdown_content"
    REPORT_DATA = "report_data"

    # ========================================
    # Human Review (Phase 15)
    # ========================================
    REVIEW_PENDING = "review_pending"
    REVIEW_DATA = "review_data"
    HUMAN_DECISION = "human_decision"
    HUMAN_FEEDBACK = "human_feedback"
    STATE_MODIFICATIONS = "state_modifications"

    # ========================================
    # Error Handling (Phase 16)
    # ========================================
    ERRORS = "errors"
    FALLBACK_USED = "fallback_used"
    DEGRADED_COMPONENTS = "degraded_components"


class DefaultValue:
    """Default values for workflow configuration."""

    # Quality thresholds
    MIN_QUALITY_SCORE = 85.0
    MAX_ITERATIONS = 2

    # Search settings
    MAX_SEARCH_QUERIES = 5
    RESULTS_PER_QUERY = 10
    MAX_CONTENT_LENGTH = 5000

    # Cost limits
    MAX_COST_PER_RESEARCH = 1.0  # USD

    # Timeouts
    SEARCH_TIMEOUT_SECONDS = 30
    LLM_TIMEOUT_SECONDS = 60
    TOTAL_TIMEOUT_SECONDS = 300

    # Token limits
    MAX_INPUT_TOKENS = 100000
    MAX_OUTPUT_TOKENS = 4096

    # Quality weights
    WEIGHT_COMPLETENESS = 0.25
    WEIGHT_CONSISTENCY = 0.25
    WEIGHT_COVERAGE = 0.25
    WEIGHT_ACCURACY = 0.25

    # Retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 2.0

    # Circuit breaker
    CIRCUIT_FAILURE_THRESHOLD = 5
    CIRCUIT_RECOVERY_TIMEOUT = 30.0


class AgentName:
    """Standard agent names."""

    RESEARCHER = "researcher"
    ANALYST = "analyst"
    FINANCIAL = "financial"
    MARKET = "market"
    PRODUCT = "product"
    COMPETITOR = "competitor"
    ESG = "esg"
    BRAND = "brand"
    SOCIAL_MEDIA = "social_media"
    SALES = "sales"
    SYNTHESIZER = "synthesizer"
    LOGIC_CRITIC = "logic_critic"


class NodeName:
    """Standard node names in workflows."""

    # Data Collection
    CLASSIFY = "classify"
    GENERATE_QUERIES = "generate_queries"
    SEARCH = "search"
    SEC_EDGAR = "sec_edgar"
    WEBSITE_SCRAPING = "website_scraping"
    FETCH_NEWS = "fetch_news"
    FETCH_FINANCIAL = "fetch_financial"

    # Analysis
    ANALYZE = "analyze"
    EXTRACT_DATA = "extract_data"
    FINANCIAL_ANALYSIS = "financial_analysis"
    MARKET_ANALYSIS = "market_analysis"
    ESG_ANALYSIS = "esg_analysis"
    BRAND_ANALYSIS = "brand_analysis"

    # Quality
    QUALITY_CHECK = "quality_check"
    LOGIC_CRITIC = "logic_critic"

    # Output
    SYNTHESIZE = "synthesize"
    SAVE_REPORT = "save_report"

    # Subgraphs
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    QUALITY = "quality"
    OUTPUT = "output"


class EventType:
    """Event types for streaming."""

    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    WORKFLOW_ERROR = "workflow_error"
    NODE_START = "node_start"
    NODE_COMPLETE = "node_complete"
    NODE_ERROR = "node_error"
    STATE_UPDATE = "state_update"
    TOKEN = "token"
    PROGRESS = "progress"


class ReviewDecision:
    """Human review decisions."""

    APPROVE = "approve"
    REJECT = "reject"
    REVISE = "revise"
    MODIFY = "modify"
