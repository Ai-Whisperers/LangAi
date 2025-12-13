"""
GitHub API Client.

Free tier: 60 requests/hour (unauthenticated), 5,000/hour (authenticated)
Provides: Repository data, organization info, code search

Documentation: https://docs.github.com/en/rest
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base_client import BaseAPIClient
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class GitHubRepo:
    """GitHub repository data."""
    name: str
    full_name: str
    description: str
    url: str
    homepage: Optional[str]
    stars: int
    forks: int
    watchers: int
    language: str
    open_issues: int
    created_at: str
    updated_at: str
    pushed_at: str
    topics: List[str]
    is_fork: bool
    is_archived: bool

    @classmethod
    def from_dict(cls, data: Dict) -> "GitHubRepo":
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description", "") or "",
            url=data.get("html_url", ""),
            homepage=data.get("homepage"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            language=data.get("language", "") or "",
            open_issues=data.get("open_issues_count", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            pushed_at=data.get("pushed_at", ""),
            topics=data.get("topics", []),
            is_fork=data.get("fork", False),
            is_archived=data.get("archived", False)
        )


@dataclass
class GitHubOrg:
    """GitHub organization data."""
    login: str
    name: str
    description: str
    blog: str
    location: str
    email: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    avatar_url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "GitHubOrg":
        return cls(
            login=data.get("login", ""),
            name=data.get("name", "") or "",
            description=data.get("description", "") or "",
            blog=data.get("blog", "") or "",
            location=data.get("location", "") or "",
            email=data.get("email", "") or "",
            public_repos=data.get("public_repos", 0),
            public_gists=data.get("public_gists", 0),
            followers=data.get("followers", 0),
            following=data.get("following", 0),
            created_at=data.get("created_at", ""),
            avatar_url=data.get("avatar_url", "")
        )


@dataclass
class GitHubUser:
    """GitHub user data."""
    login: str
    name: str
    company: str
    blog: str
    location: str
    email: str
    bio: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict) -> "GitHubUser":
        return cls(
            login=data.get("login", ""),
            name=data.get("name", "") or "",
            company=data.get("company", "") or "",
            blog=data.get("blog", "") or "",
            location=data.get("location", "") or "",
            email=data.get("email", "") or "",
            bio=data.get("bio", "") or "",
            public_repos=data.get("public_repos", 0),
            public_gists=data.get("public_gists", 0),
            followers=data.get("followers", 0),
            following=data.get("following", 0),
            created_at=data.get("created_at", "")
        )


class GitHubClient(BaseAPIClient):
    """
    GitHub API Client.

    Unauthenticated: 60 requests/hour
    Authenticated: 5,000 requests/hour

    Features:
    - Organization profiles
    - Repository data
    - User profiles
    - Code search
    - Repository search
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        super().__init__(
            api_key=token,
            env_var="GITHUB_TOKEN",
            cache_ttl=3600,
            rate_limit_calls=5000 if token else 60,
            rate_limit_period=3600.0
        )

    def _get_headers(self) -> Dict[str, str]:
        """Add GitHub-specific headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # =========================================================================
    # Organizations
    # =========================================================================

    async def get_organization(self, org_name: str) -> Optional[GitHubOrg]:
        """
        Get organization profile.

        Args:
            org_name: Organization login/username

        Returns:
            GitHubOrg or None
        """
        try:
            data = await self._request(f"orgs/{org_name}")
            return GitHubOrg.from_dict(data) if data else None
        except Exception as e:
            logger.warning(f"Error fetching org {org_name}: {e}")
            return None

    async def get_org_repos(
        self,
        org_name: str,
        sort: str = "stars",
        per_page: int = 30,
        page: int = 1
    ) -> List[GitHubRepo]:
        """
        Get organization's repositories.

        Args:
            org_name: Organization login
            sort: Sort by (created, updated, pushed, full_name, stars)
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of GitHubRepo objects
        """
        try:
            data = await self._request(
                f"orgs/{org_name}/repos",
                {"sort": sort, "per_page": min(per_page, 100), "page": page}
            )
            return [GitHubRepo.from_dict(repo) for repo in (data or [])]
        except Exception as e:
            logger.warning(f"Error fetching repos for {org_name}: {e}")
            return []

    # =========================================================================
    # Users
    # =========================================================================

    async def get_user(self, username: str) -> Optional[GitHubUser]:
        """
        Get user profile.

        Args:
            username: GitHub username

        Returns:
            GitHubUser or None
        """
        try:
            data = await self._request(f"users/{username}")
            return GitHubUser.from_dict(data) if data else None
        except Exception as e:
            logger.warning(f"Error fetching user {username}: {e}")
            return None

    async def get_user_repos(
        self,
        username: str,
        sort: str = "stars",
        per_page: int = 30
    ) -> List[GitHubRepo]:
        """
        Get user's repositories.

        Args:
            username: GitHub username
            sort: Sort by (created, updated, pushed, full_name)
            per_page: Results per page

        Returns:
            List of GitHubRepo objects
        """
        try:
            data = await self._request(
                f"users/{username}/repos",
                {"sort": sort, "per_page": min(per_page, 100)}
            )
            return [GitHubRepo.from_dict(repo) for repo in (data or [])]
        except Exception as e:
            logger.warning(f"Error fetching repos for user {username}: {e}")
            return []

    # =========================================================================
    # Repositories
    # =========================================================================

    async def get_repo(self, owner: str, repo: str) -> Optional[GitHubRepo]:
        """
        Get repository details.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            GitHubRepo or None
        """
        try:
            data = await self._request(f"repos/{owner}/{repo}")
            return GitHubRepo.from_dict(data) if data else None
        except Exception as e:
            logger.warning(f"Error fetching repo {owner}/{repo}: {e}")
            return None

    async def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get repository language breakdown.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dict mapping language to bytes of code
        """
        try:
            return await self._request(f"repos/{owner}/{repo}/languages") or {}
        except Exception as e:
            logger.warning(f"Error fetching languages for {owner}/{repo}: {e}")
            return {}

    async def get_repo_contributors(
        self,
        owner: str,
        repo: str,
        per_page: int = 30
    ) -> List[Dict]:
        """
        Get repository contributors.

        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Results per page

        Returns:
            List of contributor dicts with login and contributions count
        """
        try:
            return await self._request(
                f"repos/{owner}/{repo}/contributors",
                {"per_page": min(per_page, 100)}
            ) or []
        except Exception as e:
            logger.warning(f"Error fetching contributors for {owner}/{repo}: {e}")
            return []

    # =========================================================================
    # Search
    # =========================================================================

    async def search_repos(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10
    ) -> List[GitHubRepo]:
        """
        Search for repositories.

        Args:
            query: Search query (supports GitHub search syntax)
            sort: Sort by (stars, forks, help-wanted-issues, updated)
            order: Sort order (asc, desc)
            per_page: Results per page

        Returns:
            List of GitHubRepo objects

        Query examples:
            - "machine learning language:python"
            - "org:microsoft"
            - "topic:ai stars:>1000"
        """
        try:
            data = await self._request(
                "search/repositories",
                {"q": query, "sort": sort, "order": order, "per_page": per_page}
            )
            items = data.get("items", []) if data else []
            return [GitHubRepo.from_dict(repo) for repo in items]
        except Exception as e:
            logger.warning(f"Error searching repos: {e}")
            return []

    async def search_code(
        self,
        query: str,
        per_page: int = 10
    ) -> List[Dict]:
        """
        Search for code.

        Args:
            query: Search query (supports GitHub code search syntax)
            per_page: Results per page

        Returns:
            List of code search results

        Query examples:
            - "function calculateTotal language:javascript"
            - "org:facebook filename:package.json"
        """
        try:
            data = await self._request(
                "search/code",
                {"q": query, "per_page": per_page}
            )
            return data.get("items", []) if data else []
        except Exception as e:
            logger.warning(f"Error searching code: {e}")
            return []

    # =========================================================================
    # Company Analysis
    # =========================================================================

    async def analyze_company_github(
        self,
        org_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive GitHub analysis for a company.

        Args:
            org_name: GitHub organization name

        Returns:
            Dict with organization info, repos, languages, and metrics
        """
        result = {
            "organization": None,
            "repos": [],
            "metrics": {
                "total_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "languages": {},
                "avg_stars_per_repo": 0
            },
            "top_repos": [],
            "popular_topics": []
        }

        # Get organization
        org = await self.get_organization(org_name)
        if org:
            result["organization"] = {
                "name": org.name,
                "description": org.description,
                "location": org.location,
                "blog": org.blog,
                "public_repos": org.public_repos,
                "followers": org.followers
            }

        # Get repositories
        repos = await self.get_org_repos(org_name, per_page=100)
        result["repos"] = repos
        result["metrics"]["total_repos"] = len(repos)

        if repos:
            # Calculate metrics
            result["metrics"]["total_stars"] = sum(r.stars for r in repos)
            result["metrics"]["total_forks"] = sum(r.forks for r in repos)
            result["metrics"]["avg_stars_per_repo"] = round(
                result["metrics"]["total_stars"] / len(repos), 1
            )

            # Language distribution
            languages = {}
            for repo in repos:
                if repo.language:
                    languages[repo.language] = languages.get(repo.language, 0) + 1
            result["metrics"]["languages"] = dict(
                sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]
            )

            # Top repos by stars
            top_repos = sorted(repos, key=lambda x: x.stars, reverse=True)[:10]
            result["top_repos"] = [
                {
                    "name": r.name,
                    "description": r.description[:100] if r.description else "",
                    "stars": r.stars,
                    "forks": r.forks,
                    "language": r.language,
                    "url": r.url
                }
                for r in top_repos
            ]

            # Popular topics
            topics = {}
            for repo in repos:
                for topic in repo.topics:
                    topics[topic] = topics.get(topic, 0) + 1
            result["popular_topics"] = [
                t for t, _ in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:15]
            ]

        return result
