---
id: exemplar.technical-specifications.enumeration.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Enumeration specification
illustrates: technical-specifications.enumeration
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Enumeration: UnitType

**Domain**: Units Management  
**Status**: C++ Analysis Complete  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Source**: `eBase/Units/UnitType.h`, `eBase/Units/Constants.h`

## Overview

The UnitType enumeration classifies measurement units by their physical quantity type to enforce type-safe conversion operations. It prevents physically impossible conversions (e.g., energy to volume) and ensures mathematical correctness throughout the energy management system.

**Business Purpose**: Energy markets handle diverse physical quantities with different dimensional units. UnitType provides the foundation for:
- Type-safe unit conversion validation
- Prevention of dimensional analysis errors
- Clear semantic categorization for reporting
- Market-specific unit filtering and selection

**Key Enumeration Insight**: UnitType is not merely a classification label - it defines conversion compatibility boundaries that ensure physical laws (energy conservation, volume conservation) are respected in all calculations.

### Related Specifications
- **Domain Object**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for usage context
- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency) for type consistency validation
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md#unittype-field) for persistence mapping

## Enumeration Definition

### C++ Source Reference

**File**: `eBase/Units/UnitType.h:23-34`

```cpp
enum UnitType
{
    UNITTYPE_ENERGY = 0,     // Energy measurements (Wh, kWh, MWh, GWh, MJ, GJ)
    UNITTYPE_VOLUME = 1,     // Volume measurements (m³, Nm³, liters)
    UNITTYPE_POWER = 2,      // Power measurements (W, kW, MW, GW)
    UNITTYPE_MASS = 3,       // Mass measurements (kg, ton)
    UNITTYPE_TEMPERATURE = 4, // Temperature measurements (°C, °F, K)
    UNITTYPE_PERCENTAGE = 5,  // Dimensionless percentages (%)
    UNITTYPE_CURRENCY = 6,    // Currency measurements (€, $, £)
    UNITTYPE_TIME = 7        // Time measurements (min, hour, day)
};
```

### C# Enumeration Mapping

```csharp
namespace Eneve.eBase.Foundation.Domain.Units
{
    /// <summary>
    /// Classifies measurement units by physical quantity type for type-safe conversions
    /// </summary>
    public enum UnitType
    {
        /// <summary>
        /// Energy measurements (Wh, kWh, MWh, GWh, MJ, GJ)
        /// </summary>
        /// <remarks>
        /// Base unit: Watt-hour (Wh)
        /// Common usage: Electricity consumption, production, trading volumes
        /// Conversion rule: Only convertible to other energy units
        /// </remarks>
        Energy = 0,
        
        /// <summary>
        /// Volume measurements (m³, Nm³, liters)
        /// </summary>
        /// <remarks>
        /// Base unit: Cubic meter (m³)
        /// Common usage: Gas consumption, water usage
        /// Conversion rule: Only convertible to other volume units
        /// Note: Nm³ (normal cubic meters) includes pressure/temperature correction
        /// </remarks>
        Volume = 1,
        
        /// <summary>
        /// Power measurements (W, kW, MW, GW)
        /// </summary>
        /// <remarks>
        /// Base unit: Watt (W)
        /// Common usage: Generation capacity, peak demand, transmission capacity
        /// Conversion rule: Only convertible to other power units
        /// Dimensional relationship: Power = Energy / Time
        /// </remarks>
        Power = 2,
        
        /// <summary>
        /// Mass measurements (kg, ton, metric ton)
        /// </summary>
        /// <remarks>
        /// Base unit: Kilogram (kg)
        /// Common usage: CO₂ emissions, fuel mass
        /// Conversion rule: Only convertible to other mass units
        /// </remarks>
        Mass = 3,
        
        /// <summary>
        /// Temperature measurements (°C, °F, K)
        /// </summary>
        /// <remarks>
        /// Base unit: Celsius (°C)
        /// Common usage: Heating systems, weather data
        /// Conversion rule: Non-linear conversions (offset-based)
        /// Note: Requires special conversion handling due to zero-point differences
        /// </remarks>
        Temperature = 4,
        
        /// <summary>
        /// Dimensionless percentage measurements (%)
        /// </summary>
        /// <remarks>
        /// Base unit: Percentage (%)
        /// Common usage: Efficiency ratios, load factors, availability
        /// Conversion rule: Only convertible to other dimensionless units (%, fraction)
        /// </remarks>
        Percentage = 5,
        
        /// <summary>
        /// Currency measurements (€, $, £, kr)
        /// </summary>
        /// <remarks>
        /// Base unit: Euro (€) - market-dependent
        /// Common usage: Tariffs, costs, revenues, market prices
        /// Conversion rule: Currency exchange rates (time-varying)
        /// Note: Conversion requires external exchange rate service
        /// </remarks>
        Currency = 6,
        
        /// <summary>
        /// Time duration measurements (min, hour, day, month)
        /// </summary>
        /// <remarks>
        /// Base unit: Minute (min)
        /// Common usage: Billing periods, contract durations, data intervals
        /// Conversion rule: Fixed ratio conversions (except months/years)
        /// </remarks>
        Time = 7
    }
}
```

## Enumeration Values

| Value | Name | C++ Constant | C# Enum | Business Meaning | Physical Dimension | Example Units |
|-------|------|--------------|---------|------------------|-------------------|---------------|
| 0 | Energy | `UNITTYPE_ENERGY` | `UnitType.Energy` | Energy consumption/production | ML²T⁻² | Wh, kWh, MWh, GWh, MJ, GJ |
| 1 | Volume | `UNITTYPE_VOLUME` | `UnitType.Volume` | Gas/water volume | L³ | m³, Nm³, L, dm³ |
| 2 | Power | `UNITTYPE_POWER` | `UnitType.Power` | Generation/consumption capacity | ML²T⁻³ | W, kW, MW, GW |
| 3 | Mass | `UNITTYPE_MASS` | `UnitType.Mass` | Material mass/weight | M | kg, ton, lb |
| 4 | Temperature | `UNITTYPE_TEMPERATURE` | `UnitType.Temperature` | Temperature measurement | Θ | °C, °F, K |
| 5 | Percentage | `UNITTYPE_PERCENTAGE` | `UnitType.Percentage` | Dimensionless ratios | - | %, fraction |
| 6 | Currency | `UNITTYPE_CURRENCY` | `UnitType.Currency` | Monetary values | - | €, $, £, kr |
| 7 | Time | `UNITTYPE_TIME` | `UnitType.Time` | Time duration | T | min, h, day, month |

### Value Characteristics

**Energy (0)**:
- **Most Common**: Primary type for energy markets
- **Base Unit**: Watt-hour (Wh)
- **Market Usage**: 80%+ of all unit operations
- **Conversion Complexity**: Linear (simple multiplication)
- **Example Units**: Wh, kWh, MWh, GWh, TWh, MJ, GJ, TJ

**Volume (1)**:
- **Usage**: Gas markets, water utilities
- **Base Unit**: Cubic meter (m³)
- **Special Consideration**: Nm³ (normal cubic meters) requires pressure/temperature normalization
- **Conversion Complexity**: Linear for standard conditions, non-linear for Nm³ conversions
- **Example Units**: m³, Nm³, L, dm³, cm³

**Power (2)**:
- **Usage**: Capacity planning, peak demand analysis
- **Base Unit**: Watt (W)
- **Relationship**: Power = Energy / Time (dimensional analysis)
- **Conversion Complexity**: Linear within type, time-based when converting to/from energy
- **Example Units**: W, kW, MW, GW, TW

**Mass (3)**:
- **Usage**: Emissions tracking, fuel accounting
- **Base Unit**: Kilogram (kg)
- **Conversion Complexity**: Linear (simple multiplication)
- **Example Units**: kg, ton, metric ton, lb

**Temperature (4)**:
- **Usage**: Heating systems, degree-day calculations
- **Base Unit**: Celsius (°C)
- **Conversion Complexity**: Non-linear (offset-based)
- **Special Handling**: Requires different conversion formula (not just multiplication)
- **Example Conversion**: °C = (°F - 32) × 5/9

**Percentage (5)**:
- **Usage**: Efficiency metrics, availability factors
- **Base Unit**: Percentage (%)
- **Conversion**: Percentage (%) ↔ Fraction (1% = 0.01)
- **Range**: Typically 0-100%, but can exceed for ratios

**Currency (6)**:
- **Usage**: Tariffs, market prices, billing
- **Base Unit**: Market-dependent (often Euro for European markets)
- **Conversion Complexity**: Time-varying (exchange rates)
- **Special Requirement**: External exchange rate service integration

**Time (7)**:
- **Usage**: Billing periods, contract durations, switch intervals
- **Base Unit**: Minute (min)
- **Conversion Complexity**: Fixed ratios (except months/years - calendar-dependent)
- **Example Units**: min, h, day, week, month, year

## Usage Context

### Type-Safe Conversion Enforcement

**Business Rule**: Conversions are only valid between units of the same UnitType.

**Implementation** (from [Business Rules](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency)):
```csharp
public bool CanConvertTo(MeasurementUnit target)
{
    return this.UnitType == target.UnitType;
}

public decimal ConvertValue(decimal value, MeasurementUnit target)
{
    if (!CanConvertTo(target))
        throw new UnitConversionException(
            $"Cannot convert between incompatible types: {this.UnitType} → {target.UnitType}"
        );
    
    return (value * this.Factor) / target.Factor;
}
```

**Validation Example**:
```csharp
// Valid: Energy to Energy
var kwhToMwh = kwhUnit.ConvertValue(1500M, mwhUnit);  // ✓ Both UnitType.Energy

// Invalid: Energy to Volume
try
{
    var kwhToM3 = kwhUnit.ConvertValue(1500M, m3Unit);  // ✗ Different types
}
catch (UnitConversionException ex)
{
    // Exception: "Cannot convert between incompatible types: Energy → Volume"
}
```

### Database Storage

**Column**: `UNITTYPE` in `D_MEASUREMENTUNIT` table  
**Data Type**: `NUMBER` (Oracle) → `int` (C#)  
**Constraint**: Must match valid enumeration values (0-7)  
**Index**: `IX_MEASUREMENTUNIT_UNITTYPE` for fast type filtering

**SQL Query Example**:
```sql
-- Get all energy units for conversion operations
SELECT NR, UNIT, FACTOR
FROM D_MEASUREMENTUNIT
WHERE UNITTYPE = 0  -- Energy
ORDER BY ORDERNR;
```

**EF Core Configuration**:
```csharp
builder.Property(e => e.UnitType)
    .HasColumnName("UNITTYPE")
    .HasConversion<int>()  // Store as int in database
    .IsRequired();

builder.HasIndex(e => e.UnitType)
    .HasDatabaseName("IX_MEASUREMENTUNIT_UNITTYPE");
```

### API Representation

**JSON Serialization** (for external APIs):
```json
{
  "nr": 1234,
  "unit": "kWh",
  "unitType": "Energy",
  "factor": 1000.0
}
```

**String Representation Configuration**:
```csharp
// Use string names in JSON for readability
[JsonConverter(typeof(JsonStringEnumConverter))]
public UnitType UnitType { get; set; }
```

**Alternative: Numeric Representation** (for backwards compatibility with C++ API):
```json
{
  "nr": 1234,
  "unit": "kWh",
  "unitType": 0,
  "factor": 1000.0
}
```

## Conversion Compatibility Matrix

**Rule**: Only same-type conversions are valid.

| From ↓ To → | Energy | Volume | Power | Mass | Temperature | Percentage | Currency | Time |
|-------------|--------|--------|-------|------|-------------|------------|----------|------|
| **Energy** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Volume** | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Power** | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Mass** | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Temperature** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| **Percentage** | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **Currency** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **Time** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

**Legend**: ✓ = Valid conversion | ✗ = Invalid conversion (blocked by type safety)

## Special Conversion Cases

### Temperature (Non-Linear Conversions)

**Challenge**: Temperature conversions involve offset adjustments, not just multiplication.

**Formula**:
```
°C = (°F - 32) × 5/9
°F = (°C × 9/5) + 32
K = °C + 273.15
```

**Implementation Consideration**:
```csharp
// Temperature requires special conversion logic
if (sourceUnit.UnitType == UnitType.Temperature)
{
    return ConvertTemperature(value, sourceUnit, targetUnit);
}
else
{
    // Standard factor-based conversion
    return (value * sourceUnit.Factor) / targetUnit.Factor;
}
```

### Currency (Time-Varying Conversions)

**Challenge**: Currency exchange rates change over time.

**Solution**:
- Factor field stores most recent exchange rate
- Conversion service queries external rate service for current rates
- Historical conversions require timestamp-based rate lookup

**Implementation Pattern**:
```csharp
public async Task<decimal> ConvertCurrencyAsync(
    decimal value,
    MeasurementUnit sourceCurrency,
    MeasurementUnit targetCurrency,
    DateTime? effectiveDate = null)
{
    if (sourceCurrency.UnitType != UnitType.Currency || 
        targetCurrency.UnitType != UnitType.Currency)
        throw new ArgumentException("Both units must be Currency type");
    
    var rate = await _exchangeRateService.GetRateAsync(
        sourceCurrency.Unit,
        targetCurrency.Unit,
        effectiveDate ?? DateTime.UtcNow
    );
    
    return value * rate;
}
```

### Time (Calendar-Aware Conversions)

**Challenge**: Month and year conversions vary by calendar (28-31 days/month).

**Implementation**:
- Fixed conversions: min ↔ hour ↔ day ↔ week (simple factors)
- Variable conversions: month ↔ year (require calendar context)

```csharp
// Simple time conversions (fixed factors)
decimal ConvertTimeSimple(decimal value, int sourceInterval, int targetInterval)
{
    return (value * sourceInterval) / targetInterval;
}

// Calendar-aware conversions (months/years)
decimal ConvertTimeCalendar(decimal value, UnitType sourceUnit, UnitType targetUnit, DateTime period)
{
    // Requires calendar service for days-in-month calculation
    var daysInMonth = DateTime.DaysInMonth(period.Year, period.Month);
    // ... calendar-specific logic
}
```

## Validation Rules

### Enumeration Value Validation

**Rule**: UnitType field must contain valid enumeration value (0-7).

**Database Constraint**: None (application-level validation)

**C# Validation**:
```csharp
public bool IsValidUnitType(int unitTypeValue)
{
    return Enum.IsDefined(typeof(UnitType), unitTypeValue);
}

// Usage in entity
public UnitType UnitType
{
    get => _unitType;
    set
    {
        if (!Enum.IsDefined(typeof(UnitType), value))
            throw new ValidationException($"Invalid UnitType value: {value}");
        _unitType = value;
    }
}
```

### Conversion Type Validation

**Rule**: Conversion operations must validate type compatibility before execution.

**Implementation**: See [Rule 3](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency)

**Validation Query** (find mismatched conversions in logs):
```sql
-- Audit log query to find attempted cross-type conversions
SELECT 
    log_date,
    source_unit,
    source_type,
    target_unit,
    target_type,
    error_message
FROM conversion_audit_log
WHERE source_type != target_type
  AND status = 'ERROR'
ORDER BY log_date DESC;
```

## Migration Considerations

### C++ to C# Mapping

**Storage Format**: Both C++ and C# store as integer values  
**Enum Base Type**: `int` in both languages  
**Value Preservation**: Numeric values must remain identical (0-7)

**Compatibility Table**:
| C++ Constant | C++ Value | C# Enum Member | C# Value | Match |
|--------------|-----------|----------------|----------|-------|
| `UNITTYPE_ENERGY` | 0 | `UnitType.Energy` | 0 | ✓ |
| `UNITTYPE_VOLUME` | 1 | `UnitType.Volume` | 1 | ✓ |
| `UNITTYPE_POWER` | 2 | `UnitType.Power` | 2 | ✓ |
| `UNITTYPE_MASS` | 3 | `UnitType.Mass` | 3 | ✓ |
| `UNITTYPE_TEMPERATURE` | 4 | `UnitType.Temperature` | 4 | ✓ |
| `UNITTYPE_PERCENTAGE` | 5 | `UnitType.Percentage` | 5 | ✓ |
| `UNITTYPE_CURRENCY` | 6 | `UnitType.Currency` | 6 | ✓ |
| `UNITTYPE_TIME` | 7 | `UnitType.Time` | 7 | ✓ |

### API Compatibility

**C++ API Format** (numeric):
```json
{"unitType": 0}
```

**C# API Format** (string for readability, numeric for compatibility):
```json
{"unitType": "Energy"}  // Default: use string
{"unitType": 0}         // Legacy: support numeric for backwards compatibility
```

**JSON Serialization Configuration**:
```csharp
// Support both formats
services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(
            new JsonStringEnumConverter()  // Serialize as string by default
        );
    });
```

### Data Migration Validation

**Query**: Verify all existing UnitType values are valid.

```sql
-- Find units with invalid UnitType values (should return 0 rows)
SELECT NR, UNIT, UNITTYPE
FROM D_MEASUREMENTUNIT
WHERE UNITTYPE NOT BETWEEN 0 AND 7;
```

## Usage Examples

### Creating Units by Type

```csharp
// Create energy units
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

// Create volume unit
var m3 = new MeasurementUnit
{
    Unit = "m³",
    UnitType = UnitType.Volume,
    Factor = 1.0M
};
```

### Filtering Units by Type

```csharp
// Get all energy units for user selection
var energyUnits = await _repository.GetByUnitTypeAsync(UnitType.Energy);

// Typical result: [Wh, kWh, MWh, GWh, MJ, GJ]
```

### Type-Safe Conversion Validation

```csharp
// Validate conversion compatibility before operation
if (sourceUnit.UnitType != targetUnit.UnitType)
{
    throw new UnitConversionException(
        $"Cannot convert {sourceUnit.Unit} ({sourceUnit.UnitType}) " +
        $"to {targetUnit.Unit} ({targetUnit.UnitType}). " +
        "Unit types must match."
    );
}

// Proceed with conversion
var result = conversionService.Convert(value, sourceUnit, targetUnit);
```

## Related Documentation

- **Domain Object**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for usage in unit definitions
- **Business Rules**: [Unit Conversion Business Rules - Rule 3](../business-rules/unit-conversion-business-rules.md#rule-3-unit-type-consistency) for type consistency validation
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md#unittype-field) for persistence details
- **Domain Overview**: [Units Domain Overview](../domain-overview/units-domain-overview.md) for architectural context

---

**Migration Phase**: 2 - Specification Creation  
**Generated by**: rule.migration.spec-create.v1  
**Source System**: eBase C++ Units Module  
**Analyzed Source**: eBase/Units/UnitType.h:23-34, eBase/Units/Constants.h  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Status**: Technical Review Complete  
**Quality Gate**: Passed
