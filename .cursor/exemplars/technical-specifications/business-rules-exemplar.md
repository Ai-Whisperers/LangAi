---
id: exemplar.technical-specifications.business-rules.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Business Rules specification
illustrates: technical-specifications.business-rules
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Business Rules: Measurement Unit Conversion

**Domain**: Units Management  
**Status**: C++ Source Analysis Complete  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Source**: `eBase/Units/UnitManager.cpp`, `eBase/Units/ConversionEngine.cpp`

## Overview

This specification documents the business rules governing measurement unit conversions in the eBase energy management system. These rules ensure accurate energy calculations, consistent unit handling across market operations, and proper volume conservation during unit transformations.

**Key Business Insight**: All unit conversions must preserve energy volume (conservation of energy principle), with conversion factors maintaining bidirectional consistency and precision requirements enforced throughout the calculation chain.

### Related Specifications
- **Domain Object**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md)
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md)
- **Enumerations**: [UnitType Enumeration](../enumerations/unit-type-enum.md)

## Business Logic

### Rule 1: Conversion Factor Validation

**Source**: `UnitManager.cpp:145-178`

**Business Description**: Conversion factors must be positive, non-zero values to ensure mathematically valid unit conversions.

**Algorithm**:
1. Upon unit creation or factor modification
2. Validate factor > 0 and factor != null
3. Check for extreme values (< 0.000001 or > 1000000) and log warnings
4. Reject factor if validation fails

**Example**:
```
Input: MeasurementUnit.Factor = 1000.0 (kWh → Wh)
Result: Valid (1 kWh = 1000 Wh)

Input: MeasurementUnit.Factor = 0
Result: Invalid (zero factor creates division by zero)

Input: MeasurementUnit.Factor = -100
Result: Invalid (negative factors violate physical laws)
```

**Validation Logic**:
```csharp
bool IsValidConversionFactor(decimal factor)
{
    if (factor <= 0) return false;
    if (factor < 0.000001M) LogWarning("Extremely small factor");
    if (factor > 1000000M) LogWarning("Extremely large factor");
    return true;
}
```

### Rule 2: Bidirectional Conversion Symmetry

**Source**: `ConversionEngine.cpp:234-289`

**Business Description**: When Unit A converts to Unit B with factor F, Unit B must convert to Unit A with factor 1/F to maintain energy volume conservation.

**Algorithm**:
1. For primary conversion A → B with factor F
2. Inverse conversion B → A must use factor 1/F
3. Round-trip conversion A → B → A must equal original value (within tolerance)
4. System validates symmetry on counter unit assignment

**Example**:
```
Setup:
- Unit A (kWh) with Factor = 1000 (base unit Wh)
- Unit B (MWh) with Factor = 0.001 (base unit Wh)

Validation:
- kWh → MWh: value * 0.001 = result
- MWh → kWh: value * 1000 = original
- Round-trip: 100 kWh → 0.1 MWh → 100 kWh ✓

Counter Unit Relationship:
- Unit A.CounterUnitId = Unit B.Id
- Unit B.CounterUnitId = Unit A.Id
- Validates: A.Factor * B.Factor ≈ 1.0 (within tolerance)
```

**Implementation Note**: C++ implementation uses floating-point arithmetic with epsilon tolerance (1e-9) for equality checks. C# implementation must maintain identical tolerance to preserve behavior.

### Rule 3: Unit Type Consistency

**Source**: `UnitManager.cpp:312-347`, `eBase/Units/TypeValidator.cpp:89-134`

**Business Description**: Conversion operations are only valid between units of the same UnitType. Cross-type conversions (e.g., volume to energy) are forbidden.

**Algorithm**:
1. Before conversion operation
2. Validate source.UnitType == target.UnitType
3. If types differ, throw ConversionException
4. Log attempted cross-type conversions for security audit

**Example**:
```
Valid:
- Source: kWh (UnitType = Energy)
- Target: MWh (UnitType = Energy)
- Result: Conversion allowed

Invalid:
- Source: m³ (UnitType = Volume)
- Target: kWh (UnitType = Energy)
- Result: ConversionException thrown
- Reason: Physical units not compatible
```

**Enumeration Reference**: See [UnitType Enumeration](../enumerations/unit-type-enum.md) for complete type definitions and compatibility matrix.

### Rule 4: Switch Interval Alignment

**Source**: `ConversionEngine.cpp:445-512`

**Business Description**: When converting time-series energy data, source and target units must have compatible switch intervals. Conversions between incompatible intervals require temporal aggregation/disaggregation.

**Algorithm**:
1. Check source.SwitchInterval and target.SwitchInterval
2. If intervals equal → direct value conversion
3. If intervals compatible (one divides other evenly) → aggregation/disaggregation allowed
4. If intervals incompatible → require explicit temporal resampling

**Example**:
```
Compatible Intervals:
- Source: 15-minute interval
- Target: 60-minute interval
- Operation: Sum 4 source periods into 1 target period

Compatible Intervals (reverse):
- Source: 60-minute interval
- Target: 15-minute interval  
- Operation: Distribute source value across 4 target periods

Incompatible Intervals:
- Source: 15-minute interval
- Target: 20-minute interval
- Operation: Requires temporal resampling (not simple conversion)
- Result: Conversion blocked, explicit resampling API required
```

**Compatibility Matrix**:
| Source | Target | Operation |
|--------|--------|-----------|
| 15 min | 15 min | Direct conversion |
| 15 min | 60 min | Aggregate (sum 4 periods) |
| 60 min | 15 min | Disaggregate (divide by 4) |
| 15 min | 20 min | Blocked (incompatible) |
| 30 min | 45 min | Blocked (incompatible) |

### Rule 5: Precision and Rounding

**Source**: `ConversionEngine.cpp:589-643`

**Business Description**: Conversion operations must maintain sufficient precision to prevent cumulative rounding errors in energy calculations, especially for billing scenarios.

**Algorithm**:
1. All intermediate calculations use maximum available precision (double in C++, decimal in C#)
2. Apply rounding only at final output stage
3. Rounding mode: Banker's rounding (round to even) for fairness
4. Minimum precision: 6 decimal places for billing calculations
5. Log precision loss warnings if result has fewer significant digits than input

**Example**:
```
Scenario: Convert 1234.56789 kWh to MWh

Calculation:
- Input: 1234.56789 kWh (9 significant digits)
- Factor: 0.001 (kWh → MWh)
- Intermediate: 1.23456789 MWh (full precision maintained)
- Output (6 decimals): 1.234568 MWh
- Rounding: Applied at display, not during calculation

Billing Context:
- Energy value: 1234.56789 kWh
- Tariff: €0.25 per kWh
- Incorrect (rounded early): 1234.57 * 0.25 = €308.6425
- Correct (full precision): 1234.56789 * 0.25 = €308.6419725
- Difference: €0.0005725 (accumulates over millions of calculations)
```

**C# Migration Note**: Use `decimal` type for financial calculations instead of C++ `double` to eliminate floating-point precision issues.

## Rule Implementation

### C# Domain Entity Constraints

**Validation Rules for MeasurementUnit Entity**:
```csharp
public class MeasurementUnit
{
    // Rule 1: Conversion Factor Validation
    private decimal _factor;
    public decimal Factor
    {
        get => _factor;
        set
        {
            if (value <= 0)
                throw new ValidationException("Factor must be positive");
            if (value < 0.000001M)
                Logger.Warn($"Extremely small factor: {value}");
            if (value > 1000000M)
                Logger.Warn($"Extremely large factor: {value}");
            _factor = value;
        }
    }

    // Rule 2: Bidirectional Conversion Symmetry
    public void ValidateCounterUnitSymmetry(MeasurementUnit counterUnit)
    {
        const decimal tolerance = 0.000000001M;
        decimal product = this.Factor * counterUnit.Factor;
        if (Math.Abs(product - 1.0M) > tolerance)
            throw new ValidationException(
                $"Asymmetric conversion: {this.Factor} * {counterUnit.Factor} != 1.0"
            );
    }

    // Rule 3: Unit Type Consistency
    public bool CanConvertTo(MeasurementUnit target)
    {
        return this.UnitType == target.UnitType;
    }

    // Rule 4: Switch Interval Alignment
    public bool HasCompatibleInterval(MeasurementUnit target)
    {
        if (this.SwitchInterval == target.SwitchInterval)
            return true;
        
        int larger = Math.Max(this.SwitchInterval, target.SwitchInterval);
        int smaller = Math.Min(this.SwitchInterval, target.SwitchInterval);
        
        return (larger % smaller) == 0; // One divides the other evenly
    }
}
```

### Conversion Service Interface

```csharp
public interface IUnitConversionService
{
    // Rule 1 & 2: Validate and convert with symmetry
    decimal Convert(decimal value, MeasurementUnit source, MeasurementUnit target);
    
    // Rule 3: Type-safe conversion
    decimal ConvertSameType(decimal value, long sourceUnitId, long targetUnitId);
    
    // Rule 4: Time-series conversion with interval handling
    IEnumerable<decimal> ConvertTimeSeries(
        IEnumerable<decimal> values,
        MeasurementUnit source,
        MeasurementUnit target,
        TimeSeriesAggregation aggregation
    );
    
    // Rule 5: Precision-aware conversion
    decimal ConvertWithPrecision(
        decimal value,
        MeasurementUnit source,
        MeasurementUnit target,
        int outputPrecision
    );
}
```

## Exception Handling

### ConversionException Scenarios

**Invalid Factor Exception**:
```
Condition: Factor <= 0
Message: "Conversion factor must be positive and non-zero"
Action: Reject unit creation/modification
Logged: Yes (security audit log)
```

**Type Mismatch Exception**:
```
Condition: source.UnitType != target.UnitType
Message: "Cannot convert between incompatible unit types: {sourceType} → {targetType}"
Action: Block conversion operation
Logged: Yes (attempted cross-type conversions for audit)
```

**Interval Incompatibility Exception**:
```
Condition: Incompatible switch intervals without explicit resampling
Message: "Switch intervals {sourceInterval} and {targetInterval} are incompatible. Use explicit resampling."
Action: Require caller to use temporal resampling API
Logged: No (expected operational condition)
```

**Precision Loss Warning**:
```
Condition: Output precision < input precision by > 3 decimal places
Message: "Conversion resulted in precision loss: {inputPrecision} → {outputPrecision}"
Action: Log warning, proceed with conversion
Logged: Yes (diagnostic log)
```

## Migration Preservation

### C++ Behavior to Preserve

1. **Floating-Point Tolerance**: C++ uses epsilon tolerance (1e-9) for factor symmetry validation. C# must use same value.

2. **Rounding Mode**: C++ uses IEEE 754 default rounding (round to nearest, ties to even). C# `decimal` uses same mode by default.

3. **Validation Ordering**: C++ validates in order: factor → type → interval → precision. C# must maintain same ordering for consistent error messages.

4. **Logging Behavior**: C++ logs warnings for extreme factors and precision loss. C# must replicate exact log messages for operational continuity.

5. **Performance Optimization**: C++ caches conversion factors for frequently used unit pairs. C# implementation must include equivalent caching.

### Test Scenarios for Validation

**Regression Test Suite**:
```
Test 1: Bidirectional Conversion Symmetry
- Input: 100 kWh
- Convert: kWh → MWh → kWh
- Expected: 100 kWh (identical to input)

Test 2: Cross-Type Conversion Rejection
- Input: 50 m³ (volume)
- Target: kWh (energy)
- Expected: ConversionException thrown

Test 3: Switch Interval Aggregation
- Input: [10, 20, 30, 40] kWh (15-min intervals)
- Target: MWh (60-min intervals)
- Expected: [0.1] MWh (sum of 4 periods)

Test 4: Precision Preservation
- Input: 1234.56789012345 kWh (14 decimals)
- Convert: kWh → MWh
- Expected: 1.23456789012345 MWh (14 decimals preserved)

Test 5: Invalid Factor Rejection
- Input: MeasurementUnit with Factor = 0
- Expected: ValidationException on construction
```

## Performance Considerations

### Caching Strategy

**C++ Implementation** (`ConversionEngine.cpp:78-112`):
```
- LRU cache for last 100 conversion factor pairs
- Cache key: (sourceUnitId, targetUnitId)
- Cache invalidation: On unit modification
- Hit rate: ~95% in production (most conversions reuse common pairs)
```

**C# Migration**:
```csharp
// Replicate C++ caching for performance equivalence
private readonly LruCache<(long, long), decimal> _factorCache 
    = new LruCache<(long, long), decimal>(capacity: 100);

public decimal GetCachedFactor(long sourceId, long targetId)
{
    var key = (sourceId, targetId);
    if (_factorCache.TryGet(key, out var factor))
        return factor;
    
    factor = CalculateConversionFactor(sourceId, targetId);
    _factorCache.Add(key, factor);
    return factor;
}
```

### Batch Conversion Optimization

**Rule**: When converting multiple values between same unit pair, calculate factor once and reuse.

**C++ Behavior**: `ConversionEngine::BatchConvert()` calculates factor once per batch.

**C# Implementation**:
```csharp
public IEnumerable<decimal> BatchConvert(
    IEnumerable<decimal> values,
    long sourceUnitId,
    long targetUnitId)
{
    decimal factor = GetCachedFactor(sourceUnitId, targetUnitId);
    return values.Select(v => v * factor);
}
```

## Related Documentation

- **Domain Model**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md)
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md)
- **Enumerations**: [UnitType Enumeration](../enumerations/unit-type-enum.md), [TimeSeriesAggregation Enumeration](../enumerations/time-series-aggregation-enum.md)
- **Integration Points**: [Unit Conversion API](../integration/unit-conversion-api.md)
- **C# Implementation Guide**: [Unit Conversion Service Implementation](../../implementation/units/conversion-service-implementation.md)

---

**Migration Phase**: 2 - Specification Creation  
**Generated by**: rule.migration.spec-create.v1  
**Source System**: eBase C++ Units Module  
**Analyzed Source**: eBase/Units/*.cpp, eBase/Units/*.h  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Status**: Technical Review Complete  
**Quality Gate**: Passed
