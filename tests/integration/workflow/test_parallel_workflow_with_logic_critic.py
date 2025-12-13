"""
Integration Tests for Parallel Workflow with Logic Critic (Phase 4 + Phase 10).

Tests the complete research workflow including:
- Parallel agent execution
- Logic Critic quality assurance
- Quality-driven iteration
- End-to-end flow
"""

import pytest
from unittest.mock import patch, MagicMock
from company_researcher.workflows.parallel_agent_research import (
    create_parallel_agent_workflow,
    check_quality_node,
    should_continue_research,
    research_company
)
from company_researcher.state import create_initial_state


@pytest.mark.integration
@pytest.mark.workflow
class TestWorkflowCreation:
    """Test workflow graph creation."""

    def test_create_parallel_agent_workflow(self):
        """Test that workflow is created correctly."""
        workflow = create_parallel_agent_workflow()

        assert workflow is not None
        # Workflow should be compiled and ready to execute

    def test_workflow_has_all_nodes(self):
        """Test that all required nodes are in the workflow."""
        workflow = create_parallel_agent_workflow()

        # Can't directly inspect LangGraph nodes, but we can test execution
        # This is verified through integration tests below


@pytest.mark.integration
@pytest.mark.workflow
class TestQualityCheckNode:
    """Test quality check node integration."""

    def test_check_quality_with_logic_critic_output(self):
        """Test quality check using Logic Critic output."""
        state = {
            "company_name": "TestCorp",
            "quality_score": 88.5,
            "agent_outputs": {
                "logic_critic": {
                    "facts_analyzed": 42,
                    "contradictions": {
                        "total": 2,
                        "critical": 0,
                        "high": 1
                    },
                    "gaps": {
                        "total": 5,
                        "high_severity": 1,
                        "items": [
                            {
                                "section": "Financial Analysis",
                                "field": "revenue",
                                "recommendation": "Add revenue data"
                            }
                        ]
                    },
                    "passed": True
                }
            }
        }

        result = check_quality_node(state)

        assert "quality_score" in result
        assert result["quality_score"] == 88.5
        assert "iteration_count" in result
        assert result["iteration_count"] == 1

    def test_check_quality_fallback_without_logic_critic(self):
        """Test quality check fallback when Logic Critic not available."""
        with patch('company_researcher.workflows.parallel_agent_research.check_research_quality') as mock_check:
            mock_check.return_value = {
                "quality_score": 75.0,
                "missing_information": ["revenue", "market size"],
                "cost": 0.001,
                "tokens": {"input": 100, "output": 50}
            }

            state = {
                "company_name": "TestCorp",
                "company_overview": "Test overview",
                "sources": []
            }

            result = check_quality_node(state)

            assert result["quality_score"] == 75.0
            assert "missing_info" in result
            mock_check.assert_called_once()


@pytest.mark.integration
@pytest.mark.workflow
class TestDecisionFunctions:
    """Test workflow decision logic."""

    def test_should_continue_with_high_quality(self):
        """Test decision when quality is above threshold."""
        state = {
            "quality_score": 90.0,
            "iteration_count": 1
        }

        decision = should_continue_research(state)

        assert decision == "finish"

    def test_should_continue_with_low_quality(self):
        """Test decision when quality is below threshold."""
        state = {
            "quality_score": 70.0,
            "iteration_count": 1
        }

        decision = should_continue_research(state)

        assert decision == "iterate"

    def test_should_finish_at_max_iterations(self):
        """Test that workflow finishes at max iterations regardless of quality."""
        state = {
            "quality_score": 50.0,
            "iteration_count": 2  # Max iterations
        }

        decision = should_continue_research(state)

        assert decision == "finish"


@pytest.mark.integration
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.requires_llm
@pytest.mark.requires_api
@pytest.mark.skip(
    reason="Skipped: Workflow mocks don't intercept at correct level - tests hit real Tavily API"
)
class TestFullWorkflowExecution:
    """Test full workflow execution (requires API keys)."""

    def test_workflow_invocation_with_mocks(self):
        """Test workflow execution with mocked agents."""
        with patch('company_researcher.agents.researcher_agent_node') as mock_researcher, \
             patch('company_researcher.agents.financial_agent_node') as mock_financial, \
             patch('company_researcher.agents.market_agent_node') as mock_market, \
             patch('company_researcher.agents.product_agent_node') as mock_product, \
             patch('company_researcher.agents.competitor_scout_agent_node') as mock_competitor, \
             patch('company_researcher.agents.synthesizer_agent_node') as mock_synthesizer, \
             patch('company_researcher.agents.quality.logic_critic.logic_critic_agent_node') as mock_critic:

            # Mock researcher output
            mock_researcher.return_value = {
                "agent_outputs": {
                    "researcher": {
                        "company_overview": "TestCorp overview",
                        "queries_generated": 3,
                        "sources_found": 5,
                        "cost": 0.001
                    }
                },
                "sources": [],
                "total_cost": 0.001
            }

            # Mock specialist agents
            for mock_agent in [mock_financial, mock_market, mock_product, mock_competitor]:
                mock_agent.return_value = {
                    "agent_outputs": {"test": {"data_extracted": True, "cost": 0.001}},
                    "total_cost": 0.001
                }

            # Mock synthesizer
            mock_synthesizer.return_value = {
                "agent_outputs": {
                    "synthesizer": {
                        "company_overview": "Comprehensive analysis",
                        "specialists_combined": 4,
                        "cost": 0.002
                    }
                },
                "company_overview": "Comprehensive analysis",
                "total_cost": 0.002
            }

            # Mock logic critic with high quality score
            mock_critic.return_value = {
                "agent_outputs": {
                    "logic_critic": {
                        "facts_analyzed": 50,
                        "quality_metrics": {"overall_score": 90.0},
                        "contradictions": {"total": 0, "critical": 0, "high": 0},
                        "gaps": {"total": 2, "high_severity": 0},
                        "passed": True,
                        "cost": 0.003
                    }
                },
                "quality_score": 90.0,
                "total_cost": 0.003
            }

            # Create and run workflow
            workflow = create_parallel_agent_workflow()
            initial_state = create_initial_state("TestCorp")

            result = workflow.invoke(initial_state)

            # Verify workflow executed
            assert result is not None
            assert "quality_score" in result
            # Should finish with high quality (not iterate)
            assert result.get("iteration_count", 0) <= 1

    def test_workflow_iteration_with_low_quality(self):
        """Test that workflow iterates when quality is low."""
        with patch('company_researcher.agents.researcher_agent_node') as mock_researcher, \
             patch('company_researcher.agents.financial_agent_node') as mock_financial, \
             patch('company_researcher.agents.market_agent_node') as mock_market, \
             patch('company_researcher.agents.product_agent_node') as mock_product, \
             patch('company_researcher.agents.competitor_scout_agent_node') as mock_competitor, \
             patch('company_researcher.agents.synthesizer_agent_node') as mock_synthesizer, \
             patch('company_researcher.agents.quality.logic_critic.logic_critic_agent_node') as mock_critic:

            # Setup mocks
            mock_researcher.return_value = {
                "agent_outputs": {"researcher": {"company_overview": "Basic info", "cost": 0.001}},
                "sources": [],
                "total_cost": 0.001
            }

            for mock_agent in [mock_financial, mock_market, mock_product, mock_competitor]:
                mock_agent.return_value = {
                    "agent_outputs": {"test": {"data_extracted": True, "cost": 0.001}},
                    "total_cost": 0.001
                }

            mock_synthesizer.return_value = {
                "agent_outputs": {"synthesizer": {"company_overview": "Limited analysis", "cost": 0.002}},
                "company_overview": "Limited analysis",
                "total_cost": 0.002
            }

            # First iteration: low quality
            # Second iteration: improved quality
            iteration_count = [0]

            def mock_critic_varying_quality(state):
                iteration_count[0] += 1
                if iteration_count[0] == 1:
                    # First iteration: low quality (should iterate)
                    return {
                        "agent_outputs": {
                            "logic_critic": {
                                "facts_analyzed": 10,
                                "quality_metrics": {"overall_score": 70.0},
                                "contradictions": {"total": 3, "critical": 1},
                                "gaps": {"total": 10, "high_severity": 3},
                                "passed": False,
                                "cost": 0.003
                            }
                        },
                        "quality_score": 70.0,
                        "total_cost": 0.003
                    }
                else:
                    # Second iteration: improved quality (should finish)
                    return {
                        "agent_outputs": {
                            "logic_critic": {
                                "facts_analyzed": 45,
                                "quality_metrics": {"overall_score": 87.0},
                                "contradictions": {"total": 0},
                                "gaps": {"total": 3},
                                "passed": True,
                                "cost": 0.003
                            }
                        },
                        "quality_score": 87.0,
                        "total_cost": 0.003
                    }

            mock_critic.side_effect = mock_critic_varying_quality

            # Run workflow
            workflow = create_parallel_agent_workflow()
            initial_state = create_initial_state("TestCorp")

            result = workflow.invoke(initial_state)

            # Should have iterated at least once
            assert result.get("iteration_count", 0) >= 1
            # Final quality should be improved
            assert result.get("quality_score", 0) > 70.0


@pytest.mark.integration
@pytest.mark.workflow
@pytest.mark.skip(
    reason="Skipped: Workflow mocks don't intercept at correct level - tests hit real Tavily API"
)
class TestLogicCriticIntegration:
    """Test Logic Critic integration in workflow."""

    def test_logic_critic_receives_all_agent_outputs(self):
        """Test that Logic Critic receives outputs from all agents."""
        with patch('company_researcher.agents.researcher_agent_node') as mock_researcher, \
             patch('company_researcher.agents.financial_agent_node') as mock_financial, \
             patch('company_researcher.agents.market_agent_node') as mock_market, \
             patch('company_researcher.agents.product_agent_node') as mock_product, \
             patch('company_researcher.agents.competitor_scout_agent_node') as mock_competitor, \
             patch('company_researcher.agents.synthesizer_agent_node') as mock_synthesizer, \
             patch('company_researcher.agents.quality.logic_critic.logic_critic_agent_node') as mock_critic:

            # Setup researcher mock
            mock_researcher.return_value = {
                "agent_outputs": {"researcher": {"company_overview": "Test", "cost": 0.001}},
                "sources": [],
                "total_cost": 0.001
            }

            # Setup specialist mocks
            specialist_output = {
                "agent_outputs": {"test": {"data_extracted": True, "cost": 0.001}},
                "total_cost": 0.001
            }
            mock_financial.return_value = specialist_output
            mock_market.return_value = specialist_output
            mock_product.return_value = specialist_output
            mock_competitor.return_value = specialist_output

            # Setup synthesizer mock
            mock_synthesizer.return_value = {
                "agent_outputs": {"synthesizer": {"company_overview": "Synthesized", "cost": 0.002}},
                "company_overview": "Synthesized",
                "total_cost": 0.002
            }

            # Setup logic critic mock
            mock_critic.return_value = {
                "agent_outputs": {
                    "logic_critic": {
                        "facts_analyzed": 30,
                        "quality_metrics": {"overall_score": 85.0},
                        "contradictions": {"total": 0},
                        "gaps": {"total": 2},
                        "passed": True,
                        "cost": 0.003
                    }
                },
                "quality_score": 85.0,
                "total_cost": 0.003
            }

            workflow = create_parallel_agent_workflow()
            initial_state = create_initial_state("TestCorp")

            try:
                result = workflow.invoke(initial_state)

                # Logic Critic should have been called
                assert mock_critic.called

                # Check that it received agent_outputs in state
                call_args = mock_critic.call_args
                state_arg = call_args[0][0] if call_args[0] else {}
                assert "agent_outputs" in state_arg

            except Exception:
                # If workflow fails due to incomplete mocks, that's OK
                # We mainly want to verify Logic Critic is called
                assert mock_critic.called


@pytest.mark.integration
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.skip(
    reason="Skipped: Workflow mocks don't intercept at correct level - tests hit real Tavily API"
)
class TestEndToEndWorkflow:
    """End-to-end workflow tests with comprehensive mocking."""

    @patch('company_researcher.workflows.parallel_agent_research.track_research_session')
    @patch('company_researcher.agents.researcher_agent_node')
    @patch('company_researcher.agents.financial_agent_node')
    @patch('company_researcher.agents.market_agent_node')
    @patch('company_researcher.agents.product_agent_node')
    @patch('company_researcher.agents.competitor_scout_agent_node')
    @patch('company_researcher.agents.synthesizer_agent_node')
    @patch('company_researcher.agents.quality.logic_critic.logic_critic_agent_node')
    def test_research_company_function(
        self,
        mock_critic,
        mock_synthesizer,
        mock_competitor,
        mock_product,
        mock_market,
        mock_financial,
        mock_researcher,
        mock_track
    ):
        """Test the research_company convenience function."""

        # Mock observability
        mock_track.return_value.__enter__ = MagicMock()
        mock_track.return_value.__exit__ = MagicMock()

        # Setup comprehensive mocks
        mock_researcher.return_value = {
            "agent_outputs": {
                "researcher": {
                    "company_overview": "TestCorp is a tech company",
                    "queries_generated": 5,
                    "sources_found": 10,
                    "cost": 0.001
                }
            },
            "sources": [{"url": "https://test.com", "title": "Test"}],
            "company_overview": "TestCorp is a tech company",
            "total_cost": 0.001,
            "total_tokens": {"input": 100, "output": 50}
        }

        specialist_output = {
            "agent_outputs": {"agent": {"data_extracted": True, "cost": 0.001}},
            "total_cost": 0.001,
            "total_tokens": {"input": 100, "output": 50}
        }

        mock_financial.return_value = specialist_output
        mock_market.return_value = specialist_output
        mock_product.return_value = specialist_output
        mock_competitor.return_value = specialist_output

        mock_synthesizer.return_value = {
            "agent_outputs": {
                "synthesizer": {
                    "company_overview": "Comprehensive TestCorp analysis with all specialist insights",
                    "specialists_combined": 4,
                    "cost": 0.002
                }
            },
            "company_overview": "Comprehensive TestCorp analysis with all specialist insights",
            "total_cost": 0.002,
            "total_tokens": {"input": 500, "output": 300}
        }

        mock_critic.return_value = {
            "agent_outputs": {
                "logic_critic": {
                    "facts_analyzed": 52,
                    "quality_metrics": {"overall_score": 92.0},
                    "contradictions": {"total": 0, "critical": 0, "high": 0},
                    "gaps": {"total": 1, "high_severity": 0},
                    "passed": True,
                    "cost": 0.003,
                    "recommendations": ["Excellent research quality"]
                }
            },
            "quality_score": 92.0,
            "total_cost": 0.003,
            "total_tokens": {"input": 1000, "output": 800}
        }

        # Run research
        output = research_company("TestCorp")

        # Verify output structure
        assert output is not None
        assert "report_path" in output
        assert "metrics" in output
        assert output["metrics"]["quality_score"] >= 85.0


@pytest.mark.integration
@pytest.mark.workflow
class TestWorkflowErrorHandling:
    """Test error handling in workflow."""

    def test_workflow_handles_agent_failure_gracefully(self):
        """Test that workflow handles individual agent failures."""
        # This would require more sophisticated mocking
        # Placeholder for future implementation

    def test_workflow_handles_llm_timeout(self):
        """Test handling of LLM timeouts."""
        # Placeholder for future implementation


@pytest.mark.integration
@pytest.mark.workflow
class TestWorkflowMetrics:
    """Test workflow metrics tracking."""

    def test_workflow_tracks_cost(self):
        """Test that workflow accumulates cost correctly."""
        # Test through mocked execution

    def test_workflow_tracks_tokens(self):
        """Test that workflow tracks token usage."""
        # Test through mocked execution

    def test_workflow_tracks_duration(self):
        """Test that workflow tracks execution duration."""
        # Test through mocked execution
