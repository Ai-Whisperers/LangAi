# Technical Feature Documentation - Example

**Related Rule**: `technical-feature-documentation-rule.mdc`

## Example: TF-001 Domain Entity Framework

```markdown
# Technical Feature TF-001: Domain Entity Framework

## Feature Header
- **Feature ID**: TF-001
- **Feature Title**: Standardized Domain Entity and Repository Framework
- **Business Feature**: BF-001 - Configuration Data Extraction
- **Epic**: EPP-192 - Standard Configuration Management
- **Status**: In Progress
- **Priority**: High
- **Technical Complexity**: High
- **Created**: 2025-01-15
- **Last Updated**: 2025-01-20

## Technical Context

### Technical Problem
Need a standardized framework for domain entities and repositories to ensure consistent data access patterns across all bootstrapped configuration tables. Currently:
- No consistent domain entity structure exists
- Data access is ad-hoc and duplicated
- No standardized validation or business rule enforcement
- Difficult to test and maintain
- Inconsistent patterns across different tables

### Business Impact
- **Enables Consistent Data Extraction**: Provides the foundation for all data extraction features
- **Provides Technical Foundation**: All other technical features depend on this framework
- **Ensures Maintainability**: Consistent patterns make code easier to understand and maintain
- **Improves Quality**: Standardized approach reduces bugs and improves testability

### Technical Value
- **Consistent Data Access Patterns**: Same approach across all 11 tables
- **Reusable Repository Implementations**: Generic repository pattern reduces code duplication
- **Standardized Validation and Business Rules**: Consistent rule enforcement across all entities
- **Improved Testability**: Easy to unit test and integration test
- **Maintainability**: Clear structure and patterns make maintenance easier
- **Extensibility**: Easy to add new tables and entities

### Success Metrics
- All 11 tables have standardized domain entities and repositories implemented
- Consistent patterns across all implementations (measured through code review)
- Full unit test coverage for all operations (>90% coverage)
- Zero SQL injection vulnerabilities
- Performance meets requirements (<100ms for single entity operations)

## User Stories

### Primary User Story
**As a** developer
**I want to** have standardized domain entities and repositories
**So that** I can consistently extract, transform, and persist EBASE bootstrapped configuration data across all supported tables without duplicating code

**Acceptance Criteria:**
- Domain entities exist for all 11 bootstrapped configuration tables with proper property mappings
- Repository interfaces and implementations follow consistent patterns
- Dapper mappings are standardized and reusable
- Entity validation and business rules are encapsulated
- Foreign key relationships are properly handled
- Unit tests cover all entity and repository operations
- Performance requirements are met (<100ms for single entity operations)
- Security requirements are satisfied (SQL injection prevention)

### Secondary User Stories

#### 1. Data Consistency Story
**As a** system architect
**I want** consistent data access patterns across all bootstrapped configuration tables
**So that** I can ensure data integrity and maintainability

**Acceptance Criteria:**
- All repositories implement the same interface
- All entities follow the same base structure
- Foreign key relationships are consistently handled
- Transaction management is standardized

#### 2. Testing Support Story
**As a** QA engineer
**I want** standardized entity and repository patterns
**So that** I can create consistent unit tests and integration tests

**Acceptance Criteria:**
- All entities are testable with mock data
- All repositories can be mocked for unit testing
- Integration tests can use consistent patterns
- Test coverage is measurable and tracked

## Technical Requirements

### Functional Requirements

#### 1. Domain Entities
- Create domain entities for all 11 bootstrapped configuration tables:
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
- All entities inherit from BaseEntity with common properties (NR, audit fields)
- Property mappings match database column names
- Support for nullable types where appropriate

#### 2. Repository Pattern
- Generic IRepository<T> interface with standard CRUD operations:
  - GetByIdAsync(int id)
  - GetAllAsync()
  - AddAsync(T entity)
  - UpdateAsync(T entity)
  - DeleteAsync(int id)
- Specific repository interfaces for specialized queries
- Repository<T> base implementation with Dapper
- Support for transaction management

#### 3. Validation and Business Rules
- Validation attributes on entity properties
- Business rule validation methods
- Validation errors with clear messages
- Integration with FluentValidation

### Non-Functional Requirements

#### Performance
- Single entity operations complete in <100ms
- Batch operations handle 1,000+ entities efficiently
- Efficient parameter handling with Dapper
- Connection pooling for database connections

#### Security
- SQL injection prevention through parameterized queries
- Proper parameter handling and validation
- Secure connection string management
- Audit logging for all operations

#### Scalability
- Support for large datasets (10,000+ rows)
- Efficient memory usage
- Batch processing capabilities
- Concurrent access support

#### Maintainability
- Consistent code patterns across all repositories
- Clear naming conventions
- Comprehensive documentation
- Easy to add new tables and entities

### Integration Requirements

#### Database Integration
- Dapper micro-ORM for data access
- Support for MSSQL Server 2019+
- Integration with existing EBASE database schema
- Connection string configuration

#### Transaction Management
- Support for database transactions
- Rollback capabilities on errors
- Unit of Work pattern for complex operations
- Isolation level configuration

### Data Requirements

#### Domain Entities
- Property mappings for all database columns
- Support for foreign key relationships
- Support for complex types (binary data, JSON)
- Audit fields (created date, modified date)

#### Repository Implementation
- Generic repository for common operations
- Specific repositories for specialized queries
- Dapper mapping configurations
- Query parameterization

## Architecture and Design

### Architecture Impact

#### New Domain Layer
- **Entities Directory**: All domain entities
- **Repositories Directory**: Repository interfaces and implementations
- **Validation Directory**: Validation attributes and business rules
- **Foundation for Other Features**: All other technical features depend on this

#### Integration Points
- Existing EBASE database schema (read/write)
- Configuration management system (connection strings)
- Logging infrastructure (operation logging)
- Testing infrastructure (unit and integration tests)

### Design Patterns

#### Domain-Driven Design (DDD)
- Domain entities represent business concepts
- Entities encapsulate business rules
- Repository pattern abstracts data access
- Clear separation between domain and infrastructure

#### Repository Pattern
- Abstract data access logic
- Single responsibility for data operations
- Testable through interfaces
- Consistent CRUD operations

#### Generic Repository Pattern
- Generic IRepository<T> for common operations
- Specific repositories for specialized queries
- Reduce code duplication
- Consistent interface across all entities

#### Unit of Work Pattern
- Transaction management
- Coordinate multiple repository operations
- Ensure data consistency
- Rollback capabilities

### Technology Stack

#### Development
- **Language**: C# (.NET Framework 4.8 or .NET 6+)
- **ORM**: Dapper (micro-ORM for performance)
- **Database**: MSSQL Server 2019+
- **Validation**: FluentValidation
- **Serialization**: Newtonsoft.Json

#### Testing
- **Unit Testing**: NUnit or xUnit
- **Mocking**: Moq
- **Test Data**: Bogus (for fake data generation)
- **Coverage**: Coverlet

#### Tools
- **IDE**: Visual Studio 2022
- **Version Control**: Git
- **CI/CD**: Azure DevOps or GitHub Actions

### Component Design

```
EBase.ConfigMgmt/
├── Domain/
│   ├── Entities/
│   │   ├── BaseEntity.cs
│   │   ├── MeasurementUnit.cs
│   │   ├── MeterProduct.cs
│   │   ├── Meter.cs
│   │   ├── Allocation.cs
│   │   ├── Storage.cs
│   │   ├── Contract.cs
│   │   ├── VirtualMeter.cs
│   │   ├── Administration.cs
│   │   ├── FormulaType.cs
│   │   ├── PortfolioTemplate.cs
│   │   └── ContractTemplate.cs
│   ├── Repositories/
│   │   ├── IRepository.cs
│   │   ├── Repository.cs
│   │   ├── IMeasurementUnitRepository.cs
│   │   ├── MeasurementUnitRepository.cs
│   │   └── [Other specific repositories...]
│   └── Validation/
│       ├── ValidationAttributes/
│       │   ├── RequiredNotEmptyAttribute.cs
│       │   └── ValidReferenceAttribute.cs
│       └── BusinessRules/
│           ├── MeasurementUnitValidator.cs
│           └── [Other validators...]
└── Infrastructure/
    ├── Data/
    │   ├── DapperContext.cs
    │   ├── UnitOfWork.cs
    │   └── ConnectionFactory.cs
    └── Configuration/
        └── DatabaseSettings.cs
```

## Implementation Details

### Implementation Approach

#### Phase 1: Foundation (Week 1)
1. Create BaseEntity abstract class with common properties
2. Implement generic IRepository<T> interface
3. Implement generic Repository<T> base class with Dapper
4. Set up Dapper configuration and mappings
5. Implement connection management and pooling

#### Phase 2: Core Entities (Week 2)
1. Create domain entities for first 5 tables:
   - MeasurementUnit (D_BETREKKING)
   - MeterProduct (D_PORTFOLIOTYPE)
   - Meter (D_FLEXMETERNR)
   - Allocation (D_FLEXCONSTRUCTIE)
   - Storage (D_FLEXOPSLAG)
2. Implement specific repositories for specialized queries
3. Add validation attributes and business rules
4. Write unit tests for all entities and repositories

#### Phase 3: Remaining Entities (Week 3)
1. Create domain entities for remaining 6 tables:
   - Contract (D_FLEXCONTRACT)
   - VirtualMeter (D_FLEXMETER)
   - Administration (D_FLEXADMINISTRATIE)
   - FormulaType (D_FORMULETYPE)
   - PortfolioTemplate (D_PORTFOLIOTEMPLATE)
   - ContractTemplate (D_CONTRACTTEMPLATE)
2. Implement specific repositories
3. Add validation and business rules
4. Write unit tests

#### Phase 4: Testing and Refinement (Week 4)
1. Integration testing with real database
2. Performance testing and optimization
3. Security testing (SQL injection, parameter handling)
4. Code review and refinement
5. Documentation completion

### Code Structure

#### Base Entity
```csharp
/// <summary>
/// Base entity class with common properties for all domain entities
/// </summary>
public abstract class BaseEntity
{
    /// <summary>
    /// Unique identifier (primary key)
    /// </summary>
    public int NR { get; set; }

    /// <summary>
    /// Date and time when the entity was created
    /// </summary>
    public DateTime CreatedDate { get; set; }

    /// <summary>
    /// Date and time when the entity was last modified (nullable)
    /// </summary>
    public DateTime? ModifiedDate { get; set; }

    /// <summary>
    /// Username of the user who created the entity
    /// </summary>
    public string CreatedBy { get; set; }

    /// <summary>
    /// Username of the user who last modified the entity
    /// </summary>
    public string ModifiedBy { get; set; }
}
```

#### Domain Entity Example
```csharp
/// <summary>
/// Represents a measurement unit (BETREKKING) in the EBASE system
/// </summary>
public class MeasurementUnit : BaseEntity
{
    /// <summary>
    /// Unit name or symbol (e.g., "kWh", "m3")
    /// </summary>
    [Required]
    [MaxLength(50)]
    public string Unit { get; set; }

    /// <summary>
    /// Conversion factor to base unit
    /// </summary>
    public decimal Factor { get; set; }

    /// <summary>
    /// Switch value for unit type classification
    /// </summary>
    public int Switch { get; set; }

    /// <summary>
    /// Interval type for meter readings
    /// </summary>
    public int Interval { get; set; }

    /// <summary>
    /// Unit type classification
    /// </summary>
    public int UnitType { get; set; }

    /// <summary>
    /// Foreign key to counter unit (nullable)
    /// </summary>
    public int? CounterUnitNR { get; set; }

    /// <summary>
    /// Navigation property to counter unit
    /// </summary>
    public MeasurementUnit CounterUnit { get; set; }
}
```

#### Repository Interface
```csharp
/// <summary>
/// Generic repository interface for CRUD operations
/// </summary>
/// <typeparam name="T">Entity type (must inherit from BaseEntity)</typeparam>
public interface IRepository<T> where T : BaseEntity
{
    /// <summary>
    /// Get entity by ID
    /// </summary>
    Task<T> GetByIdAsync(int id);

    /// <summary>
    /// Get all entities
    /// </summary>
    Task<IEnumerable<T>> GetAllAsync();

    /// <summary>
    /// Add new entity
    /// </summary>
    Task<T> AddAsync(T entity);

    /// <summary>
    /// Update existing entity
    /// </summary>
    Task<T> UpdateAsync(T entity);

    /// <summary>
    /// Delete entity by ID
    /// </summary>
    Task DeleteAsync(int id);

    /// <summary>
    /// Check if entity exists by ID
    /// </summary>
    Task<bool> ExistsAsync(int id);
}
```

#### Repository Implementation
```csharp
/// <summary>
/// Generic repository implementation using Dapper
/// </summary>
public class Repository<T> : IRepository<T> where T : BaseEntity
{
    protected readonly IDbConnection _connection;
    protected readonly string _tableName;

    public Repository(IDbConnection connection, string tableName)
    {
        _connection = connection;
        _tableName = tableName;
    }

    public virtual async Task<T> GetByIdAsync(int id)
    {
        var sql = $"SELECT * FROM {_tableName} WHERE NR = @Id";
        return await _connection.QuerySingleOrDefaultAsync<T>(sql, new { Id = id });
    }

    public virtual async Task<IEnumerable<T>> GetAllAsync()
    {
        var sql = $"SELECT * FROM {_tableName}";
        return await _connection.QueryAsync<T>(sql);
    }

    public virtual async Task<T> AddAsync(T entity)
    {
        // Implementation with INSERT and SCOPE_IDENTITY()
        // ...
    }

    public virtual async Task<T> UpdateAsync(T entity)
    {
        // Implementation with UPDATE
        // ...
    }

    public virtual async Task DeleteAsync(int id)
    {
        var sql = $"DELETE FROM {_tableName} WHERE NR = @Id";
        await _connection.ExecuteAsync(sql, new { Id = id });
    }

    public virtual async Task<bool> ExistsAsync(int id)
    {
        var sql = $"SELECT COUNT(1) FROM {_tableName} WHERE NR = @Id";
        var count = await _connection.ExecuteScalarAsync<int>(sql, new { Id = id });
        return count > 0;
    }
}
```

### Dependencies

#### NuGet Packages
- **Dapper** (v2.0+): Micro-ORM for efficient database access
- **System.Data.SqlClient** (v4.8+): SQL Server data provider
- **Newtonsoft.Json** (v13.0+): JSON serialization
- **FluentValidation** (v11.0+): Validation framework
- **Microsoft.Extensions.Configuration** (v6.0+): Configuration management

#### Development Dependencies
- **NUnit** or **xUnit**: Unit testing framework
- **Moq** (v4.18+): Mocking framework
- **Bogus** (v34.0+): Fake data generation
- **Coverlet** (v6.0+): Code coverage

### Configuration

#### Database Connection Strings
```json
{
  "ConnectionStrings": {
    "EBaseDb": "Server=localhost;Database=EBASE;Integrated Security=true;TrustServerCertificate=true;"
  }
}
```

#### Dapper Configuration
```csharp
// Custom type handlers for special types
SqlMapper.AddTypeHandler(new JsonTypeHandler());
SqlMapper.AddTypeHandler(new DateTimeOffsetHandler());

// Column name mapping
DefaultTypeMap.MatchNamesWithUnderscores = true;
```

#### Logging Configuration
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "EBase.ConfigMgmt.Domain": "Debug"
    }
  }
}
```

## Testing Strategy

### Unit Testing

#### Entity Tests
- Test property getters and setters
- Test validation attributes
- Test business rule methods
- Test entity relationships

#### Repository Tests
- Test all CRUD operations
- Test with mock database connections
- Test parameter handling
- Test null and edge cases
- Target: >90% code coverage

```csharp
[Test]
public async Task GetByIdAsync_WithValidId_ReturnsEntity()
{
    // Arrange
    var mockConnection = new Mock<IDbConnection>();
    var repository = new Repository<MeasurementUnit>(mockConnection.Object, "D_BETREKKING");

    // Act
    var result = await repository.GetByIdAsync(1);

    // Assert
    Assert.IsNotNull(result);
    Assert.AreEqual(1, result.NR);
}
```

### Integration Testing

#### Database Integration Tests
- Test with real database (test environment)
- Test transaction management and rollback
- Test foreign key relationships
- Test concurrent access
- Test performance with large datasets

```csharp
[Test]
public async Task IntegrationTest_AddAndRetrieveEntity()
{
    // Arrange
    using var connection = new SqlConnection(TestConnectionString);
    using var transaction = connection.BeginTransaction();
    var repository = new MeasurementUnitRepository(connection, transaction);

    var entity = new MeasurementUnit
    {
        Unit = "kWh",
        Factor = 1.0m,
        Switch = 1,
        Interval = 15,
        UnitType = 1
    };

    // Act
    var added = await repository.AddAsync(entity);
    var retrieved = await repository.GetByIdAsync(added.NR);

    // Assert
    Assert.AreEqual(entity.Unit, retrieved.Unit);

    // Cleanup
    transaction.Rollback();
}
```

### Performance Testing

#### Performance Benchmarks
- Single entity operations: <100ms
- Batch operations (100 entities): <1 second
- Large query (10,000 entities): <5 seconds
- Memory usage: <100MB for 10,000 entities

```csharp
[Test]
public async Task PerformanceTest_GetAllAsync()
{
    var stopwatch = Stopwatch.StartNew();
    var entities = await repository.GetAllAsync();
    stopwatch.Stop();

    Assert.Less(stopwatch.ElapsedMilliseconds, 5000,
        "GetAllAsync should complete in less than 5 seconds");
}
```

### Security Testing

#### SQL Injection Prevention
- Test with malicious input strings
- Verify parameterized queries are used
- Test special characters in data
- Verify no dynamic SQL concatenation

```csharp
[Test]
public async Task SecurityTest_SqlInjectionPrevention()
{
    // Attempt SQL injection
    var maliciousInput = "'; DROP TABLE D_BETREKKING; --";

    // Should safely handle the input (parameterized query)
    var result = await repository.GetByIdAsync(maliciousInput);

    // Should return null, not execute the SQL
    Assert.IsNull(result);
}
```

## Deployment and Operations

### Deployment Requirements

#### Assembly Deployment
- Deploy as NuGet package or shared library
- Version using Semantic Versioning (SemVer)
- Include XML documentation
- Strong-name signing for security

#### Database Schema
- Verify database schema compatibility
- Check for required columns and types
- Validate foreign key relationships
- Ensure indexes exist for performance

#### Configuration
- Connection string in configuration file
- Environment-specific settings
- Logging configuration
- Feature flags for gradual rollout

### Monitoring and Logging

#### Operation Logging
- Log all database operations (INFO level)
- Log errors with stack traces (ERROR level)
- Log performance metrics (DEBUG level)
- Include correlation IDs for tracing

#### Performance Monitoring
- Monitor query execution times
- Track connection pool usage
- Monitor memory consumption
- Alert on performance degradation

#### Audit Trail
- Log all data modifications
- Include user information
- Include timestamps
- Include before/after values for updates

### Error Handling

#### Database Connection Errors
- Retry logic with exponential backoff
- Circuit breaker pattern for repeated failures
- Clear error messages for connection issues
- Fallback to cached data where appropriate

#### Transaction Errors
- Automatic rollback on errors
- Log transaction failures
- Preserve transaction context for retry
- Clear error reporting to caller

#### Validation Errors
- Collect all validation errors
- Return clear, actionable error messages
- Include field names and validation rules
- Support localization

### Performance Considerations

#### Connection Pooling
- Enable connection pooling (default in ADO.NET)
- Configure min/max pool size
- Monitor pool exhaustion
- Proper connection disposal

#### Query Optimization
- Use appropriate indexes
- Avoid SELECT *
- Use pagination for large result sets
- Consider compiled queries for hot paths

#### Memory Management
- Dispose connections properly
- Use streaming for large datasets
- Avoid loading entire result sets into memory
- Monitor garbage collection

#### Caching Strategies
- Cache frequently accessed, rarely changed data
- Use distributed cache for multi-instance deployments
- Implement cache invalidation
- Monitor cache hit rates

## Acceptance Criteria

### Technical Acceptance Criteria
- [ ] All 11 bootstrapped configuration tables have standardized domain entities
- [ ] All entities inherit from BaseEntity with proper property mappings
- [ ] Repository interfaces and implementations follow consistent patterns
- [ ] Dapper mappings are standardized and reusable
- [ ] Entity validation and business rules are encapsulated
- [ ] Foreign key relationships are properly handled
- [ ] Unit tests cover all entity and repository operations (>90% coverage)
- [ ] Integration tests pass with real database
- [ ] Performance requirements are met (<100ms for single operations)
- [ ] Security requirements are satisfied (no SQL injection vulnerabilities)
- [ ] Code review completed and approved
- [ ] Documentation is complete and accurate

### Definition of Done
- [ ] Feature is implemented according to specifications
- [ ] All acceptance criteria are met and verified
- [ ] Code review completed and approved by senior developer
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests written and passing
- [ ] Performance tests meet requirements
- [ ] Security testing completed (SQL injection prevention)
- [ ] Documentation complete (code comments, README, architecture docs)
- [ ] Deployed to development environment and tested
- [ ] Deployment guide created
- [ ] Rollback plan documented
- [ ] Knowledge transfer to team completed
```
