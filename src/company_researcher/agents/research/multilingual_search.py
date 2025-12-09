"""
Multilingual Search Generator - Generates search queries in multiple languages.

This module provides:
- Language detection for company names
- Query generation in English, Spanish, Portuguese
- Parent company lookup for subsidiaries
- Region-specific search strategies
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages for search queries."""
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"


class Region(Enum):
    """Geographic regions."""
    NORTH_AMERICA = "north_america"
    LATAM_BRAZIL = "latam_brazil"
    LATAM_SPANISH = "latam_spanish"
    EUROPE = "europe"
    ASIA = "asia"
    UNKNOWN = "unknown"


@dataclass
class MultilingualQuery:
    """A search query with language metadata."""
    query: str
    language: Language
    topic: str
    priority: int = 1


# Parent company mappings for common subsidiaries
PARENT_COMPANY_MAP = {
    # Telecom - América Móvil
    "claro": "América Móvil",
    "telcel": "América Móvil",
    "telmex": "América Móvil",
    "embratel": "América Móvil",
    "net": "América Móvil",
    "tracfone": "América Móvil",
    "claro argentina": "América Móvil",
    "claro chile": "América Móvil",
    "claro colombia": "América Móvil",
    "claro peru": "América Móvil",
    "claro ecuador": "América Móvil",
    "claro puerto rico": "América Móvil",
    "claro nicaragua": "América Móvil",
    "claro guatemala": "América Móvil",
    "claro honduras": "América Móvil",
    "claro el salvador": "América Móvil",
    "claro costa rica": "América Móvil",
    "claro panama": "América Móvil",
    "claro paraguay": "América Móvil",
    "claro uruguay": "América Móvil",
    "claro republica dominicana": "América Móvil",
    # Telecom - Telefónica
    "vivo": "Telefónica",
    "movistar": "Telefónica",
    "movistar argentina": "Telefónica",
    "movistar chile": "Telefónica",
    "movistar colombia": "Telefónica",
    "movistar peru": "Telefónica",
    "movistar venezuela": "Telefónica",
    "movistar mexico": "Telefónica",
    "movistar ecuador": "Telefónica",
    "movistar uruguay": "Telefónica",
    # Telecom - Others
    "tim brasil": "Telecom Italia",
    "oi": "Oi S.A.",
    "entel": "Empresas Copec",
    "tigo": "Millicom International",
    "tigo guatemala": "Millicom International",
    "tigo honduras": "Millicom International",
    "tigo el salvador": "Millicom International",
    "tigo colombia": "Millicom International",
    "tigo bolivia": "Millicom International",
    "tigo paraguay": "Millicom International",
    # Banking - Brazil
    "itaú": "Itaú Unibanco",
    "bradesco": "Banco Bradesco",
    "santander brasil": "Banco Santander",
    "banco do brasil": "Banco do Brasil S.A.",
    "caixa economica": "Caixa Econômica Federal",
    "nubank": "Nu Holdings",
    # Banking - Mexico
    "bbva bancomer": "BBVA",
    "banamex": "Citigroup",
    "banorte": "Grupo Financiero Banorte",
    "banco azteca": "Grupo Salinas",
    "inbursa": "Grupo Carso",
    # Banking - Others
    "banco de chile": "Quiñenco",
    "bancolombia": "Grupo Empresarial Antioqueño",
    "banco de bogota": "Grupo Aval",
    "banco galicia": "Grupo Financiero Galicia",
    "banco de credito": "Credicorp",
    "interbank": "Intercorp",
    # Retail - FEMSA
    "oxxo": "FEMSA",
    "farmacias guadalajara": "FEMSA",
    "coca-cola femsa": "FEMSA",
    # Retail - Falabella
    "falabella": "S.A.C.I. Falabella",
    "sodimac": "S.A.C.I. Falabella",
    "tottus": "S.A.C.I. Falabella",
    "banco falabella": "S.A.C.I. Falabella",
    # Retail - Cencosud
    "jumbo": "Cencosud",
    "easy": "Cencosud",
    "paris": "Cencosud",
    "santa isabel": "Cencosud",
    "wong": "Cencosud",
    "metro peru": "Cencosud",
    # Retail - Others
    "walmart mexico": "Walmart Inc",
    "walmart chile": "Walmart Inc",
    "liverpool": "El Puerto de Liverpool",
    "lojas americanas": "Americanas S.A.",
    "magazine luiza": "Magazine Luiza S.A.",
    # Mining
    "vale": "Vale S.A.",
    "codelco": "Corporación Nacional del Cobre",
    "southern peru": "Grupo México",
    "antamina": "BHP Group / Glencore",
    # Energy - Brazil
    "petrobras": "Petrobras S.A.",
    "copel": "Companhia Paranaense de Energia",
    "cemig": "Companhia Energética de Minas Gerais",
    "eletrobras": "Centrais Elétricas Brasileiras",
    "cpfl energia": "CPFL Energia",
    # Energy - Mexico
    "pemex": "Petróleos Mexicanos",
    "cfe": "Comisión Federal de Electricidad",
    # Energy - Others
    "ecopetrol": "Ecopetrol S.A.",
    "ypf": "YPF S.A.",
    "pdvsa": "Petróleos de Venezuela",
    "enap": "Empresa Nacional del Petróleo",
    # Construction
    "odebrecht": "Novonor",
    "ica": "Empresas ICA",
    "cemex": "CEMEX S.A.B.",
    "tigre": "Grupo Tigre",
    # Food & Beverages
    "ambev": "Anheuser-Busch InBev",
    "bimbo": "Grupo Bimbo",
    "gruma": "Gruma S.A.B.",
    "sigma alimentos": "Alfa S.A.B.",
    "jbs": "JBS S.A.",
    "brf": "BRF S.A.",
    "marfrig": "Marfrig Global Foods",
    "arcor": "Grupo Arcor",
    "nutresa": "Grupo Nutresa",
    # Airlines
    "avianca": "Avianca Holdings",
    "latam": "LATAM Airlines Group",
    "gol": "Gol Linhas Aéreas",
    "azul": "Azul S.A.",
    "aeromexico": "Grupo Aeroméxico",
    "volaris": "Volaris",
    # Media & Entertainment
    "televisa": "TelevisaUnivision",
    "tv azteca": "Grupo Salinas",
    "globo": "Grupo Globo",
    "record": "Grupo Record",
    # Industrial Conglomerates
    "grupo carso": "Grupo Carso",
    "grupo alfa": "Alfa S.A.B.",
    "grupo industrial saltillo": "GIS S.A.B.",
    "votorantim": "Votorantim S.A.",
    "ultrapar": "Ultrapar Participações",
    "itausa": "Itaúsa - Investimentos Itaú",
    "grupo empresarial antioqueno": "Grupo Empresarial Antioqueño",
}

# Country indicators in company names - ORDER MATTERS (more specific first)
COUNTRY_INDICATORS = {
    # Mexico FIRST because S.A. de C.V. is more specific than just S.A.
    "mexico": {
        "patterns": [
            r"\bS\.?A\.?\s*de\s*C\.?V\.?\b", r"\bméxico\b", r"\bmexico\b", r"\bmexicano?\b",
            r"\bBMV\b", r"\bMXN\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "brazil": {
        "patterns": [
            r"\bbrasil\b", r"\bbrasileira?\b", r"\bLtda\.?\b",
            r"\bB3\b", r"\bBOVESPA\b", r"\bBRL\b", r"\bR\$",
            r"\bS\.?A\.?\b(?!\s*de\s*C\.?V\.?)",  # S.A. but NOT followed by de C.V.
            r"\bpetrobras\b", r"\bvale\b", r"\bitaú\b", r"\bbradesco\b",  # Major Brazilian companies
        ],
        "region": Region.LATAM_BRAZIL,
        "language": Language.PORTUGUESE,
    },
    "argentina": {
        "patterns": [
            r"\bargentin[ao]\b", r"\bBCBA\b", r"\bARS\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "chile": {
        "patterns": [
            r"\bchile\b", r"\bchilena?\b", r"\bBCS\b", r"\bCLP\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "colombia": {
        "patterns": [
            r"\bcolombia\b", r"\bcolombian[ao]\b", r"\bBVC\b", r"\bCOP\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "peru": {
        "patterns": [
            r"\bperú?\b", r"\bperuan[ao]\b", r"\bBVL\b", r"\bPEN\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "paraguay": {
        "patterns": [
            r"\bparaguay\b", r"\bparaguay[ao]\b", r"\bBVPASA\b", r"\bPYG\b",
            r"\basunción\b", r"\basuncion\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "ecuador": {
        "patterns": [
            r"\becuador\b", r"\becuatorian[ao]\b", r"\bBVQ\b",
            r"\bguayaquil\b", r"\bquito\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "venezuela": {
        "patterns": [
            r"\bvenezuela\b", r"\bvenezolan[ao]\b", r"\bBVC\b", r"\bVES\b", r"\bVEF\b",
            r"\bcaracas\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "uruguay": {
        "patterns": [
            r"\buruguay\b", r"\buruguay[ao]\b", r"\bBVMV\b", r"\bUYU\b",
            r"\bmontevideo\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "bolivia": {
        "patterns": [
            r"\bbolivia\b", r"\bbolivian[ao]\b", r"\bBBV\b", r"\bBOB\b",
            r"\bla paz\b", r"\bsanta cruz\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "panama": {
        "patterns": [
            r"\bpanama\b", r"\bpanamá\b", r"\bpanameñ[ao]\b", r"\bBVP\b", r"\bPAB\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "costa_rica": {
        "patterns": [
            r"\bcosta rica\b", r"\bcostarricens[ae]\b", r"\bBNV\b", r"\bCRC\b",
            r"\bsan josé\b", r"\bsan jose\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "guatemala": {
        "patterns": [
            r"\bguatemala\b", r"\bguatemalte[ck]o\b", r"\bBVN\b", r"\bGTQ\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "dominican_republic": {
        "patterns": [
            r"\bdominicana?\b", r"\brepública dominicana\b", r"\bBVRD\b", r"\bDOP\b",
            r"\bsanto domingo\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "honduras": {
        "patterns": [
            r"\bhonduras\b", r"\bhondureñ[ao]\b", r"\bHNL\b",
            r"\btegucigalpa\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "el_salvador": {
        "patterns": [
            r"\bel salvador\b", r"\bsalvadoreñ[ao]\b", r"\bSSV\b",
            r"\bsan salvador\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "nicaragua": {
        "patterns": [
            r"\bnicaragua\b", r"\bnicaraguens[ae]\b", r"\bNIO\b",
            r"\bmanagua\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "cuba": {
        "patterns": [
            r"\bcuba\b", r"\bcuban[ao]\b", r"\bCUP\b", r"\bCUC\b",
            r"\bla habana\b", r"\bhavana\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
    "puerto_rico": {
        "patterns": [
            r"\bpuerto rico\b", r"\bpuertorriqueñ[ao]\b", r"\bboricua\b",
            r"\bsan juan\b",
        ],
        "region": Region.LATAM_SPANISH,
        "language": Language.SPANISH,
    },
}

# Search query templates by topic and language
QUERY_TEMPLATES = {
    "overview": {
        Language.ENGLISH: [
            "{company} company overview",
            "{company} about history founded",
            "{company} corporate profile",
        ],
        Language.SPANISH: [
            "{company} empresa perfil",
            "{company} historia fundación",
            "{company} quiénes somos",
        ],
        Language.PORTUGUESE: [
            "{company} empresa perfil",
            "{company} história fundação",
            "{company} quem somos",
        ],
    },
    "financial": {
        Language.ENGLISH: [
            "{company} revenue 2024 annual report",
            "{company} financial results earnings",
            "{company} market cap valuation",
        ],
        Language.SPANISH: [
            "{company} ingresos 2024",
            "{company} resultados financieros",
            "{company} reporte anual",
        ],
        Language.PORTUGUESE: [
            "{company} receita 2024",
            "{company} resultados financeiros",
            "{company} relatório anual",
        ],
    },
    "products": {
        Language.ENGLISH: [
            "{company} products services offerings",
            "{company} main business lines",
        ],
        Language.SPANISH: [
            "{company} productos servicios",
            "{company} líneas de negocio",
        ],
        Language.PORTUGUESE: [
            "{company} produtos serviços",
            "{company} áreas de negócio",
        ],
    },
    "competitors": {
        Language.ENGLISH: [
            "{company} competitors market share",
            "{company} vs competition comparison",
        ],
        Language.SPANISH: [
            "{company} competidores mercado",
            "{company} participación mercado",
        ],
        Language.PORTUGUESE: [
            "{company} concorrentes mercado",
            "{company} participação mercado",
        ],
    },
    "news": {
        Language.ENGLISH: [
            "{company} latest news 2024",
            "{company} recent developments",
        ],
        Language.SPANISH: [
            "{company} noticias 2024",
            "{company} últimas novedades",
        ],
        Language.PORTUGUESE: [
            "{company} notícias 2024",
            "{company} últimas novidades",
        ],
    },
    "leadership": {
        Language.ENGLISH: [
            "{company} CEO leadership team",
            "{company} executives management",
        ],
        Language.SPANISH: [
            "{company} CEO directivos",
            "{company} equipo directivo",
        ],
        Language.PORTUGUESE: [
            "{company} CEO diretoria",
            "{company} equipe executiva",
        ],
    },
}


class MultilingualSearchGenerator:
    """Generates multilingual search queries for company research."""

    def __init__(self):
        """Initialize the search generator."""
        self.parent_company_map = PARENT_COMPANY_MAP
        self.country_indicators = COUNTRY_INDICATORS
        self.query_templates = QUERY_TEMPLATES

    def detect_region(
        self,
        company_name: str,
        additional_context: str = ""
    ) -> Tuple[Region, Language]:
        """
        Detect the likely region and primary language for a company.

        Args:
            company_name: Name of the company
            additional_context: Additional text context for detection

        Returns:
            Tuple of (Region, Language)
        """
        combined_text = f"{company_name} {additional_context}".lower()

        for country, info in self.country_indicators.items():
            for pattern in info["patterns"]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    logger.info(f"Detected {country} company: {company_name}")
                    return info["region"], info["language"]

        # Default to North America / English
        return Region.NORTH_AMERICA, Language.ENGLISH

    def get_parent_company(self, company_name: str) -> Optional[str]:
        """
        Look up the parent company for a known subsidiary.

        Args:
            company_name: Name of the company

        Returns:
            Parent company name if found, None otherwise
        """
        name_lower = company_name.lower().strip()

        # Direct match
        if name_lower in self.parent_company_map:
            return self.parent_company_map[name_lower]

        # Partial match
        for subsidiary, parent in self.parent_company_map.items():
            if subsidiary in name_lower or name_lower in subsidiary:
                return parent

        return None

    def generate_queries(
        self,
        company_name: str,
        region: Optional[Region] = None,
        language: Optional[Language] = None,
        topics: Optional[List[str]] = None,
        include_english: bool = True,
        max_queries: int = 15,
    ) -> List[MultilingualQuery]:
        """
        Generate multilingual search queries for a company.

        Args:
            company_name: Name of the company to research
            region: Detected region (auto-detected if not provided)
            language: Primary language (auto-detected if not provided)
            topics: List of topics to generate queries for
            include_english: Always include English queries
            max_queries: Maximum number of queries to generate

        Returns:
            List of MultilingualQuery objects
        """
        # Auto-detect region and language if not provided
        if region is None or language is None:
            detected_region, detected_language = self.detect_region(company_name)
            region = region or detected_region
            language = language or detected_language

        # Default topics
        if topics is None:
            topics = ["overview", "financial", "products", "competitors", "news", "leadership"]

        queries = []
        languages_to_use = [language]

        # Add English if not already included
        if include_english and Language.ENGLISH not in languages_to_use:
            languages_to_use.append(Language.ENGLISH)

        # Generate queries for each topic and language
        for topic in topics:
            if topic not in self.query_templates:
                continue

            for lang in languages_to_use:
                templates = self.query_templates[topic].get(lang, [])
                for template in templates:
                    query_text = template.format(company=company_name)
                    priority = 1 if lang == language else 2  # Native language has higher priority

                    queries.append(MultilingualQuery(
                        query=query_text,
                        language=lang,
                        topic=topic,
                        priority=priority
                    ))

        # Sort by priority and limit
        queries.sort(key=lambda q: q.priority)
        return queries[:max_queries]

    def get_parent_company_queries(
        self,
        company_name: str,
        max_queries: int = 5
    ) -> List[str]:
        """
        Generate queries for the parent company if this is a subsidiary.

        Args:
            company_name: Name of the subsidiary
            max_queries: Maximum number of queries

        Returns:
            List of query strings for parent company
        """
        parent = self.get_parent_company(company_name)
        if not parent:
            return []

        queries = [
            f"{parent} company overview",
            f"{parent} {company_name} subsidiary",
            f"{parent} revenue financial results",
            f"{parent} corporate structure",
            f"{parent} annual report",
        ]

        return queries[:max_queries]

    def get_alternative_name_queries(
        self,
        company_name: str,
        max_queries: int = 5
    ) -> List[str]:
        """
        Generate queries with alternative company name variations.

        Args:
            company_name: Original company name
            max_queries: Maximum number of queries

        Returns:
            List of query strings with name variations
        """
        variations = []

        # Remove common suffixes
        name = company_name
        suffixes = [" S.A.", " SA", " Ltda", " Inc", " Corp", " LLC", " S.A. de C.V."]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break

        # Add variations
        variations.append(f'"{name}" company')  # Exact match
        variations.append(f"{name} empresa")  # Spanish
        variations.append(f"{name} empresa brasileira")  # Brazilian

        # Add without special characters
        clean_name = re.sub(r'[^\w\s]', '', name)
        if clean_name != name:
            variations.append(f"{clean_name} company")

        return variations[:max_queries]


def create_multilingual_generator() -> MultilingualSearchGenerator:
    """Factory function to create MultilingualSearchGenerator."""
    return MultilingualSearchGenerator()
