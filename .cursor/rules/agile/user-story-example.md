# User Story Documentation - Example

**Related Rule**: `user-story-documentation-rule.mdc`

## Example: US-001 Extract Configuration Data

```markdown
# User Story US-001: Extract Configuration Data

## Story Header
- **Story ID**: US-001
- **Story Title**: Extract Configuration Data from EBASE Environments
- **Feature**: TF-001 - Data Extraction Engine
- **Epic**: EPP-192 - Standard Configuration Management
- **Status**: In Progress
- **Priority**: High
- **Story Points**: 8
- **Created**: 2025-01-15
- **Last Updated**: 2025-01-20

## User Story

### Main Story
**As a** system administrator  
**I want to** extract bootstrapped configuration data from different EBASE environments in various formats  
**So that** I can analyze, compare, and backup core configuration data for standardization purposes

### User Type
- **Primary User**: System Administrator
  - Responsible for environment configuration and maintenance
  - Needs to ensure consistency across environments
  - Performs configuration backup and restore operations
  
- **Secondary Users**: 
  - **Data Analyst**: Uses extracted data for analysis and reporting
  - **Configuration Manager**: Manages configuration templates and standards

### Business Value
- **Enables Configuration Standardization**: Provides the data foundation needed to compare and align configurations across different EBASE environments
- **Reduces Manual Effort**: Automates what was previously a manual, time-consuming process of extracting configuration data
- **Provides Foundation for Comparison**: Creates the baseline data needed for configuration comparison and validation features
- **Supports Compliance and Audit**: Creates documented snapshots of configuration state for compliance and audit purposes
- **Reduces Risk**: Enables configuration backup and restore capabilities, reducing risk of configuration loss

## Acceptance Criteria

### Given-When-Then Format

#### Scenario 1: Extract all configuration tables
**Given** I have access to an EBASE environment with proper credentials  
**When** I run the extraction process for all 11 bootstrapped configuration tables  
**Then** I receive data in the selected format (Excel, JSON, CSV, SQL)  
**And** the data includes all records from the specified tables  
**And** the data includes metadata (timestamp, environment name, table structure)  
**And** the extraction completes within 5 minutes for up to 10,000 records per table

#### Scenario 2: Extract specific table with filtering
**Given** I have access to an EBASE environment  
**When** I run the extraction process for a specific table with filtering criteria (e.g., WHERE Switch = 1)  
**Then** I receive only the filtered data in the selected format  
**And** the filtering criteria are correctly applied (verified by record count)  
**And** the filtered data matches what I would get from a manual SQL query

#### Scenario 3: Handle large datasets
**Given** I have access to an EBASE environment with large datasets (>10,000 records)  
**When** I run the extraction process  
**Then** the process completes successfully without memory issues  
**And** progress is reported every second throughout the extraction  
**And** the process can be cancelled at any time without leaving incomplete files  
**And** memory usage stays under 500MB

#### Scenario 4: Handle connection failures
**Given** I am extracting data from an EBASE environment  
**When** a database connection failure occurs during extraction  
**Then** the system retries the operation up to 3 times with exponential backoff  
**And** if all retries fail, I receive a clear error message indicating the connection problem  
**And** any partially extracted data is cleaned up

#### Scenario 5: Export in multiple formats simultaneously
**Given** I have access to an EBASE environment  
**When** I select multiple export formats (e.g., Excel, JSON, CSV)  
**Then** the system exports the data in all selected formats  
**And** all format files contain the same data  
**And** each format is properly structured and valid

### Functional Requirements
- [ ] Extract data from all 11 bootstrapped configuration tables:
  - D_BETREKKING (MeasurementUnit)
  - D_PORTFOLIOTYPE (MeterProduct)
  - D_FLEXMETERNR (Meter)
  - D_FLEXCONSTRUCTIE (Allocation)
  - D_FLEXOPSLAG (Storage)
  - D_FLEXCONTRACT (Contract)
  - D_FLEXMETER (VirtualMeter)
  - D_FLEXADMINISTRATIE (Administration)
  - D_FORMULETYPE (FormulaType)
  - D_PORTFOLIOTEMPLATE (PortfolioTemplate)
  - D_CONTRACTTEMPLATE (ContractTemplate)
- [ ] Export to Excel (XLSX) with proper formatting and metadata
- [ ] Export to JSON with nested object structures for related data
- [ ] Export to CSV with configurable delimiters (comma, semicolon, tab)
- [ ] Export to SQL INSERT/UPDATE scripts
- [ ] Support configurable sorting by any column (ascending/descending)
- [ ] Include extraction metadata (timestamp, environment name, table structure)
- [ ] Handle binary file references (pictograms, icons) correctly
- [ ] Support table selection (single table, multiple tables, or all tables)
- [ ] Support filtering with WHERE clause syntax
- [ ] Display real-time progress during extraction
- [ ] Support cancellation of long-running extractions
- [ ] Save extracted files to user-specified directory

### Non-Functional Requirements

#### Performance
- [ ] Extract large datasets efficiently (within 5 minutes for 10,000 records per table)
- [ ] Memory usage stays under 500MB during extraction
- [ ] Support for concurrent extraction requests (at least 3 simultaneous users)
- [ ] Progress reporting updates every 1 second
- [ ] File writing optimized for large datasets (streaming)

#### Security
- [ ] Secure database connections with proper authentication (Windows or SQL auth)
- [ ] Connection strings encrypted in configuration
- [ ] Audit logging for all extraction operations
- [ ] No sensitive data in log files
- [ ] Proper file permissions on exported files (read/write for current user only)

#### Usability
- [ ] Clear progress indicators showing current table and percentage complete
- [ ] Meaningful error messages with resolution suggestions
- [ ] Intuitive configuration interface
- [ ] Sensible defaults for common scenarios
- [ ] Help text available for all options

#### Reliability
- [ ] Handle network interruptions and retry automatically (up to 3 retries)
- [ ] Handle database connection failures gracefully
- [ ] Validate configuration before starting extraction
- [ ] Atomic file operations (complete file or no file)
- [ ] Clean up temporary files on error or cancellation

### Edge Cases
- [ ] Handle empty tables gracefully (create file with headers only)
- [ ] Handle database connection failures (retry with exponential backoff)
- [ ] Handle permission errors for specific tables (skip table and continue, log error)
- [ ] Handle very large binary files (pictograms >10MB) without memory issues
- [ ] Handle special characters in data (Unicode, quotes, newlines)
- [ ] Handle NULL values correctly in all formats
- [ ] Handle reserved keywords in SQL export
- [ ] Handle file system full errors during export
- [ ] Handle invalid filter syntax (validate before extraction)
- [ ] Handle invalid sort column names (validate before extraction)

## Technical Considerations

### Technical Approach
1. **Domain Entities and Repositories**
   - Use domain entities from Feature TF-001 (Domain Entity Framework)
   - Leverage repository pattern for consistent data access
   - Support for all 11 configuration tables

2. **Format-Specific Exporters**
   - Strategy pattern for different export formats
   - ExcelExporter using EPPlus library
   - JsonExporter using Newtonsoft.Json
   - CsvExporter using StreamWriter
   - SqlExporter for SQL scripts

3. **Progress Reporting**
   - Event-based progress reporting mechanism
   - Progress percentage, current table, estimated time remaining
   - Support for cancellation tokens

4. **Error Handling**
   - Retry logic with exponential backoff for transient failures
   - Clear error messages with resolution suggestions
   - Comprehensive logging for troubleshooting
   - Graceful degradation (skip failed tables, continue with others)

### Dependencies

#### Feature Dependencies
- **Feature TF-001**: Domain Entity Framework
  - All 11 domain entities must be implemented
  - Repository interfaces and implementations required
  - Dapper configuration and mappings needed

#### Library Dependencies
- **EPPlus** (v5.0+): Excel file generation
- **Newtonsoft.Json** (v13.0+): JSON serialization
- **Dapper** (v2.0+): Data access
- **System.Data.SqlClient** (v4.8+): SQL Server connectivity
- **Microsoft.Extensions.Configuration** (v6.0+): Configuration management
- **Serilog** (v3.0+): Logging

#### Infrastructure Dependencies
- Access to EBASE database environments
- Database read permissions on all 11 configuration tables
- File system write permissions for output directory
- Network connectivity to database servers

### Integration Points

#### Database Integration
- **Connection**: SQL Server 2019+ with Integrated Security or SQL Authentication
- **Data Access**: Dapper for efficient querying
- **Transaction**: Read-only queries (no transaction needed)
- **Timeout**: Configurable query timeout (default 30 seconds)

#### File System Integration
- **Output Directory**: User-specified directory for exported files
- **File Naming**: Convention: `{TableName}_{Timestamp}.{ext}`
- **Subdirectories**: Create subdirectories by format if multiple formats selected
- **Cleanup**: Remove temporary files on error or cancellation

#### Logging System
- **Operation Logging**: Log start, progress, and completion of extractions
- **Error Logging**: Log all errors with stack traces
- **Audit Logging**: Log user, timestamp, tables extracted, file locations
- **Performance Logging**: Log extraction times and record counts

#### Configuration System
- **Connection Strings**: Stored in configuration file or environment variables
- **Export Settings**: Default formats, sort order, filter criteria
- **Output Settings**: Default output directory, file naming convention
- **Performance Settings**: Query timeout, batch size, retry count

### Data Requirements

#### Source Data
- **Tables**: All 11 bootstrapped configuration tables
- **Permissions**: SELECT permission on all tables
- **Data Types**: Support for all SQL Server data types (VARCHAR, INT, DECIMAL, VARBINARY, DATETIME, etc.)
- **Binary Data**: Handle VARBINARY columns (pictograms, icons)

#### Metadata
- **Extraction Timestamp**: Date and time of extraction
- **Environment Name**: Name of source environment
- **Table Schema**: Column names, data types, constraints
- **Record Count**: Number of records extracted per table
- **User Information**: Username who performed extraction

#### Configuration Data
- **Export Configuration**: Selected formats, sorting, filtering
- **Connection Configuration**: Connection string, authentication method
- **Output Configuration**: Output directory, file naming pattern

## Design and UX

### User Interface

#### Configuration Screen
- **Connection Section**
  - Connection string input (with test connection button)
  - Authentication method selection (Windows/SQL)
  - Environment name input (for metadata)

- **Table Selection**
  - Checkbox list of all 11 tables (select all/none buttons)
  - Filter input for WHERE clause (optional)
  - Sort column and direction selection

- **Format Selection**
  - Checkbox list of formats (Excel, JSON, CSV, SQL)
  - Format-specific options (e.g., CSV delimiter)

- **Output Settings**
  - Output directory browser
  - File naming pattern input
  - Overwrite/append option

- **Action Buttons**
  - Start Extraction button (disabled until configuration valid)
  - Validate Configuration button
  - Cancel button

#### Progress Screen
- **Overall Progress**
  - Progress bar (0-100%)
  - Current status text (e.g., "Extracting D_BETREKKING...")
  - Estimated time remaining

- **Table Progress**
  - List of tables with status (Pending, In Progress, Complete, Error)
  - Record count for completed tables
  - Elapsed time per table

- **Action Buttons**
  - Cancel Extraction button
  - View Logs button

#### Results Screen
- **Summary**
  - Total tables extracted
  - Total records extracted
  - Total time elapsed
  - File locations

- **Detailed Results**
  - Table-by-table results with record counts
  - Any errors or warnings
  - File paths for each exported file

- **Action Buttons**
  - Open Output Folder button
  - Export Again button
  - Close button

### User Experience

#### Happy Path Flow
1. User opens extraction configuration screen
2. User enters connection information or selects saved profile
3. User tests connection (green checkmark if successful)
4. User selects tables (or uses "Select All")
5. User selects export formats
6. User browses for output directory
7. User clicks "Start Extraction"
8. System validates configuration
9. Progress screen shows real-time progress
10. Extraction completes successfully
11. Results screen shows summary with file locations
12. User clicks "Open Output Folder" to view files

#### Error Flow
1. User enters invalid connection string
2. User clicks "Start Extraction"
3. System validates configuration
4. System shows error message: "Invalid connection string. Please check server name and authentication method."
5. User corrects connection string
6. User tests connection (success)
7. User proceeds with extraction

#### Cancellation Flow
1. User starts extraction
2. Extraction is in progress (2 of 11 tables complete)
3. User realizes incorrect filter was applied
4. User clicks "Cancel Extraction"
5. System prompts: "Are you sure you want to cancel? Progress will be lost."
6. User confirms cancellation
7. System cancels operation, cleans up temporary files
8. System shows message: "Extraction cancelled. Completed tables: 2 of 11. Files have been deleted."

### Accessibility
- **Keyboard Navigation**: Full keyboard support (Tab, Enter, Escape)
- **Screen Reader**: ARIA labels on all form controls
- **High Contrast**: Support for Windows high contrast mode
- **Focus Indicators**: Clear visual focus indicators on all interactive elements
- **Error Announcement**: Screen reader announces validation errors

### Responsive Design
- **Desktop**: Full feature set, side-by-side layout
- **Tablet**: Stacked layout, all features available
- **Touch**: Large buttons and controls (44x44px minimum)
- **Zoom**: UI remains functional at 200% zoom

## Testing Requirements

### Test Scenarios

#### 1. Happy Path Testing
**Test Case 1.1**: Extract all tables in Excel format
- Steps:
  1. Configure connection to test environment
  2. Select all 11 tables
  3. Select Excel format only
  4. Start extraction
- Expected: Excel file created with all 11 tables (separate sheets)
- Verify: File can be opened in Excel, data matches database

**Test Case 1.2**: Extract single table in all formats
- Steps:
  1. Configure connection to test environment
  2. Select D_BETREKKING table only
  3. Select all formats (Excel, JSON, CSV, SQL)
  4. Start extraction
- Expected: 4 files created (one per format)
- Verify: All files contain same data, proper formatting

**Test Case 1.3**: Extract with filtering
- Steps:
  1. Configure connection to test environment
  2. Select D_BETREKKING table
  3. Add filter: WHERE Switch = 1
  4. Select CSV format
  5. Start extraction
- Expected: CSV file with filtered records only
- Verify: Record count matches manual SQL query with same filter

**Test Case 1.4**: Extract with sorting
- Steps:
  1. Configure connection to test environment
  2. Select D_BETREKKING table
  3. Set sort column: Unit, direction: Ascending
  4. Select JSON format
  5. Start extraction
- Expected: JSON file with records sorted by Unit
- Verify: Records are in ascending alphabetical order

#### 2. Error Handling Testing

**Test Case 2.1**: Invalid connection string
- Steps:
  1. Enter invalid connection string (non-existent server)
  2. Click Start Extraction
- Expected: Error message: "Cannot connect to database. Please check server name and authentication."
- Verify: No files created, operation fails gracefully

**Test Case 2.2**: Permission denied on table
- Steps:
  1. Configure connection with user who lacks permission on D_FLEXMETER
  2. Select all 11 tables
  3. Start extraction
- Expected: Extraction continues, skips D_FLEXMETER with warning
- Verify: 10 tables extracted successfully, clear warning message for failed table

**Test Case 2.3**: Network interruption
- Steps:
  1. Start extraction
  2. Simulate network interruption (disable network)
  3. Wait for retry logic
- Expected: System retries 3 times, then fails with clear error
- Verify: Error message indicates network issue, suggests checking connection

**Test Case 2.4**: Output directory read-only
- Steps:
  1. Configure output directory to read-only location
  2. Start extraction
- Expected: Error during validation: "Output directory is read-only. Please select a different location."
- Verify: No extraction attempted, clear error message

**Test Case 2.5**: Disk full during export
- Steps:
  1. Start extraction to nearly-full disk
  2. Wait for disk full error
- Expected: Extraction fails with error: "Insufficient disk space. Please free up space or select a different location."
- Verify: Partial files are cleaned up

#### 3. Performance Testing

**Test Case 3.1**: Large dataset extraction
- Setup: Create test environment with 50,000 records in D_BETREKKING
- Steps:
  1. Extract D_BETREKKING in all formats
  2. Measure time and memory
- Expected: Completes in under 15 minutes, memory stays under 500MB
- Verify: All records present in output, no data loss

**Test Case 3.2**: Concurrent extractions
- Setup: 3 users performing extractions simultaneously
- Steps:
  1. Start 3 extractions at same time (different tables)
  2. Monitor performance
- Expected: All extractions complete successfully without errors
- Verify: No data corruption, reasonable performance (< 2x single extraction time)

**Test Case 3.3**: Memory usage monitoring
- Setup: Large datasets in all 11 tables
- Steps:
  1. Start extraction of all tables in all formats
  2. Monitor memory usage throughout extraction
- Expected: Memory usage stays under 500MB at all times
- Verify: No memory leaks, memory released after completion

#### 4. Format Testing

**Test Case 4.1**: Excel format validation
- Steps:
  1. Extract data in Excel format
  2. Open in Microsoft Excel
- Expected: File opens without errors, proper formatting
- Verify: Headers present, data types correct, no #REF or #VALUE errors

**Test Case 4.2**: JSON structure validation
- Steps:
  1. Extract data in JSON format
  2. Validate JSON structure
- Expected: Valid JSON that parses without errors
- Verify: JSON validator passes, structure matches schema

**Test Case 4.3**: CSV delimiter handling
- Steps:
  1. Extract data in CSV format with comma delimiter
  2. Import into Excel
  3. Extract same data with semicolon delimiter
  4. Import into Excel
- Expected: Both import correctly without issues
- Verify: Data columns align correctly, no split/merged columns

**Test Case 4.4**: SQL script execution
- Steps:
  1. Extract data in SQL INSERT format
  2. Execute SQL script against empty test database
  3. Verify data matches source
- Expected: SQL executes without errors, data matches
- Verify: Record counts match, data values identical

### Test Data

#### Standard Test Data
- **Small Dataset**: 10-100 records per table
- **Medium Dataset**: 1,000-5,000 records per table
- **Large Dataset**: 10,000+ records per table
- **Special Characters**: Data with Unicode, quotes, newlines, tabs
- **NULL Values**: Records with NULL in various columns
- **Binary Data**: Pictogram and icon binary data
- **Edge Cases**: Maximum length strings, maximum/minimum numeric values

#### Test Environments
- **Development**: Small dataset, fast for iterative testing
- **Staging**: Medium dataset, production-like schema
- **Performance**: Large dataset, stress testing
- **Security**: Restricted permissions, test error handling

### Performance Testing

#### Performance Benchmarks
- Extract 1,000 records: <30 seconds
- Extract 10,000 records: <5 minutes
- Extract 50,000 records: <15 minutes
- Memory usage: <500MB at peak
- File write speed: >1,000 records/second for CSV
- Concurrent users: Support 3 simultaneous extractions

#### Performance Monitoring
- Track extraction time per table
- Monitor memory usage throughout extraction
- Monitor CPU usage
- Monitor disk I/O
- Monitor network latency

### Security Testing

#### SQL Injection Prevention
- Test with malicious input in filter: `'; DROP TABLE D_BETREKKING; --`
- Expected: Input treated as literal string, no SQL execution
- Verify: Parameterized queries used, no dynamic SQL

#### Authentication Testing
- Test with invalid credentials
- Test with expired credentials
- Test with insufficient permissions
- Expected: Clear error messages, no security information leakage

#### Data Protection
- Verify connection strings encrypted in configuration
- Verify no sensitive data in log files
- Verify proper file permissions on exported files
- Expected: Secure by default

## Definition of Done

### Completion Criteria
- [ ] User story is implemented according to specifications
- [ ] All acceptance criteria are met and tested
- [ ] Code review is completed and approved
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests written and passing
- [ ] Performance requirements met (benchmarks passed)
- [ ] Security review completed (no vulnerabilities found)
- [ ] User acceptance testing completed successfully

### Quality Gates
- [ ] Code quality checks pass (no critical SonarQube issues)
- [ ] All automated tests pass (unit, integration, end-to-end)
- [ ] Manual testing completed and signed off by QA
- [ ] Performance benchmarks met (documented test results)
- [ ] Security scan completed and passed (no high/critical vulnerabilities)
- [ ] Accessibility requirements met (WCAG 2.1 AA compliant)

### Documentation
- [ ] Technical documentation updated (architecture, component design)
- [ ] User documentation created (user guide with screenshots)
- [ ] API documentation updated (if applicable)
- [ ] Deployment documentation updated (installation, configuration)
- [ ] Release notes prepared (features, known issues, breaking changes)

### Deployment
- [ ] Feature deployed to development environment and tested
- [ ] Feature deployed to staging environment and tested
- [ ] Staging testing completed and signed off
- [ ] Production deployment plan ready and reviewed
- [ ] Rollback plan documented and tested
- [ ] Monitoring and alerting configured
- [ ] Support team trained on new feature
```


