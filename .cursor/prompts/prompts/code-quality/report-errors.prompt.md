---
name: report-errors
description: "Systematically diagnose and fix errors from compiler/runtime/linter"
category: code-quality
tags: code-quality, errors, debugging, diagnosis, compilation
argument-hint: "Paste exact error messages in <error_messages> tags"
---

# Report Errors (Pattern-Based)

This prompt enables systematic error diagnosis by providing exact error messages to the AI.

**Pattern**: Error List Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: 100% diagnosis accuracy with exact error text  
**Use When**: Compilation errors, runtime errors, linter warnings, test failures

---

## Required Context

- **Error Messages**: Exact error text from compiler/runtime/linter (copy-paste)
- **Context** (Optional but helpful): What changed before errors appeared

---

## Reasoning Process

The AI should:
1. **Parse All Errors**: Read complete error list, don't stop at first error
2. **Identify Patterns**: Group related errors (e.g., all null reference warnings)
3. **Find Root Cause**: Determine which error(s) are primary vs secondary symptoms
4. **Propose Solution**: Fix root cause, which often resolves multiple symptoms
5. **Validate**: Ensure proposed fix addresses all related errors

---

## Basic Usage

**Just paste the exact error messages. No preamble needed.**

```
<error_messages>
[PASTE EXACT ERROR TEXT HERE]
</error_messages>
```

**Note**: Using XML delimiters `<error_messages>` prevents context bleeding for large error lists.

---

## Examples

### Compilation Errors
```
'ExportMetadata' does not implement interface member 'IExportMetadata.BusinessDescription'

'ExportMetadata' does not implement interface member 'IExportMetadata.DomainTypeName'

'ExportMetadata' does not implement interface member 'IExportMetadata.GetColumnDefinitions()'

Dereference of a possibly null reference.

The type or namespace name 'IExportColumnMetadata' could not be found (are you missing a using directive or an assembly reference?)
```

### Runtime Errors
```
System.NullReferenceException: Object reference not set to an instance of an object.
   at MyApp.Service.ProcessData(String input) in C:\Projects\MyApp\Service.cs:line 42
   at MyApp.Controller.HandleRequest() in C:\Projects\MyApp\Controller.cs:line 18
```

### Test Failures
```
Failed   Test1
Error Message:
   Expected: 42
   Actual:   0
   at MyApp.Tests.CalculatorTests.Add_ShouldReturnSum() in CalculatorTests.cs:line 23

Failed   Test2
Error Message:
   Assert.IsNotNull failed.
```

### Linter Warnings
```
CS8600: Converting null literal or possible null value to non-nullable type.
CS8625: Cannot convert null literal to non-nullable reference type.
CS8602: Dereference of a possibly null reference.
```

---

## What This Pattern Does

✅ AI analyzes all errors for patterns  
✅ AI identifies root causes (not just symptoms)  
✅ AI proposes fixes for all related errors  
✅ AI often fixes multiple errors in one pass  
✅ File/line information helps locate problems precisely  

---

## Best Practices

### ✅ Do This:
- Paste **exact** error text (copy from terminal/IDE)
- Include **all** errors (not just the first one)
- Include **file paths and line numbers** if available
- Include **stack traces** for runtime errors
- Keep errors from **same build/run** together

### ❌ Don't Do This:
- Paraphrase errors ("something about null reference")
- Only paste first error (might not be root cause)
- Mix errors from different builds
- Add extra commentary before errors
- Omit error codes (CS8602, etc.)

---

## With Optional Context

If errors appeared after a specific change:

```
These errors appeared after [WHAT CHANGED]:

[PASTE ERROR LIST]
```

### Example
```
These errors appeared after adding IParentReferenceResolver:

'ExportMetadata' does not implement interface member 'IExportMetadata.GetColumnDefinitions()'
[... more errors ...]
```

---

## Filtering Requests

If you want to prioritize:

```
Fix these critical errors first:
[ERROR LIST]

(ignore the warnings for now)
```

---

## Expected AI Response

AI will:
1. **Analyze** all errors for patterns
2. **Identify** root causes
3. **Propose** fixes (typically file-by-file)
4. **Implement** fixes systematically
5. **Explain** what was wrong

---

## Follow-up Workflow

### Iteration Pattern

**Round 1:**
```
[paste error list]
```
→ AI fixes batch 1

**Round 2: Compile again, paste new errors**
```
[paste remaining errors]
```
→ AI fixes batch 2

**Round 3: Verify**
```
all compiles now, no errors, not even warnings
```
→ Done!

---

## Common Error Categories

### Interface Implementation
```
'ClassName' does not implement interface member 'IInterface.MethodName'
```

### Null Reference
```
Dereference of a possibly null reference.
Possible null reference argument for parameter 'name'
```

### Missing Type/Namespace
```
The type or namespace name 'TypeName' could not be found
```

### Async/Await
```
This async method lacks 'await' operators and will run synchronously.
```

---

## Multi-Repo Errors

If errors span multiple repositories:

```
Errors in DataMigrator repo:
[error list]

Errors in Foundation repo:
[error list]

(These may be related)
```

---

## Tips

- **Paste raw** - copy directly from terminal/IDE
- **Full context** - include all lines of each error
- **Group related** - errors from same build together
- **Be patient** - complex error chains may need multiple rounds
- **Verify fixes** - compile after each batch

---

## Success Indicators

✅ Error count decreases each iteration  
✅ Root causes fixed (not just symptoms)  
✅ Fixes don't introduce new errors  
✅ Final: Clean compilation with no warnings  

---

## Anti-Pattern (Don't Do This)

❌ **Paraphrasing**:
```
I'm getting some interface implementation errors and null reference warnings
```
→ Too vague, AI can't locate problem

✅ **Exact errors**:
```
'ExportMetadata' does not implement interface member 'IExportMetadata.BusinessDescription'
Dereference of a possibly null reference.
```
→ AI knows exactly what to fix

---

## Expected AI Response

When you provide errors, the AI should:

1. **Acknowledge Error Count**
   ```
   Analyzing [N] errors...
   ```

2. **Categorize Errors**
   ```
   Found error patterns:
   - [N] Interface implementation issues
   - [N] Null reference warnings
   - [N] Missing type definitions
   ```

3. **Identify Root Cause**
   ```
   Root cause: [Primary issue causing cascade]
   Secondary issues: [Issues that will resolve when root fixed]
   ```

4. **Propose Fix**
   ```
   Fixing [file.cs]:
   - Add missing interface members
   - Add null checks
   - Add using statement for [namespace]
   ```

5. **Implement Fixes** (file-by-file)
   - Make changes systematically
   - Explain each fix
   - Anticipate which errors will clear

---

## Quality Criteria

Before claiming errors resolved, verify:

- [ ] All errors analyzed (not just first one)
- [ ] Root cause identified (not just symptoms)
- [ ] Fix proposed for all related errors
- [ ] Changes implemented systematically
- [ ] No new errors introduced by fixes
- [ ] User instructed to recompile and report remaining errors

---

## Iteration Pattern

For large error lists, expect multiple rounds:

**Round 1**: Paste all errors → AI fixes primary batch  
**Round 2**: Recompile, paste remaining errors → AI fixes next batch  
**Round 3**: Recompile, confirm clean build → Done

---

## Related Prompts

- `code-quality/iterative-refinement.md` - For fixing specific issues after errors cleared
- `ticket/activate-ticket.md` - Return to ticket work after fixing errors

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)  
**Pattern ID**: #5 Error List Pattern  
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0

