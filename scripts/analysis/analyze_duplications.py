#!/usr/bin/env python3
"""
Analyze code duplication in the codebase.
"""
import hashlib
import os
import re
from collections import defaultdict

src_dir = "src"

# Pattern definitions
logger_init = re.compile(r"logger\s*=\s*logging\.getLogger\(__name__\)")
validation_pattern = re.compile(r"def\s+(validate_\w+|_validate_\w+)\(")
import_pattern = re.compile(r"^from\s+([\w.]+)\s+import", re.MULTILINE)
error_pattern = re.compile(r"try:.*?except\s+\w+\s+as\s+e:", re.DOTALL)
dataclass_pattern = re.compile(r"@dataclass\s+class\s+(\w+)")
basemodel_pattern = re.compile(r"class\s+(\w+)\(BaseModel\)")

# Collect files
py_files = []
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith(".py"):
            py_files.append(os.path.join(root, file))

print(f"Analyzing {len(py_files)} Python files...")
print("=" * 80)
print()

# 1. Logger initializations
logger_files = []
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            if logger_init.search(content):
                logger_files.append(filepath.replace(os.sep, "/"))
    except Exception as e:
        pass

print(f"1. DUPLICATE LOGGER INITIALIZATION: {len(logger_files)} files")
print(f"   Suggestion: Create a base logger utility")
print()

# 2. Validation functions
validation_funcs = defaultdict(list)
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                match = validation_pattern.search(line)
                if match:
                    func_name = match.group(1)
                    validation_funcs[func_name].append((filepath.replace(os.sep, "/"), i))
    except Exception as e:
        pass

dup_validations = {k: v for k, v in validation_funcs.items() if len(v) > 1}
print(f"2. DUPLICATE VALIDATION FUNCTIONS: {len(dup_validations)} function names")
for func, locations in sorted(dup_validations.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"   {func}: {len(locations)} occurrences")
    for loc in locations[:3]:
        print(f"      - {loc[0]}:{loc[1]}")
print()

# 3. Common imports
from_imports = defaultdict(list)
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            imports = import_pattern.findall(content)
            for imp in imports:
                from_imports[imp].append(filepath.replace(os.sep, "/"))
    except Exception as e:
        pass

common_imports = {k: v for k, v in from_imports.items() if len(v) > 50}
print(f"3. MOST COMMON IMPORTS: {len(common_imports)} import sources used >50 times")
for imp, files in sorted(common_imports.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"   {imp}: {len(files)} files")
print()

# 4. Error handling patterns
error_blocks = defaultdict(list)
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if "try:" in line:
                    error_blocks["try_except"].append((filepath.replace(os.sep, "/"), i))
                if "except Exception as e:" in line:
                    error_blocks["generic_except"].append((filepath.replace(os.sep, "/"), i))
    except Exception as e:
        pass

print(f"4. ERROR HANDLING PATTERNS")
print(f'   Try blocks: {len(error_blocks["try_except"])} occurrences')
print(f'   Generic except: {len(error_blocks["generic_except"])} occurrences')
print()

# 5. Dataclass/Pydantic models
dataclasses = defaultdict(list)
basemodels = defaultdict(list)
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                dc_match = dataclass_pattern.search(line)
                if dc_match:
                    dataclasses[dc_match.group(1)].append((filepath.replace(os.sep, "/"), i))
                bm_match = basemodel_pattern.search(line)
                if bm_match:
                    basemodels[bm_match.group(1)].append((filepath.replace(os.sep, "/"), i))
    except Exception as e:
        pass

dup_dataclasses = {k: v for k, v in dataclasses.items() if len(v) > 1}
dup_basemodels = {k: v for k, v in basemodels.items() if len(v) > 1}
print(f"5. DUPLICATE MODEL NAMES")
print(f"   Duplicate @dataclass names: {len(dup_dataclasses)}")
for name, locations in sorted(dup_dataclasses.items(), key=lambda x: -len(x[1]))[:5]:
    print(f"      {name}: {len(locations)} occurrences")
print(f"   Duplicate BaseModel names: {len(dup_basemodels)}")
for name, locations in sorted(dup_basemodels.items(), key=lambda x: -len(x[1]))[:5]:
    print(f"      {name}: {len(locations)} occurrences")
print()

# 6. Find files with similar structures
print("6. SIMILAR FILE STRUCTURES")
file_structures = defaultdict(list)
for filepath in py_files:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract function signatures
            funcs = re.findall(r"^(async )?def\s+(\w+)\(", content, re.MULTILINE)
            if len(funcs) > 3:
                sig = tuple(sorted([f[1] for f in funcs]))
                file_structures[sig].append(filepath.replace(os.sep, "/"))
    except Exception as e:
        pass

similar = {k: v for k, v in file_structures.items() if len(v) > 1}
print(f"   Files with identical function signatures: {len(similar)} groups")
for sigs, files in sorted(similar.items(), key=lambda x: -len(x[1]))[:3]:
    print(f"   {len(files)} files with similar structure:")
    for f in files[:3]:
        print(f"      - {f}")
print()

print("=" * 80)
print("Analysis complete!")
