"""
Reference Data for Company Research.

Static data and templates extracted from researcher.py to reduce file size.
Contains:
- Company to ticker symbol mappings
- Static company data for fallback
- Gap detection patterns and templates
- Report section definitions
"""

from typing import Dict, List, Any


# ============================================================================
# GAP FILLING CONFIGURATION
# ============================================================================

GAP_QUERY_TEMPLATES: Dict[str, List[str]] = {
    "market_cap": [
        '"{company}" market capitalization 2024',
        '"{company}" stock price market cap valuation',
    ],
    "stock_price": [
        '"{company}" stock price today 52 week high low',
        '"{company}" {ticker} share price performance',
    ],
    "pe_ratio": [
        '"{company}" P/E ratio valuation metrics 2024',
        '"{company}" price earnings ratio financial analysis',
    ],
    "revenue_segments": [
        '"{company}" revenue by segment breakdown 2024',
        '"{company}" business segment revenue contribution',
    ],
    "competitors": [
        '"{company}" competitors market share comparison',
        '"{company}" vs competitors analysis industry',
    ],
    "acquisitions": [
        '"{company}" acquisitions partnerships 2024',
        '"{company}" M&A mergers acquisitions deals',
    ],
    "leadership": [
        '"{company}" CEO leadership team executives',
        '"{company}" management team board directors',
    ],
    "employees": [
        '"{company}" employee count workforce size 2024',
        '"{company}" number of employees headcount',
    ],
    "mission": [
        '"{company}" mission vision statement values',
        '"{company}" company mission about us',
    ],
    "market_share": [
        '"{company}" market share industry position 2024',
        '"{company}" market share percentage ranking',
    ],
}

# Financial gaps that can be skipped when API data is available
FINANCIAL_API_GAPS = {"market_cap", "stock_price", "pe_ratio", "employees"}

# Gap detection patterns (regex patterns that indicate missing data)
GAP_PATTERNS: Dict[str, List[str]] = {
    "market_cap": [
        r"market cap(?:italization)?[:\s]*(?:data )?not available",
        r"market cap(?:italization)?[:\s]*N/?A",
        r"market capitalization\s*\n+Data not available",
    ],
    "stock_price": [
        r"stock (?:price|performance)[:\s]*(?:data )?not available",
        r"current price[:\s]*(?:data )?not available",
        r"52-week range[:\s]*(?:data )?not available",
    ],
    "pe_ratio": [
        r"P/?E ratio[:\s]*(?:data )?not available",
        r"valuation metrics[:\s]*(?:data )?not available",
    ],
    "revenue_segments": [
        r"revenue by segment[:\s]*(?:data )?not available",
        r"business segment[:\s]*(?:data )?not available",
    ],
    "competitors": [
        r"(?:main )?competitors[:\s]*(?:data )?not available",
        r"competitors[:\s]*N/?A",
        r"competitor.*market share[:\s]*(?:data )?not available",
    ],
    "acquisitions": [
        r"acquisitions[:\s]*(?:data )?not available",
        r"partnerships[:\s]*(?:data )?not available",
        r"M&A[:\s]*(?:data )?not available",
    ],
    "leadership": [
        r"(?:CEO|leadership)[:\s]*(?:data )?not available",
        r"leadership team[:\s]*(?:data )?not available",
    ],
    "employees": [
        r"employee(?:s| count)?[:\s]*(?:data )?not available",
        r"workforce[:\s]*(?:data )?not available",
    ],
    "mission": [
        r"mission[/:]?(?:vision)?[:\s]*(?:data )?not available",
    ],
    "market_share": [
        r"market share[:\s]*(?:data )?not available",
        r"market share by segment[:\s]*(?:data )?not available",
    ],
}

# Priority of gaps (higher = more important to fill)
GAP_PRIORITY: Dict[str, int] = {
    "market_cap": 9,
    "stock_price": 8,
    "revenue_segments": 8,
    "pe_ratio": 7,
    "market_share": 7,
    "competitors": 6,
    "leadership": 6,
    "acquisitions": 5,
    "employees": 4,
    "mission": 3,
}


# ============================================================================
# REPORT SECTION DEFINITIONS
# ============================================================================

REPORT_SECTIONS: Dict[str, Dict[str, Any]] = {
    "executive_summary": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Executive Summary", r"##?\s*Summary"],
        "min_length": 300,
        "required_elements": ["revenue", "market", "position"],
    },
    "company_overview": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Company Overview"],
        "min_length": 200,
        "required_elements": ["founded", "headquarters", "employees"],
    },
    "financial_performance": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Financial Performance"],
        "min_length": 300,
        "required_elements": ["revenue", "growth", "profit"],
    },
    "market_position": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Market Position"],
        "min_length": 200,
        "required_elements": ["market cap", "stock", "valuation"],
    },
    "products_services": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Products?\s*[&\+]?\s*Services?"],
        "min_length": 200,
        "required_elements": ["product", "segment", "service"],
    },
    "strategic_initiatives": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Strategic Initiatives?"],
        "min_length": 150,
        "required_elements": ["strategy", "initiative", "investment"],
    },
    "competitive_landscape": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Competitive?\s*Landscape"],
        "min_length": 200,
        "required_elements": ["competitor", "advantage", "market share"],
    },
    "recent_developments": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?Recent Developments?"],
        "min_length": 150,
        "required_elements": ["2024", "announce", "launch"],
    },
    "swot_analysis": {
        "patterns": [r"##?\s*(?:\d+\.?\s*)?SWOT Analysis"],
        "min_length": 300,
        "required_elements": ["strength", "weakness", "opportunit", "threat"],
    },
}


# ============================================================================
# COMPANY TO TICKER MAPPING
# ============================================================================

COMPANY_TICKER_MAP: Dict[str, str] = {
    # FAANG / Big Tech
    "apple": "AAPL",
    "apple inc": "AAPL",
    "microsoft": "MSFT",
    "microsoft corporation": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "alphabet inc": "GOOGL",
    "amazon": "AMZN",
    "amazon.com": "AMZN",
    "meta": "META",
    "meta platforms": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "nvidia": "NVDA",
    "tesla": "TSLA",
    "tesla inc": "TSLA",

    # Other major tech
    "adobe": "ADBE",
    "salesforce": "CRM",
    "oracle": "ORCL",
    "ibm": "IBM",
    "intel": "INTC",
    "amd": "AMD",
    "advanced micro devices": "AMD",
    "cisco": "CSCO",
    "cisco systems": "CSCO",
    "qualcomm": "QCOM",
    "broadcom": "AVGO",
    "paypal": "PYPL",
    "shopify": "SHOP",
    "zoom": "ZM",
    "zoom video": "ZM",
    "snowflake": "SNOW",
    "uber": "UBER",
    "lyft": "LYFT",
    "airbnb": "ABNB",
    "spotify": "SPOT",
    "twitter": "X",
    "x corp": "X",
    "snap": "SNAP",
    "snapchat": "SNAP",
    "pinterest": "PINS",
    "palantir": "PLTR",
    "crowdstrike": "CRWD",
    "datadog": "DDOG",
    "servicenow": "NOW",
    "workday": "WDAY",
    "splunk": "SPLK",
    "atlassian": "TEAM",
    "twilio": "TWLO",
    "docusign": "DOCU",
    "okta": "OKTA",
    "cloudflare": "NET",
    "mongodb": "MDB",
    "elastic": "ESTC",
    "hashicorp": "HCP",
    "confluent": "CFLT",

    # Financial
    "jpmorgan": "JPM",
    "jpmorgan chase": "JPM",
    "bank of america": "BAC",
    "wells fargo": "WFC",
    "goldman sachs": "GS",
    "morgan stanley": "MS",
    "visa": "V",
    "mastercard": "MA",
    "american express": "AXP",
    "blackrock": "BLK",
    "charles schwab": "SCHW",
    "square": "SQ",
    "block": "SQ",
    "coinbase": "COIN",
    "robinhood": "HOOD",

    # Retail/Consumer
    "walmart": "WMT",
    "costco": "COST",
    "target": "TGT",
    "home depot": "HD",
    "lowes": "LOW",
    "nike": "NKE",
    "starbucks": "SBUX",
    "mcdonalds": "MCD",
    "coca-cola": "KO",
    "coke": "KO",
    "pepsi": "PEP",
    "pepsico": "PEP",
    "procter & gamble": "PG",
    "p&g": "PG",
    "johnson & johnson": "JNJ",
    "disney": "DIS",
    "walt disney": "DIS",

    # Healthcare/Pharma
    "pfizer": "PFE",
    "moderna": "MRNA",
    "eli lilly": "LLY",
    "merck": "MRK",
    "abbvie": "ABBV",
    "unitedhealth": "UNH",
    "cvs health": "CVS",

    # Industrial/Energy
    "exxon": "XOM",
    "exxonmobil": "XOM",
    "chevron": "CVX",
    "boeing": "BA",
    "lockheed martin": "LMT",
    "general electric": "GE",
    "ge": "GE",
    "caterpillar": "CAT",
    "3m": "MMM",
    "honeywell": "HON",

    # Telecom
    "at&t": "T",
    "verizon": "VZ",
    "t-mobile": "TMUS",
    "comcast": "CMCSA",

    # Automotive
    "ford": "F",
    "general motors": "GM",
    "gm": "GM",
    "rivian": "RIVN",
    "lucid": "LCID",

    # Semiconductors
    "tsmc": "TSM",
    "taiwan semiconductor": "TSM",
    "asml": "ASML",
    "micron": "MU",
    "texas instruments": "TXN",
    "lam research": "LRCX",
    "applied materials": "AMAT",
}


# ============================================================================
# STATIC COMPANY DATA (Fallback when search doesn't find info)
# ============================================================================

COMPANY_STATIC_DATA: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "ceo": "Tim Cook",
        "founded": "April 1, 1976",
        "headquarters": "Cupertino, California, USA",
        "founders": "Steve Jobs, Steve Wozniak, Ronald Wayne",
        "employees": "164,000",
        "recent_products": [
            "iPad Pro with M4 chip (May 2024)",
            "iPad Air M2 in two sizes (May 2024)",
            "Apple Pencil Pro (May 2024)",
            "iMac with M4 chip (October 2024)",
            "Mac mini with M4/M4 Pro (October 2024)",
            "MacBook Pro with M4 (October 2024)",
        ],
        "ai_initiatives": "Apple Intelligence - AI system integrated into iOS 18, iPadOS 18, and macOS Sequoia (announced WWDC 2024)",
    },
    "MSFT": {
        "ceo": "Satya Nadella",
        "founded": "April 4, 1975",
        "headquarters": "Redmond, Washington, USA",
        "founders": "Bill Gates, Paul Allen",
        "employees": "228,000",
        "recent_products": [
            "Microsoft Copilot (2023-2024)",
            "Surface Pro 10 (2024)",
            "Surface Laptop 6 (2024)",
            "Windows 11 24H2 (2024)",
        ],
        "ai_initiatives": "Microsoft Copilot - AI assistant integrated across Microsoft 365, Windows, and Azure; $13B investment in OpenAI",
    },
    "GOOGL": {
        "ceo": "Sundar Pichai",
        "founded": "September 4, 1998",
        "headquarters": "Mountain View, California, USA",
        "founders": "Larry Page, Sergey Brin",
        "employees": "182,000",
        "recent_products": [
            "Pixel 9, Pixel 9 Pro, Pixel 9 Pro Fold (August 2024)",
            "Pixel Watch 3 (August 2024)",
            "Gemini 1.5 Pro (2024)",
            "Google Workspace AI features (2024)",
        ],
        "ai_initiatives": "Google Gemini - multimodal AI model; Bard rebranded to Gemini; AI integrated across Search, Workspace, and Cloud",
    },
    "AMZN": {
        "ceo": "Andy Jassy",
        "founded": "July 5, 1994",
        "headquarters": "Seattle, Washington, USA",
        "founders": "Jeff Bezos",
        "employees": "1,500,000+",
        "recent_products": [
            "Amazon Echo (new generation 2024)",
            "AWS Bedrock AI services (2024)",
            "Amazon Q AI assistant (2024)",
        ],
        "ai_initiatives": "Amazon Bedrock, Amazon Q, Alexa AI improvements, AWS AI/ML services",
    },
    "META": {
        "ceo": "Mark Zuckerberg",
        "founded": "February 4, 2004",
        "headquarters": "Menlo Park, California, USA",
        "founders": "Mark Zuckerberg, Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, Chris Hughes",
        "employees": "67,000",
        "recent_products": [
            "Meta Quest 3 (2023)",
            "Llama 3 AI model (2024)",
            "Ray-Ban Meta smart glasses (2023-2024)",
            "Threads social platform (2023)",
        ],
        "ai_initiatives": "Llama open-source LLMs; Meta AI assistant; AI-powered content moderation",
    },
    "NVDA": {
        "ceo": "Jensen Huang",
        "founded": "January 1993",
        "headquarters": "Santa Clara, California, USA",
        "founders": "Jensen Huang, Chris Malachowsky, Curtis Priem",
        "employees": "29,600",
        "recent_products": [
            "NVIDIA H100 GPU (2022-2024)",
            "NVIDIA H200 GPU (2024)",
            "NVIDIA Blackwell B100 (announced 2024)",
            "GeForce RTX 40 Series (2022-2024)",
        ],
        "ai_initiatives": "CUDA platform; AI data center GPUs; NVIDIA AI Enterprise; Omniverse",
    },
    "TSLA": {
        "ceo": "Elon Musk",
        "founded": "July 1, 2003",
        "headquarters": "Austin, Texas, USA",
        "founders": "Martin Eberhard, Marc Tarpenning (Elon Musk joined later)",
        "employees": "140,000+",
        "recent_products": [
            "Cybertruck (2023-2024)",
            "Model 3 Highland refresh (2024)",
            "Tesla Semi (limited production)",
            "FSD v12 (2024)",
        ],
        "ai_initiatives": "Full Self-Driving (FSD); Optimus humanoid robot; Dojo supercomputer",
    },
}


def get_ticker_for_company(company_name: str) -> str:
    """
    Get ticker symbol for a company name.

    Args:
        company_name: Company name to look up

    Returns:
        Ticker symbol or empty string if not found
    """
    return COMPANY_TICKER_MAP.get(company_name.lower().strip(), "")


def get_static_company_data(ticker: str) -> Dict[str, Any]:
    """
    Get static company data for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with static company data or empty dict
    """
    return COMPANY_STATIC_DATA.get(ticker.upper(), {})
