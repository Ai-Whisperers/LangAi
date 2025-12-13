"""
Celery Tasks for Research Operations.

Provides asynchronous task processing for:
- Single company research
- Batch company processing
- Scheduled updates
- Report generation

Configuration:
    Set REDIS_URL environment variable for broker/backend:
    export REDIS_URL=redis://localhost:6379/0

Usage:
    # Start worker
    celery -A company_researcher.tasks worker --loglevel=info

    # Start scheduler (for periodic tasks)
    celery -A company_researcher.tasks beat --loglevel=info

    # From code
    from company_researcher.tasks import research_single_company
    result = research_single_company.delay("Tesla")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils import get_config, utc_now

try:
    from celery import Celery, group
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None


# Initialize Celery app
if CELERY_AVAILABLE:
    app = Celery(
        'research_tasks',
        broker=get_config('REDIS_URL', default='redis://localhost:6379/0'),
        backend=get_config('REDIS_URL', default='redis://localhost:6379/0')
    )

    # Celery configuration
    app.conf.update(
        # Serialization
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',

        # Timezone
        timezone='UTC',
        enable_utc=True,

        # Task tracking
        task_track_started=True,
        task_time_limit=600,  # 10 minutes max per task
        task_soft_time_limit=540,  # Soft limit at 9 minutes

        # Result expiration
        result_expires=86400,  # Results expire after 24 hours

        # Worker settings
        worker_prefetch_multiplier=1,  # One task at a time
        worker_concurrency=4,  # 4 concurrent workers

        # Task routing (optional)
        task_routes={
            'research.*': {'queue': 'research'},
            'reports.*': {'queue': 'reports'},
        },

        # Retry settings
        task_default_retry_delay=60,  # 1 minute between retries
        task_max_retries=3,
    )

    @app.task(bind=True, name='research.single_company')
    def research_single_company(
        self,
        company_name: str,
        config: Optional[Dict] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Execute research for a single company.

        Args:
            company_name: Company to research
            config: Optional configuration override
            save_to_db: Whether to save results to database

        Returns:
            Research results dictionary
        """
        from ..workflows.parallel_agent_research import run_parallel_research
        from ..database import get_repository

        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Starting research',
                'company': company_name,
                'started_at': utc_now().isoformat()
            }
        )

        try:
            # Create database record
            repo = get_repository() if save_to_db else None
            run = None
            if repo:
                run = repo.create_research_run(
                    company_name=company_name,
                    config_snapshot=config,
                    triggered_by='celery_task'
                )

            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Running research workflow',
                    'company': company_name,
                    'run_id': run.run_id if run else None
                }
            )

            # Run research
            result = run_parallel_research(company_name, config)

            # Save to database
            if repo and run:
                # Save agent outputs
                for agent_name, output in result.get('agent_outputs', {}).items():
                    repo.save_agent_output(
                        research_run_id=run.id,
                        agent_name=agent_name,
                        analysis=output.get('analysis', ''),
                        cost=output.get('cost', 0),
                        input_tokens=output.get('tokens', {}).get('input', 0),
                        output_tokens=output.get('tokens', {}).get('output', 0)
                    )

                # Save sources
                repo.save_sources_bulk(run.id, result.get('sources', []))

                # Complete run
                repo.complete_research_run(
                    run_id=run.run_id,
                    total_cost=result.get('total_cost', 0),
                    total_input_tokens=result.get('total_tokens', {}).get('input', 0),
                    total_output_tokens=result.get('total_tokens', {}).get('output', 0)
                )

            return {
                'status': 'completed',
                'company': company_name,
                'run_id': run.run_id if run else None,
                'total_cost': result.get('total_cost', 0),
                'completed_at': utc_now().isoformat()
            }

        except Exception as e:
            # Mark as failed in database
            if repo and run:
                repo.fail_research_run(run.run_id, str(e))

            # Raise for Celery retry
            raise self.retry(exc=e)

    @app.task(bind=True, name='research.batch_companies')
    def research_batch_companies(
        self,
        company_names: List[str],
        config: Optional[Dict] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Execute research for multiple companies.

        Args:
            company_names: List of companies to research
            config: Optional configuration override
            parallel: Whether to run in parallel (True) or sequential (False)

        Returns:
            Batch results dictionary
        """
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Starting batch research',
                'total_companies': len(company_names),
                'started_at': utc_now().isoformat()
            }
        )

        if parallel:
            # Create group of parallel tasks
            job = group(
                research_single_company.s(name, config)
                for name in company_names
            )
            result = job.apply_async()

            # Wait for all to complete
            results = result.get(timeout=3600)  # 1 hour timeout
        else:
            # Run sequentially
            results = []
            for i, name in enumerate(company_names):
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Processing {i+1}/{len(company_names)}',
                        'current_company': name
                    }
                )
                result = research_single_company(name, config)
                results.append(result)

        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')

        return {
            'status': 'completed',
            'total': len(company_names),
            'successful': successful,
            'failed': failed,
            'results': results,
            'completed_at': utc_now().isoformat()
        }

    @app.task(name='research.update_company_data')
    def update_company_data(
        company_name: str,
        force: bool = False,
        max_age_days: int = 7
    ) -> Dict[str, Any]:
        """
        Update company data if stale.

        Args:
            company_name: Company to update
            force: Force update even if fresh
            max_age_days: Maximum age before data is stale

        Returns:
            Update result dictionary
        """
        from datetime import timedelta
        from ..database import get_repository

        repo = get_repository()

        # Check last research
        if not force:
            recent = repo.get_recent_research(company_name, limit=1, status='completed')

            if recent:
                last_run = recent[0]
                last_completed = datetime.fromisoformat(last_run['completed_at'])

                if (utc_now() - last_completed) < timedelta(days=max_age_days):
                    return {
                        'status': 'skipped',
                        'reason': 'Data is fresh',
                        'last_updated': last_run['completed_at'],
                        'company': company_name
                    }

        # Run new research
        result = research_single_company(company_name)

        return {
            'status': 'updated',
            'company': company_name,
            'run_id': result.get('run_id'),
            'completed_at': utc_now().isoformat()
        }

    @app.task(name='reports.generate')
    def generate_report(
        research_run_id: str,
        formats: Optional[List[str]] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate report from research results.

        Args:
            research_run_id: Research run ID
            formats: Output formats (markdown, excel, pdf)
            output_dir: Output directory

        Returns:
            Report generation result
        """
        from ..database import get_repository

        if formats is None:
            formats = ['markdown']

        repo = get_repository()
        run = repo.get_research_run(research_run_id)

        if not run:
            return {
                'status': 'failed',
                'error': f'Research run {research_run_id} not found'
            }

        generated_files = {}

        # Get agent outputs
        outputs = repo.get_agent_outputs(run.id)

        # Build report data
        report_data = {
            'company_name': run.company.name if hasattr(run, 'company') else 'Unknown',
            'run_id': research_run_id,
            'completed_at': run.completed_at.isoformat() if run.completed_at else None,
            'total_cost': run.total_cost,
            'agent_outputs': {
                o.agent_name: o.analysis
                for o in outputs
            }
        }

        # Generate each format
        for fmt in formats:
            if fmt == 'markdown':
                # Generate markdown report
                from ..output.report_generator import MarkdownReportGenerator
                generator = MarkdownReportGenerator()
                filepath = generator.generate(report_data, output_dir)
                generated_files['markdown'] = filepath

        return {
            'status': 'completed',
            'run_id': research_run_id,
            'formats': formats,
            'files': generated_files,
            'generated_at': utc_now().isoformat()
        }

    @app.task(name='research.cleanup_old_runs')
    def cleanup_old_runs(days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Cleanup old research runs.

        Args:
            days_to_keep: Number of days to retain

        Returns:
            Cleanup result
        """
        from datetime import timedelta
        from ..database import get_repository

        repo = get_repository()
        cutoff = utc_now() - timedelta(days=days_to_keep)

        # This would need implementation in repository
        # For now, return a placeholder
        return {
            'status': 'completed',
            'cutoff_date': cutoff.isoformat(),
            'runs_deleted': 0
        }

    # Periodic task schedule
    app.conf.beat_schedule = {
        # Daily cleanup at 3 AM UTC
        'cleanup-old-runs': {
            'task': 'research.cleanup_old_runs',
            'schedule': 86400.0,  # Daily
            'kwargs': {'days_to_keep': 30}
        },
    }

else:
    # Celery not available - provide stub functions
    app = None

    def research_single_company(*args, **kwargs):
        raise ImportError("Celery is required for async tasks. Install with: pip install celery redis")

    def research_batch_companies(*args, **kwargs):
        raise ImportError("Celery is required for async tasks. Install with: pip install celery redis")

    def update_company_data(*args, **kwargs):
        raise ImportError("Celery is required for async tasks. Install with: pip install celery redis")

    def generate_report(*args, **kwargs):
        raise ImportError("Celery is required for async tasks. Install with: pip install celery redis")


# Helper functions (available regardless of Celery)

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a task by ID.

    Args:
        task_id: Celery task ID

    Returns:
        Task status dictionary
    """
    if not CELERY_AVAILABLE:
        raise ImportError("Celery is required")

    result = AsyncResult(task_id, app=app)

    return {
        'task_id': task_id,
        'status': result.status,
        'ready': result.ready(),
        'successful': result.successful() if result.ready() else None,
        'result': result.result if result.ready() else None,
        'info': result.info
    }


def cancel_task(task_id: str) -> bool:
    """
    Cancel a running task.

    Args:
        task_id: Celery task ID

    Returns:
        True if revoked successfully
    """
    if not CELERY_AVAILABLE:
        raise ImportError("Celery is required")

    result = AsyncResult(task_id, app=app)
    result.revoke(terminate=True)
    return True
