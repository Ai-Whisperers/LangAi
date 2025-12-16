#!/usr/bin/env python
"""
Workflow Visualizer - Generate visual diagrams of the research workflow.

Usage:
    python visualize_workflow.py [--format mermaid|json|png|html] [--output FILE]

Outputs:
    - Mermaid diagram (viewable at mermaid.live)
    - JSON graph data
    - PNG image (requires graphviz)
    - Interactive HTML
"""

import argparse
import json
from pathlib import Path


def create_workflow_diagram():
    """Create a Mermaid diagram of the comprehensive workflow."""

    # Define the workflow structure
    diagram = """graph TD
    %% Styling
    classDef phase fill:#1a1a2e,stroke:#16213e,color:#fff
    classDef data fill:#0f3460,stroke:#16213e,color:#fff
    classDef analysis fill:#533483,stroke:#16213e,color:#fff
    classDef quality fill:#e94560,stroke:#16213e,color:#fff
    classDef output fill:#00b894,stroke:#16213e,color:#fff

    %% Phase 1: Data Collection
    subgraph P1["📥 PHASE 1: DATA COLLECTION"]
        START([🚀 START]) --> GQ[Generate Queries<br/>Multilingual]
        GQ --> SEARCH[Web Search<br/>Tavily/Serper/DDG]
        SEARCH --> FF[Fetch Financial<br/>FMP/Finnhub/Yahoo]
        FF --> FN[Fetch News<br/>NewsAPI/GNews/RSS]
    end

    %% Phase 2: Parallel Analysis
    subgraph P2["🔬 PHASE 2: PARALLEL ANALYSIS"]
        FN --> CA[Core Analysis<br/>ResearcherAgent]
        CA --> FA[Financial Analysis<br/>FinancialAgent]
        FA --> MA[Market Analysis<br/>MarketAgent]
        MA --> EA[ESG Analysis<br/>ESGAgent]
        EA --> BA[Brand Analysis<br/>BrandAuditorAgent]
        BA --> NS[News Sentiment<br/>SentimentAnalyzer]
    end

    %% Phase 3: Quality Assurance
    subgraph P3["✅ PHASE 3: QUALITY ASSURANCE"]
        NS --> ED[Extract Data<br/>StructuredExtractor]
        ED --> QC{Quality Check<br/>≥85%?}
        QC -->|No, retry| CA
        QC -->|Yes| CM
    end

    %% Phase 4: Advanced Analysis
    subgraph P4["📊 PHASE 4: ADVANCED ANALYSIS"]
        CM[Competitive Matrix<br/>CompetitiveMatrixGenerator]
        CM --> RA[Risk Assessment<br/>RiskQuantifier]
        RA --> IT[Investment Thesis<br/>ThesisGenerator]
    end

    %% Phase 5: Output
    subgraph P5["📄 PHASE 5: OUTPUT"]
        IT --> SR[Save Report<br/>Markdown + JSON]
        SR --> DONE([✅ COMPLETE])
    end

    %% Apply styles
    class P1 phase
    class GQ,SEARCH,FF,FN data
    class CA,FA,MA,EA,BA,NS analysis
    class ED,QC quality
    class CM,RA,IT analysis
    class SR output
"""
    return diagram


def create_agent_diagram():
    """Create a diagram showing all agents and their relationships."""

    diagram = """graph TB
    %% Agent Organization Diagram

    subgraph CORE["🎯 CORE AGENTS"]
        R[ResearcherAgent<br/>Initial Research]
        A[AnalystAgent<br/>Data Analysis]
        S[SynthesizerAgent<br/>Report Generation]
        CC[CompanyClassifier<br/>Type Detection]
    end

    subgraph FINANCIAL["💰 FINANCIAL AGENTS"]
        FA[FinancialAgent<br/>Revenue Analysis]
        EFA[EnhancedFinancialAgent<br/>Advanced Metrics]
        IA[InvestmentAnalystAgent<br/>DCF/Valuation]
    end

    subgraph MARKET["📈 MARKET AGENTS"]
        MA[MarketAgent<br/>Market Size]
        EMA[EnhancedMarketAgent<br/>TAM/SAM/SOM]
        CS[CompetitorScoutAgent<br/>Competitive Landscape]
        CAA[ComparativeAnalystAgent<br/>Head-to-Head]
    end

    subgraph RESEARCH["🔍 RESEARCH AGENTS"]
        DR[DeepResearchAgent<br/>Multi-iteration]
        RA[ReasoningAgent<br/>Hypothesis Testing]
        TA[TrendAnalystAgent<br/>Forecasting]
        ML[MultilingualSearch<br/>10+ Languages]
        CMG[CompetitiveMatrix<br/>Position Mapping]
        RQ[RiskQuantifier<br/>Risk Scoring]
        ITG[InvestmentThesis<br/>Bull/Bear Cases]
        NSA[NewsSentiment<br/>AI Sentiment]
    end

    subgraph SPECIALIZED["🎨 SPECIALIZED AGENTS"]
        ESG[ESGAgent<br/>E/S/G Analysis]
        BA[BrandAuditorAgent<br/>Brand Health]
        SMA[SocialMediaAgent<br/>Social Analysis]
        SI[SalesIntelligenceAgent<br/>Lead Scoring]
        PA[ProductAgent<br/>Product Analysis]
        RCA[RegulatoryAgent<br/>Compliance]
    end

    subgraph QUALITY["✅ QUALITY AGENTS"]
        LC[LogicCriticAgent<br/>Validates Reasoning]
        QE[QualityEnforcer<br/>Blocks Bad Reports]
        DT[DataThresholdChecker<br/>Min Data Quality]
    end

    %% Relationships
    R --> FA & MA & ESG
    FA --> IA
    MA --> CS --> CAA
    R --> DR --> RA
    S --> QUALITY

    classDef core fill:#3498db,stroke:#2980b9,color:#fff
    classDef financial fill:#27ae60,stroke:#1e8449,color:#fff
    classDef market fill:#9b59b6,stroke:#8e44ad,color:#fff
    classDef research fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef specialized fill:#f39c12,stroke:#d68910,color:#fff
    classDef quality fill:#1abc9c,stroke:#16a085,color:#fff

    class R,A,S,CC core
    class FA,EFA,IA financial
    class MA,EMA,CS,CAA market
    class DR,RA,TA,ML,CMG,RQ,ITG,NSA research
    class ESG,BA,SMA,SI,PA,RCA specialized
    class LC,QE,DT quality
"""
    return diagram


def create_integration_diagram():
    """Create a diagram showing all external integrations."""

    diagram = """graph LR
    %% External Integrations

    subgraph APP["🖥️ COMPANY RESEARCHER"]
        API[REST API<br/>FastAPI]
        WF[Workflow Engine<br/>LangGraph]
        AG[AI Agents<br/>16+ Agents]
    end

    subgraph LLM["🤖 LLM PROVIDERS"]
        ANT[Anthropic<br/>Claude]
        OAI[OpenAI<br/>GPT-4]
        DS[DeepSeek<br/>Ultra-cheap]
        GRQ[Groq<br/>Ultra-fast]
        GEM[Gemini<br/>2M context]
    end

    subgraph SEARCH["🔍 SEARCH"]
        TAV[Tavily<br/>$0.01/query]
        SER[Serper<br/>$0.001/query]
        DDG[DuckDuckGo<br/>FREE]
        WIKI[Wikipedia<br/>FREE]
    end

    subgraph FIN["💰 FINANCIAL"]
        FMP[FMP<br/>Fundamentals]
        FH[Finnhub<br/>Real-time]
        POL[Polygon<br/>Historical]
        SEC[SEC EDGAR<br/>FREE]
        YF[yfinance<br/>FREE]
    end

    subgraph NEWS["📰 NEWS"]
        NAPI[NewsAPI]
        GN[GNews]
        MS[Mediastack]
        GNRSS[Google RSS<br/>FREE]
    end

    subgraph SCRAPE["🕷️ SCRAPING"]
        FC[Firecrawl]
        SG[ScrapeGraph]
        C4AI[Crawl4AI<br/>FREE]
        JINA[Jina Reader<br/>FREE]
    end

    subgraph OBS["📊 OBSERVABILITY"]
        LF[Langfuse<br/>FREE tier]
        LS[LangSmith]
        AO[AgentOps]
        OT[OpenTelemetry]
    end

    APP --> LLM & SEARCH & FIN & NEWS & SCRAPE
    APP --> OBS

    classDef app fill:#2c3e50,stroke:#1a252f,color:#fff
    classDef llm fill:#3498db,stroke:#2980b9,color:#fff
    classDef search fill:#27ae60,stroke:#1e8449,color:#fff
    classDef fin fill:#f39c12,stroke:#d68910,color:#fff
    classDef news fill:#9b59b6,stroke:#8e44ad,color:#fff
    classDef scrape fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef obs fill:#1abc9c,stroke:#16a085,color:#fff

    class API,WF,AG app
    class ANT,OAI,DS,GRQ,GEM llm
    class TAV,SER,DDG,WIKI search
    class FMP,FH,POL,SEC,YF fin
    class NAPI,GN,MS,GNRSS news
    class FC,SG,C4AI,JINA scrape
    class LF,LS,AO,OT obs
"""
    return diagram


def create_html_viewer(mermaid_code: str, title: str = "Workflow Visualization") -> str:
    """Create an interactive HTML page with the Mermaid diagram."""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #00b894;
            margin-bottom: 30px;
        }}
        .diagram-container {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            overflow-x: auto;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
        .controls {{
            text-align: center;
            margin-bottom: 20px;
        }}
        button {{
            background: #00b894;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #00a187;
        }}
        .info {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 {title}</h1>

        <div class="controls">
            <button onclick="zoomIn()">🔍 Zoom In</button>
            <button onclick="zoomOut()">🔍 Zoom Out</button>
            <button onclick="resetZoom()">↺ Reset</button>
            <button onclick="downloadSVG()">💾 Download SVG</button>
        </div>

        <div class="diagram-container" id="diagram">
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </div>

        <div class="info">
            <h3>📌 Legend</h3>
            <ul>
                <li><strong>Blue nodes</strong>: Core processing agents</li>
                <li><strong>Purple nodes</strong>: Analysis components</li>
                <li><strong>Green nodes</strong>: Data collection</li>
                <li><strong>Red nodes</strong>: Quality gates</li>
                <li><strong>Dashed lines</strong>: Conditional flows</li>
            </ul>
        </div>
    </div>

    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});

        let scale = 1;

        function zoomIn() {{
            scale *= 1.2;
            document.querySelector('.mermaid svg').style.transform = `scale(${{scale}})`;
        }}

        function zoomOut() {{
            scale *= 0.8;
            document.querySelector('.mermaid svg').style.transform = `scale(${{scale}})`;
        }}

        function resetZoom() {{
            scale = 1;
            document.querySelector('.mermaid svg').style.transform = `scale(1)`;
        }}

        function downloadSVG() {{
            const svg = document.querySelector('.mermaid svg');
            const svgData = new XMLSerializer().serializeToString(svg);
            const blob = new Blob([svgData], {{type: 'image/svg+xml'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'workflow.svg';
            a.click();
        }}
    </script>
</body>
</html>"""
    return html


def main():
    # Fix Windows encoding issues
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Visualize Company Researcher workflows")
    parser.add_argument(
        "--format", choices=["mermaid", "json", "html", "all"], default="all", help="Output format"
    )
    parser.add_argument("--output", "-o", default="outputs/visualizations", help="Output directory")
    parser.add_argument(
        "--diagram",
        choices=["workflow", "agents", "integrations", "all"],
        default="all",
        help="Which diagram to generate",
    )

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    diagrams = {
        "workflow": ("Research Workflow", create_workflow_diagram),
        "agents": ("Agent Architecture", create_agent_diagram),
        "integrations": ("External Integrations", create_integration_diagram),
    }

    if args.diagram == "all":
        selected = diagrams.keys()
    else:
        selected = [args.diagram]

    for diagram_name in selected:
        title, generator = diagrams[diagram_name]
        mermaid_code = generator()

        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print(f"{'='*60}")

        if args.format in ["mermaid", "all"]:
            mermaid_file = output_dir / f"{diagram_name}.md"
            with open(mermaid_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n```mermaid\n{mermaid_code}\n```\n")
            print(f"[OK] Mermaid saved: {mermaid_file}")

        if args.format in ["html", "all"]:
            html_file = output_dir / f"{diagram_name}.html"
            html_content = create_html_viewer(mermaid_code, title)
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[OK] HTML saved: {html_file}")

        if args.format in ["json", "all"]:
            # Simple JSON export of structure
            json_file = output_dir / f"{diagram_name}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"name": diagram_name, "title": title, "mermaid": mermaid_code}, f, indent=2
                )
            print(f"[OK] JSON saved: {json_file}")

        # Always print Mermaid to console
        print(f"\n📋 Mermaid Code (copy to mermaid.live):\n")
        print(mermaid_code)

    print(f"\n{'='*60}")
    print(f"🎉 Visualizations saved to: {output_dir.absolute()}")
    print(f"{'='*60}")
    print("\n💡 Tips:")
    print("   • Open .html files in browser for interactive view")
    print("   • Paste .md content in https://mermaid.live for editing")
    print("   • Use VS Code + Mermaid extension for preview")


if __name__ == "__main__":
    main()
