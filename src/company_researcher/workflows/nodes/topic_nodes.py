"""
Topic research workflow nodes.

These nodes are intentionally schema-light and reuse existing integrations:
- SearchRouter (web search with fallbacks)
- NewsProvider (news search with fallbacks)
- GitHubClient (repo discovery)
- SmartLLMClient (planning + synthesis)
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from ...config import get_config
from ...integrations.github_client import GitHubClient, GitHubRepo
from ...integrations.news import NewsQuality, smart_news_search_sync
from ...integrations.search_router import get_search_router
from ...llm.model_router import TaskType
from ...llm.smart_client import get_smart_client
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


def _dedupe_by_url(items: List[Dict[str, Any]], url_key: str = "url") -> List[Dict[str, Any]]:
    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for it in items:
        url = str(it.get(url_key, "") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(it)
    return out


def _safe_parse_json_object(text: str) -> Dict[str, Any]:
    """
    Best-effort JSON object parser that tolerates fenced blocks and extra text.
    """
    if not text:
        return {}
    # Strip common code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    # Try direct JSON parse
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        pass
    # Fallback: extract first {...} region
    m = re.search(r"\{[\s\S]*\}", cleaned)
    if not m:
        return {}
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def generate_topic_plan_node(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = (state.get("topic") or state.get("subject") or state.get("company_name") or "").strip()
    if not topic:
        raise ValueError(
            "❌ ERROR: Missing topic for topic planning\n\n"
            "Explanation: Topic research requires a non-empty topic/subject string.\n\n"
            "Solution: Provide a topic via input state ('topic' or 'subject').\n\n"
            "Location: workflows/nodes/topic_nodes.py:generate_topic_plan_node\n"
        )

    client = get_smart_client()
    prompt = f"""
You are planning a topic research run.

Topic: {topic}

Return ONLY valid JSON with this schema:
{{
  "canonical_topic": "string",
  "synonyms": ["string", "..."],
  "subtopics": ["string", "..."],
  "beginner_prereqs": ["string", "..."],
  "key_terms": ["string", "..."],
  "search_queries": ["string", "..."],              // 8-12 web search queries
  "news_queries": ["string", "..."],                // 3-6 news queries
  "github_queries": ["string", "..."]               // 3-6 GitHub repo search queries (GitHub syntax)
}}

Guidelines:
- Include a spread from beginner (intro, tutorials) to state-of-the-art (recent surveys, benchmarks, top conferences).
- Prefer precise queries (include years like 2024/2025 for SOTA).
- GitHub queries should use qualifiers when useful (e.g., language:python, stars:>200, pushed:>2024-01-01).
"""

    result = client.complete(prompt=prompt, task_type=TaskType.SEARCH_QUERY.value)
    plan = _safe_parse_json_object(result.content)

    canonical = (plan.get("canonical_topic") or topic).strip()
    subtopics = [
        s.strip() for s in (plan.get("subtopics") or []) if isinstance(s, str) and s.strip()
    ]
    search_queries = [
        s.strip() for s in (plan.get("search_queries") or []) if isinstance(s, str) and s.strip()
    ]
    news_queries = [
        s.strip() for s in (plan.get("news_queries") or []) if isinstance(s, str) and s.strip()
    ]
    github_queries = [
        s.strip() for s in (plan.get("github_queries") or []) if isinstance(s, str) and s.strip()
    ]

    # Guardrails: always have at least a couple queries
    if not search_queries:
        search_queries = [
            f"{canonical} overview",
            f"{canonical} tutorial",
            f"{canonical} state of the art 2025",
            f"{canonical} survey 2024",
        ]
    if not news_queries:
        news_queries = [canonical]
    if not github_queries:
        github_queries = [f"{canonical} stars:>200", f"{canonical} pushed:>2024-01-01 stars:>50"]

    plan["canonical_topic"] = canonical
    plan["subtopics"] = subtopics
    plan["search_queries"] = search_queries
    plan["news_queries"] = news_queries
    plan["github_queries"] = github_queries

    return {
        "research_type": "topic",
        "subject": canonical,
        "topic": canonical,
        "topic_plan": plan,
        "topic_subtopics": subtopics,
        "search_queries": search_queries,
        "news_queries": news_queries,
        "github_queries": github_queries,
        "total_cost": result.cost,
        "total_tokens": {"input": result.input_tokens, "output": result.output_tokens},
    }


def topic_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    queries = state.get("search_queries") or []
    if not isinstance(queries, list) or not queries:
        return {"search_results": [], "sources": [], "search_trace": [], "search_stats": {}}

    config = get_config()
    router = get_search_router()

    search_results: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    search_trace: List[Dict[str, Any]] = []
    total_search_cost = 0.0

    max_per_query = max(1, int(getattr(config, "search_results_per_query", 3)))
    max_total = max(1, int(getattr(config, "max_search_results", 15)))

    # Ensure we always try the canonical topic itself (helps free Wikipedia fallback).
    topic = (state.get("topic") or state.get("subject") or "").strip()
    if topic:
        seen = set()
        merged = []
        for q in [topic] + list(queries):
            q = str(q).strip()
            if not q or q.lower() in seen:
                continue
            seen.add(q.lower())
            merged.append(q)
        queries = merged

    for q in queries:
        if len(search_results) >= max_total:
            break

        # Free-first with optional paid fallback (only when free is insufficient AND budget allows).
        response = router.search(query=q, quality="premium", max_results=max_per_query)
        try:
            search_trace.append(response.to_dict())
        except Exception:
            search_trace.append(
                {
                    "query": q,
                    "provider": getattr(response, "provider", ""),
                    "quality_tier": getattr(response, "quality_tier", ""),
                    "cost": getattr(response, "cost", 0.0),
                    "cached": getattr(response, "cached", False),
                    "success": getattr(response, "success", False),
                    "error": getattr(response, "error", None),
                    "results": [],
                }
            )

        if response.success and response.results:
            for item in response.results:
                if len(search_results) >= max_total:
                    break
                d = item.to_dict()
                search_results.append(
                    {
                        "title": d.get("title", ""),
                        "url": d.get("url", ""),
                        "content": d.get("snippet", ""),
                        "score": d.get("score", 0.0),
                    }
                )
                sources.append(
                    {
                        "title": d.get("title", "") or "Untitled",
                        "url": d.get("url", ""),
                        "score": d.get("score", 0.0),
                        "source_type": "web",
                    }
                )
            total_search_cost += float(getattr(response, "cost", 0.0) or 0.0)

    sources = _dedupe_by_url(sources)
    stats = router.get_stats()

    return {
        "search_results": search_results,
        "sources": sources,
        "search_trace": search_trace,
        "search_stats": stats,
        "total_cost": float(state.get("total_cost", 0.0) or 0.0) + total_search_cost,
    }


def fetch_topic_news_node(state: Dict[str, Any]) -> Dict[str, Any]:
    config = get_config()
    topic = (state.get("topic") or state.get("subject") or "").strip()
    queries = state.get("news_queries") or [topic]
    queries = [str(q).strip() for q in queries if str(q).strip()]
    if not queries:
        return {"topic_news": None}

    _ = config  # retained for parity; free news path does not require keys
    from_date = utc_now() - timedelta(days=30)  # best-effort metadata only

    all_articles: List[Dict[str, Any]] = []
    for q in queries[:6]:
        try:
            res = smart_news_search_sync(q, max_results=10, quality=NewsQuality.FREE)
            if res and getattr(res, "articles", None):
                for a in res.articles:
                    all_articles.append(
                        a.to_dict() if hasattr(a, "to_dict") else getattr(a, "__dict__", {}) or {}
                    )
        except Exception as e:  # noqa: BLE001 - best-effort enrichment
            logger.warning("Topic news search failed query=%s error=%s", q, str(e))

    # Normalize to sources for citation
    news_sources: List[Dict[str, Any]] = []
    for a in all_articles:
        url = a.get("url") or ""
        title = a.get("title") or a.get("source_name") or a.get("source") or "News article"
        news_sources.append(
            {
                "title": f"{title} (news)",
                "url": url,
                "score": 1.0,
                "source_type": "news",
                "published_at": a.get("published_at") or a.get("publishedAt"),
                "source": a.get("source_name") or a.get("source"),
            }
        )

    news_sources = _dedupe_by_url(news_sources)

    # Merge into existing sources (keep original ordering by appending)
    merged_sources = _dedupe_by_url((state.get("sources") or []) + news_sources)

    return {
        "topic_news": {"query": topic, "articles": all_articles, "count": len(all_articles)},
        "sources": merged_sources,
    }


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if not (loop and loop.is_running()):
        return asyncio.run(coro)

    # Fall back to running the coroutine in a dedicated thread/loop.
    import threading

    out: Dict[str, Any] = {}
    err: Dict[str, BaseException] = {}

    def _runner() -> None:
        try:
            out["result"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001 - propagate to caller
            err["exc"] = exc

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join()
    if "exc" in err:
        raise err["exc"]
    return out.get("result")


def _repo_to_dict(repo: GitHubRepo, score: float) -> Dict[str, Any]:
    category = _categorize_repo(repo)
    return {
        "full_name": repo.full_name,
        "name": repo.name,
        "description": repo.description,
        "url": repo.url,
        "homepage": repo.homepage,
        "stars": repo.stars,
        "forks": repo.forks,
        "watchers": repo.watchers,
        "language": repo.language,
        "open_issues": repo.open_issues,
        "created_at": repo.created_at,
        "updated_at": repo.updated_at,
        "pushed_at": repo.pushed_at,
        "topics": repo.topics,
        "is_fork": repo.is_fork,
        "is_archived": repo.is_archived,
        "score": score,
        "category": category,
    }


def _score_repo(repo: GitHubRepo) -> float:
    # Simple heuristic: stars dominate, slight penalty for archived/forks.
    score = float(repo.stars) + 0.2 * float(repo.forks)
    if repo.is_archived:
        score *= 0.2
    if repo.is_fork:
        score *= 0.6
    return score


def _categorize_repo(repo: GitHubRepo) -> str:
    hay = " ".join(
        [repo.full_name or "", repo.name or "", repo.description or "", " ".join(repo.topics or [])]
    ).lower()
    if "awesome" in hay:
        return "curated_list"
    if any(k in hay for k in ("dataset", "datasets", "data set", "benchmark")):
        return "dataset_benchmark"
    if any(k in hay for k in ("paper", "arxiv", "survey", "replication")):
        return "paper_reference"
    if any(k in hay for k in ("tutorial", "course", "learn", "example", "cookbook")):
        return "tutorial_examples"
    if any(k in hay for k in ("framework", "library", "sdk", "toolkit")):
        return "framework_library"
    return "repo"


def discover_github_repos_node(state: Dict[str, Any]) -> Dict[str, Any]:
    config = get_config()
    topic = (state.get("topic") or state.get("subject") or "").strip()
    queries = state.get("github_queries") or []
    queries = [str(q).strip() for q in queries if str(q).strip()]
    if not queries:
        queries = [f"{topic} stars:>200", f"{topic} pushed:>2024-01-01 stars:>50"]

    async def _search_all() -> Dict[str, GitHubRepo]:
        repos: Dict[str, GitHubRepo] = {}
        async with GitHubClient(config.github_token) as client:
            for q in queries[:6]:
                # Fetch 1-2 pages depending on limits. (Search API caps at 1,000 results anyway.)
                for page in (1, 2):
                    try:
                        found = await client.search_repos(query=q, per_page=50, page=page)
                    except Exception as e:  # noqa: BLE001 - best-effort enrichment
                        logger.warning(
                            "GitHub repo search failed query=%s page=%s error=%s", q, page, str(e)
                        )
                        found = []
                    for r in found or []:
                        if not r.full_name:
                            continue
                        repos.setdefault(r.full_name.lower(), r)
        return repos

    try:
        repos_by_fullname = _run_async(_search_all())
    except Exception as e:  # noqa: BLE001 - best-effort enrichment
        logger.warning("GitHub repo discovery failed: %s", str(e))
        repos_by_fullname = {}

    repos: List[Tuple[GitHubRepo, float]] = []
    for r in repos_by_fullname.values():
        repos.append((r, _score_repo(r)))

    repos.sort(key=lambda t: t[1], reverse=True)
    top = repos[:100]

    repo_dicts = [_repo_to_dict(r, score) for r, score in top]

    repo_sources = [
        {
            "title": f"{d['full_name']} (GitHub)",
            "url": d["url"],
            "score": 1.0,
            "source_type": "github",
        }
        for d in repo_dicts[:50]
        if d.get("url")
    ]
    merged_sources = _dedupe_by_url((state.get("sources") or []) + repo_sources)

    return {"github_repos": repo_dicts, "sources": merged_sources}


def synthesize_topic_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    client = get_smart_client()
    topic = (state.get("topic") or state.get("subject") or "").strip()

    plan = state.get("topic_plan") or {}
    subtopics = plan.get("subtopics") or state.get("topic_subtopics") or []
    subtopics = [s for s in subtopics if isinstance(s, str) and s.strip()]

    search_results = state.get("search_results") or []
    news = (state.get("topic_news") or {}).get("articles") or []
    repos = state.get("github_repos") or []

    # Keep context compact.
    top_results = search_results[:15]
    top_news = news[:10]
    top_repos = repos[:20]

    sources = state.get("sources") or []
    sources = _dedupe_by_url([s for s in sources if isinstance(s, dict) and s.get("url")])[:30]

    sources_md = "\n".join(
        [f"[{i}] {s.get('title','Source')} - {s.get('url')}" for i, s in enumerate(sources, 1)]
    )

    prompt = f"""
You are writing a rigorous topic research report in Markdown.

Topic: {topic}
Subtopics (if any): {json.dumps(subtopics[:12])}

Context (web search results, summarized):
{json.dumps(top_results, ensure_ascii=False)[:12000]}

Context (latest news articles, summarized):
{json.dumps(top_news, ensure_ascii=False)[:12000]}

Context (GitHub repos, summarized):
{json.dumps(top_repos, ensure_ascii=False)[:12000]}

Sources you MUST cite in-text using bracket numbers like [3], and include a final References section that lists all sources exactly once:
{sources_md}

Write sections:
1) Beginner-friendly introduction (definitions, motivation, prerequisites)
2) Core concepts (with simple examples)
3) Timeline of key milestones
4) Current state of the art (as of 2024-2025): best-known approaches, benchmarks, open-source landscape
5) Practical guidance: how to get started, what to build, common pitfalls
6) Open problems & research directions
7) References (numbered, matching citations)

Constraints:
- Be explicit when uncertain; don’t invent claims that aren’t supported by the provided context.
- Include at least 10 citations across the report.
"""

    result = client.complete(prompt=prompt, task_type=TaskType.SYNTHESIS.value)
    report_md = result.content.strip()

    return {
        "topic_report": report_md,
        "total_cost": result.cost,
        "total_tokens": {"input": result.input_tokens, "output": result.output_tokens},
    }


def topic_quality_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    report = (state.get("topic_report") or "").strip()
    if not report:
        return {
            "topic_quality": {"passed": False, "issues": ["missing_report"]},
            "topic_quality_passed": False,
            "quality_score": 0.0,
        }

    issues: List[str] = []
    sources = _dedupe_by_url(
        [s for s in (state.get("sources") or []) if isinstance(s, dict)], url_key="url"
    )
    if len(sources) < 10:
        issues.append("insufficient_sources")

    must_have = [
        "Beginner",
        "Core",
        "Timeline",
        "state of the art",
        "Open",
        "References",
    ]
    lower = report.lower()
    if lower.count("[") < 10:
        issues.append("not_enough_citations")
    if sources:
        # Ensure citations don't reference source indices we didn't provide.
        import re

        nums = [int(n) for n in re.findall(r"\[(\d+)\]", report) if n.isdigit()]
        if nums and max(nums) > len(sources):
            issues.append("citation_index_out_of_range")
    for key in must_have:
        if key.lower() not in lower:
            issues.append(f"missing_section:{key}")

    passed = len(issues) == 0
    return {
        "topic_quality": {"passed": passed, "issues": issues},
        "topic_quality_passed": passed,
        "quality_score": 90.0 if passed else 60.0,
    }


def refine_topic_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    client = get_smart_client()
    report = (state.get("topic_report") or "").strip()
    quality = state.get("topic_quality") or {}
    issues = quality.get("issues") or []

    sources = state.get("sources") or []
    sources = _dedupe_by_url([s for s in sources if isinstance(s, dict) and s.get("url")])[:30]
    sources_md = "\n".join(
        [f"[{i}] {s.get('title','Source')} - {s.get('url')}" for i, s in enumerate(sources, 1)]
    )

    prompt = f"""
You are revising a Markdown topic report to meet quality requirements.

Known issues: {json.dumps(issues)}

Sources (must cite using [n] and keep references aligned):
{sources_md}

Current report:
{report[:14000]}

Fix the issues with minimal churn:
- Ensure missing sections exist with clear headings.
- Ensure at least 10 citations [n] appear and correspond to the provided sources.
- Keep the References section numbered and deduplicated.

Return ONLY the revised Markdown report.
"""
    result = client.complete(prompt=prompt, task_type=TaskType.SYNTHESIS.value)
    return {
        "topic_report": result.content.strip(),
        "total_cost": result.cost,
        "total_tokens": {"input": result.input_tokens, "output": result.output_tokens},
    }
