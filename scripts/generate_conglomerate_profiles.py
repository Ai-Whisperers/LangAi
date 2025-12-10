"""
Generate individual research profiles for LATAM conglomerates.

Converts the multi-conglomerate YAML files into individual company profiles
suitable for the research system.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List


def create_company_profile(conglomerate: Dict[str, Any], country: str, region: str) -> Dict[str, Any]:
    """Create a research-compatible company profile from conglomerate data."""

    # Extract key figures
    key_figures = conglomerate.get("key_figures", [])
    ceo = ""
    for fig in key_figures:
        if isinstance(fig, dict):
            role = fig.get("role", "").lower()
            if any(term in role for term in ["ceo", "chairman", "president", "founder", "leader"]):
                ceo = fig.get("name", "")
                break

    # Extract subsidiaries as services
    services = []
    subsidiaries = conglomerate.get("subsidiaries", {})
    if isinstance(subsidiaries, dict):
        for sector, companies in subsidiaries.items():
            if isinstance(companies, list):
                for company in companies:
                    if isinstance(company, dict):
                        name = company.get("name", "")
                        comp_sector = company.get("sector", sector)
                        if name:
                            services.append(f"{name} ({comp_sector})")
                    elif isinstance(company, str):
                        services.append(company)

    # Extract competitors from the same country/region
    competitors = []

    # Build research focus areas
    sectors = conglomerate.get("sectors", [])
    research_focus = [
        f"Market position in {', '.join(sectors[:3])}" if sectors else "Market position",
        "Financial performance and revenue breakdown",
        "Competitive landscape and market share",
        "Strategic initiatives and expansion plans",
        "Corporate governance and family ownership structure",
        "M&A activity and recent acquisitions",
        "ESG initiatives and sustainability"
    ]

    # Build priority queries
    name = conglomerate.get("name", "")
    priority_queries = [
        f"{name} revenue 2024",
        f"{name} market cap",
        f"{name} subsidiaries portfolio",
        f"{name} financial results",
        f"{name} expansion strategy",
        f"{name} competitive position {country}"
    ]

    # Get stock info if available
    ticker = conglomerate.get("stock_symbol", conglomerate.get("stock", ""))

    # Get founding info
    founded = str(conglomerate.get("founded", ""))

    # Get headquarters
    headquarters = conglomerate.get("headquarters", f"{country}")

    # Get controlling family
    family = conglomerate.get("controlling_family", "")

    # Get employee count
    employees = conglomerate.get("employees", "")

    # Get market cap or assets
    market_cap = conglomerate.get("market_cap", "")
    aum = conglomerate.get("assets_under_management", "")
    revenues = conglomerate.get("revenues", "")

    # Build notes
    notes_raw = conglomerate.get("notes", "")
    notes = notes_raw.strip() if isinstance(notes_raw, str) else ""

    profile = {
        "company": {
            "name": name,
            "legal_name": conglomerate.get("legal_name", name),
            "ticker": ticker,
            "website": conglomerate.get("website", ""),
            "industry": "Conglomerate / Diversified Holdings",
            "country": country,
            "region": region,
            "founded": founded,
            "headquarters": headquarters,
            "sectors": sectors,
            "details": {
                "ceo": ceo,
                "employees": str(employees) if employees else "",
                "controlling_family": family,
                "market_cap": market_cap,
                "assets_under_management": aum,
                "revenues": revenues,
            },
            "services": services[:15],  # Limit to 15 main subsidiaries
            "notes": notes
        },
        "research": {
            "focus_areas": research_focus,
            "priority_queries": priority_queries
        },
        "competitors": competitors
    }

    return profile


def process_country_file(filepath: Path, output_dir: Path) -> List[str]:
    """Process a country YAML file and generate individual profiles."""

    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    country = data.get("country", filepath.stem.replace("_", " ").title())
    region = data.get("region", "LATAM")

    generated = []

    # Handle regular country files
    conglomerates = data.get("conglomerates", [])

    # Handle Central America file which has multiple country sections
    if not conglomerates:
        for key in data.keys():
            if key.endswith("_conglomerates"):
                country_name = key.replace("_conglomerates", "").replace("_", " ").title()
                conglomerates_list = data[key]
                if not isinstance(conglomerates_list, list):
                    continue
                for cong in conglomerates_list:
                    if not isinstance(cong, dict):
                        continue
                    profile = create_company_profile(cong, country_name, region)

                    # Generate filename
                    safe_name = cong.get("name", "unknown").lower()
                    safe_name = safe_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')

                    # Create country subfolder
                    country_dir = output_dir / country_name.lower().replace(" ", "_")
                    country_dir.mkdir(parents=True, exist_ok=True)

                    output_path = country_dir / f"{safe_name}.yaml"

                    with open(output_path, 'w', encoding='utf-8') as f:
                        yaml.dump(profile, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

                    generated.append(str(output_path))
                    print(f"  Generated: {output_path.name}")
    else:
        # Regular country file
        for cong in conglomerates:
            profile = create_company_profile(cong, country, region)

            # Generate filename
            safe_name = cong.get("name", "unknown").lower()
            safe_name = safe_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')

            # Create country subfolder
            country_dir = output_dir / country.lower().replace(" ", "_")
            country_dir.mkdir(parents=True, exist_ok=True)

            output_path = country_dir / f"{safe_name}.yaml"

            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(profile, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            generated.append(str(output_path))
            print(f"  Generated: {output_path.name}")

    return generated


def main():
    """Generate all conglomerate profiles."""

    # Paths
    source_dir = Path("research_targets/latam_conglomerates")
    output_dir = Path("research_targets/latam_conglomerates_profiles")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each country file
    country_files = [
        "mexico.yaml",
        "brazil.yaml",
        "chile.yaml",
        "colombia.yaml",
        "argentina.yaml",
        "peru.yaml",
        "central_america.yaml"
    ]

    all_generated = []

    for filename in country_files:
        filepath = source_dir / filename
        if filepath.exists():
            print(f"\nProcessing {filename}...")
            generated = process_country_file(filepath, output_dir)
            all_generated.extend(generated)
        else:
            print(f"Warning: {filename} not found")

    print(f"\n{'='*60}")
    print(f"Total profiles generated: {len(all_generated)}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*60}")

    # Create a market config file
    market_config = {
        "market": {
            "name": "LATAM Conglomerates",
            "region": "Latin America",
            "industry": "Diversified Holdings / Conglomerates",
            "notes": "Major family-controlled business groups across Latin America",
            "key_metrics": [
                "Market capitalization",
                "Revenue",
                "Assets under management",
                "Number of subsidiaries",
                "Geographic presence",
                "Family ownership percentage"
            ]
        }
    }

    with open(output_dir / "_market_config.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(market_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nMarket config created: {output_dir / '_market_config.yaml'}")

    return all_generated


if __name__ == "__main__":
    main()
