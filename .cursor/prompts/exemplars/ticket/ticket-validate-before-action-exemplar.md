# Ticket Validate-Before-Action Exemplar

## Examples (Few-Shot)

### Example 1: Complex Feature Implementation

**Input**:
```xml
<spec>@FEATURE-OAUTH-LOGIN.md</spec>
<ticket>@EBASE-12345</ticket>
<action>validate your understanding, then execute</action>
```

**Reasoning**:
Specification contains complex OAuth2 implementation requirements with multiple providers, token management, session handling. High-risk change affecting authentication system. AI must validate understanding before proceeding to prevent security vulnerabilities.

**Expected Output - Phase 1 (Validation)**:
```markdown
## ✅ Validation Summary: EBASE-12345 OAuth Login

### Understanding

I will implement OAuth2 authentication for user login supporting Google and GitHub providers, with:
- Authorization Code flow with PKCE
- Token management (access, refresh)
- Session management with secure cookies
- Automatic token refresh
- Logout functionality

### Approach

**Phase 1: Core Infrastructure (Day 1-2)**
1. Create `IOAuthProvider` interface for provider abstraction
2. Implement `GoogleOAuthProvider` and `GitHubOAuthProvider`
3. Add `OAuthConfiguration` settings class
4. Create `OAuthStateManager` for CSRF protection

**Phase 2: Authentication Flow (Day 2-3)**
1. Implement `/auth/login` endpoint (redirects to provider)
2. Implement `/auth/callback` endpoint (handles provider response)
3. Add token exchange logic (authorization code → access token)
4. Implement token validation

**Phase 3: Session Management (Day 3-4)**
1. Create `SessionManager` with Redis backing
2. Implement secure cookie storage (HttpOnly, Secure flags)
3. Add session creation/validation middleware
4. Implement automatic token refresh logic

**Phase 4: Testing & Security (Day 4-5)**
1. Unit tests for providers, state management, token handling
2. Integration tests for complete OAuth flow
3. Security review (CSRF, token storage, session hijacking)
4. Manual testing with real providers

### Files to Modify/Create

**New Files**:
- `Authentication/OAuth/IOAuthProvider.cs` - Provider interface
- `Authentication/OAuth/GoogleOAuthProvider.cs` - Google implementation
- `Authentication/OAuth/GitHubOAuthProvider.cs` - GitHub implementation
- `Authentication/OAuth/OAuthConfiguration.cs` - Settings model
- `Authentication/OAuth/OAuthStateManager.cs` - CSRF protection
- `Authentication/Controllers/AuthController.cs` - Login/callback endpoints
- `Authentication/Session/SessionManager.cs` - Session handling
- `Authentication/Middleware/AuthenticationMiddleware.cs` - Request auth

**Modified Files**:
- `Startup.cs` - Register OAuth services, configure middleware
- `appsettings.json` - Add OAuth client IDs, secrets, Redis connection
- `Program.cs` - Configure authentication pipeline

### Success Criteria

- [ ] User can log in with Google account (authorization flow completes)
- [ ] User can log in with GitHub account (authorization flow completes)
- [ ] Access tokens stored securely in HttpOnly cookies
- [ ] Session persists across requests
- [ ] Token automatically refreshes when expired
- [ ] Logout clears session and tokens
- [ ] CSRF protection prevents state hijacking
- [ ] All unit tests pass (95%+ coverage)
- [ ] Integration tests verify complete flow
- [ ] Security review finds no critical issues

### Risks & Mitigations

**Risk 1: Token Storage Vulnerability**
- Impact: HIGH (could expose user tokens)
- Likelihood: MEDIUM (if not implemented correctly)
- Mitigation: Use HttpOnly, Secure, SameSite=Strict cookies; never expose in JavaScript

**Risk 2: CSRF Attack on OAuth State**
- Impact: HIGH (could allow account takeover)
- Likelihood: MEDIUM (common OAuth vulnerability)
- Mitigation: Implement OAuthStateManager with cryptographic state validation

**Risk 3: Refresh Token Expiration Handling**
- Impact: MEDIUM (user logged out unexpectedly)
- Likelihood: LOW (if automatic refresh implemented)
- Mitigation: Implement sliding expiration, automatic refresh before expiration

### Dependencies

- **External Libraries**: Microsoft.AspNetCore.Authentication.OAuth (NuGet)
- **Services**: Redis for session storage
- **Provider Setup**: Google OAuth app, GitHub OAuth app (client IDs/secrets)

### Questions/Clarifications

- [ ] What's the token expiration policy? (Suggest: access 1h, refresh 30 days)
- [ ] Should we support remember-me functionality? (Extended session)
- [ ] What happens to existing sessions when user logs out from provider?
- [ ] Do we need to support additional providers (Microsoft, etc.) in future?

---

**Ready to proceed?** Please confirm approach or provide corrections before I begin implementation.
```

**User Response**: "Looks good, please proceed"

**Expected Output - Phase 2 (Execution)**:
```markdown
## Executing OAuth Login Implementation

### Phase 1: Core Infrastructure ✅

**Created**: `IOAuthProvider` interface
```csharp
public interface IOAuthProvider
{
    string GetAuthorizationUrl(string state, string redirectUri);
    Task<OAuthToken> ExchangeCodeForTokenAsync(string code, string redirectUri);
    Task<UserInfo> GetUserInfoAsync(string accessToken);
}
```

**Created**: `GoogleOAuthProvider` implementation (complete)
**Created**: `GitHubOAuthProvider` implementation (complete)
**Created**: `OAuthConfiguration` settings model
**Created**: `OAuthStateManager` for CSRF protection

---

### Phase 2: Authentication Flow ✅

**Created**: `/auth/login` endpoint (redirects to provider with state)
**Created**: `/auth/callback` endpoint (validates state, exchanges code, creates session)
**Implemented**: Token exchange logic with error handling

---

### Phase 3: Session Management ✅

**Created**: `SessionManager` with Redis backing
**Implemented**: Secure cookie storage (HttpOnly, Secure, SameSite=Strict)
**Created**: Authentication middleware for request validation
**Implemented**: Automatic token refresh (checks expiration, refreshes if <5 min remaining)

---

### Phase 4: Testing & Security ✅

**Unit Tests**:
- 15 tests for OAuth providers (Google, GitHub)
- 8 tests for state management (generation, validation)
- 12 tests for token handling (exchange, refresh, validation)
- **Result**: 35 tests, 97% coverage, all passing

**Integration Tests**:
- Complete OAuth flow (Google)
- Complete OAuth flow (GitHub)
- Token refresh flow
- Logout flow
- **Result**: 4 tests, all passing

**Security Review**:
- ✅ CSRF protection via state validation
- ✅ Token storage secure (HttpOnly cookies)
- ✅ No token exposure in logs/responses
- ✅ Automatic session expiration
- **Result**: No critical issues found

---

### ✅ Implementation Complete

**Success Criteria Validation**:
- ✅ Google login working (tested with real account)
- ✅ GitHub login working (tested with real account)
- ✅ Tokens secure in HttpOnly cookies
- ✅ Session persistence verified
- ✅ Automatic token refresh confirmed
- ✅ Logout clears session successfully
- ✅ CSRF protection validated
- ✅ Unit tests: 35/35 passing (97% coverage)
- ✅ Integration tests: 4/4 passing
- ✅ Security review: No critical issues

**Files Created/Modified**: 11 new files, 3 modified files
**Test Coverage**: 97%
**Implementation Time**: ~4.5 days (within estimate)

**Next Steps**:
1. Deploy to staging for QA testing
2. Update API documentation
3. Create runbook for OAuth provider setup
```

### Example 2: High-Risk Database Migration

**Input**:
```xml
<spec>@DATABASE-MIGRATION-PLAN.md</spec>
<ticket>@EBASE-98765</ticket>
<action>this is critical - validate thoroughly, then execute only if certain</action>
```

**Reasoning**:
Database migration is high-risk. AI must validate understanding of migration script, rollback plan, data preservation requirements before execution.

**Expected Output - Phase 1 (Validation)**:
```markdown
## ✅ Validation Summary: EBASE-98765 Database Migration

**⚠️ CRITICAL OPERATION - Extra scrutiny applied**

### Understanding

I will execute a database schema migration to add audit columns (CreatedBy, CreatedDate, ModifiedBy, ModifiedDate) to 14 configuration tables without data loss.

### Approach

**Phase 1: Pre-Migration Safety (30 min)**
1. Backup current database (`BACKUP DATABASE TO migration_backup_20251208.bak`)
2. Verify backup integrity
3. Create rollback script (tested on copy)
4. Validate no active transactions

**Phase 2: Migration Execution (1 hour)**
1. Add columns to tables (nullable initially to avoid data loss)
2. Populate CreatedBy/CreatedDate from existing audit log
3. Set default values for ModifiedBy/ModifiedDate
4. Verify data integrity (row counts, data sampling)

**Phase 3: Validation (30 min)**
1. Run data integrity checks
2. Verify all 14 tables updated
3. Test application with new schema
4. Confirm no data loss

**Phase 4: Finalization (30 min)**
1. Update application code to use new columns
2. Deploy application changes
3. Document rollback procedure
4. Archive backup

### Files to Modify

**SQL Scripts**:
- `migrations/20251208_add_audit_columns.sql` - Migration script
- `migrations/20251208_rollback_audit_columns.sql` - Rollback script

**Application Code**:
- `Repositories/BaseRepository.cs` - Add audit column handling
- `Entities/IAuditable.cs` - New interface for audit tracking

### Success Criteria

- [ ] All 14 tables have new audit columns
- [ ] No data loss (row counts match pre-migration)
- [ ] Historical created dates populated from audit log
- [ ] Application queries work with new schema
- [ ] Rollback script tested and ready
- [ ] Backup verified and stored
- [ ] Zero errors in migration log

### Risks & Mitigations

**Risk 1: Data Loss During Migration**
- Impact: CRITICAL (unacceptable)
- Likelihood: LOW (if nullable columns used initially)
- Mitigation: Add columns as nullable, populate data, then set constraints; full backup before migration

**Risk 2: Long-Running Migration Locks Tables**
- Impact: HIGH (production downtime)
- Likelihood: MEDIUM (depends on table size)
- Mitigation: Schedule during maintenance window; use chunked updates if tables large

**Risk 3: Application Breaks with New Schema**
- Impact: HIGH (production outage)
- Likelihood: LOW (if code deployed simultaneously)
- Mitigation: Deploy code changes immediately after schema migration; test on staging first

### Pre-Execution Checklist

- [ ] Maintenance window scheduled (low traffic period)
- [ ] Stakeholders notified of migration
- [ ] Backup storage verified (sufficient space)
- [ ] Rollback script tested on database copy
- [ ] Application code changes ready to deploy
- [ ] Monitoring dashboard ready (track migration progress)

### Questions/Clarifications

- [ ] Is maintenance window approved for [DATE TIME]?
- [ ] Should I proceed if backup verification fails? (Answer: NO)
- [ ] What's the rollback decision timeline if issues arise? (Suggest: 5 min max)

---

**⚠️ CRITICAL**: Please confirm maintenance window, backup storage, and rollback readiness before I proceed with execution. This migration cannot be undone easily if data loss occurs.

**Ready to proceed?** Please explicitly approve with "APPROVED - PROCEED WITH MIGRATION" or provide corrections.
```

**User Response**: "APPROVED - PROCEED WITH MIGRATION. Maintenance window confirmed."

**Expected Output - Phase 2 (Execution)**:
```markdown
## Executing Database Migration: EBASE-98765

### Phase 1: Pre-Migration Safety ✅

**Backup Created**:
- File: `migration_backup_20251208_153000.bak`
- Size: 2.4 GB
- Integrity: VERIFIED (RESTORE VERIFYONLY passed)
- Storage: Network backup location confirmed

**Rollback Script**:
- Tested on database copy: SUCCESS
- Execution time: 45 seconds
- Ready for immediate use if needed

**Active Transactions**: None (verified)

---

### Phase 2: Migration Execution ✅

**Step 1**: Adding audit columns (nullable) to 14 tables... ✅ Complete (12 seconds)
**Step 2**: Populating CreatedBy/CreatedDate from audit log... ✅ Complete (3 min 24 sec)
**Step 3**: Setting default ModifiedBy/ModifiedDate values... ✅ Complete (45 seconds)

**Data Integrity Verification**:
- Row counts: ALL MATCH pre-migration (14/14 tables)
- Sample data check: PASS (100 rows per table verified)
- Foreign key constraints: INTACT
- Index integrity: VERIFIED

---

### Phase 3: Validation ✅

**Data Integrity Checks**: ALL PASS
- No NULL values in CreatedDate (expected historical data populated)
- All 14 tables updated successfully
- No orphaned records
- No constraint violations

**Application Testing**:
- Read operations: SUCCESS (5/5 queries)
- Write operations: SUCCESS (5/5 inserts/updates)
- Audit column population: VERIFIED (new records have correct audit data)

**Data Loss Check**: ZERO DATA LOSS
- Pre-migration row count: 145,823 rows
- Post-migration row count: 145,823 rows
- Difference: 0 (100% data preservation)

---

### Phase 4: Finalization ✅

**Application Code Deployed**:
- BaseRepository updated with audit handling
- IAuditable interface implemented
- Deployment successful, no errors

**Documentation**:
- Rollback procedure documented
- Backup archived at network location
- Migration log saved

---

### ✅ Migration Complete

**Success Criteria Validation**:
- ✅ All 14 tables have new audit columns
- ✅ No data loss (145,823 rows preserved)
- ✅ Historical created dates populated
- ✅ Application queries work correctly
- ✅ Rollback script tested and ready (not needed)
- ✅ Backup verified and archived
- ✅ Zero errors in migration log

**Migration Statistics**:
- Total Time: 8 minutes 32 seconds
- Downtime: 4 minutes (during schema changes)
- Tables Updated: 14/14
- Data Loss: 0 rows
- Errors: 0

**Post-Migration Status**: PRODUCTION STABLE, all services operational

**Rollback**: NOT NEEDED (migration successful)
```

---

