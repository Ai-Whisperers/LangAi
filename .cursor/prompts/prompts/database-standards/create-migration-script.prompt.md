---
name: create-migration-script
description: "Create a database migration script with proper safety checks, transactions, and rollback strategy"
category: database-standards
tags: database, migration, sql, mssql, oracle, schema-change
argument-hint: "Description of database change and target database"
---

# Create Database Migration Script

Please create a database migration script for the following change:

**Change Description**: `[REPLACE WITH DESCRIPTION OF DATABASE CHANGE]`
**Database**: `[REPLACE WITH: MSSQL/Oracle]`
**Version**: `[REPLACE WITH VERSION NUMBER, e.g., 1.0.0]`

## Script Requirements

1. **Header Documentation**:
   ```sql
   /*******************************************************************************
   * Script: [Script Name]
   * Purpose: [Clear description of what this script does]
   * Author: [Your Name]
   * Date: [YYYY-MM-DD]
   * Version: [X.Y.Z]
   * 
   * Dependencies:
   *   - [List any required prior scripts or objects]
   * 
   * Rollback Strategy:
   *   - [How to undo this change]
   * 
   * Testing:
   *   - [How to verify success]
   *******************************************************************************/
   ```

2. **Safety Checks**:
   - Transaction wrapper
   - Idempotency checks (IF NOT EXISTS, etc.)
   - Validation of prerequisites
   - Error handling with meaningful messages
   - SET NOCOUNT ON (for MSSQL)

3. **Migration Structure**:
   ```sql
   BEGIN TRY
       BEGIN TRANSACTION;
       
       -- Validation checks
       -- [Ensure preconditions are met]
       
       -- Main migration logic
       -- [Actual changes here]
       
       -- Verification checks
       -- [Confirm changes applied correctly]
       
       COMMIT TRANSACTION;
       PRINT 'Migration completed successfully';
   END TRY
   BEGIN CATCH
       IF @@TRANCOUNT > 0
           ROLLBACK TRANSACTION;
       PRINT 'Error: ' + ERROR_MESSAGE();
       THROW;
   END CATCH
   ```

4. **For Schema Changes**:
   - Create tables/columns
   - Create indexes
   - Create constraints
   - Update statistics
   - Grant permissions

5. **For Data Changes**:
   - Backup critical data (if applicable)
   - Batch large updates
   - Validate data before and after
   - Log changes

6. **Rollback Script**:
   - Create companion rollback script
   - Test rollback thoroughly
   - Document rollback procedure

## Script Types

Based on change type, use appropriate template:

- **Upgrade Script**: Version-to-version upgrade
- **Solution Script**: Specific problem fix
- **Creation Script**: New object creation
- **Materialized View**: View/materialized view creation

## Deliverable

Provide:

1. Complete migration script with proper structure
2. Rollback script
3. Testing script (SELECT statements to verify)
4. Documentation for tracking sheet entry
5. Deployment instructions

Apply standards from:

- `.cursor/rules/database-standards/sql-coding-standards-rule.mdc`
- `.cursor/rules/database-standards/template-usage-rule.mdc`
- `.cursor/rules/database-standards/development-workflow-rule.mdc`
- `.cursor/rules/database-standards/tracking-standards-rule.mdc`
- `.cursor/rules/database-standards/mssql-standards-rule.mdc` (if MSSQL)
- `.cursor/rules/database-standards/oracle-standards-rule.mdc` (if Oracle)

