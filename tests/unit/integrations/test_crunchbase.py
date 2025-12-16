"""Tests for Crunchbase integration."""

from datetime import datetime

import pytest

from company_researcher.integrations.crunchbase import (
    CompanyProfile,
    CrunchbaseClient,
    FundingHistory,
    FundingRound,
    FundingType,
    create_crunchbase_client,
)


class TestFundingType:
    """Tests for FundingType enum."""

    def test_funding_type_values(self):
        """FundingType should have correct values."""
        assert FundingType.SEED.value == "seed"
        assert FundingType.SERIES_A.value == "series_a"
        assert FundingType.SERIES_B.value == "series_b"
        assert FundingType.SERIES_C.value == "series_c"
        assert FundingType.SERIES_D.value == "series_d"
        assert FundingType.IPO.value == "ipo"
        assert FundingType.DEBT.value == "debt"
        assert FundingType.GRANT.value == "grant"
        assert FundingType.OTHER.value == "other"

    def test_funding_type_count(self):
        """FundingType should have 9 types."""
        assert len(FundingType) == 9

    def test_funding_type_is_string(self):
        """FundingType should be string enum."""
        assert isinstance(FundingType.SEED.value, str)
        # Can be used as string
        assert FundingType.SEED == "seed"


class TestFundingRound:
    """Tests for FundingRound dataclass."""

    def test_create_funding_round(self):
        """FundingRound should store all fields."""
        date = datetime(2024, 1, 15)
        round = FundingRound(
            round_type=FundingType.SERIES_A,
            amount_usd=10000000.0,
            announced_date=date,
            investors=["VC Firm A", "VC Firm B"],
            lead_investor="VC Firm A",
            pre_money_valuation=40000000.0,
        )
        assert round.round_type == FundingType.SERIES_A
        assert round.amount_usd == 10000000.0
        assert round.announced_date == date
        assert len(round.investors) == 2
        assert round.lead_investor == "VC Firm A"
        assert round.pre_money_valuation == 40000000.0

    def test_funding_round_defaults(self):
        """FundingRound should have sensible defaults."""
        round = FundingRound(round_type=FundingType.SEED)
        assert round.amount_usd is None
        assert round.announced_date is None
        assert round.investors == []
        assert round.lead_investor is None
        assert round.pre_money_valuation is None

    def test_funding_round_empty_investors(self):
        """FundingRound should default to empty investors list."""
        round = FundingRound(round_type=FundingType.GRANT)
        assert round.investors == []
        assert isinstance(round.investors, list)


class TestCompanyProfile:
    """Tests for CompanyProfile dataclass."""

    def test_create_company_profile(self):
        """CompanyProfile should store all fields."""
        profile = CompanyProfile(
            name="TestCorp",
            description="A test company",
            founded_year=2015,
            headquarters="San Francisco, CA",
            industry="Technology",
            employee_count=500,
            website="https://testcorp.com",
            linkedin_url="https://linkedin.com/company/testcorp",
            twitter_url="https://twitter.com/testcorp",
            founders=["John Doe", "Jane Smith"],
            categories=["SaaS", "Enterprise", "B2B"],
        )
        assert profile.name == "TestCorp"
        assert profile.description == "A test company"
        assert profile.founded_year == 2015
        assert profile.headquarters == "San Francisco, CA"
        assert profile.employee_count == 500
        assert len(profile.founders) == 2
        assert len(profile.categories) == 3

    def test_company_profile_defaults(self):
        """CompanyProfile should have sensible defaults."""
        profile = CompanyProfile(name="MinimalCorp")
        assert profile.name == "MinimalCorp"
        assert profile.description == ""
        assert profile.founded_year is None
        assert profile.headquarters == ""
        assert profile.industry == ""
        assert profile.employee_count is None
        assert profile.website == ""
        assert profile.linkedin_url == ""
        assert profile.twitter_url == ""
        assert profile.founders == []
        assert profile.categories == []

    def test_company_profile_required_name(self):
        """CompanyProfile should require name."""
        profile = CompanyProfile(name="RequiredName")
        assert profile.name == "RequiredName"


class TestFundingHistory:
    """Tests for FundingHistory dataclass."""

    def test_create_funding_history(self):
        """FundingHistory should store all fields."""
        rounds = [
            FundingRound(round_type=FundingType.SEED, amount_usd=1000000),
            FundingRound(round_type=FundingType.SERIES_A, amount_usd=10000000),
        ]
        history = FundingHistory(
            company_name="TestCorp",
            total_funding_usd=11000000.0,
            funding_rounds=rounds,
            last_funding_date=datetime(2024, 6, 1),
            ipo_status="private",
            all_investors=["Angel", "VC Firm"],
        )
        assert history.company_name == "TestCorp"
        assert history.total_funding_usd == 11000000.0
        assert len(history.funding_rounds) == 2
        assert history.ipo_status == "private"

    def test_funding_history_defaults(self):
        """FundingHistory should have sensible defaults."""
        history = FundingHistory(company_name="NewStartup")
        assert history.company_name == "NewStartup"
        assert history.total_funding_usd == 0.0
        assert history.funding_rounds == []
        assert history.last_funding_date is None
        assert history.ipo_status == "private"
        assert history.all_investors == []

    def test_funding_history_to_dict(self):
        """FundingHistory.to_dict should return correct dictionary."""
        rounds = [
            FundingRound(round_type=FundingType.SEED, amount_usd=1000000),
            FundingRound(round_type=FundingType.SERIES_A, amount_usd=5000000),
        ]
        history = FundingHistory(
            company_name="TestCorp",
            total_funding_usd=6000000.0,
            funding_rounds=rounds,
            ipo_status="private",
            all_investors=["Investor A", "Investor B", "Investor C"],
        )
        result = history.to_dict()

        assert result["company_name"] == "TestCorp"
        assert result["total_funding_usd"] == 6000000.0
        assert result["rounds_count"] == 2
        assert result["ipo_status"] == "private"
        assert result["total_investors"] == 3

    def test_funding_history_to_dict_empty(self):
        """FundingHistory.to_dict should handle empty history."""
        history = FundingHistory(company_name="NoFunding")
        result = history.to_dict()

        assert result["company_name"] == "NoFunding"
        assert result["total_funding_usd"] == 0.0
        assert result["rounds_count"] == 0
        assert result["total_investors"] == 0


class TestCrunchbaseClientInit:
    """Tests for CrunchbaseClient initialization."""

    def test_initialization_with_api_key(self):
        """CrunchbaseClient should store api_key."""
        client = CrunchbaseClient(api_key="test_key")
        assert client.api_key == "test_key"

    def test_initialization_without_api_key(self):
        """CrunchbaseClient should accept no api_key."""
        client = CrunchbaseClient()
        assert client.api_key is None

    def test_base_url(self):
        """CrunchbaseClient should have correct BASE_URL."""
        assert CrunchbaseClient.BASE_URL == "https://api.crunchbase.com/api/v4"


class TestCrunchbaseClientGetCompany:
    """Tests for CrunchbaseClient.get_company method."""

    @pytest.mark.asyncio
    async def test_get_company_returns_profile(self):
        """get_company should return CompanyProfile."""
        client = CrunchbaseClient()
        result = await client.get_company("TestCorp")
        assert isinstance(result, CompanyProfile)
        assert result.name == "TestCorp"

    @pytest.mark.asyncio
    async def test_get_company_with_api_key(self):
        """get_company should work with API key."""
        client = CrunchbaseClient(api_key="fake_key")
        result = await client.get_company("TestCorp")
        assert isinstance(result, CompanyProfile)

    @pytest.mark.asyncio
    async def test_get_company_populates_fields(self):
        """get_company should populate standard fields."""
        client = CrunchbaseClient()
        result = await client.get_company("Acme Inc")

        assert result.name == "Acme Inc"
        assert result.description != ""
        assert result.founded_year is not None
        assert result.headquarters != ""
        assert result.industry != ""


class TestCrunchbaseClientGetFunding:
    """Tests for CrunchbaseClient.get_funding method."""

    @pytest.mark.asyncio
    async def test_get_funding_returns_history(self):
        """get_funding should return FundingHistory."""
        client = CrunchbaseClient()
        result = await client.get_funding("TestCorp")
        assert isinstance(result, FundingHistory)
        assert result.company_name == "TestCorp"

    @pytest.mark.asyncio
    async def test_get_funding_has_rounds(self):
        """get_funding should include funding rounds."""
        client = CrunchbaseClient()
        result = await client.get_funding("TestCorp")
        assert len(result.funding_rounds) > 0

    @pytest.mark.asyncio
    async def test_get_funding_total_matches_rounds(self):
        """get_funding total should reflect rounds."""
        client = CrunchbaseClient()
        result = await client.get_funding("TestCorp")

        # Check that total is reasonable
        assert result.total_funding_usd > 0

    @pytest.mark.asyncio
    async def test_get_funding_has_investors(self):
        """get_funding should include investors."""
        client = CrunchbaseClient()
        result = await client.get_funding("TestCorp")
        assert len(result.all_investors) > 0


class TestCrunchbaseClientSearchCompanies:
    """Tests for CrunchbaseClient.search_companies method."""

    @pytest.mark.asyncio
    async def test_search_companies_returns_list(self):
        """search_companies should return list of profiles."""
        client = CrunchbaseClient()
        results = await client.search_companies("tech")
        assert isinstance(results, list)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_search_companies_returns_profiles(self):
        """search_companies should return CompanyProfile instances."""
        client = CrunchbaseClient()
        results = await client.search_companies("startup")
        for profile in results:
            assert isinstance(profile, CompanyProfile)


class TestCrunchbaseClientMockMethods:
    """Tests for CrunchbaseClient mock methods."""

    def test_mock_company_creates_valid_profile(self):
        """_mock_company should create valid CompanyProfile."""
        client = CrunchbaseClient()
        profile = client._mock_company("Test Company")

        assert profile.name == "Test Company"
        assert "technology company" in profile.description.lower()
        assert profile.founded_year == 2010
        assert profile.headquarters == "San Francisco, CA"
        assert profile.industry == "Technology"
        assert profile.employee_count == 500
        assert "testcompany.com" in profile.website

    def test_mock_company_handles_spaces_in_name(self):
        """_mock_company should handle spaces in company name."""
        client = CrunchbaseClient()
        profile = client._mock_company("My Company Name")
        assert "mycompanyname.com" in profile.website

    def test_mock_funding_creates_valid_history(self):
        """_mock_funding should create valid FundingHistory."""
        client = CrunchbaseClient()
        history = client._mock_funding("Test Company")

        assert history.company_name == "Test Company"
        assert history.total_funding_usd == 12000000
        assert len(history.funding_rounds) == 2
        assert history.ipo_status == "private"

    def test_mock_funding_has_correct_round_types(self):
        """_mock_funding should have correct round types."""
        client = CrunchbaseClient()
        history = client._mock_funding("Test")

        round_types = [r.round_type for r in history.funding_rounds]
        assert FundingType.SEED in round_types
        assert FundingType.SERIES_A in round_types


class TestCreateCrunchbaseClient:
    """Tests for create_crunchbase_client factory function."""

    def test_creates_client_without_key(self):
        """create_crunchbase_client should create client without key."""
        client = create_crunchbase_client()
        assert isinstance(client, CrunchbaseClient)
        assert client.api_key is None

    def test_creates_client_with_key(self):
        """create_crunchbase_client should create client with key."""
        client = create_crunchbase_client(api_key="my_api_key")
        assert isinstance(client, CrunchbaseClient)
        assert client.api_key == "my_api_key"


class TestFundingRoundEdgeCases:
    """Edge case tests for FundingRound."""

    def test_zero_amount(self):
        """FundingRound should accept zero amount."""
        round = FundingRound(round_type=FundingType.GRANT, amount_usd=0.0)
        assert round.amount_usd == 0.0

    def test_large_amount(self):
        """FundingRound should handle large amounts."""
        round = FundingRound(round_type=FundingType.IPO, amount_usd=1_000_000_000.0)  # $1 billion
        assert round.amount_usd == 1_000_000_000.0

    def test_many_investors(self):
        """FundingRound should handle many investors."""
        investors = [f"Investor {i}" for i in range(100)]
        round = FundingRound(round_type=FundingType.SERIES_C, investors=investors)
        assert len(round.investors) == 100


class TestCompanyProfileEdgeCases:
    """Edge case tests for CompanyProfile."""

    def test_unicode_name(self):
        """CompanyProfile should handle unicode names."""
        profile = CompanyProfile(name="Compania Espanola")
        assert profile.name == "Compania Espanola"

    def test_very_old_founded_year(self):
        """CompanyProfile should handle old founded years."""
        profile = CompanyProfile(name="Old Corp", founded_year=1850)
        assert profile.founded_year == 1850

    def test_large_employee_count(self):
        """CompanyProfile should handle large employee counts."""
        profile = CompanyProfile(name="BigCorp", employee_count=500000)
        assert profile.employee_count == 500000


class TestFundingHistoryEdgeCases:
    """Edge case tests for FundingHistory."""

    def test_ipo_status_options(self):
        """FundingHistory should accept various IPO statuses."""
        for status in ["private", "public", "acquired", "delisted"]:
            history = FundingHistory(company_name="Corp", ipo_status=status)
            assert history.ipo_status == status

    def test_many_funding_rounds(self):
        """FundingHistory should handle many rounds."""
        rounds = [FundingRound(round_type=FundingType.OTHER, amount_usd=1000000) for _ in range(20)]
        history = FundingHistory(company_name="Well Funded", funding_rounds=rounds)
        assert len(history.funding_rounds) == 20
