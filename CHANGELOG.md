# Changelog

All notable changes to the Company Researcher System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial project setup and planning documents
- Comprehensive README.md with project overview
- Documentation TODO roadmap
- Folder structure (research/, project-management/, docs/)
- Architecture Decision Records (ADRs)
- Project management files (TODO.md, BACKLOG.md, milestones.md)
- CONTRIBUTING.md with coding standards
- Research references and experiments log
- .env.example template

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [0.1.0-alpha] - 2025-12-05

### Phase 0: Proof of Concept

**Status:** 🔄 In Progress

#### Added
- Project initialization
- Planning documentation
- Development environment setup guide

#### Goals
- [ ] Hello World prototype (single-agent research)
- [ ] Validate API integrations (Claude, Tavily)
- [ ] Generate basic markdown report for Tesla
- [ ] Confirm cost < $0.50, time < 5 minutes

---

## Future Releases (Planned)

### [0.2.0] - Phase 1: Basic Research Loop (Target: 2025-12-26)
- Single-agent research workflow with LangGraph
- Structured state management
- Markdown report generation
- Basic error handling
- Unit test suite (50%+ coverage)
- CLI interface

### [0.3.0] - Phase 2: Multi-Agent System (Target: 2026-01-16)
- Supervisor agent implementation
- 4 specialized worker agents (Financial, Market, Competitor, Report Writer)
- Agent coordination logic
- Integration tests
- Performance benchmarks

### [0.4.0] - Phase 3: API & Infrastructure (Target: 2026-01-30)
- FastAPI REST API
- WebSocket streaming support
- PostgreSQL database setup
- Redis caching layer
- Authentication & rate limiting
- Docker containerization
- CI/CD pipeline

### [0.5.0] - Phase 4: Memory & Intelligence (Target: 2026-02-13)
- Qdrant vector database
- Memory storage for past research
- Semantic search implementation
- Cache hit logic (70%+ cost savings)
- Source quality tracking
- Cross-company insight extraction

### [0.6.0] - Phase 5: Full Agent Suite (Target: 2026-02-27)
- Remaining 10 specialized agents
- Complete 14-agent system
- Full agent coordination
- Comprehensive test suite (80%+ coverage)

### [1.0.0] - Phase 6: Production Launch (Target: 2026-03-13)
- Production deployment
- Monitoring & alerting (AgentOps, LangSmith, Prometheus)
- User documentation
- Web dashboard (optional)
- Beta user testing
- Performance optimization

---

## Version History Format

Each release will include:

### [Version] - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed
- Changes to existing functionality

#### Deprecated
- Features marked for removal

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security patches and improvements

---

## Notes

- **Pre-1.0.0:** Breaking changes may occur between minor versions
- **Post-1.0.0:** Semantic versioning will be strictly followed
- **Breaking Changes:** Will be clearly marked with `BREAKING CHANGE:` in commits
- **Migration Guides:** Will be provided for major version upgrades

---

## How to Contribute to Changelog

When making significant changes:

1. Add entry under `[Unreleased]` section
2. Use appropriate category (Added, Changed, Fixed, etc.)
3. Write clear, user-facing descriptions
4. Reference issue/PR numbers: `(#123)`
5. On release, move items from Unreleased to new version section

**Example:**
```markdown
### Added
- Memory system for caching past research (#45)
- PDF export with custom branding (#52)

### Fixed
- Financial agent timeout issue (#48)
- Supervisor routing bug for edge cases (#51)
```

---

Last Updated: 2025-12-05
