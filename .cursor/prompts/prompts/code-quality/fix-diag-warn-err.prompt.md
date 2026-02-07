---
name: fix-diag-warn-err
description: "Identify ALL disabled analyzers, enable them iteratively one-by-one, compile and fix all errors - achieve ultimate standard with zero diagnostics except allowed test suppressions"
category: code-quality
tags: diagnostics, analyzers, errors, warnings, suggestions, zero-tolerance, iterative-enablement, ultimate-standard
argument-hint: "File or folder paths containing the diagnostics"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/diagnostic-messages-agent-application-rule.mdc
---

# Ultimate Standard - Complete Analyzer Enablement & Diagnostic Resolution

**CRITICAL**: Identify ALL disabled analyzers, enable them iteratively ONE BY ONE, compile after each enablement, fix ALL resulting errors before proceeding to next analyzer. Only specific test method suppressions allowed. End result: ALL analyzers enabled, zero diagnostics except documented test suppressions - ultimate code quality standard achieved.

---

## Purpose

- Resolve ALL analyzer diagnostics (errors, warnings, suggestions) in provided files.
- **CRITICAL**: Use iterative staged approach - enable disabled analyzers ONE BY ONE, compile, fix errors, then enable next analyzer.
- End result: zero diagnostics, all analyzers enabled, no suppressions except explicitly allowed test validations.
- Keep behavior unchanged and produce minimal, targeted diffs.

## CRITICAL: Ultimate Standard - Enable ALL Disabled Analyzers Iteratively

**GOAL**: Lift code to ultimate standard by fixing ALL analyzer diagnostics (errors, warnings, suggestions) through systematic iterative enablement of ALL disabled analyzers.

**DO NOT enable all at once**. Systematically identify and enable EVERY disabled analyzer one by one, compiling and fixing all errors after each enablement until ALL analyzers are enabled and ALL diagnostics are resolved.

**Process for Each Analyzer**:
```
Identify disabled analyzer → Enable analyzer → dotnet build → Fix ALL errors → dotnet build (verify clean) → Next analyzer
```

**Only Suppressions Allowed**: Specific test method suppressions (documented below). ALL other diagnostics from ALL analyzers must be fixed to achieve ultimate standard.

## Required Context

- Paths to files that contain the diagnostics.
- Current diagnostic messages for all errors, warnings, and suggestions.
- Applicable logging/event ID conventions for the target code (reuse existing IDs).

## Reasoning Process (for AI Agent)

Before applying fixes, the AI should:
1. **Understand Scope**: Identify all diagnostics (errors/warnings/suggestions) in provided files
2. **CRITICAL - Ultimate Standard Iterative Approach**:
   - **Phase 1**: Assess current state - identify ALL disabled analyzers in configuration
   - **Phase 2**: Create complete enablement plan for ALL disabled analyzers (may include CA1303, CA1848, CA2007, IDE0060, IDE0005, and others)
   - **Phase 3**: Enable ONE disabled analyzer at a time (any order, but systematically)
   - **Phase 4**: Compile and fix ALL resulting errors for that analyzer (no suppressions except test methods)
   - **Phase 5**: Repeat Phases 3-4 for each disabled analyzer until ALL are enabled
   - **Phase 6**: Achieve ultimate standard - zero diagnostics except explicitly allowed test suppressions
3. **Prioritize Fixes**: Errors first, then warnings, then suggestions; safety/performance over style
4. **Preserve Behavior**: Ensure all fixes maintain existing functionality and don't introduce new issues
5. **Zero Tolerance**: End result must have zero diagnostics, all analyzers enabled, no suppressions except explicitly allowed test validations
6. **Validate Results**: Confirm fixes resolve all diagnostics and build succeeds
7. **Forbidden Transformations**: NEVER change `Any()` to `Count() > 0` - this transformation is explicitly prohibited and should be handled separately

## Target Diagnostics

**All analyzer diagnostics from the iterative enablement process** - these examples show types of issues that will appear when enabling each disabled analyzer one-by-one:
- **Errors**: Build-breaking issues that appear when enabling each analyzer (fix ALL before proceeding)
- **Warnings**: Code quality issues surfaced during enablement (fix ALL before proceeding)
- **Suggestions**: Style/best practice recommendations (fix ALL before proceeding)

**IMPORTANT**: These are examples of issues you'll encounter. The process is NOT to fix random diagnostics, but to systematically enable each disabled analyzer from the list and fix every diagnostic that appears.

Specific examples of issues that will appear:
- **CA1062**: Add argument null checks for externally visible methods
- **CA1307**: Use string comparison overloads with `StringComparison`
- **CA1848**: Replace direct logger calls with cached `LoggerMessage` delegates
- **IDE0060**: Remove unused parameters or rename to discards

## Examples (Few-Shot)

### Example 1: CA1062 Null Guard Addition

**Before**:
```csharp
public void ProcessData(string input)
{
    var result = input.ToUpper(); // CA1062: input could be null
}
```

**After**:
```csharp
public void ProcessData(string input)
{
    ArgumentNullException.ThrowIfNull(input);
    var result = input.ToUpper();
}
```

### Example 2: CA1307 String Comparison Fix

**Before**:
```csharp
if (fileName.EndsWith(".json")) // CA1307: Missing StringComparison
{
    // process JSON file
}
```

**After**:
```csharp
if (fileName.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
{
    // process JSON file
}
```

### Example 3: CA1848 LoggerMessage Delegate

**Before**:
```csharp
_logger.LogInformation("Processing file {FileName}", fileName); // CA1848: Direct logger call
```

**After**:
```csharp
private static readonly Action<ILogger, string, Exception?> ProcessFileStart =
    LoggerMessage.Define<string>(LogLevel.Information, new EventId(1001, "ProcessFileStart"),
        "Processing file {FileName}");

ProcessFileStart(_logger, fileName, null);
```

### Example 4: IDE0060 Unused Parameter

**Before**:
```csharp
public void OnTimerElapsed(object sender, EventArgs e) // IDE0060: e is unused
{
    // timer logic here
}
```

**After**:
```csharp
public void OnTimerElapsed(object sender, EventArgs _) // Renamed to discard
{
    // timer logic here
}
```

## Fix Patterns
- **CA1062**: Guard reference parameters at method entry before any dereference.
  ```csharp
  ArgumentNullException.ThrowIfNull(options);
  ArgumentException.ThrowIfNullOrWhiteSpace(filePath);
  ```
- **CA1307**: Add explicit `StringComparison`.
  - `name.EndsWith("Id")` → `name.EndsWith("Id", StringComparison.OrdinalIgnoreCase)`
  - `string.Equals(a, b)` → `string.Equals(a, b, StringComparison.Ordinal)`
- **CA1848**: Define cached `LoggerMessage` delegates and use them.
  ```csharp
  private static readonly Action<ILogger, string, Exception?> ImportStart =
      LoggerMessage.Define<string>(LogLevel.Information, new EventId(1001, "ImportStart"),
          "Starting JSON import from {FilePath}");

  // usage
  Log.ImportStart(_logger, filePath, null);
  ```
  - Place the static `Log` class near the top of the file.
  - Reuse stable event IDs grouped by feature.
- **IDE0060**: If a parameter is unused, rename it to `_` (or `_1`, `_2`). If it should be used, wire it into the logic instead of discarding.

## Forbidden Transformations

**CRITICAL**: The following transformations are explicitly PROHIBITED:

### 🚫 `Any()` → `Count() > 0` Transformation
- **NEVER** change `collection.Any()` to `collection.Count() > 0`
- **NEVER** change `collection.Any(predicate)` to `collection.Count(predicate) > 0`
- **Reason**: This transformation may have performance implications and should be evaluated separately
- **Action**: If you encounter diagnostics suggesting this change, document them separately and do NOT apply the transformation
- **Note**: User will handle this specific issue later or determine if it's a non-fixable problem

#### Why Analyzers Might Incorrectly Suggest This Change
⚠️ **IMPORTANT**: The suggestion to change `Any()` to `Count() > 0` is generally misguided and should be discouraged. `Any()` is ALWAYS more performant than `Count() > 0` for existence checking.

Analyzers may incorrectly recommend `Count() > 0` over `Any()` due to these flawed assumptions:

1. **❌ Misguided ICollection<T> Assumption**: While `Count` is a property (O(1)), `Count() > 0` still requires property access AND comparison. `Any()` short-circuits on first element found - always faster.

2. **❌ False Predicate Consistency**: `Count(predicate) > 0` vs `Any(predicate)` have different purposes. `Any()` is for existence, `Count()` is for counting. Using `Count()` for existence is semantically wrong.

3. **❌ Poor Debugging Justification**: If you need the actual count for debugging, get the count separately. Don't sacrifice performance for debugging convenience.

4. **❌ Questionable LINQ Provider Claims**: Modern LINQ providers (EF Core, LINQ-to-SQL) optimize `Any()` correctly. `Count() > 0` often generates less efficient SQL.

5. **❌ Discouraged Code Style**: Teams preferring `Count() > 0` over `Any()` have outdated performance knowledge. This pattern should be actively discouraged.

**FACT**: `Any()` is ALWAYS more performant than `Count() > 0` because:
- `Any()` stops at the first matching element (short-circuiting)
- `Count() > 0` must process the entire collection to count all elements
- Even with `ICollection<T>`, `Count > 0` still requires property access + comparison vs `Any()`'s optimized enumeration

**Recommendation**: These analyzer suggestions should be suppressed or the analyzer configuration should be updated to not suggest this anti-pattern.

## Process

### CRITICAL: Ultimate Standard - Identify & Enable ALL Disabled Analyzers

**ULTIMATE STANDARD GOAL**: Zero diagnostics across ALL analyzers - achieve perfect code quality.

**DO NOT enable all analyzers at once**. Use this exact iterative approach to reach ultimate standard:

1. **Assess Current State**: Identify ALL disabled analyzers in configuration files (.editorconfig, project files)
2. **Create Enablement Plan**: List all disabled analyzers that need to be enabled (may include CA1303, CA1848, CA2007, IDE0060, IDE0005, and any others currently disabled)
3. **Enable One Analyzer**: Choose ONE disabled analyzer from the complete list
4. **Compile & Fix**: Run build, fix ALL errors that appear from enabling this analyzer
5. **Verify Clean**: Ensure build succeeds with zero new errors for this analyzer
6. **Repeat**: Enable next analyzer, compile, fix errors, repeat until ALL analyzers are enabled
7. **Ultimate Validation**: Confirm zero diagnostics remain except explicitly allowed test suppressions

**Iteration Pattern for Ultimate Standard**:
```
For each disabled analyzer in complete list:
  1. Enable analyzer in configuration (change severity from "none" to "warning"/"error")
  2. dotnet build
  3. Fix ALL compilation errors from this analyzer (no suppressions except test methods)
  4. dotnet build (verify clean for this analyzer)
  5. Move to next disabled analyzer
  6. Repeat until ALL analyzers enabled and ALL diagnostics resolved
```

### Step 1: Scope Analysis
- Identify all files containing any diagnostics (errors/warnings/suggestions)
- Confirm files are within provided scope boundaries
- Count total diagnostics by severity to track progress
- **Flag Forbidden Transformations**: Identify any diagnostics that would require the forbidden `Any()` → `Count() > 0` transformation

### Step 2: Current State Assessment
- Check which analyzers are currently enabled vs disabled
- Start with currently active analyzers only
- Document baseline diagnostic count before enabling additional analyzers

### Step 3: Iterative Analyzer Enablement
For each disabled analyzer in the list above:
- **Enable**: Change severity from "none" to "warning" or "error" in configuration
- **Compile**: Run `dotnet build` to see new diagnostics
- **Fix All**: Resolve every diagnostic introduced by this analyzer
- **Verify**: Build succeeds with zero new errors
- **Document**: Record what was fixed for this analyzer

### Step 4: Allowed Suppressions (Test Methods Only)
Only these specific suppressions are allowed:
- **Test Method Parameter Suppressions**: `[SuppressMessage("IDE0060", "Remove unused parameter", Justification = "Required for test method signature consistency")]`
- **Test Setup/Teardown Suppressions**: `[SuppressMessage("CA1303", "Do not pass literals as localized parameters", Justification = "Test strings don't need localization")]`
- **Reason**: Test methods often have required signatures or use literal strings for testing

**NO OTHER SUPPRESSIONS ALLOWED**. Fix all other diagnostics.

### Step 5: Validation
- Run `dotnet build` to verify no errors
- Run `dotnet format analyzers --include <paths>` to check all severities
- Confirm zero diagnostics at all levels (except explicitly allowed test suppressions)
- Validate that functionality remains unchanged

### Step 6: Report Results
- Summarize analyzers enabled and fixes applied for each
- Confirm zero diagnostics remain (with only allowed test suppressions)
- Provide confidence level in complete resolution

## Expected Output

**Code Changes**:
- Modified source files with all diagnostics resolved through iterative analyzer enablement
- Each disabled analyzer enabled one-by-one, compiled, and all errors fixed before proceeding
- Only allowed suppressions are specific test method suppressions (see Process section)
- No behavioral changes to existing functionality
- Preserved code formatting and style

**Validation Report**:
```markdown
## Ultimate Standard - ALL Analyzers Enabled

### All Disabled Analyzers Identified & Enabled (One By One)
[List will vary based on actual disabled analyzers found]

1. **[Analyzer ID]** ([Analyzer Description])
   - Files modified: [count]
   - Fixes applied: [specific changes]

2. **[Analyzer ID]** ([Analyzer Description])
   - Files modified: [count]
   - Fixes applied: [specific changes]

[... continues for ALL disabled analyzers that were enabled ...]

### Allowed Suppressions Applied (Test Methods Only)
- Test parameter suppressions: [count] `[SuppressMessage("IDE0060", ...)]`
- Test string suppressions: [count] `[SuppressMessage("CA1303", ...)]`
- Justification: Required for test method signatures and test data

### Forbidden Transformations (Not Applied)
- Any() → Count() > 0 suggestions: [count] identified but NOT fixed
- Files with forbidden transformations: [list of files]

### Validation Results
✅ `dotnet build` succeeds after each analyzer enablement
✅ All analyzers now enabled (previously disabled ones activated)
✅ Zero diagnostics except explicitly allowed test suppressions
✅ No functional changes introduced
✅ Iterative process completed: enable → compile → fix → repeat

### Final State
- All previously disabled analyzers now enabled and clean
- Zero errors, zero warnings, zero suggestions (except allowed test suppressions)
- Code compiles cleanly with all analyzers active
- Only suppressions are documented test method exceptions
```

**Change Details**:
- Specific line numbers and changes made
- Rationale for each fix applied
- Any edge cases handled

## Quality Checklist
- [ ] ALL disabled analyzers identified in configuration files (.editorconfig, project files)
- [ ] Iterative process followed: each disabled analyzer enabled one-by-one
- [ ] After each analyzer enablement: compiled successfully and all errors fixed
- [ ] ALL previously disabled analyzers now enabled and clean (verified individually)
- [ ] Only allowed suppressions applied (test methods only):
  - [ ] Test parameter suppressions: `[SuppressMessage("IDE0060", ...)]`
  - [ ] Test string suppressions: `[SuppressMessage("CA1303", ...)]`
- [ ] Zero diagnostics remain at all severity levels (except explicitly allowed test suppressions)
- [ ] All analyzers enabled, no other suppressions in final state
- [ ] `dotnet build` passes with all analyzers active
- [ ] Forbidden transformations (Any() → Count() > 0) properly documented and not applied

## Troubleshooting

### Issue: CA1062 diagnostics persist after adding guards
**Cause**: Guards added in wrong location or insufficient coverage
**Solution**: Ensure `ArgumentNullException.ThrowIfNull()` is called immediately after method entry, before any dereference of the parameter

### Issue: CA1848 LoggerMessage not recognized
**Cause**: Missing `using Microsoft.Extensions.Logging;` or incorrect delegate definition
**Solution**: Add using statement and verify delegate signature matches the log call

### Issue: StringComparison overload not available
**Cause**: Using older .NET version that doesn't support StringComparison
**Solution**: Use explicit `string.Equals(a, b, StringComparison.Ordinal)` instead of method chaining

### Issue: Any() → Count() > 0 transformation diagnostics remain
**Cause**: Analyzer suggests changing `Any()` to `Count() > 0` but this transformation is forbidden
**Solution**: This is expected behavior. These diagnostics should remain unfixed as per the forbidden transformations rule. Document them separately for manual review.

### Issue: dotnet format analyzers command fails
**Cause**: dotnet-format tool not installed or wrong syntax
**Solution**: Install with `dotnet tool install -g dotnet-format` and use correct syntax

## Usage Modes

### Quick Fix Mode
For single files with specific diagnostics:
```
@fix-info-lines src/Services/PaymentService.cs
```

### Batch Fix Mode
For entire directories or multiple files:
```
@fix-info-lines src/ --batch
```

### Targeted Fix Mode
For specific diagnostic types:
```
@fix-info-lines src/ --only CA1062,CA1848
```

## Related Prompts

- `code-quality/validate-code-quality.prompt.md` - Comprehensive code quality validation
- `code-quality/fix-warnings.prompt.md` - Fix warning-level diagnostics
- `code-quality/add-xml-documentation.prompt.md` - Add missing XML documentation
- `logging/standardize-logging.prompt.md` - Standardize logging patterns

## Related Rules

- `.cursor/rules/quality/zero-warnings-zero-errors-rule.mdc` - Zero tolerance for warnings/errors
- `.cursor/rules/quality/code-quality-enforcement-rule.mdc` - Code quality enforcement standards
- `.cursor/rules/documentation/documentation-standards-rule.mdc` - Documentation requirements
- `.cursor/rules/diagnostic-messages-agent-application-rule.mdc` - Diagnostic message quality

## Usage
```
@fix-info-lines src/Services/ImportService.cs
```

---

**Created**: 2025-12-13
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Enhanced**: 2025-12-13 (Prompt optimization workflow)
