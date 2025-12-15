---
name: review-sql-script
description: "Review SQL script for safety, performance, style standards, and platform compliance"
category: database-standards
tags: database, sql, code-review, safety, performance, mssql, oracle
argument-hint: "Script path or content to review"
---

# Review SQL Script Quality in [Script]

Review a SQL script for compliance with safety, performance, and style standards.

**Required Context**:

- `[SCRIPT_PATH]`: Path to the .sql file.
- `[TARGET_DB]`: MSSQL or Oracle (defaults to MSSQL).

**Optional Parameters**:

- `[SCRIPT_CONTENT]`: (Optional) Raw SQL content if file reading fails.

## Reasoning Process

1. **Header Scan**: Verify documentation (Author, Date, Purpose, Dependencies).
2. **Safety Check**: Look for `BEGIN TRAN`, `COMMIT`, `ROLLBACK`, and idempotency checks (`IF EXISTS`).
3. **Performance Scan**: Check for SARGable queries, index usage, and dangerous patterns (cursors).
4. **Style Check**: Verify naming conventions (UPPERCASE keywords, PascalCase objects).
5. **Logic Analysis**: Ensure the script achieves its stated purpose without side effects.

## Process

1. **Header Documentation**:
   - Script purpose clearly documented?
   - Author and date present?
   - Version number included?
   - Dependencies documented?
   - Rollback strategy documented?

2. **SQL Coding Standards**:
   - Consistent formatting and indentation?
   - Keywords in UPPERCASE?
   - Object names following naming conventions?
   - Proper use of whitespace?
   - Meaningful aliases used?

3. **Safety Checks**:
   - Transaction handling (BEGIN/COMMIT/ROLLBACK)?
   - Idempotency (can script run multiple times safely)?
   - Existence checks before CREATE/DROP?
   - Data validation before modifications?
   - Proper error handling?

4. **Performance Considerations**:
   - Appropriate indexes defined?
   - Efficient query patterns?
   - Avoid cursors when set-based operations possible?
   - Large operations batched appropriately?
   - Statistics updates after index changes?

5. **Platform Specifics**:
   - **MSSQL**: Proper data types, schemas, no Oracle syntax.
   - **Oracle**: Migration plan noted (if legacy).

6. **Version Control**:
   - Script versioning strategy?
   - Upgrade path clear?
   - Compatible with tracking sheet?

## Examples (Few-Shot)

**Input**:
```sql
update Users set Active = 0 where Id = 1
```

**Reasoning**:

- Missing `BEGIN TRAN` / `ROLLBACK` safety.
- Keywords `update`, `set`, `where` should be UPPERCASE.
- No header documentation.

**Output**:
> **Critical Issue**: Missing Transaction Handling. Script is unsafe.
> **Style Issue**: Keywords should be UPPERCASE.
> **Fix**: Wrap in `BEGIN TRY/CATCH` block with explicit Transaction control.

## Expected Output

**Deliverables**:

1. Safety Assessment (Safe/Unsafe).
2. List of Issues (Critical, Major, Minor).
3. Refactored Code Snippets.

**Format**: Markdown Report.

## Quality Criteria

- [ ] Safety (Transactions/Idempotency) is the #1 priority.
- [ ] Header requirements checked.
- [ ] Performance risks identified.

---

**Applies Rules**:

- `.cursor/rules/database-standards/sql-coding-standards-rule.mdc`
- `.cursor/rules/database-standards/mssql-standards-rule.mdc`
- `.cursor/rules/database-standards/development-workflow-rule.mdc`

