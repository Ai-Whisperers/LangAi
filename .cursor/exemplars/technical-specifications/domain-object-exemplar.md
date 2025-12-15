---
id: exemplar.technical-specifications.domain-object.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Domain Object specification
illustrates: technical-specifications.domain-object
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Domain Object: MeasurementUnit

**Domain**: Units Management  
**Status**: C++ Analysis Complete  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Source**: `eBase/Units/MeasurementUnit.h`, `eBase/Units/MeasurementUnit.cpp`

## Overview

The MeasurementUnit domain object represents units of measurement for energy calculations and conversions throughout the eBase energy management system. It serves as the foundation for all unit-based calculations, tariff applications, and market data exchange operations.

### Purpose

**Business Context**: Energy markets operate with diverse measurement units (kWh, MWh, GWh, m³, etc.). The MeasurementUnit domain object provides a standardized representation that enables:
- Accurate unit conversions with bidirectional symmetry
- Tariff calculations with correct unit semantics
- Market data exchange with proper unit metadata
- Time-series aggregation with interval-aware conversions

**Key Domain Insight**: MeasurementUnit is not merely a label - it encapsulates conversion mathematics, temporal intervals, and type safety constraints that ensure energy conservation throughout all system calculations.

### Related Specifications

- **Database Schema**: [Units Database Schema](../database/units-database-schema.md#d_measurementunit-table) for complete field specifications and constraints
- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md) for validation logic and conversion algorithms
- **Enumerations**: [UnitType Enumeration](../enumerations/unit-type-enum.md) for unit classification values
- **Domain Overview**: [Units Domain Overview](../domain-overview/units-domain-overview.md) for architectural context

## Domain Fields

### Identity Fields

**Nr (long)**  
- **Business Meaning**: System-assigned unique identifier for the measurement unit
- **Usage**: Primary key for database persistence, foreign key references from other domains
- **Validation**: Must be positive, auto-generated from GENCOUNTER_SEQ
- **C++ Source**: `MeasurementUnit.h:45` - `long m_Nr`
- **C# Mapping**: `public long Nr { get; private set; }`

**Unit (string, required)**  
- **Business Meaning**: Human-readable unit symbol for display (e.g., "kWh", "MWh", "m³")
- **Usage**: User interface display, report generation, data export labels
- **Validation**: Maximum 20 characters, must be unique within tenant, required field
- **C++ Source**: `MeasurementUnit.h:47` - `AnsiString m_Unit`
- **C# Mapping**: `public string Unit { get; set; }`
- **Example Values**: "kWh", "MWh", "GWh", "m³", "Nm³", "MJ"

### Classification Fields

**UnitType (int, required)**  
- **Business Meaning**: Classification of unit category for type-safe conversions
- **Usage**: Prevents invalid cross-type conversions (e.g., volume to energy)
- **Validation**: Must match valid UnitType enumeration value
- **C++ Source**: `MeasurementUnit.h:52` - `int m_UnitType`
- **C# Mapping**: `public UnitType UnitType { get; set; }`
- **Enumeration Reference**: See [UnitType Enumeration](../enumerations/unit-type-enum.md) for valid values (Energy=0, Volume=1, Power=2, etc.)

**OrderNr (double, optional)**  
- **Business Meaning**: Display order for user interface listings and dropdowns
- **Usage**: Sorts units in logical sequence (e.g., kWh before MWh before GWh)
- **Validation**: Non-negative, defaults to 0 if not specified
- **C++ Source**: `MeasurementUnit.h:49` - `double m_OrderNr`
- **C# Mapping**: `public double? OrderNr { get; set; }`

### Conversion Fields

**Factor (decimal, required)**  
- **Business Meaning**: Conversion multiplier to base unit for this unit type
- **Usage**: Core conversion mathematics - all conversions use factor-based calculations
- **Validation**: Must be positive and non-zero (see [Business Rules](../business-rules/unit-conversion-business-rules.md#rule-1-conversion-factor-validation))
- **C++ Source**: `MeasurementUnit.cpp:234` - `double m_Factor`
- **C# Mapping**: `public decimal Factor { get; set; }`
- **Example**: kWh factor=1000 means 1 kWh = 1000 Wh (base unit)

**CounterUnitId (long, optional)**  
- **Business Meaning**: Reference to inverse unit for bidirectional conversion validation
- **Usage**: Ensures conversion symmetry (A→B→A preserves value)
- **Validation**: Must reference valid MeasurementUnit if specified
- **C++ Source**: `MeasurementUnit.h:54` - `long m_CounterUnitId`
- **C# Mapping**: `public long? CounterUnitId { get; set; }`
- **Navigation**: `public virtual MeasurementUnit CounterUnit { get; set; }`
- **Example**: kWh (factor=1000) counter is MWh (factor=0.001)

### Temporal Fields

**SwitchInterval (int, optional)**  
- **Business Meaning**: Time interval in minutes for time-series data using this unit
- **Usage**: Ensures compatible interval conversions for time-series aggregation
- **Validation**: Must be 1-60 minutes for standard intervals, null for non-temporal units
- **C++ Source**: `MeasurementUnit.h:56` - `int m_SwitchInterval`
- **C# Mapping**: `public int? SwitchInterval { get; set; }`
- **Example Values**: 15 (quarterly), 60 (hourly), null (non-temporal like totals)

### Relationship Fields

**MeterProductId (long, optional)**  
- **Business Meaning**: Default meter product associated with this unit
- **Usage**: Links units to metering equipment for data collection context
- **Validation**: Must reference valid MeterProduct if specified
- **C++ Source**: `MeasurementUnit.h:58` - `long m_MeterProductId`
- **C# Mapping**: `public long? MeterProductId { get; set; }`
- **Navigation**: `public virtual MeterProduct MeterProduct { get; set; }`

## Domain Relationships

### Self-Reference: Counter Unit

**Relationship Type**: Optional self-reference for conversion symmetry  
**Cardinality**: 0..1 (unit may or may not have a counter unit)  
**Purpose**: Validates bidirectional conversion mathematics

```
MeasurementUnit (kWh, Factor=1000)
  ↔ CounterUnit: MeasurementUnit (MWh, Factor=0.001)

Validation: kWh.Factor * MWh.Factor ≈ 1.0
```

**Business Rule**: See [Bidirectional Conversion Symmetry](../business-rules/unit-conversion-business-rules.md#rule-2-bidirectional-conversion-symmetry)

### Foreign Reference: MeterProduct

**Relationship Type**: Many-to-one (many units can reference one meter product)  
**Cardinality**: 0..1 (unit may be independent of meter products)  
**Purpose**: Associates units with specific metering equipment

```
MeterProduct (Electricity Meter)
  ← MeasurementUnit (kWh)
  ← MeasurementUnit (MWh)
  ← MeasurementUnit (GWh)
```

**Database Schema**: See [Units Database Schema - Foreign Keys](../database/units-database-schema.md#foreign-key-constraints)

### Inverse Reference: Profile.UnitId

**Relationship Type**: One-to-many (one unit referenced by many profiles)  
**Cardinality**: 1..* (profiles must specify a unit)  
**Purpose**: Profiles use units for consumption pattern definitions

```
MeasurementUnit (kWh)
  → Profile (Residential Profile, UnitId = kWh.Nr)
  → Profile (Commercial Profile, UnitId = kWh.Nr)
  → Profile (Industrial Profile, UnitId = kWh.Nr)
```

**Cross-Domain Reference**: See [Profile Domain Object](../../profiles/domain-objects/profile-domain-object.md) in Profiles domain

## Business Rules

This domain object enforces these business rules:

1. **Conversion Factor Validation**: Factor must be positive and non-zero - See [Rule 1](../business-rules/unit-conversion-business-rules.md#rule-1-conversion-factor-validation)

2. **Bidirectional Conversion Symmetry**: Counter unit relationships must maintain mathematical symmetry - See [Rule 2](../business-rules/unit-conversion-business-rules.md#rule-2-bidirectional-conversion-symmetry)

3. **Unit Type Consistency**: Conversions only valid between same unit types - See [Rule 3](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency)

4. **Switch Interval Alignment**: Time-series conversions require compatible intervals - See [Rule 4](../business-rules/unit-conversion-business-rules.md#rule-4-switch-interval-alignment)

5. **Unit Symbol Uniqueness**: Unit symbols must be unique within tenant

**Validation Example**:
```csharp
// Rule 1: Factor validation
public decimal Factor
{
    get => _factor;
    set
    {
        if (value <= 0)
            throw new ValidationException("Factor must be positive");
        _factor = value;
    }
}

// Rule 5: Unit symbol uniqueness (repository level)
public async Task<bool> IsUnitSymbolUniqueAsync(string unit, long? excludeId = null)
{
    return !await _context.MeasurementUnits
        .AnyAsync(u => u.Unit == unit && u.Nr != excludeId);
}
```

## C# Implementation Guidance

### Domain Entity Class Structure

```csharp
namespace Eneve.eBase.Foundation.Domain.Units
{
    /// <summary>
    /// Represents a measurement unit for energy calculations and conversions
    /// </summary>
    public class MeasurementUnit : IAggregateRoot
    {
        // Identity fields
        public long Nr { get; private set; }
        public string Unit { get; set; } = string.Empty;
        
        // Classification fields
        public UnitType UnitType { get; set; }
        public double? OrderNr { get; set; }
        
        // Conversion fields
        private decimal _factor;
        public decimal Factor
        {
            get => _factor;
            set
            {
                if (value <= 0)
                    throw new ValidationException("Factor must be positive and non-zero");
                _factor = value;
            }
        }
        
        public long? CounterUnitId { get; set; }
        public virtual MeasurementUnit? CounterUnit { get; set; }
        
        // Temporal fields
        public int? SwitchInterval { get; set; }
        
        // Relationship fields
        public long? MeterProductId { get; set; }
        public virtual MeterProduct? MeterProduct { get; set; }
        
        // Domain methods
        public bool CanConvertTo(MeasurementUnit target)
        {
            return this.UnitType == target.UnitType;
        }
        
        public decimal ConvertValue(decimal value, MeasurementUnit target)
        {
            if (!CanConvertTo(target))
                throw new InvalidOperationException(
                    $"Cannot convert between incompatible types: {UnitType} → {target.UnitType}"
                );
            
            // Convert to base unit, then to target unit
            return (value * this.Factor) / target.Factor;
        }
        
        public void ValidateCounterUnitSymmetry()
        {
            if (CounterUnit == null) return;
            
            const decimal tolerance = 0.000000001M;
            decimal product = this.Factor * CounterUnit.Factor;
            if (Math.Abs(product - 1.0M) > tolerance)
                throw new ValidationException(
                    $"Counter unit symmetry violation: {Factor} * {CounterUnit.Factor} != 1.0"
                );
        }
    }
}
```

### Repository Interface

```csharp
namespace Eneve.eBase.Foundation.Infrastructure.Units
{
    public interface IMeasurementUnitRepository : IRepository<MeasurementUnit>
    {
        // Query by business keys
        Task<MeasurementUnit?> GetByUnitSymbolAsync(string unit);
        Task<IEnumerable<MeasurementUnit>> GetByUnitTypeAsync(UnitType unitType);
        
        // Validation queries
        Task<bool> IsUnitSymbolUniqueAsync(string unit, long? excludeId = null);
        Task<bool> ExistsAsync(long nr);
        
        // Relationship queries
        Task<MeasurementUnit?> GetWithCounterUnitAsync(long nr);
        Task<IEnumerable<MeasurementUnit>> GetByMeterProductAsync(long meterProductId);
        
        // Conversion support
        Task<decimal> GetConversionFactorAsync(long sourceUnitId, long targetUnitId);
    }
}
```

### Entity Framework Core Configuration

```csharp
public class MeasurementUnitConfiguration : IEntityTypeConfiguration<MeasurementUnit>
{
    public void Configure(EntityTypeBuilder<MeasurementUnit> builder)
    {
        builder.ToTable("D_MEASUREMENTUNIT");
        
        // Primary key
        builder.HasKey(e => e.Nr);
        builder.Property(e => e.Nr)
            .HasColumnName("NR")
            .ValueGeneratedOnAdd();
        
        // Required fields
        builder.Property(e => e.Unit)
            .HasColumnName("UNIT")
            .HasMaxLength(20)
            .IsRequired();
        
        builder.Property(e => e.UnitType)
            .HasColumnName("UNITTYPE")
            .IsRequired();
        
        builder.Property(e => e.Factor)
            .HasColumnName("FACTOR")
            .HasColumnType("decimal(18,9)")
            .IsRequired();
        
        // Optional fields
        builder.Property(e => e.OrderNr)
            .HasColumnName("ORDERNR");
        
        builder.Property(e => e.SwitchInterval)
            .HasColumnName("SWITCHINTERVAL");
        
        builder.Property(e => e.CounterUnitId)
            .HasColumnName("COUNTERUNITID");
        
        builder.Property(e => e.MeterProductId)
            .HasColumnName("METERPRODUCTID");
        
        // Unique constraint
        builder.HasIndex(e => e.Unit)
            .IsUnique()
            .HasDatabaseName("UX_MEASUREMENTUNIT_UNIT");
        
        // Self-reference relationship
        builder.HasOne(e => e.CounterUnit)
            .WithMany()
            .HasForeignKey(e => e.CounterUnitId)
            .OnDelete(DeleteBehavior.SetNull);
        
        // Foreign key to MeterProduct
        builder.HasOne(e => e.MeterProduct)
            .WithMany()
            .HasForeignKey(e => e.MeterProductId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}
```

## Migration Requirements

### Data Persistence

**C++ Storage**: Database-backed using `D_MEASUREMENTUNIT` table  
**C# Storage**: Entity Framework Core with SQL Server  
**Migration Path**: Direct table mapping with data type conversions

**Key Considerations**:
- C++ `double` for Factor → C# `decimal` for financial precision
- C++ `AnsiString` → C# `string` (UTF-8 encoding)
- Nullable foreign keys properly represented in C#

### Behavioral Preservation

**C++ Behaviors to Replicate**:
1. Factor validation on assignment (not just on save)
2. Counter unit symmetry validation before database commit
3. Type-safe conversion checks before calculation
4. Precision maintenance during conversion operations
5. Logging behavior for validation failures

**Test Scenarios**:
```
Test: Factor Validation
- C++ behavior: Throws exception immediately on Factor assignment of 0
- C# must: Throw ValidationException in property setter

Test: Counter Unit Symmetry
- C++ behavior: Validates on m_CounterUnitId assignment
- C# must: Validate in ValidateCounterUnitSymmetry() called before SaveChanges

Test: Type-Safe Conversion
- C++ behavior: Returns error code if types incompatible
- C# must: Throw InvalidOperationException with same message format
```

### Backwards Compatibility

**API Contracts**:
- External systems reference units by `Unit` symbol (business key)
- API endpoints must accept both `Nr` (ID) and `Unit` (symbol)
- JSON serialization must match existing C++ API format

**Example JSON** (maintain compatibility):
```json
{
  "nr": 1234,
  "unit": "kWh",
  "unitType": 0,
  "factor": 1000.0,
  "switchInterval": 15,
  "counterUnitId": 1235
}
```

## Usage Examples

### Creating a MeasurementUnit

```csharp
// Create kilowatt-hour (kWh) unit
var kwhUnit = new MeasurementUnit
{
    Unit = "kWh",
    UnitType = UnitType.Energy,
    Factor = 1000.0M,  // 1 kWh = 1000 Wh (base unit)
    SwitchInterval = 15,  // 15-minute intervals
    OrderNr = 10.0
};

// Validate and save
if (await _repository.IsUnitSymbolUniqueAsync(kwhUnit.Unit))
{
    await _repository.AddAsync(kwhUnit);
    await _unitOfWork.SaveChangesAsync();
}
```

### Setting Up Counter Units

```csharp
// Create MWh as counter to kWh
var mwhUnit = new MeasurementUnit
{
    Unit = "MWh",
    UnitType = UnitType.Energy,
    Factor = 0.001M,  // 1 MWh = 0.001 * base (mathematically 1000000 Wh)
    SwitchInterval = 15,
    OrderNr = 20.0,
    CounterUnitId = kwhUnit.Nr  // Reference kWh as counter
};

// Update kWh to reference MWh as counter
kwhUnit.CounterUnitId = mwhUnit.Nr;

// Validate symmetry
kwhUnit.ValidateCounterUnitSymmetry();  // Should pass: 1000 * 0.001 = 1.0

await _unitOfWork.SaveChangesAsync();
```

### Performing Unit Conversion

```csharp
// Convert 1500 kWh to MWh
var kwhUnit = await _repository.GetByUnitSymbolAsync("kWh");
var mwhUnit = await _repository.GetByUnitSymbolAsync("MWh");

decimal valueInKwh = 1500.0M;
decimal valueInMwh = kwhUnit.ConvertValue(valueInKwh, mwhUnit);
// Result: 1.5 MWh

// Verify round-trip
decimal backToKwh = mwhUnit.ConvertValue(valueInMwh, kwhUnit);
// Result: 1500.0 kWh (exact match)
```

## Related Documentation

- **Database Schema**: [Units Database Schema](../database/units-database-schema.md) for complete table structure and constraints
- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md) for validation and conversion logic
- **Enumerations**: [UnitType Enumeration](../enumerations/unit-type-enum.md) for classification values
- **Domain Overview**: [Units Domain Overview](../domain-overview/units-domain-overview.md) for architectural context
- **Integration Points**: [Unit Conversion API](../integration/unit-conversion-api.md) for external system integration
- **C# Implementation**: [MeasurementUnit Service Implementation](../../implementation/units/measurement-unit-service.md)

---

**Migration Phase**: 2 - Specification Creation  
**Generated by**: rule.migration.spec-create.v1  
**Source System**: eBase C++ Units Module  
**Analyzed Source**: eBase/Units/MeasurementUnit.h:45-58, eBase/Units/MeasurementUnit.cpp:89-456  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Status**: Technical Review Complete  
**Quality Gate**: Passed
