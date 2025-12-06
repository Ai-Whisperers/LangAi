"""
Specialized Agents - Domain-specific research agents.

Agents for specialized analysis:
- BrandAuditorAgent: Brand perception analysis
- SocialMediaAgent: Social presence analysis
- SalesIntelligenceAgent: B2B prospecting
- ProductAgent: Product analysis
"""

from .brand_auditor import (
    BrandAuditorAgent,
    brand_auditor_agent_node,
    create_brand_auditor,
    BrandStrength,
    BrandHealth,
)
from .social_media import (
    SocialMediaAgent,
    social_media_agent_node,
    create_social_media_agent,
    SocialPlatform,
    PlatformMetrics,
)
from .sales_intelligence import (
    SalesIntelligenceAgent,
    sales_intelligence_agent_node,
    create_sales_intelligence_agent,
    LeadScore,
    BuyingSignal,
)
from .product import ProductAgent, product_agent_node, create_product_agent

__all__ = [
    # Brand Auditor
    "BrandAuditorAgent",
    "brand_auditor_agent_node",
    "create_brand_auditor",
    "BrandStrength",
    "BrandHealth",
    # Social Media
    "SocialMediaAgent",
    "social_media_agent_node",
    "create_social_media_agent",
    "SocialPlatform",
    "PlatformMetrics",
    # Sales Intelligence
    "SalesIntelligenceAgent",
    "sales_intelligence_agent_node",
    "create_sales_intelligence_agent",
    "LeadScore",
    "BuyingSignal",
    # Product
    "ProductAgent",
    "product_agent_node",
    "create_product_agent",
]
