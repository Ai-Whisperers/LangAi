---
id: exemplar.technical-specifications.domain-overview.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Domain Overview specification
illustrates: technical-specifications.domain-overview
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Domain Overview: Units Management

**Domain**: Units Management
**Status**: Specification Complete
**Created**: 2025-11-29
**Last Updated**: 2025-11-29
**Source**: eBase C++ Units Module Analysis

## Overview

The Units Management domain provides a comprehensive framework for defining, managing, and converting measurement units throughout the eBase energy management system. This domain is foundational to all energy calculations, market operations, billing processes, and data exchange activities.

**Strategic Importance**: Units Management is a cross-cutting concern that touches every domain in the system. Accurate unit handling ensures energy conservation, billing correctness, and regulatory compliance across all market operations.

### Domain Purpose

**Business Problem**: Energy markets operate with diverse measurement units (kWh, MWh, GWh, m³, Nm³, MJ, etc.) across different contexts (consumption, production, capacity, trading). Without a centralized unit management system:
- Conversion errors lead to billing inaccuracies
- Cross-market data exchange fails due to unit incompatibilities
- Reporting becomes inconsistent across business processes
- Regulatory compliance is difficult to maintain

**Domain Solution**: The Units Management domain provides:
- Standardized unit definitions with conversion mathematics
- Type-safe conversion operations with bidirectional validation
- Temporal interval handling for time-series data
- Integration with market operations, billing, and reporting

### Key Domain Insight

**Core Principle**: Units are not merely labels - they encapsulate conversion mathematics, temporal semantics, and type safety constraints that ensure energy conservation and calculation correctness throughout the entire system.

## Domain Architecture

### Bounded Context

**Context Boundary**: Units Management owns:
- Measurement unit definitions and metadata
- Conversion factor mathematics and validation
- Unit type classifications and compatibility rules
- Switch interval semantics for time-series operations

**External Dependencies**:
- **Products Domain**: MeterProduct references for metering context
- **Profiles Domain**: Profile units for consumption patterns
- **Markets Domain**: Market-specific unit preferences
- **Calendars Domain**: Temporal interval calculations

**Integration Points**:
- **Inbound**: Unit creation/modification from configuration management
- **Outbound**: Unit metadata for all calculation domains
- **Bidirectional**: Conversion services consumed system-wide

### Domain Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Units Management Domain                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ MeasurementUnit  │◄────────│   UnitType       │          │
│  │  (Aggregate Root)│         │  (Enumeration)   │          │
│  └────────┬─────────┘         └──────────────────┘          │
│           │                                                   │
│           │ CounterUnit (self-reference)                     │
│           ↓                                                   │
│  ┌───────────────────┐                                       │
│  │ MeasurementUnit   │                                       │
│  │  (Counter Unit)   │                                       │
│  └───────────────────┘                                       │
│                                                               │
│  ┌───────────────────────────────────────┐                  │
│  │    UnitConversionService              │                  │
│  │  ┌─────────────────────────────────┐  │                  │
│  │  │ • Convert(value, source, target)│  │                  │
│  │  │ • ValidateSymmetry()             │  │                  │
│  │  │ • BatchConvert()                 │  │                  │
│  │  │ • ConvertTimeSeries()            │  │                  │
│  │  └─────────────────────────────────┘  │                  │
│  └───────────────────────────────────────┘                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

External Domain Integration:
  ↑                      ↑                      ↑
  │                      │                      │
Products Domain    Profiles Domain    Markets Domain
(MeterProduct)      (Profile.UnitId)   (Market preferences)
```

### Aggregate Roots

**MeasurementUnit** (Primary Aggregate):
- **Identity**: Nr (long, system-generated)
- **Business Keys**: Unit symbol (string, tenant-unique)
- **Invariants**:
  - Factor must be positive and non-zero
  - Counter unit relationship must maintain mathematical symmetry
  - Type-safe conversions enforced within UnitType
- **Lifecycle**: Created by configuration management, rarely modified, never deleted (soft delete with validity periods)

### Domain Services

**UnitConversionService**:
- **Responsibility**: Performs unit conversions with validation
- **Operations**:
  - `Convert(value, sourceUnit, targetUnit)` - Basic conversion
  - `BatchConvert(values, sourceUnit, targetUnit)` - Optimized batch processing
  - `ConvertTimeSeries(series, sourceUnit, targetUnit, aggregation)` - Interval-aware conversion
- **Stateless**: No internal state, thread-safe for concurrent operations

**UnitValidationService**:
- **Responsibility**: Validates unit definitions and conversion requests
- **Operations**:
  - `ValidateConversionFactor(factor)` - Rule 1 enforcement
  - `ValidateCounterUnitSymmetry(unit, counterUnit)` - Rule 2 enforcement
  - `ValidateTypeCompatibility(sourceType, targetType)` - Rule 3 enforcement
- **Cross-cutting**: Used by repositories, domain entities, and services

## Entity Relationships

### Internal Domain Relationships

**MeasurementUnit ↔ MeasurementUnit (Counter Unit)**:
- **Type**: Optional self-reference
- **Cardinality**: 0..1
- **Purpose**: Bidirectional conversion validation
- **Example**: kWh (factor=1000) ↔ MWh (factor=0.001)
- **Constraint**: Product of factors must equal 1.0 (within tolerance)

**Database Implementation**: See [Units Database Schema - Self-Reference](../database/units-database-schema.md#counterunitid-self-reference)

### Cross-Domain Relationships

**MeterProduct → MeasurementUnit**:
- **Type**: Many-to-one (products reference default units)
- **Cardinality**: 0..1 (optional default unit per product)
- **Purpose**: Meter products define default measurement units
- **Direction**: Products domain depends on Units domain
- **Reference**: See [MeterProduct Domain Object](../../products/domain-objects/meter-product-domain-object.md)

**Profile → MeasurementUnit**:
- **Type**: Many-to-one (profiles specify consumption units)
- **Cardinality**: 1 (profiles must have a unit)
- **Purpose**: Profiles use units for consumption pattern definitions
- **Direction**: Profiles domain depends on Units domain
- **Reference**: See [Profile Domain Object](../../profiles/domain-objects/profile-domain-object.md)

### Entity Relationship Diagram

```
    ┌──────────────────────┐
    │   MeasurementUnit    │◄──────────────┐
    │  ┌────────────────┐  │               │ CounterUnit
    │  │ Nr (PK)        │  │               │ (self-reference)
    │  │ Unit           │  │◄──────────────┘
    │  │ UnitType       │  │
    │  │ Factor         │  │
    │  │ SwitchInterval │  │
    │  │ CounterUnitId  │  │
    │  │ MeterProductId │  │
    │  └────────────────┘  │
    └──────────────────────┘
              ▲      ▲
              │      │
              │      │
    ┌─────────┘      └──────────┐
    │                           │
┌───────────┐           ┌───────────┐
│  Profile  │           │MeterProduct│
│┌─────────┐│           │┌─────────┐│
││UnitId(FK)││           ││DefaultUnitId(FK)││
│└─────────┘│           │└─────────┘│
└───────────┘           └───────────┘
```

**Complete ERD**: See [Units Entity Relationships](../database/units-entity-relationships.md) for full database-level relationships

## Domain Specifications

### Domain Objects

- **[MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md)**: Complete field specifications, business rules, and C# implementation guidance

### Business Rules

- **[Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md)**: Validation logic, conversion algorithms, and exception handling

### Enumerations

- **[UnitType Enumeration](../enumerations/unit-type-enum.md)**: Unit classification values (Energy, Volume, Power, etc.)

### Database Schema

- **[Units Database Schema](../database/units-database-schema.md)**: `D_MEASUREMENTUNIT` table structure, constraints, and indexes

### Integration Points

- **[Unit Conversion API](../integration/unit-conversion-api.md)**: External system integration for conversion services

## Key Business Rules

This domain enforces critical business rules:

1. **Conversion Factor Validation**: Factors must be positive and non-zero to ensure mathematically valid conversions
   - **Rule ID**: [Rule 1](../business-rules/unit-conversion-business-rules.md#rule-1-conversion-factor-validation)
   - **Impact**: Prevents division by zero and negative energy values
   - **Enforcement**: Domain entity property setter

2. **Bidirectional Conversion Symmetry**: Counter unit relationships must maintain mathematical symmetry (A→B→A = A)
   - **Rule ID**: [Rule 2](../business-rules/unit-conversion-business-rules.md#rule-2-bidirectional-conversion-symmetry)
   - **Impact**: Ensures energy conservation in round-trip conversions
   - **Enforcement**: Domain service validation before persist

3. **Unit Type Consistency**: Conversions only valid between same unit types (no energy→volume conversions)
   - **Rule ID**: [Rule 3](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency)
   - **Impact**: Prevents physically impossible conversions
   - **Enforcement**: Domain service pre-conversion check

4. **Switch Interval Alignment**: Time-series conversions require compatible intervals
   - **Rule ID**: [Rule 4](../business-rules/unit-conversion-business-rules.md#rule-4-switch-interval-alignment)
   - **Impact**: Ensures proper temporal aggregation/disaggregation
   - **Enforcement**: Time-series conversion service

5. **Precision and Rounding**: Maintains calculation precision to prevent cumulative errors
   - **Rule ID**: [Rule 5](../business-rules/unit-conversion-business-rules.md#rule-5-precision-and-rounding)
   - **Impact**: Critical for billing accuracy over millions of calculations
   - **Enforcement**: Conversion service implementation

## Migration Considerations

### C++ to C# Translation

**Key Differences**:
| Aspect | C++ Implementation | C# Target | Migration Notes |
|--------|-------------------|-----------|-----------------|
| Numeric Type | `double` for Factor | `decimal` for Factor | Use decimal for financial precision |
| String Type | `AnsiString` | `string` (UTF-8) | Direct mapping, no encoding issues |
| Validation | Immediate throw in setter | Property validation + domain service | Maintain immediate validation |
| Persistence | Direct database access | Entity Framework Core | ORM configuration required |

**Behavioral Preservation**:
- Epsilon tolerance for factor symmetry (1e-9) must be identical
- Validation error messages must match C++ format for API compatibility
- Logging behavior for warnings must be replicated
- Performance caching strategy must be equivalent

### Database Migration

**Schema Changes**: None - C# uses existing `D_MEASUREMENTUNIT` table
**Data Migration**: None - existing data remains valid
**Constraint Migration**: EF Core must replicate all C++ database constraints

**Migration Validation**:
```sql
-- Validate factor symmetry for counter unit pairs
SELECT
    u1.NR as Unit1_Nr,
    u1.UNIT as Unit1_Symbol,
    u1.FACTOR as Unit1_Factor,
    u2.NR as Unit2_Nr,
    u2.UNIT as Unit2_Symbol,
    u2.FACTOR as Unit2_Factor,
    (u1.FACTOR * u2.FACTOR) as Product,
    ABS((u1.FACTOR * u2.FACTOR) - 1.0) as Deviation
FROM D_MEASUREMENTUNIT u1
INNER JOIN D_MEASUREMENTUNIT u2 ON u1.COUNTERUNITID = u2.NR
WHERE ABS((u1.FACTOR * u2.FACTOR) - 1.0) > 0.000000001;

-- Should return 0 rows (no symmetry violations)
```

### Integration Continuity

**API Compatibility**:
- REST endpoints must accept both `Nr` (ID) and `Unit` (symbol)
- JSON response format must match existing C++ API
- Error messages must maintain same structure for client compatibility

**Example API Contract** (preserve compatibility):
```json
POST /api/units/convert
{
  "value": 1500.0,
  "sourceUnit": "kWh",
  "targetUnit": "MWh"
}

Response:
{
  "convertedValue": 1.5,
  "sourceUnit": "kWh",
  "targetUnit": "MWh",
  "factor": 0.001,
  "timestamp": "2025-11-29T12:34:56Z"
}
```

## Usage Scenarios

### Scenario 1: Create Standard Energy Units

**Business Context**: Bootstrap new tenant with standard energy units

**Process**:
1. Create base unit (Wh - watt-hour)
2. Create kWh with factor 1000 (1 kWh = 1000 Wh)
3. Create MWh with factor 0.001 (1 MWh = 1000 kWh = 1000000 Wh)
4. Link kWh ↔ MWh as counter units
5. Validate symmetry: 1000 * 0.001 = 1.0 ✓

**Implementation**:
```csharp
var wh = new MeasurementUnit
{
    Unit = "Wh",
    UnitType = UnitType.Energy,
    Factor = 1.0M
};

var kwh = new MeasurementUnit
{
    Unit = "kWh",
    UnitType = UnitType.Energy,
    Factor = 1000.0M
};

var mwh = new MeasurementUnit
{
    Unit = "MWh",
    UnitType = UnitType.Energy,
    Factor = 0.001M
};

// Link counter units
kwh.CounterUnitId = mwh.Nr;
mwh.CounterUnitId = kwh.Nr;

// Validate symmetry before save
kwh.ValidateCounterUnitSymmetry();
```

### Scenario 2: Convert Time-Series Energy Data

**Business Context**: Convert 15-minute kWh meter readings to hourly MWh for reporting

**Process**:
1. Source: 15-minute kWh readings [10, 20, 30, 40] kWh
2. Target: 60-minute MWh aggregated value
3. Aggregation: Sum 4 periods (10+20+30+40 = 100 kWh)
4. Conversion: 100 kWh → 0.1 MWh
5. Result: [0.1] MWh for the hour

**Implementation**:
```csharp
var sourceData = new[] { 10M, 20M, 30M, 40M }; // kWh per 15-min
var sourceUnit = await _repository.GetByUnitSymbolAsync("kWh");
var targetUnit = await _repository.GetByUnitSymbolAsync("MWh");

var result = await _conversionService.ConvertTimeSeries(
    sourceData,
    sourceUnit,
    targetUnit,
    TimeSeriesAggregation.Sum
);

// result: [0.1M] MWh
```

### Scenario 3: Validate Cross-Market Data Exchange

**Business Context**: Ensure imported market data uses compatible units before processing

**Process**:
1. External system sends data in "MW" (megawatts - power)
2. Internal system expects "kWh" (kilowatt-hours - energy)
3. Validation detects type mismatch (Power vs. Energy)
4. Conversion blocked, error returned to sender
5. Manual intervention required to clarify data semantics

**Implementation**:
```csharp
var externalUnit = await _repository.GetByUnitSymbolAsync("MW");
var internalUnit = await _repository.GetByUnitSymbolAsync("kWh");

if (!externalUnit.CanConvertTo(internalUnit))
{
    throw new UnitConversionException(
        $"Cannot convert {externalUnit.Unit} ({externalUnit.UnitType}) " +
        $"to {internalUnit.Unit} ({internalUnit.UnitType}). " +
        "Unit types are incompatible."
    );
}
```

## Performance Characteristics

### Expected Volumes

| Metric | Typical | Maximum | Notes |
|--------|---------|---------|-------|
| Total Units per Tenant | 50-100 | 500 | Standard energy units plus custom tenant units |
| Conversion Operations/Second | 1000-5000 | 50000 | Peak during batch processing |
| Database Queries/Second | 100-500 | 2000 | Most served from cache |
| Cache Hit Rate | 95% | 99% | Factor pairs heavily reused |

### Optimization Strategies

**Conversion Factor Caching**:
- LRU cache for last 100 factor pairs
- Cache key: `(sourceUnitId, targetUnitId)`
- Invalidation: On unit modification (rare)
- Impact: 10x performance improvement on cached conversions

**Batch Conversion Optimization**:
- Calculate factor once per batch instead of per value
- Use SIMD for large arrays (C# Vector<T>)
- Impact: 5-20x performance improvement for large batches

**Query Optimization**:
- Index on `Unit` symbol for business key lookups
- Eager load `CounterUnit` for symmetry validation
- Compiled queries for frequently-used patterns

## Stakeholder Guidance

### For Business Analysts

**What You Need to Know**:
- Units define how energy is measured and converted across all operations
- Incorrect unit handling directly impacts billing accuracy and customer satisfaction
- Unit conversions must preserve energy volume (no energy lost or created)
- Each market may have preferred units - system must handle all variants

**Your Responsibilities**:
- Validate unit definitions match regulatory requirements
- Confirm conversion factors align with industry standards
- Review unit catalogs for completeness and accuracy
- Sign off on unit-related business rules

### For Developers

**What You Need to Know**:
- MeasurementUnit is an aggregate root with strong invariants
- Use `decimal` for all conversion calculations (not `double` or `float`)
- Always validate type compatibility before conversion
- Conversion service is stateless and thread-safe

**Your Responsibilities**:
- Enforce validation rules in domain entity
- Implement EF Core configuration correctly
- Replicate C++ caching strategy for performance
- Maintain API compatibility with existing systems

### For QA/Testers

**What You Need to Know**:
- Unit conversion errors are critical defects (billing impact)
- Test round-trip conversions (A→B→A must equal A exactly)
- Validate cross-type conversion rejections
- Performance tests must include caching scenarios

**Your Responsibilities**:
- Validate all 5 business rules with comprehensive test cases
- Test edge cases (extreme factors, null counter units, incompatible types)
- Verify precision maintenance in conversion chains
- Confirm API compatibility with C++ system

## Related Documentation

### Domain Documentation
- **[MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md)**: Complete entity specification
- **[Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md)**: Validation and conversion logic
- **[UnitType Enumeration](../enumerations/unit-type-enum.md)**: Unit classification values

### Database Documentation
- **[Units Database Schema](../database/units-database-schema.md)**: `D_MEASUREMENTUNIT` table structure
- **[Units Entity Relationships](../database/units-entity-relationships.md)**: Complete ERD

### Integration Documentation
- **[Unit Conversion API](../integration/unit-conversion-api.md)**: External system integration

### Implementation Guidance
- **[MeasurementUnit Service Implementation](../../implementation/units/measurement-unit-service.md)**: C# implementation guide
- **[Conversion Service Implementation](../../implementation/units/conversion-service-implementation.md)**: Performance optimization guide

---

**Migration Phase**: 2 - Specification Creation
**Generated by**: rule.migration.spec-create.v1
**Source System**: eBase C++ Units Module
**Analyzed Source**: eBase/Units/*.cpp, eBase/Units/*.h
**Created**: 2025-11-29
**Last Updated**: 2025-11-29
**Status**: Stakeholder Review Complete
**Quality Gate**: Passed
