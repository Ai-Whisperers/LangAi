---
id: exemplar.agile.technical-feature.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Technical Feature
illustrates: agile.technical-feature-documentation
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-agile
  last_review: 2025-12-06
---

# Technical Feature Exemplar: TF-001 - Domain Entity Framework

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
Need a standardized framework for domain entities and repositories to ensure consistent data access patterns across all bootstrapped configuration tables.

### Business Impact
- Enables consistent data extraction across all supported tables
- Provides foundation for all other technical features
- Ensures maintainable and testable code structure

### Technical Value
- Consistent data access patterns
- Reusable repository implementations
- Standardized validation and business rules
- Improved testability and maintainability

### Success Metrics
- All 11 tables have standardized domain entities and repositories
- Consistent patterns across all implementations
- Full unit test coverage for all operations

## User Stories
### Primary User Story
As a developer, I want to have standardized domain entities and repositories so that I can consistently extract, transform, and persist EBASE bootstrapped configuration data across all supported tables without duplicating code.

**Acceptance Criteria:**
- Domain entities exist for all 11 bootstrapped configuration tables with proper property mappings
- Repository interfaces and implementations follow consistent patterns
- Dapper mappings are standardized and reusable
- Entity validation and business rules are encapsulated
- Foreign key relationships are properly handled
- Unit tests cover all entity and repository operations

### Secondary User Stories
1. **Data Consistency Story**: As a system architect, I want consistent data access patterns across all bootstrapped configuration tables so that I can ensure data integrity and maintainability.

2. **Testing Support Story**: As a QA engineer, I want standardized entity and repository patterns so that I can create consistent unit tests and integration tests.

## Technical Requirements
### Functional Requirements
- Create domain entities for all 11 bootstrapped configuration tables
- Implement repository pattern with generic CRUD operations
- Support for transaction management and rollback capabilities
- Include validation attributes and business rule enforcement

### Non-Functional Requirements
- **Performance**: Efficient database access with proper parameter handling
- **Security**: SQL injection prevention and proper parameter handling
- **Scalability**: Support for large datasets and batch operations
- **Maintainability**: Consistent patterns and reusable components

### Integration Requirements
- Integration with Dapper micro-ORM
- Support for MSSQL database connections
- Integration with existing EBASE database schema
- Support for transaction management

### Data Requirements
- Domain entities with proper property mappings
- Repository interfaces and implementations
- Dapper mapping configurations
- Validation and business rule implementations

## Architecture and Design
### Architecture Impact
- New domain layer with standardized entities
- Repository pattern implementation
- Integration with existing EBASE systems
- Foundation for all other technical features

### Design Patterns
- Domain-Driven Design (DDD) principles
- Repository pattern for data access
- Generic repository pattern for common operations
- Unit of Work pattern for transaction management

### Technology Stack
- C# with .NET Framework/Core
- Dapper micro-ORM for data access
- MSSQL database
- Unit testing framework (NUnit/xUnit)

### Component Design
```
Domain Layer:
├── Entities/
│   ├── BaseEntity.cs
│   ├── MeasurementUnit.cs
│   ├── MeterProduct.cs
│   ├── MeterPictogram.cs
│   ├── GridPointType.cs
│   ├── PhysicalProduct.cs
│   ├── Market.cs
│   ├── Country.cs
│   ├── Calendar.cs
│   ├── CalendarEntry.cs
│   ├── Profile.cs
│   └── ProfileClass.cs
├── Repositories/
│   ├── IRepository<T>.cs
│   ├── Repository<T>.cs
│   ├── IMeasurementUnitRepository.cs
│   ├── MeasurementUnitRepository.cs
│   └── [Other specific repositories...]
└── Validation/
    ├── ValidationAttributes/
    │   ├── RequiredFieldAttribute.cs
    │   ├── RangeAttribute.cs
    │   └── CustomValidationAttribute.cs
    └── BusinessRules/
        ├── IBusinessRule.cs
        ├── MeasurementUnitBusinessRule.cs
        └── [Other business rules...]
```

## Implementation Details
### Implementation Approach
1. Create base entity classes with common properties (NR, audit fields)
2. Implement repository pattern with generic CRUD operations
3. Use Dapper for efficient database access with proper parameter handling
4. Include validation attributes and business rule enforcement
5. Support for transaction management and rollback capabilities

### Code Structure
```csharp
// Base entity
public abstract class BaseEntity
{
    public int NR { get; set; }
    public DateTime CreatedDate { get; set; }
    public DateTime? ModifiedDate { get; set; }
    public string CreatedBy { get; set; }
    public string ModifiedBy { get; set; }
}

// Domain entity example
public class MeasurementUnit : BaseEntity
{
    public string Unit { get; set; }
    public decimal Factor { get; set; }
    public int Switch { get; set; }
    public int Interval { get; set; }
    public int UnitType { get; set; }
    public int? CounterUnitNR { get; set; }
}

// Repository interface
public interface IRepository<T> where T : BaseEntity
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<IEnumerable<T>> GetByFilterAsync(Expression<Func<T, bool>> filter);
    Task<T> AddAsync(T entity);
    Task<T> UpdateAsync(T entity);
    Task DeleteAsync(int id);
    Task<bool> ExistsAsync(int id);
}

// Repository implementation
public class Repository<T> : IRepository<T> where T : BaseEntity
{
    private readonly IDbConnection _connection;
    private readonly string _tableName;

    public Repository(IDbConnection connection, string tableName)
    {
        _connection = connection;
        _tableName = tableName;
    }

    public async Task<T> GetByIdAsync(int id)
    {
        var sql = $"SELECT * FROM {_tableName} WHERE NR = @Id";
        return await _connection.QueryFirstOrDefaultAsync<T>(sql, new { Id = id });
    }

    public async Task<IEnumerable<T>> GetAllAsync()
    {
        var sql = $"SELECT * FROM {_tableName}";
        return await _connection.QueryAsync<T>(sql);
    }

    // Additional implementation methods...
}
```

### Dependencies
- **Dapper**: 2.0.123 (micro-ORM for data access)
- **System.Data.SqlClient**: 4.8.5 (MSSQL database provider)
- **Newtonsoft.Json**: 13.0.3 (for serialization)
- **FluentValidation**: 11.8.1 (for validation)

### Configuration
- **Database connection strings**: appsettings.json
- **Dapper mapping configurations**: Mapping classes
- **Validation rule configurations**: Validation attributes and business rules
- **Logging configurations**: Serilog or NLog settings

## Testing Strategy
### Unit Testing
- Test all repository operations (CRUD) with mocked database connections
- Test entity validation and business rules
- Test Dapper mappings and queries
- Test transaction management and rollback scenarios

### Integration Testing
- Test database operations with real database
- Test transaction management and rollback
- Test foreign key relationships
- Test performance with large datasets

### Performance Testing
- Test query performance with large datasets (10,000+ records)
- Test memory usage and garbage collection
- Test concurrent access patterns
- Test transaction isolation levels

### Security Testing
- Test SQL injection prevention
- Test parameter handling and validation
- Test authentication and authorization
- Test data access permissions

## Deployment and Operations
### Deployment Requirements
- Database schema compatibility verification
- Connection string configuration and validation
- Assembly deployment and versioning
- Configuration file management and validation

### Monitoring and Logging
- Database operation logging with performance metrics
- Entity validation error logging
- Repository operation audit trail
- Performance monitoring and alerting

### Error Handling
- Database connection error handling with retry logic
- Transaction rollback on errors with proper cleanup
- Validation error reporting with detailed messages
- Logging and monitoring integration for error tracking

### Performance Considerations
- Connection pooling configuration for optimal performance
- Query optimization and indexing recommendations
- Memory management for large datasets
- Caching strategies for frequently accessed data

## Acceptance Criteria
### Technical Acceptance Criteria
- [ ] All 11 bootstrapped configuration tables have standardized domain entities
- [ ] Repository interfaces and implementations follow consistent patterns
- [ ] Dapper mappings are standardized and reusable
- [ ] Entity validation and business rules are encapsulated
- [ ] Foreign key relationships are properly handled
- [ ] Unit tests cover all entity and repository operations
- [ ] Performance requirements are met (queries complete within 5 seconds)
- [ ] Security requirements are satisfied (SQL injection prevention)

### Definition of Done
- [ ] Feature is implemented and tested
- [ ] All acceptance criteria are met
- [ ] Code review is completed
- [ ] Unit tests pass with >90% coverage
- [ ] Integration tests pass
- [ ] Performance tests meet requirements
- [ ] Security review is completed
- [ ] Documentation is complete and accurate
- [ ] Feature is deployed to staging environment

## Additional Information
### Architecture Diagrams
- Domain layer architecture diagram
- Repository pattern implementation diagram
- Entity relationship diagram for all 11 tables
- Data access flow diagram

### Code Examples
```csharp
// Specific repository interface
public interface IMeasurementUnitRepository : IRepository<MeasurementUnit>
{
    Task<MeasurementUnit> GetByUnitAsync(string unit);
    Task<IEnumerable<MeasurementUnit>> GetByUnitTypeAsync(int unitType);
    Task<IEnumerable<MeasurementUnit>> GetCounterUnitsAsync();
}

// Business rule implementation
public class MeasurementUnitBusinessRule : IBusinessRule<MeasurementUnit>
{
    public ValidationResult Validate(MeasurementUnit entity)
    {
        var result = new ValidationResult();
        
        if (string.IsNullOrWhiteSpace(entity.Unit))
            result.AddError("Unit", "Unit name is required");
            
        if (entity.Factor <= 0)
            result.AddError("Factor", "Factor must be greater than zero");
            
        return result;
    }
}
```

### Related Documents
- **EPP-192 Epic**: Standard Configuration Management
- **BF-001 Business Feature**: Configuration Data Extraction
- **EBASE Database Schema**: Table structure documentation
- **Dapper Documentation**: Micro-ORM usage guidelines

### Technical Notes
- Use fixed record numbering ranges (below 1000) for standard configurations
- Implement proper audit trail for all entity changes
- Consider caching strategies for frequently accessed entities
- Ensure backward compatibility with existing EBASE systems

