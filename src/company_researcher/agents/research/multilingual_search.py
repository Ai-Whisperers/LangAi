"""
Multilingual Search Generator - Generates search queries in multiple languages.

This module provides:
- Language detection for company names
- Query generation in 9 languages (English, Spanish, Portuguese, French, German, Italian, Chinese, Japanese, Korean)
- Parent company lookup for subsidiaries (130+ mappings)
- Region-specific search strategies
- Regional data sources for market-specific research (Latin America, Europe, Asia)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from ...utils import get_logger

logger = get_logger(__name__)


class Language(Enum):
    """Supported languages for search queries."""
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


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


@dataclass
class RegionalSource:
    """A regional data source for market-specific research."""
    name: str
    url: str
    language: Language
    country: str
    data_types: List[str]  # e.g., ["financial", "news", "regulatory"]
    search_template: Optional[str] = None  # e.g., "site:{url} {query}"


# Brand disambiguation mappings - for generic names that collide with common words
# Maps company_name -> (legal_name, industry_identifier, alternative_names)
BRAND_DISAMBIGUATION_MAP = {
    # Telecom brands with generic names
    "personal": ("Núcleo S.A.", "telecomunicaciones", ["Personal Paraguay", "Telecom Personal"]),
    "personal paraguay": ("Núcleo S.A.", "telecomunicaciones", ["Telecom Personal", "operador móvil"]),
    "personal argentina": ("Telecom Argentina S.A.", "telecomunicaciones", ["Telecom Personal Argentina"]),
    "tigo": ("Millicom International", "telecomunicaciones", ["Tigo mobile"]),
    "tigo paraguay": ("Telefónica Celular del Paraguay S.A.", "telecomunicaciones", ["Millicom Paraguay"]),
    "claro": ("América Móvil", "telecomunicaciones", ["Claro móvil"]),
    "vivo": ("Telefônica Brasil", "telecomunicações", ["Vivo celular"]),
    "movistar": ("Telefónica", "telecomunicaciones", ["Movistar móvil"]),
    "entel": ("Empresas Copec", "telecomunicaciones", ["Entel Chile móvil"]),
    "wom": ("Novator Partners", "telecomunicaciones", ["WOM Chile móvil"]),
    # Banks with generic names
    "personal finance": ("Personal Finance Company", "banking", []),
    "first bank": ("First Bank", "financial services", []),
    # Retail with generic names
    "target": ("Target Corporation", "retail", ["Target stores"]),
    "best buy": ("Best Buy Co.", "retail", ["Best Buy electronics"]),
}

# Parent company mappings for common subsidiaries
PARENT_COMPANY_MAP = {
    # Telecom - Personal (Telecom Argentina)
    "personal": "Telecom Argentina",
    "personal paraguay": "Telecom Argentina",
    "núcleo s.a.": "Telecom Argentina",
    "nucleo s.a.": "Telecom Argentina",
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
        Language.FRENCH: [
            "{company} entreprise présentation",
            "{company} histoire fondation",
            "{company} profil corporate",
        ],
        Language.GERMAN: [
            "{company} Unternehmen Übersicht",
            "{company} Geschichte Gründung",
            "{company} Firmenprofil",
        ],
        Language.ITALIAN: [
            "{company} azienda panoramica",
            "{company} storia fondazione",
            "{company} profilo aziendale",
        ],
        Language.CHINESE: [
            "{company} 公司概况",
            "{company} 历史 成立",
            "{company} 企业简介",
        ],
        Language.JAPANESE: [
            "{company} 会社概要",
            "{company} 歴史 設立",
            "{company} 企業プロフィール",
        ],
        Language.KOREAN: [
            "{company} 회사 개요",
            "{company} 역사 설립",
            "{company} 기업 프로필",
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
        Language.FRENCH: [
            "{company} chiffre d'affaires 2024",
            "{company} résultats financiers",
            "{company} rapport annuel",
        ],
        Language.GERMAN: [
            "{company} Umsatz 2024",
            "{company} Finanzergebnisse",
            "{company} Geschäftsbericht",
        ],
        Language.ITALIAN: [
            "{company} fatturato 2024",
            "{company} risultati finanziari",
            "{company} bilancio annuale",
        ],
        Language.CHINESE: [
            "{company} 营收 2024",
            "{company} 财务业绩",
            "{company} 年报",
        ],
        Language.JAPANESE: [
            "{company} 売上高 2024",
            "{company} 業績",
            "{company} 年次報告書",
        ],
        Language.KOREAN: [
            "{company} 매출 2024",
            "{company} 재무 실적",
            "{company} 연례 보고서",
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
        Language.FRENCH: [
            "{company} produits services",
            "{company} lignes d'activité",
        ],
        Language.GERMAN: [
            "{company} Produkte Dienstleistungen",
            "{company} Geschäftsfelder",
        ],
        Language.ITALIAN: [
            "{company} prodotti servizi",
            "{company} linee di business",
        ],
        Language.CHINESE: [
            "{company} 产品服务",
            "{company} 业务线",
        ],
        Language.JAPANESE: [
            "{company} 製品サービス",
            "{company} 事業部門",
        ],
        Language.KOREAN: [
            "{company} 제품 서비스",
            "{company} 사업 부문",
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
        Language.FRENCH: [
            "{company} concurrents marché",
            "{company} part de marché",
        ],
        Language.GERMAN: [
            "{company} Wettbewerber Marktanteil",
            "{company} Konkurrenten Vergleich",
        ],
        Language.ITALIAN: [
            "{company} concorrenti mercato",
            "{company} quota di mercato",
        ],
        Language.CHINESE: [
            "{company} 竞争对手",
            "{company} 市场份额",
        ],
        Language.JAPANESE: [
            "{company} 競合他社",
            "{company} 市場シェア",
        ],
        Language.KOREAN: [
            "{company} 경쟁사",
            "{company} 시장 점유율",
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
        Language.FRENCH: [
            "{company} actualités 2024",
            "{company} communiqués récents",
        ],
        Language.GERMAN: [
            "{company} Nachrichten 2024",
            "{company} aktuelle Entwicklungen",
        ],
        Language.ITALIAN: [
            "{company} notizie 2024",
            "{company} comunicati recenti",
        ],
        Language.CHINESE: [
            "{company} 新闻 2024",
            "{company} 最新动态",
        ],
        Language.JAPANESE: [
            "{company} ニュース 2024",
            "{company} 最新情報",
        ],
        Language.KOREAN: [
            "{company} 뉴스 2024",
            "{company} 최신 소식",
        ],
    },
    "leadership": {
        Language.ENGLISH: [
            "{company} CEO leadership team",
            "{company} executives management",
            "{company} CEO appointed 2024",
            "{company} chief executive officer name",
        ],
        Language.SPANISH: [
            "{company} CEO directivos",
            "{company} equipo directivo",
            "{company} gerente general nombre",
            "{company} presidente ejecutivo",
        ],
        Language.PORTUGUESE: [
            "{company} CEO diretoria",
            "{company} equipe executiva",
            "{company} presidente executivo nome",
        ],
        Language.FRENCH: [
            "{company} PDG directeur général",
            "{company} équipe de direction",
        ],
        Language.GERMAN: [
            "{company} CEO Vorstandsvorsitzender",
            "{company} Führungsteam Management",
        ],
        Language.ITALIAN: [
            "{company} CEO amministratore delegato",
            "{company} team dirigenziale",
        ],
        Language.CHINESE: [
            "{company} CEO 首席执行官",
            "{company} 管理团队",
        ],
        Language.JAPANESE: [
            "{company} CEO 社長",
            "{company} 経営陣",
        ],
        Language.KOREAN: [
            "{company} CEO 대표이사",
            "{company} 경영진",
        ],
    },
    # Dedicated CEO appointment topic - critical for finding recent executive changes
    "ceo_appointment": {
        Language.ENGLISH: [
            "{company} new CEO appointed 2024",
            "{company} CEO appointment announcement",
            "{company} chief executive named",
            "who is the CEO of {company}",
        ],
        Language.SPANISH: [
            "{company} nuevo CEO nombrado 2024",
            "{company} designación director general",
            "{company} gerente general asume",
            "quién es el CEO de {company}",
            "{company} nombramiento ejecutivo",
        ],
        Language.PORTUGUESE: [
            "{company} novo CEO nomeado 2024",
            "{company} nomeação CEO diretor",
            "quem é o CEO da {company}",
            "{company} assume presidência",
        ],
        Language.FRENCH: [
            "{company} nouveau PDG nommé 2024",
            "qui est le PDG de {company}",
        ],
        Language.GERMAN: [
            "{company} neuer CEO ernannt 2024",
            "wer ist der CEO von {company}",
        ],
        Language.ITALIAN: [
            "{company} nuovo CEO nominato 2024",
            "chi è il CEO di {company}",
        ],
        Language.CHINESE: [
            "{company} 新CEO任命 2024",
            "{company} 谁是CEO",
        ],
        Language.JAPANESE: [
            "{company} 新CEO就任 2024",
            "{company} 社長 誰",
        ],
        Language.KOREAN: [
            "{company} 신임 CEO 임명 2024",
            "{company} CEO 누구",
        ],
    },
    # NEW TOPICS - Critical for comprehensive research
    "regulatory": {
        Language.ENGLISH: [
            "{company} regulatory compliance licenses",
            "{company} regulator approval certification",
            "{company} regulatory filings SEC EDGAR",
            "{company} spectrum license telecom",
        ],
        Language.SPANISH: [
            "{company} regulador licencias cumplimiento",
            "{company} CONATEL regulatorio",
            "{company} autorización regulatoria",
            "{company} espectro licencia telecomunicaciones",
        ],
        Language.PORTUGUESE: [
            "{company} regulador licenças conformidade",
            "{company} CVM ANATEL regulatório",
            "{company} autorização regulamentar",
        ],
        Language.FRENCH: [
            "{company} réglementaire conformité licences",
            "{company} autorité régulation",
        ],
        Language.GERMAN: [
            "{company} regulatorisch Compliance Lizenzen",
            "{company} Aufsichtsbehörde Genehmigung",
        ],
        Language.ITALIAN: [
            "{company} regolamentare conformità licenze",
            "{company} autorità regolazione",
        ],
        Language.CHINESE: [
            "{company} 监管合规许可证",
            "{company} 监管机构批准",
        ],
        Language.JAPANESE: [
            "{company} 規制コンプライアンスライセンス",
            "{company} 規制当局承認",
        ],
        Language.KOREAN: [
            "{company} 규제 준수 라이선스",
            "{company} 규제 기관 승인",
        ],
    },
    "subscribers": {
        Language.ENGLISH: [
            "{company} subscribers customers total",
            "{company} mobile subscribers 2024",
            "{company} customer base users",
            "{company} market share subscribers percentage",
        ],
        Language.SPANISH: [
            "{company} suscriptores clientes total",
            "{company} abonados móviles 2024",
            "{company} base clientes usuarios",
            "{company} participación mercado porcentaje",
        ],
        Language.PORTUGUESE: [
            "{company} assinantes clientes total",
            "{company} assinantes móveis 2024",
            "{company} base clientes usuários",
        ],
        Language.FRENCH: [
            "{company} abonnés clients total",
            "{company} abonnés mobiles 2024",
        ],
        Language.GERMAN: [
            "{company} Abonnenten Kunden gesamt",
            "{company} Mobilfunkkunden 2024",
        ],
        Language.ITALIAN: [
            "{company} abbonati clienti totale",
            "{company} clienti mobili 2024",
        ],
        Language.CHINESE: [
            "{company} 订阅用户客户总数",
            "{company} 移动用户 2024",
        ],
        Language.JAPANESE: [
            "{company} 加入者顧客数",
            "{company} モバイル加入者 2024",
        ],
        Language.KOREAN: [
            "{company} 가입자 고객 총",
            "{company} 모바일 가입자 2024",
        ],
    },
    "debt_structure": {
        Language.ENGLISH: [
            "{company} debt bonds credit rating",
            "{company} senior notes bonds due",
            "{company} refinancing debt structure",
            "{company} credit rating Moody S&P Fitch",
        ],
        Language.SPANISH: [
            "{company} deuda bonos calificación crediticia",
            "{company} notas senior bonos vencimiento",
            "{company} refinanciamiento estructura deuda",
        ],
        Language.PORTUGUESE: [
            "{company} dívida títulos rating crédito",
            "{company} debêntures vencimento",
            "{company} refinanciamento estrutura dívida",
        ],
        Language.FRENCH: [
            "{company} dette obligations notation crédit",
            "{company} refinancement structure dette",
        ],
        Language.GERMAN: [
            "{company} Schulden Anleihen Kreditrating",
            "{company} Refinanzierung Schuldenstruktur",
        ],
        Language.ITALIAN: [
            "{company} debito obbligazioni rating credito",
            "{company} rifinanziamento struttura debito",
        ],
        Language.CHINESE: [
            "{company} 债务债券信用评级",
            "{company} 再融资债务结构",
        ],
        Language.JAPANESE: [
            "{company} 債務社債信用格付け",
            "{company} 借り換え負債構造",
        ],
        Language.KOREAN: [
            "{company} 부채 채권 신용등급",
            "{company} 차환 부채 구조",
        ],
    },
    "geographic_breakdown": {
        Language.ENGLISH: [
            "{company} revenue by country region",
            "{company} geographic breakdown operations",
            "{company} international presence markets",
        ],
        Language.SPANISH: [
            "{company} ingresos por país región",
            "{company} desglose geográfico operaciones",
            "{company} presencia internacional mercados",
        ],
        Language.PORTUGUESE: [
            "{company} receita por país região",
            "{company} breakdown geográfico operações",
            "{company} presença internacional mercados",
        ],
        Language.FRENCH: [
            "{company} chiffre affaires par pays région",
            "{company} répartition géographique",
        ],
        Language.GERMAN: [
            "{company} Umsatz nach Land Region",
            "{company} geografische Aufschlüsselung",
        ],
        Language.ITALIAN: [
            "{company} fatturato per paese regione",
            "{company} distribuzione geografica",
        ],
        Language.CHINESE: [
            "{company} 按国家地区收入",
            "{company} 地域分布",
        ],
        Language.JAPANESE: [
            "{company} 国別地域別売上高",
            "{company} 地域別内訳",
        ],
        Language.KOREAN: [
            "{company} 국가별 지역별 매출",
            "{company} 지역별 분류",
        ],
    },
    "management_quality": {
        Language.ENGLISH: [
            "{company} CEO track record background",
            "{company} management tenure experience",
            "{company} executive compensation salary",
            "{company} board directors composition",
        ],
        Language.SPANISH: [
            "{company} CEO trayectoria antecedentes",
            "{company} gerencia experiencia directivos",
            "{company} remuneración ejecutivos",
            "{company} junta directores composición",
        ],
        Language.PORTUGUESE: [
            "{company} CEO trajetória experiência",
            "{company} diretoria experiência gestão",
            "{company} remuneração executivos",
        ],
        Language.FRENCH: [
            "{company} PDG parcours expérience",
            "{company} direction expérience",
        ],
        Language.GERMAN: [
            "{company} CEO Werdegang Erfahrung",
            "{company} Management Erfahrung",
        ],
        Language.ITALIAN: [
            "{company} CEO percorso esperienza",
            "{company} management esperienza",
        ],
        Language.CHINESE: [
            "{company} CEO 履历背景",
            "{company} 管理层经验",
        ],
        Language.JAPANESE: [
            "{company} CEO 経歴 背景",
            "{company} 経営陣 経験",
        ],
        Language.KOREAN: [
            "{company} CEO 경력 배경",
            "{company} 경영진 경험",
        ],
    },
    "macro_economy": {
        Language.ENGLISH: [
            "{country} GDP growth economy 2024",
            "{country} inflation currency exchange rate",
            "{country} economic outlook forecast",
            "{country} telecommunications market size",
        ],
        Language.SPANISH: [
            "{country} PIB crecimiento economía 2024",
            "{country} inflación tipo cambio moneda",
            "{country} perspectivas económicas pronóstico",
            "{country} mercado telecomunicaciones tamaño",
        ],
        Language.PORTUGUESE: [
            "{country} PIB crescimento economia 2024",
            "{country} inflação taxa câmbio moeda",
            "{country} perspectivas econômicas previsão",
        ],
        Language.FRENCH: [
            "{country} PIB croissance économie 2024",
            "{country} inflation taux change",
        ],
        Language.GERMAN: [
            "{country} BIP Wachstum Wirtschaft 2024",
            "{country} Inflation Wechselkurs",
        ],
        Language.ITALIAN: [
            "{country} PIL crescita economia 2024",
            "{country} inflazione tasso cambio",
        ],
        Language.CHINESE: [
            "{country} GDP 增长 经济 2024",
            "{country} 通胀 汇率",
        ],
        Language.JAPANESE: [
            "{country} GDP 成長 経済 2024",
            "{country} インフレ 為替レート",
        ],
        Language.KOREAN: [
            "{country} GDP 성장 경제 2024",
            "{country} 인플레이션 환율",
        ],
    },
    "partnerships_acquisitions": {
        Language.ENGLISH: [
            "{company} acquisitions mergers M&A",
            "{company} partnerships alliances joint venture",
            "{company} strategic investment",
        ],
        Language.SPANISH: [
            "{company} adquisiciones fusiones M&A",
            "{company} alianzas socios joint venture",
            "{company} inversión estratégica",
        ],
        Language.PORTUGUESE: [
            "{company} aquisições fusões M&A",
            "{company} parcerias alianças joint venture",
            "{company} investimento estratégico",
        ],
        Language.FRENCH: [
            "{company} acquisitions fusions M&A",
            "{company} partenariats alliances",
        ],
        Language.GERMAN: [
            "{company} Übernahmen Fusionen M&A",
            "{company} Partnerschaften Allianzen",
        ],
        Language.ITALIAN: [
            "{company} acquisizioni fusioni M&A",
            "{company} partnership alleanze",
        ],
        Language.CHINESE: [
            "{company} 收购兼并 M&A",
            "{company} 合作伙伴 联盟",
        ],
        Language.JAPANESE: [
            "{company} 買収 合併 M&A",
            "{company} 提携 アライアンス",
        ],
        Language.KOREAN: [
            "{company} 인수합병 M&A",
            "{company} 파트너십 제휴",
        ],
    },
    "technology_infrastructure": {
        Language.ENGLISH: [
            "{company} network infrastructure 4G 5G",
            "{company} technology innovation R&D",
            "{company} patents intellectual property",
            "{company} digital transformation technology",
        ],
        Language.SPANISH: [
            "{company} infraestructura red 4G 5G",
            "{company} tecnología innovación I+D",
            "{company} patentes propiedad intelectual",
            "{company} transformación digital tecnología",
        ],
        Language.PORTUGUESE: [
            "{company} infraestrutura rede 4G 5G",
            "{company} tecnologia inovação P&D",
            "{company} patentes propriedade intelectual",
        ],
        Language.FRENCH: [
            "{company} infrastructure réseau 4G 5G",
            "{company} technologie innovation R&D",
        ],
        Language.GERMAN: [
            "{company} Netzwerkinfrastruktur 4G 5G",
            "{company} Technologie Innovation F&E",
        ],
        Language.ITALIAN: [
            "{company} infrastruttura rete 4G 5G",
            "{company} tecnologia innovazione R&D",
        ],
        Language.CHINESE: [
            "{company} 网络基础设施 4G 5G",
            "{company} 技术创新研发",
        ],
        Language.JAPANESE: [
            "{company} ネットワークインフラ 4G 5G",
            "{company} 技術革新 R&D",
        ],
        Language.KOREAN: [
            "{company} 네트워크 인프라 4G 5G",
            "{company} 기술 혁신 R&D",
        ],
    },
    "customer_metrics": {
        Language.ENGLISH: [
            "{company} ARPU average revenue per user",
            "{company} churn rate customer retention",
            "{company} customer satisfaction NPS score",
            "{company} prepaid postpaid mix",
        ],
        Language.SPANISH: [
            "{company} ARPU ingreso promedio por usuario",
            "{company} tasa churn rotación clientes",
            "{company} satisfacción cliente NPS",
            "{company} prepago pospago mezcla",
        ],
        Language.PORTUGUESE: [
            "{company} ARPU receita média por usuário",
            "{company} taxa churn rotatividade clientes",
            "{company} satisfação cliente NPS",
        ],
        Language.FRENCH: [
            "{company} ARPU revenu moyen par utilisateur",
            "{company} taux attrition fidélisation",
        ],
        Language.GERMAN: [
            "{company} ARPU durchschnittlicher Umsatz pro Nutzer",
            "{company} Kundenabwanderungsrate",
        ],
        Language.ITALIAN: [
            "{company} ARPU ricavo medio per utente",
            "{company} tasso abbandono clienti",
        ],
        Language.CHINESE: [
            "{company} ARPU 每用户平均收入",
            "{company} 客户流失率",
        ],
        Language.JAPANESE: [
            "{company} ARPU ユーザー当たり平均収益",
            "{company} 解約率 顧客維持",
        ],
        Language.KOREAN: [
            "{company} ARPU 사용자당 평균 수익",
            "{company} 이탈률 고객 유지",
        ],
    },
}


# Regional data sources for market-specific research
REGIONAL_SOURCES = {
    # Latin America
    "mexico": [
        RegionalSource("BMV", "bmv.com.mx", Language.SPANISH, "Mexico",
                      ["financial", "stock"], "site:bmv.com.mx {query}"),
        RegionalSource("Expansion MX", "expansion.mx", Language.SPANISH, "Mexico",
                      ["news", "financial"]),
        RegionalSource("El Economista MX", "eleconomista.com.mx", Language.SPANISH, "Mexico",
                      ["news", "financial"]),
        RegionalSource("CNBV", "cnbv.gob.mx", Language.SPANISH, "Mexico",
                      ["regulatory"]),
    ],
    "brazil": [
        RegionalSource("B3", "b3.com.br", Language.PORTUGUESE, "Brazil",
                      ["financial", "stock"], "site:b3.com.br {query}"),
        RegionalSource("Valor Econômico", "valor.globo.com", Language.PORTUGUESE, "Brazil",
                      ["news", "financial"]),
        RegionalSource("InfoMoney", "infomoney.com.br", Language.PORTUGUESE, "Brazil",
                      ["financial", "stock"]),
        RegionalSource("Exame", "exame.com", Language.PORTUGUESE, "Brazil",
                      ["news", "business"]),
        RegionalSource("CVM", "cvm.gov.br", Language.PORTUGUESE, "Brazil",
                      ["regulatory"]),
    ],
    "argentina": [
        RegionalSource("BYMA", "byma.com.ar", Language.SPANISH, "Argentina",
                      ["financial", "stock"]),
        RegionalSource("Ámbito", "ambito.com", Language.SPANISH, "Argentina",
                      ["news", "financial"]),
        RegionalSource("El Cronista", "cronista.com", Language.SPANISH, "Argentina",
                      ["news", "financial"]),
    ],
    "chile": [
        RegionalSource("Bolsa de Santiago", "bolsadesantiago.com", Language.SPANISH, "Chile",
                      ["financial", "stock"]),
        RegionalSource("Diario Financiero", "df.cl", Language.SPANISH, "Chile",
                      ["news", "financial"]),
        RegionalSource("CMF Chile", "cmfchile.cl", Language.SPANISH, "Chile",
                      ["regulatory"]),
    ],
    "colombia": [
        RegionalSource("BVC", "bvc.com.co", Language.SPANISH, "Colombia",
                      ["financial", "stock"]),
        RegionalSource("Portafolio", "portafolio.co", Language.SPANISH, "Colombia",
                      ["news", "financial"]),
    ],
    "peru": [
        RegionalSource("BVL", "bvl.com.pe", Language.SPANISH, "Peru",
                      ["financial", "stock"]),
        RegionalSource("Gestión", "gestion.pe", Language.SPANISH, "Peru",
                      ["news", "financial"]),
    ],
    "paraguay": [
        RegionalSource("BVPASA", "bvpasa.com.py", Language.SPANISH, "Paraguay",
                      ["financial", "stock"]),
        RegionalSource("5 Días", "5dias.com.py", Language.SPANISH, "Paraguay",
                      ["news", "business"]),
        RegionalSource("La Nación PY", "lanacion.com.py", Language.SPANISH, "Paraguay",
                      ["news"]),
        RegionalSource("CONATEL", "conatel.gov.py", Language.SPANISH, "Paraguay",
                      ["regulatory", "telecom"]),
    ],
    # Europe
    "spain": [
        RegionalSource("BME", "bolsasymercados.es", Language.SPANISH, "Spain",
                      ["financial", "stock"]),
        RegionalSource("Expansión ES", "expansion.com", Language.SPANISH, "Spain",
                      ["news", "financial"]),
        RegionalSource("Cinco Días", "cincodias.elpais.com", Language.SPANISH, "Spain",
                      ["news", "financial"]),
        RegionalSource("CNMV", "cnmv.es", Language.SPANISH, "Spain",
                      ["regulatory"]),
    ],
    "germany": [
        RegionalSource("Deutsche Börse", "deutsche-boerse.com", Language.GERMAN, "Germany",
                      ["financial", "stock"]),
        RegionalSource("Handelsblatt", "handelsblatt.com", Language.GERMAN, "Germany",
                      ["news", "financial"]),
        RegionalSource("Manager Magazin", "manager-magazin.de", Language.GERMAN, "Germany",
                      ["news", "business"]),
        RegionalSource("BaFin", "bafin.de", Language.GERMAN, "Germany",
                      ["regulatory"]),
    ],
    "france": [
        RegionalSource("Euronext Paris", "euronext.com", Language.FRENCH, "France",
                      ["financial", "stock"]),
        RegionalSource("Les Echos", "lesechos.fr", Language.FRENCH, "France",
                      ["news", "financial"]),
        RegionalSource("Le Figaro Économie", "lefigaro.fr", Language.FRENCH, "France",
                      ["news", "financial"]),
        RegionalSource("AMF", "amf-france.org", Language.FRENCH, "France",
                      ["regulatory"]),
    ],
    "italy": [
        RegionalSource("Borsa Italiana", "borsaitaliana.it", Language.ITALIAN, "Italy",
                      ["financial", "stock"]),
        RegionalSource("Il Sole 24 Ore", "ilsole24ore.com", Language.ITALIAN, "Italy",
                      ["news", "financial"]),
        RegionalSource("CONSOB", "consob.it", Language.ITALIAN, "Italy",
                      ["regulatory"]),
    ],
    # Asia
    "china": [
        RegionalSource("SSE", "sse.com.cn", Language.CHINESE, "China",
                      ["financial", "stock"]),
        RegionalSource("SZSE", "szse.cn", Language.CHINESE, "China",
                      ["financial", "stock"]),
        RegionalSource("Caixin", "caixin.com", Language.CHINESE, "China",
                      ["news", "financial"]),
        RegionalSource("CSRC", "csrc.gov.cn", Language.CHINESE, "China",
                      ["regulatory"]),
    ],
    "japan": [
        RegionalSource("TSE", "jpx.co.jp", Language.JAPANESE, "Japan",
                      ["financial", "stock"]),
        RegionalSource("Nikkei", "nikkei.com", Language.JAPANESE, "Japan",
                      ["news", "financial"]),
        RegionalSource("FSA Japan", "fsa.go.jp", Language.JAPANESE, "Japan",
                      ["regulatory"]),
    ],
    "south_korea": [
        RegionalSource("KRX", "krx.co.kr", Language.KOREAN, "South Korea",
                      ["financial", "stock"]),
        RegionalSource("Maeil Business", "mk.co.kr", Language.KOREAN, "South Korea",
                      ["news", "financial"]),
        RegionalSource("FSC Korea", "fsc.go.kr", Language.KOREAN, "South Korea",
                      ["regulatory"]),
    ],
}


class MultilingualSearchGenerator:
    """Generates multilingual search queries for company research."""

    def __init__(self):
        """Initialize the search generator."""
        self.parent_company_map = PARENT_COMPANY_MAP
        self.country_indicators = COUNTRY_INDICATORS
        self.query_templates = QUERY_TEMPLATES
        self.brand_disambiguation_map = BRAND_DISAMBIGUATION_MAP

    def get_brand_disambiguation(self, company_name: str) -> Optional[dict]:
        """
        Get disambiguation info for ambiguous brand names.

        For generic brand names like "Personal" that collide with common words,
        returns legal name and industry identifiers to make queries more precise.

        Args:
            company_name: Company name to check

        Returns:
            Dict with legal_name, industry, and alternatives if disambiguation needed,
            None if company name is already unambiguous.
        """
        name_lower = company_name.lower().strip()

        if name_lower in self.brand_disambiguation_map:
            legal_name, industry, alternatives = self.brand_disambiguation_map[name_lower]
            return {
                "legal_name": legal_name,
                "industry": industry,
                "alternatives": alternatives,
                "needs_disambiguation": True
            }

        # Check partial matches
        for key, (legal_name, industry, alternatives) in self.brand_disambiguation_map.items():
            if key in name_lower or name_lower in key:
                return {
                    "legal_name": legal_name,
                    "industry": industry,
                    "alternatives": alternatives,
                    "needs_disambiguation": True
                }

        return None

    def generate_disambiguated_query(
        self,
        company_name: str,
        base_query: str,
        disambiguation: Optional[dict] = None
    ) -> List[str]:
        """
        Generate multiple query variations with disambiguation.

        For ambiguous names like "Personal", generates:
        - "Personal Paraguay" telecom revenue (with industry)
        - "Núcleo S.A." revenue (with legal name)

        Args:
            company_name: Original company name
            base_query: Base query template with {company} placeholder
            disambiguation: Disambiguation info from get_brand_disambiguation

        Returns:
            List of disambiguated query strings
        """
        queries = []

        # Always include original query
        original = base_query.format(company=company_name)
        queries.append(original)

        if disambiguation and disambiguation.get("needs_disambiguation"):
            # Add industry-qualified query
            industry = disambiguation.get("industry", "")
            if industry:
                industry_query = f'"{company_name}" {industry} {base_query.replace("{company}", "").strip()}'
                queries.append(industry_query)

            # Add legal name query
            legal_name = disambiguation.get("legal_name", "")
            if legal_name and legal_name != company_name:
                legal_query = base_query.format(company=f'"{legal_name}"')
                queries.append(legal_query)

            # Add alternative name queries
            alternatives = disambiguation.get("alternatives", [])
            for alt in alternatives[:2]:  # Limit to first 2 alternatives
                alt_query = base_query.format(company=alt)
                queries.append(alt_query)

        return queries

    def detect_country(
        self,
        company_name: str,
        additional_context: str = ""
    ) -> str:
        """
        Detect the country for a company based on name patterns.

        Args:
            company_name: Name of the company
            additional_context: Additional text context for detection

        Returns:
            Country name (capitalized) or "United States" as default
        """
        combined_text = f"{company_name} {additional_context}".lower()

        for country, info in self.country_indicators.items():
            for pattern in info["patterns"]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return country.title()  # Return capitalized country name

        return "United States"  # Default

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
        use_disambiguation: bool = True,
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
            use_disambiguation: Whether to apply brand disambiguation for generic names

        Returns:
            List of MultilingualQuery objects
        """
        # Auto-detect region and language if not provided
        if region is None or language is None:
            detected_region, detected_language = self.detect_region(company_name)
            region = region or detected_region
            language = language or detected_language

        # Detect country for macro_economy queries
        detected_country = self.detect_country(company_name)

        # Check for brand disambiguation needs
        disambiguation = None
        if use_disambiguation:
            disambiguation = self.get_brand_disambiguation(company_name)
            if disambiguation:
                logger.info(f"Brand disambiguation active for '{company_name}': "
                           f"legal_name='{disambiguation.get('legal_name')}', "
                           f"industry='{disambiguation.get('industry')}'")

        # Default topics - expanded to 16 for comprehensive research
        # CEO is critical - ceo_appointment added as dedicated topic
        if topics is None:
            topics = [
                "overview",
                "financial",
                "products",
                "competitors",
                "news",
                "leadership",
                "ceo_appointment",  # Critical for finding CEO names
                "regulatory",
                "subscribers",
                "debt_structure",
                "geographic_breakdown",
                "management_quality",
                "macro_economy",
                "partnerships_acquisitions",
                "technology_infrastructure",
                "customer_metrics",
            ]

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
                    # Pass both company and country to handle all template types
                    base_query = template.format(company=company_name, country=detected_country)
                    priority = 1 if lang == language else 2  # Native language has higher priority

                    queries.append(MultilingualQuery(
                        query=base_query,
                        language=lang,
                        topic=topic,
                        priority=priority
                    ))

                    # If disambiguation is active, add legal name and industry-qualified queries
                    if disambiguation and disambiguation.get("needs_disambiguation"):
                        legal_name = disambiguation.get("legal_name", "")
                        industry = disambiguation.get("industry", "")

                        # Add legal name query for critical topics
                        if legal_name and topic in ["overview", "financial", "leadership", "ceo_appointment"]:
                            legal_query = template.format(company=legal_name, country=detected_country)
                            queries.append(MultilingualQuery(
                                query=legal_query,
                                language=lang,
                                topic=topic,
                                priority=priority + 1  # Slightly lower priority
                            ))

                        # Add industry-qualified query for overview/news
                        if industry and topic in ["overview", "news"]:
                            industry_query = f'"{company_name}" {industry}'
                            queries.append(MultilingualQuery(
                                query=industry_query,
                                language=lang,
                                topic=topic,
                                priority=priority + 1
                            ))

        # Deduplicate queries
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.query.lower()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)

        # Sort by priority and limit
        unique_queries.sort(key=lambda q: q.priority)
        return unique_queries[:max_queries]

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

    def get_regional_source_queries(
        self,
        company_name: str,
        country: Optional[str] = None,
        data_types: Optional[List[str]] = None,
        max_queries: int = 10
    ) -> List[str]:
        """
        Generate site-specific queries targeting regional data sources.

        This enables searching regulatory bodies (CONATEL, CVM, ANATEL),
        local stock exchanges, and regional news sources directly.

        Args:
            company_name: Name of the company to research
            country: Country to get sources for (auto-detected if not provided)
            data_types: Filter sources by type (e.g., ["regulatory", "financial"])
            max_queries: Maximum number of queries to generate

        Returns:
            List of site-specific query strings

        Example:
            >>> generator = MultilingualSearchGenerator()
            >>> queries = generator.get_regional_source_queries("Tigo", country="Paraguay")
            >>> # Returns: ['site:conatel.gov.py "Tigo" licencia espectro', ...]
        """
        # Auto-detect country if not provided
        if country is None:
            country = self.detect_country(company_name)

        country_key = country.lower().replace(" ", "_")

        # Get regional sources for this country
        sources = REGIONAL_SOURCES.get(country_key, [])
        if not sources:
            logger.debug(f"No regional sources defined for country: {country}")
            return []

        # Filter by data types if specified
        if data_types:
            sources = [s for s in sources if any(dt in s.data_types for dt in data_types)]

        queries = []

        # Clean company name for search
        clean_name = company_name.strip()
        # Remove common suffixes for cleaner searches
        for suffix in [" S.A.", " SA", " Ltda", " Inc", " Corp", " LLC"]:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)].strip()
                break

        # Generate site-specific queries for each source
        for source in sources:
            base_query = f'site:{source.url} "{clean_name}"'

            # Add topic-specific queries based on data type
            if "regulatory" in source.data_types:
                if source.language == Language.SPANISH:
                    queries.append(f'{base_query} licencia regulación')
                    queries.append(f'{base_query} resolución normativa')
                elif source.language == Language.PORTUGUESE:
                    queries.append(f'{base_query} licença regulamentação')
                    queries.append(f'{base_query} resolução normativa')
                else:
                    queries.append(f'{base_query} license regulation')
                    queries.append(f'{base_query} resolution compliance')

            if "financial" in source.data_types or "stock" in source.data_types:
                if source.language == Language.SPANISH:
                    queries.append(f'{base_query} estados financieros')
                    queries.append(f'{base_query} informe anual')
                elif source.language == Language.PORTUGUESE:
                    queries.append(f'{base_query} demonstrações financeiras')
                    queries.append(f'{base_query} relatório anual')
                else:
                    queries.append(f'{base_query} financial statements')
                    queries.append(f'{base_query} annual report')

            if "news" in source.data_types:
                if source.language == Language.SPANISH:
                    queries.append(f'{base_query} CEO director ejecutivo')
                    queries.append(f'{base_query} noticias resultados')
                elif source.language == Language.PORTUGUESE:
                    queries.append(f'{base_query} CEO diretor executivo')
                    queries.append(f'{base_query} notícias resultados')
                else:
                    queries.append(f'{base_query} CEO executive')
                    queries.append(f'{base_query} news results')

            if "telecom" in source.data_types:
                if source.language == Language.SPANISH:
                    queries.append(f'{base_query} espectro frecuencia')
                    queries.append(f'{base_query} telecomunicaciones móvil')
                elif source.language == Language.PORTUGUESE:
                    queries.append(f'{base_query} espectro frequência')
                    queries.append(f'{base_query} telecomunicações móvel')
                else:
                    queries.append(f'{base_query} spectrum frequency')
                    queries.append(f'{base_query} telecommunications mobile')

        # Deduplicate and limit
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        return unique_queries[:max_queries]

    def get_all_enhanced_queries(
        self,
        company_name: str,
        include_regional: bool = True,
        include_parent: bool = True,
        include_alternatives: bool = True,
        max_total: int = 30
    ) -> List[str]:
        """
        Get all enhanced queries combining regional, parent, and alternative name queries.

        This is a convenience method for comprehensive research that combines
        all specialized query generators.

        Args:
            company_name: Name of the company
            include_regional: Include regional source queries
            include_parent: Include parent company queries
            include_alternatives: Include alternative name queries
            max_total: Maximum total queries to return

        Returns:
            Combined list of enhanced query strings
        """
        all_queries = []

        if include_regional:
            regional = self.get_regional_source_queries(company_name, max_queries=15)
            all_queries.extend(regional)
            logger.info(f"Generated {len(regional)} regional source queries")

        if include_parent:
            parent = self.get_parent_company_queries(company_name)
            all_queries.extend(parent)
            logger.info(f"Generated {len(parent)} parent company queries")

        if include_alternatives:
            alternatives = self.get_alternative_name_queries(company_name)
            all_queries.extend(alternatives)
            logger.info(f"Generated {len(alternatives)} alternative name queries")

        # Deduplicate
        seen = set()
        unique = []
        for q in all_queries:
            if q not in seen:
                seen.add(q)
                unique.append(q)

        return unique[:max_total]


def create_multilingual_generator() -> MultilingualSearchGenerator:
    """Factory function to create MultilingualSearchGenerator."""
    return MultilingualSearchGenerator()
