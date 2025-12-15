---
id: exemplar.technical-specifications.entity-relationships.v1
kind: exemplar
version: 1.0.0
description: Example of a well-structured Entity Relationships specification
illustrates: technical-specifications.entity-relationship
use: critic-only
notes: Pattern extraction only. NEVER copy content to production outputs.
provenance:
  owner: team-technical-specs
  last_review: 2025-12-06
---

# Entity Relationships: Units Domain

**Domain**: Units Management  
**Status**: Database Analysis Complete  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Source**: Oracle database configuration `GENDATABASE.ini`, C++ field access patterns

## Overview

This specification documents the complete entity relationship structure for the Units Management domain, including table schemas, foreign key relationships, indexes, and data integrity constraints. It serves as the authoritative reference for database-level relationships and persistence patterns.

**Database Context**: The Units domain uses a single primary table (`D_MEASUREMENTUNIT`) with self-referencing relationships and foreign key dependencies to other domains. All relationships are optional (nullable foreign keys) to support flexible configuration scenarios.

**Key Relationship Insight**: The self-referencing counter unit relationship creates bidirectional conversion pairs that must maintain mathematical symmetry (validated at application layer, not enforced by database constraints).

### Related Specifications
- **Domain Overview**: [Units Domain Overview](../domain-overview/units-domain-overview.md) for business context
- **Domain Objects**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for field semantics
- **Business Rules**: [Unit Conversion Business Rules](../business-rules/unit-conversion-business-rules.md) for validation logic

## Entity Relationship Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                         Units Domain ERD                               │
└───────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────┐
    │    D_MEASUREMENTUNIT           │◄────────────────┐
    │                                │                 │
    │  PK  NR                NUMBER │                 │ COUNTERUNITID
    │      UNIT              VARCHAR2│                 │ (self-reference)
    │      UNITTYPE          NUMBER  │◄────────────────┘
    │      FACTOR            NUMBER  │
    │      SWITCHINTERVAL    NUMBER  │
    │      ORDERNR           NUMBER  │
    │  FK  COUNTERUNITID     NUMBER  │
    │  FK  METERPRODUCTID    NUMBER  │────┐
    │                                │    │
    │  UK  UNIT (unique)             │    │
    │  IDX NR (primary key)          │    │
    │  IDX UNITTYPE                  │    │
    └────────────────────────────────┘    │
              ▲                            │
              │                            │
              │ UnitId (FK)                │ MeterProductId (FK)
              │                            │
    ┌─────────┴────────┐         ┌─────────▼────────┐
    │   D_PROFILE      │         │ D_METERPRODUCT   │
    │                  │         │                  │
    │  PK  NR          │         │  PK  NR          │
    │  FK  UNITID      │         │  FK  DEFAULTUNITID│
    │      ...         │         │      ...         │
    └──────────────────┘         └──────────────────┘
         (Profiles                   (Products
          Domain)                     Domain)

Legend:
  PK  = Primary Key
  FK  = Foreign Key
  UK  = Unique Key
  IDX = Index
  ─── = Foreign Key Relationship (optional, nullable)
```

## Table: D_MEASUREMENTUNIT

### Primary Key

**Column**: `NR`  
**Type**: `NUMBER` (maps to C# `long`)  
**Constraint Name**: `PK_MEASUREMENTUNIT`  
**Generation**: Auto-increment from sequence `GENCOUNTER_SEQ`  
**Business Meaning**: System-assigned unique identifier for measurement units

```sql
CONSTRAINT PK_MEASUREMENTUNIT PRIMARY KEY (NR)
```

### Unique Constraints

**Unit Symbol Uniqueness**:
- **Column**: `UNIT`
- **Constraint Name**: `UX_MEASUREMENTUNIT_UNIT`
- **Scope**: Tenant-specific (enforced within schema)
- **Business Meaning**: Unit symbols must be unique per tenant to prevent ambiguous references

```sql
CONSTRAINT UX_MEASUREMENTUNIT_UNIT UNIQUE (UNIT)
```

### Foreign Key Relationships

#### Self-Reference: Counter Unit

**Relationship**: MeasurementUnit ↔ MeasurementUnit  
**Foreign Key Column**: `COUNTERUNITID`  
**References**: `D_MEASUREMENTUNIT(NR)`  
**Constraint Name**: `FK_MEASUREMENTUNIT_COUNTER`  
**Cardinality**: 0..1 (optional counter unit)  
**Delete Rule**: `ON DELETE SET NULL`

**Business Purpose**: Establishes bidirectional conversion pairs for symmetry validation.

**Example**:
```
Unit A (kWh, NR=1000, COUNTERUNITID=1001)
  ↔ Unit B (MWh, NR=1001, COUNTERUNITID=1000)

Relationship: Unit A references Unit B as counter, Unit B references Unit A as counter
Validation: Factor_A * Factor_B ≈ 1.0 (application-level check)
```

**SQL Definition**:
```sql
CONSTRAINT FK_MEASUREMENTUNIT_COUNTER 
    FOREIGN KEY (COUNTERUNITID) 
    REFERENCES D_MEASUREMENTUNIT(NR)
    ON DELETE SET NULL
```

**C# Navigation Property**:
```csharp
public virtual MeasurementUnit? CounterUnit { get; set; }
```

#### Cross-Domain: Meter Product

**Relationship**: MeasurementUnit → MeterProduct  
**Foreign Key Column**: `METERPRODUCTID`  
**References**: `D_METERPRODUCT(NR)` (Products domain)  
**Constraint Name**: `FK_MEASUREMENTUNIT_METERPRODUCT`  
**Cardinality**: 0..1 (optional meter product association)  
**Delete Rule**: `ON DELETE SET NULL`

**Business Purpose**: Associates units with specific meter product types for default unit assignments.

**Example**:
```
MeterProduct (Electricity Meter, NR=5000)
  ← MeasurementUnit (kWh, NR=1000, METERPRODUCTID=5000)
  ← MeasurementUnit (MWh, NR=1001, METERPRODUCTID=5000)

Relationship: Multiple units can reference same meter product
Usage: Meter product defines which units are valid for that meter type
```

**SQL Definition**:
```sql
CONSTRAINT FK_MEASUREMENTUNIT_METERPRODUCT 
    FOREIGN KEY (METERPRODUCTID) 
    REFERENCES D_METERPRODUCT(NR)
    ON DELETE SET NULL
```

**C# Navigation Property**:
```csharp
public virtual MeterProduct? MeterProduct { get; set; }
```

**Cross-Reference**: See [MeterProduct Entity Relationships](../../products/database/meter-product-entity-relationships.md)

### Inverse Relationships (Referenced By)

#### Profile.UnitId → MeasurementUnit

**Relationship**: Profile → MeasurementUnit  
**Foreign Key Column**: `UNITID` in `D_PROFILE` table  
**Cardinality**: Many-to-one (many profiles can use same unit)  
**Business Purpose**: Profiles specify measurement units for consumption patterns

**Example**:
```
MeasurementUnit (kWh, NR=1000)
  ← Profile (Residential Profile, NR=2000, UNITID=1000)
  ← Profile (Commercial Profile, NR=2001, UNITID=1000)
  ← Profile (Industrial Profile, NR=2002, UNITID=1000)

Relationship: One unit referenced by multiple profiles
Constraint: Profile must have a valid unit (NOT NULL in D_PROFILE)
```

**C# Navigation Property** (if needed):
```csharp
public virtual ICollection<Profile> Profiles { get; set; }
```

**Cross-Reference**: See [Profile Entity Relationships](../../profiles/database/profile-entity-relationships.md)

## Field Specifications

**Complete Field Definitions**: See [Units Database Schema](../database/units-database-schema.md#field-specifications) for authoritative field specifications, data types, and constraints.

**Relationship-Relevant Fields**:

| Column | Type | Nullable | Default | Purpose | Relationship Impact |
|--------|------|----------|---------|---------|---------------------|
| NR | NUMBER | NOT NULL | SEQUENCE | Primary Key | Referenced by self and other domains |
| UNIT | VARCHAR2(20) | NOT NULL | - | Business Key | Must be unique per tenant |
| COUNTERUNITID | NUMBER | NULL | NULL | Foreign Key | Self-reference for conversion pairs |
| METERPRODUCTID | NUMBER | NULL | NULL | Foreign Key | Cross-domain to Products |

## Indexes

### Primary Key Index

**Index Name**: `PK_MEASUREMENTUNIT`  
**Type**: Unique clustered index  
**Columns**: `NR`  
**Purpose**: Primary key enforcement and fast lookup by ID

```sql
CREATE UNIQUE INDEX PK_MEASUREMENTUNIT ON D_MEASUREMENTUNIT(NR);
```

### Business Key Index

**Index Name**: `UX_MEASUREMENTUNIT_UNIT`  
**Type**: Unique non-clustered index  
**Columns**: `UNIT`  
**Purpose**: Fast lookup by unit symbol, enforces uniqueness

```sql
CREATE UNIQUE INDEX UX_MEASUREMENTUNIT_UNIT ON D_MEASUREMENTUNIT(UNIT);
```

### Classification Index

**Index Name**: `IX_MEASUREMENTUNIT_UNITTYPE`  
**Type**: Non-unique non-clustered index  
**Columns**: `UNITTYPE`  
**Purpose**: Fast filtering by unit type for type-safe conversion operations

```sql
CREATE INDEX IX_MEASUREMENTUNIT_UNITTYPE ON D_MEASUREMENTUNIT(UNITTYPE);
```

**Usage Pattern**: Frequently used in queries filtering compatible units for conversion:
```sql
SELECT * FROM D_MEASUREMENTUNIT WHERE UNITTYPE = 0; -- All energy units
```

### Foreign Key Indexes

**Index Name**: `IX_MEASUREMENTUNIT_COUNTERUNITID`  
**Type**: Non-unique non-clustered index  
**Columns**: `COUNTERUNITID`  
**Purpose**: Performance optimization for counter unit lookups and cascade operations

```sql
CREATE INDEX IX_MEASUREMENTUNIT_COUNTERUNITID ON D_MEASUREMENTUNIT(COUNTERUNITID);
```

**Index Name**: `IX_MEASUREMENTUNIT_METERPRODUCTID`  
**Type**: Non-unique non-clustered index  
**Columns**: `METERPRODUCTID`  
**Purpose**: Performance optimization for meter product relationships

```sql
CREATE INDEX IX_MEASUREMENTUNIT_METERPRODUCTID ON D_MEASUREMENTUNIT(METERPRODUCTID);
```

## Data Integrity Constraints

### Application-Level Constraints

These constraints are enforced by application logic, not database constraints:

**1. Factor Positivity**  
- **Rule**: `FACTOR > 0`
- **Enforcement**: Domain entity property validation
- **Reason**: Database allows any numeric value, application ensures business rule

```csharp
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
```

**2. Counter Unit Symmetry**  
- **Rule**: `Unit_A.Factor * Unit_B.Factor ≈ 1.0` where A and B are counter units
- **Enforcement**: Domain service validation before save
- **Reason**: Cannot be expressed as database CHECK constraint

```csharp
public void ValidateCounterUnitSymmetry()
{
    if (CounterUnit == null) return;
    
    const decimal tolerance = 0.000000001M;
    decimal product = this.Factor * CounterUnit.Factor;
    if (Math.Abs(product - 1.0M) > tolerance)
        throw new ValidationException($"Symmetry violation: {Factor} * {CounterUnit.Factor} != 1.0");
}
```

**3. Switch Interval Range**  
- **Rule**: `SWITCHINTERVAL BETWEEN 1 AND 60` or `NULL`
- **Enforcement**: Domain entity validation
- **Reason**: Business rule for standard intervals, application-specific

### Database-Level Constraints

**1. Primary Key Constraint**  
```sql
CONSTRAINT PK_MEASUREMENTUNIT PRIMARY KEY (NR)
```
- Ensures NR uniqueness
- Clustered index for performance

**2. Unique Constraint on Unit Symbol**  
```sql
CONSTRAINT UX_MEASUREMENTUNIT_UNIT UNIQUE (UNIT)
```
- Prevents duplicate unit symbols within tenant
- Non-clustered index for fast lookup

**3. Foreign Key Constraints**  
```sql
CONSTRAINT FK_MEASUREMENTUNIT_COUNTER 
    FOREIGN KEY (COUNTERUNITID) REFERENCES D_MEASUREMENTUNIT(NR) ON DELETE SET NULL;

CONSTRAINT FK_MEASUREMENTUNIT_METERPRODUCT 
    FOREIGN KEY (METERPRODUCTID) REFERENCES D_METERPRODUCT(NR) ON DELETE SET NULL;
```
- Ensures referential integrity
- Null foreign keys allowed (optional relationships)
- Cascading deletes set foreign keys to NULL

## Relationship Patterns

### Pattern 1: Bidirectional Conversion Pairs

**Structure**: Two units reference each other as counter units

**Setup**:
```sql
-- Create kWh unit
INSERT INTO D_MEASUREMENTUNIT (NR, UNIT, UNITTYPE, FACTOR, COUNTERUNITID)
VALUES (1000, 'kWh', 0, 1000.0, NULL);

-- Create MWh unit with counter reference to kWh
INSERT INTO D_MEASUREMENTUNIT (NR, UNIT, UNITTYPE, FACTOR, COUNTERUNITID)
VALUES (1001, 'MWh', 0, 0.001, 1000);

-- Update kWh to reference MWh as counter
UPDATE D_MEASUREMENTUNIT SET COUNTERUNITID = 1001 WHERE NR = 1000;
```

**Validation Query**:
```sql
-- Find asymmetric conversion pairs (should return 0 rows)
SELECT 
    u1.NR as Unit1_NR,
    u1.UNIT as Unit1_Symbol,
    u1.FACTOR as Unit1_Factor,
    u2.NR as Unit2_NR,
    u2.UNIT as Unit2_Symbol,
    u2.FACTOR as Unit2_Factor,
    (u1.FACTOR * u2.FACTOR) as Product,
    ABS((u1.FACTOR * u2.FACTOR) - 1.0) as Deviation
FROM D_MEASUREMENTUNIT u1
INNER JOIN D_MEASUREMENTUNIT u2 ON u1.COUNTERUNITID = u2.NR
WHERE ABS((u1.FACTOR * u2.FACTOR) - 1.0) > 0.000000001;
```

### Pattern 2: Unit Hierarchies by Type

**Structure**: Units grouped by UnitType for type-safe conversions

**Query Example**:
```sql
-- Get all energy units for conversion compatibility
SELECT NR, UNIT, FACTOR, ORDERNR
FROM D_MEASUREMENTUNIT
WHERE UNITTYPE = 0
ORDER BY ORDERNR, UNIT;
```

**Result**:
```
NR    | UNIT | FACTOR    | ORDERNR
------|------|-----------|--------
1000  | Wh   | 1.0       | 5
1001  | kWh  | 1000.0    | 10
1002  | MWh  | 0.001     | 20
1003  | GWh  | 0.000001  | 30
```

### Pattern 3: Meter Product Default Units

**Structure**: Meter products reference preferred measurement units

**Query Example**:
```sql
-- Find meter products and their default units
SELECT 
    mp.NR as MeterProduct_NR,
    mp.PRODUCTNAME as MeterProduct_Name,
    u.NR as Unit_NR,
    u.UNIT as Unit_Symbol,
    u.FACTOR as Unit_Factor
FROM D_METERPRODUCT mp
LEFT JOIN D_MEASUREMENTUNIT u ON mp.DEFAULTUNITID = u.NR
WHERE u.NR IS NOT NULL
ORDER BY mp.PRODUCTNAME;
```

## Migration Considerations

### C++ to C# Entity Framework Mapping

**Entity Configuration**:
```csharp
public class MeasurementUnitConfiguration : IEntityTypeConfiguration<MeasurementUnit>
{
    public void Configure(EntityTypeBuilder<MeasurementUnit> builder)
    {
        builder.ToTable("D_MEASUREMENTUNIT");
        
        // Primary key
        builder.HasKey(e => e.Nr);
        builder.Property(e => e.Nr).HasColumnName("NR").ValueGeneratedOnAdd();
        
        // Unique constraint on Unit symbol
        builder.HasIndex(e => e.Unit).IsUnique().HasDatabaseName("UX_MEASUREMENTUNIT_UNIT");
        builder.Property(e => e.Unit).HasColumnName("UNIT").HasMaxLength(20).IsRequired();
        
        // Classification index
        builder.HasIndex(e => e.UnitType).HasDatabaseName("IX_MEASUREMENTUNIT_UNITTYPE");
        builder.Property(e => e.UnitType).HasColumnName("UNITTYPE").IsRequired();
        
        // Self-reference relationship
        builder.HasOne(e => e.CounterUnit)
            .WithMany()
            .HasForeignKey(e => e.CounterUnitId)
            .HasConstraintName("FK_MEASUREMENTUNIT_COUNTER")
            .OnDelete(DeleteBehavior.SetNull);
        
        builder.HasIndex(e => e.CounterUnitId).HasDatabaseName("IX_MEASUREMENTUNIT_COUNTERUNITID");
        builder.Property(e => e.CounterUnitId).HasColumnName("COUNTERUNITID");
        
        // Cross-domain relationship to MeterProduct
        builder.HasOne(e => e.MeterProduct)
            .WithMany()
            .HasForeignKey(e => e.MeterProductId)
            .HasConstraintName("FK_MEASUREMENTUNIT_METERPRODUCT")
            .OnDelete(DeleteBehavior.SetNull);
        
        builder.HasIndex(e => e.MeterProductId).HasDatabaseName("IX_MEASUREMENTUNIT_METERPRODUCTID");
        builder.Property(e => e.MeterProductId).HasColumnName("METERPRODUCTID");
        
        // Other fields
        builder.Property(e => e.Factor).HasColumnName("FACTOR").HasColumnType("decimal(18,9)").IsRequired();
        builder.Property(e => e.OrderNr).HasColumnName("ORDERNR");
        builder.Property(e => e.SwitchInterval).HasColumnName("SWITCHINTERVAL");
    }
}
```

### Data Type Mapping

| Oracle Type | C++ Type | C# Type | EF Core Mapping |
|-------------|----------|---------|-----------------|
| NUMBER (ID) | long | long | `.HasColumnType("NUMBER")` |
| NUMBER (Factor) | double | decimal | `.HasColumnType("decimal(18,9)")` |
| VARCHAR2(20) | AnsiString | string | `.HasMaxLength(20)` |
| NUMBER (UnitType) | int | enum UnitType | `.HasConversion<int>()` |

### Referential Integrity Preservation

**C++ Behavior**: Deleting a meter product sets `METERPRODUCTID` to NULL in related units

**C# Replication**:
```csharp
.OnDelete(DeleteBehavior.SetNull)
```

**Validation**: Ensure cascade behavior matches C++ expectations in integration tests.

### Performance Optimization

**C++ Caching**: Units table cached in memory after first load (rarely changes)

**C# Strategy**:
```csharp
// Repository-level caching
private static readonly MemoryCache _unitCache = new MemoryCache(new MemoryCacheOptions());

public async Task<MeasurementUnit?> GetByUnitSymbolAsync(string unit)
{
    var cacheKey = $"Unit:{unit}";
    if (_unitCache.TryGetValue(cacheKey, out MeasurementUnit cachedUnit))
        return cachedUnit;
    
    var dbUnit = await _context.MeasurementUnits
        .Include(u => u.CounterUnit)
        .FirstOrDefaultAsync(u => u.Unit == unit);
    
    if (dbUnit != null)
        _unitCache.Set(cacheKey, dbUnit, TimeSpan.FromHours(24));
    
    return dbUnit;
}
```

## Validation Queries

### Referential Integrity Checks

**Orphaned Counter Unit References**:
```sql
-- Find units referencing non-existent counter units (should be 0 rows)
SELECT u.NR, u.UNIT, u.COUNTERUNITID
FROM D_MEASUREMENTUNIT u
WHERE u.COUNTERUNITID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM D_MEASUREMENTUNIT c WHERE c.NR = u.COUNTERUNITID);
```

**Orphaned Meter Product References**:
```sql
-- Find units referencing non-existent meter products (should be 0 rows)
SELECT u.NR, u.UNIT, u.METERPRODUCTID
FROM D_MEASUREMENTUNIT u
WHERE u.METERPRODUCTID IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM D_METERPRODUCT mp WHERE mp.NR = u.METERPRODUCTID);
```

### Data Quality Checks

**Duplicate Unit Symbols**:
```sql
-- Find duplicate unit symbols (should be 0 rows due to unique constraint)
SELECT UNIT, COUNT(*) as Count
FROM D_MEASUREMENTUNIT
GROUP BY UNIT
HAVING COUNT(*) > 1;
```

**Invalid Conversion Factors**:
```sql
-- Find units with invalid factors (should be 0 rows)
SELECT NR, UNIT, FACTOR
FROM D_MEASUREMENTUNIT
WHERE FACTOR <= 0 OR FACTOR IS NULL;
```

**Asymmetric Counter Unit Pairs**:
```sql
-- Find counter unit pairs with asymmetric factors (should be 0 rows)
SELECT 
    u1.NR, u1.UNIT, u1.FACTOR,
    u2.NR, u2.UNIT, u2.FACTOR,
    (u1.FACTOR * u2.FACTOR) as Product
FROM D_MEASUREMENTUNIT u1
INNER JOIN D_MEASUREMENTUNIT u2 ON u1.COUNTERUNITID = u2.NR
WHERE ABS((u1.FACTOR * u2.FACTOR) - 1.0) > 0.000000001;
```

## Related Documentation

- **Domain Overview**: [Units Domain Overview](../domain-overview/units-domain-overview.md) for business context and architectural relationships
- **Database Schema**: [Units Database Schema](../database/units-database-schema.md) for complete table structure and field specifications
- **Domain Objects**: [MeasurementUnit Domain Object](../domain/domain-objects/measurement-unit-domain-object.md) for field semantics and business rules
- **Cross-Domain**: [MeterProduct Entity Relationships](../../products/database/meter-product-entity-relationships.md), [Profile Entity Relationships](../../profiles/database/profile-entity-relationships.md)

---

**Migration Phase**: 2 - Specification Creation  
**Generated by**: rule.migration.spec-create.v1  
**Source System**: eBase C++ Database Configuration  
**Analyzed Source**: GENDATABASE.ini, eBase/Units/*.cpp field access patterns  
**Created**: 2025-11-29  
**Last Updated**: 2025-11-29  
**Status**: Database Review Complete  
**Quality Gate**: Passed
